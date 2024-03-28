import pandas as pd
from datetime import datetime
import holidays 



def main():
    #define your main data frame
    df=pd.read_csv(r'YOUR FILEPATH TO YOUR RESERVATION CSV') #RESERVATION SUMMARY CSV
    df_billing = pd.read_csv(r'YOUR FILEPATH TO YOUR BILLING SCHEUDLE CSV') #BILLINGSCHEDULE COMPLETED CSV
    company = input('Choose which Company\n')
    #create dataframe per company
    df_company = company_df(df,company)

    # display reservation trans charge plus
    reservation(df_company)
    # display Ancillary Services 
    ancillary(df_company,df_billing,company)

    #display Power losses
   # power_losses(df_billing,company)
    


#check if hourly is on peak or off peak
#only care about the STOP_TIME, in format of 2023-11-28 08:00:00 PS
def time_check(date):
    #select USA
    us_holidays = holidays.US()
    date_nozone = date[0:19]
    print(date_nozone)
    datetime_object = datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
    #if on sunday
    if datetime_object.weekday() == 6:
        return False
    elif datetime_object in us_holidays:
        return False
    elif datetime_object.hour < 7 | datetime_object.hour>22:
        return True 






#create dataframe of reservation csv per company 
def company_df(dataframe,company):
    df_company = dataframe.loc[dataframe['CUSTOMER'] == company]
    df_company = df_company[['CUSTOMER','AREF', 'INCREMENT', 'MW_GRANTED', 'MWHr', 'BILLING_RATE', 'PRICE_UNITS', 'TRANS_CHARGE','START_TIME','STOP_TIME', 'POR', 'POD', 'REQUEST_TYPE','SOURCE','SINK']]
    df_company.sort_values(by=['INCREMENT','START_TIME'], inplace = True)
    return df_company 



#show the reservation charge
def reservation(df_company):
    print(f"This is your TransCharge for {df_company.iloc[0]['CUSTOMER']}: ${df_company['TRANS_CHARGE'].sum().round(decimals=2)}")
    print(df_company.head(10))
    #print(df_company.head(5)) #eaisly see first 5 charges 
          
#show the ancillary charge
def ancillary(dataframe_res,dataframe_bill,company): #note the ancillary will need the df_res, df_bill csv, and the company for df_bill
    Yearly_Service = {'Schedule 1': 119.0833, 'Schedule 2': 173.1667, 'Schedule 3': 111.2, 'Schedule 5': 498, 'Schedule 6': 113.3333, 'Schedule 10': 117.75}
    Monthly_Service = {'Schedule 1':119.0833, 'Schedule 2': 173.000}
    Weekly_Service = {'Schedule 1': 27, 'Schedule 2': 40}
    Daily_Service= {'Schedule 1': 4, 'Schedule 2': 6}
    
    schedule_conditions = [('TOLUCA','MPPGEN'),('TOLUCA','BURBSYSTEM'), ('AIRWAY', 'AIRWAY'), ('IPP', 'IPP'), ('LASYSTEM','LASYSTEM')]

    us_holidays = holidays.US() # used later on 
    Hourly_Service_OP = {'Schedule 1': 0.344, 'Schedule 2':0.499, 'Schedule 3':0.340, 'Schedule 5':1.437,'Schedule 6':0.327, 'Schedule 10':0.34}
    Hourly_Service_OFFP = {'Schedule 1':0.163, 'Schedule 2':0.237, 'Schedule 3':0.161,'Schedule 5':0.682, 'Schedule 6':0.155, 'Schedule 10':0.161}
    #lets create a dataframe for each increment
    # add the mw per increment 

    dataframe = dataframe_res.loc[(dataframe_res['REQUEST_TYPE'] == 'ORIGINAL') | (dataframe_res['REQUEST_TYPE'] == 'DEFERRAL') | (dataframe_res['REQUEST_TYPE'] == 'RENEWAL')]
    # pull in billing schedule csv
    df_bill = dataframe_bill
    df_bill = df_bill.loc[(df_bill['Customer Code'] == company)]
    df_bill.reset_index(drop=True,inplace=True) # rearrange new dataframe for company to have a new index 
    schedule_3_bool = False #initalize to False 
    schedule_5_bool = False #initalize to False 
    schedule_10_bool = False # initialize to False 
    ##yearly
    df_yearly = dataframe.loc[dataframe['INCREMENT'] == 'YEARLY']
    total_mw_yearly = df_yearly['MW_GRANTED'].sum()
   
    # for Sched 1 and Sched 2
    schedule_1_yearly = total_mw_yearly * Yearly_Service['Schedule 1']
    schedule_2_yearly = total_mw_yearly * Yearly_Service['Schedule 2']
    #for schedule 3
    for i in df_bill.index:
        if (df_bill['POD'][i],df_bill['Sink'][i]) in schedule_conditions:
            schedule_3_bool= True 
    schedule_3_yearly = total_mw_yearly* Yearly_Service['Schedule 3']
    # for schedule 5 and 6
    for i in df_bill.index:
        if (df_bill['POR'][i], df_bill['Source'][i]) or (df_bill['POD'][i], df_bill['Sink'][i]) in schedule_conditions:
            schedule_5_bool = True
    schedule_5_yearly = total_mw_yearly * Yearly_Service['Schedule 5']
    schedule_6_yearly = total_mw_yearly * Yearly_Service['Schedule 6']
    # for schedule 10 
    for i in df_bill.index:
        if (df_bill['POR'][i], df_bill['Source'][i]) in schedule_conditions:
            schedule_10_bool = True
    schedule_10_yearly = total_mw_yearly* Yearly_Service['Schedule 10']
    
    # add up total ancillary service charges 
    if schedule_3_bool and schedule_5_bool and schedule_10_bool:
        total_ancillary_yearly = schedule_1_yearly + schedule_2_yearly + schedule_5_yearly + schedule_6_yearly + schedule_10_yearly # given both sched 3 and sched 5 are true use sched 5 for total. 
    elif schedule_10_bool and schedule_3_bool and not schedule_5_bool:
        total_ancillary_yearly = schedule_1_yearly + schedule_2_yearly + schedule_3_yearly + schedule_10_yearly
    elif not schedule_3_bool and schedule_5_bool and schedule_10_bool:
        total_ancillary_yearly = schedule_1_yearly + schedule_2_yearly + schedule_5_yearly + schedule_6_yearly + schedule_10_yearly 
    else:
        total_ancillary_yearly = schedule_1_yearly + schedule_2_yearly
    


    print_yearly = f''' 
    Yearly: {total_mw_yearly}MW
    Schedule 1 = ${schedule_1_yearly}
    Schedule 2 = ${schedule_2_yearly}
    Schedule 3 = ${schedule_3_yearly}
    Schedule 5 = ${schedule_5_yearly}
    Schedule 6 = ${schedule_6_yearly}
    Schedule 10 = ${schedule_10_yearly}
    Total Ancillary Yearly = ${total_ancillary_yearly.round(decimals=2)}
    '''
    print(print_yearly)

    ##monthly
    df_monthly = dataframe.loc[dataframe['INCREMENT'] == 'MONTHLY']
    total_mw_monthly = df_monthly['MW_GRANTED'].sum()
    # for Sched 1 and Sched 2
    schedule_1_monthly = total_mw_monthly * Monthly_Service['Schedule 1']
    schedule_2_monthly = total_mw_monthly * Monthly_Service['Schedule 2']
    print_monthly = f'''
    Monthly:
    Schedule 1 = {schedule_1_monthly}
    Schedule 2 = {schedule_2_monthly}
    '''
    print(print_monthly)

    ##weekly
    df_weekly = dataframe.loc[dataframe['INCREMENT'] == 'WEEKLY']
    total_mw_weekly = df_weekly['MW_GRANTED'].sum()
    # for Sched 1 and Sched 2
    schedule_1_weekly = total_mw_weekly * Weekly_Service['Schedule 1']
    schedule_2_weekly = total_mw_weekly * Weekly_Service['Schedule 2']
    print_weekly = f'''
    Weekly:
    Schedule 1 = {schedule_1_weekly}
    Schedule 2 = {schedule_2_weekly}
    '''
    print(print_weekly)

    ##daily 
    df_daily = dataframe.loc[dataframe['INCREMENT'] == 'DAILY']
    total_mw_daily = df_daily['MW_GRANTED'].sum()
    # for Sched 1 and Sched 2
    schedule_1_daily = total_mw_daily * Daily_Service['Schedule 1']
    schedule_2_daily = total_mw_daily * Daily_Service['Schedule 2']
    print_daily = f'''
    Daily:
    Schedule 1 = {schedule_1_daily}
    Schedule 2 = {schedule_2_daily}
    '''
    print(print_daily)

    ##hourly
    # ON PEAK is between 0700 - 2200 
    # OFF PEAK is holidays, sundays, and any other time 
    #only care about the STOP_TIME, in format of 2023-11-28 08:00:00 PS

    df_hourly = dataframe.loc[dataframe['INCREMENT'] == 'HOURLY']
    #print(df_hourly)
    df_hourly.reset_index(drop=True,inplace=True) # rearragne new df_hourly 
    #print(df_hourly['START_TIME'])
    stop_time_noTZ=df_hourly['STOP_TIME'].str[:-2] # removes timezone for stop time
    start_time_noTZ = df_hourly['START_TIME'].str[:-2] #removes timezone for start time 
    #print(start_time_noTZ)
    df_hourly.loc[:,'STOP_TIME'] = stop_time_noTZ # replaces the column stop time with the series without timezone 
    df_hourly.loc[:,'START_TIME'] = start_time_noTZ #replaces the column start time with the series without timezone 
    #print(df_hourly['START_TIME'])
    df_hourly['STOP_TIME'] = pd.to_datetime(df_hourly['STOP_TIME']) # replaces str object in column to datetime object 
    df_hourly['START_TIME'] = pd.to_datetime(df_hourly['START_TIME'])
    total_mw_onpeak_hourly = 0 #initialize 
    total_mw_offpeak_hourly = 0 #initialize 
    #calculated total MW on peak 
    for i in df_hourly.index:
        if df_hourly['START_TIME'][i] in us_holidays or df_hourly['STOP_TIME'][i] in us_holidays or df_hourly['STOP_TIME'][i].day_of_week == 6: #is a us holiday or a sunday 
            mw_offpeak=df_hourly['MWHr'][i] # MW generated Per HOUR
            total_mw_offpeak_hourly += mw_offpeak
        elif df_hourly['START_TIME'][i].hour < 7 and df_hourly['STOP_TIME'][i].hour > 22: #conditions of 0500-2300
            mw_offpeak_multipler_1 = 6 - df_hourly['START_TIME'][i].hour # should be 7 which is start time of on peak minus diff
            mw_offpeak_multipler_2 = df_hourly['STOP_TIME'][i].hour - 22 # should be stoptime minus 22
            mw_offpeak_multipler = mw_offpeak_multipler_1 + mw_offpeak_multipler_2
            total_mw_offpeak_hourly += df_hourly['MW_GRANTED'][i] * mw_offpeak_multipler 
            total_mw_onpeak_hourly += df_hourly['MW_GRANTED'][i] * 15 # 15 is the range from 0700 - 2200
        elif df_hourly['START_TIME'][i].hour < 7 and df_hourly['STOP_TIME'][i].hour in range(7,23): # conditions of 0500 - 2200
            mw_offpeak_multipler = 6 - df_hourly['START_TIME'][i].hour
            total_mw_offpeak_hourly += df_hourly['MW_GRANTED'][i] * mw_offpeak_multipler
            total_mw_onpeak_hourly += df_hourly['MW_GRANTED'][i] * ((df_hourly['STOP_TIME'][i].hour) - 6) #your stop time - 6 is on peak multipler
        elif df_hourly['START_TIME'][i].hour < 7 and df_hourly['STOP_TIME'][i].hour < 7: #0000-0700
            mw_offpeak= df_hourly['MWHr'][i]
            total_mw_offpeak_hourly += mw_offpeak
        elif df_hourly['START_TIME'][i].hour in range(6,23) and df_hourly['STOP_TIME'][i].hour > 22: #conditions of 1900 -2300
            mw_offpeak_multipler = df_hourly['STOP_TIME'][i].hour - 22
            total_mw_offpeak_hourly += df_hourly['MW_GRANTED'][i] * mw_offpeak_multipler
            total_mw_onpeak_hourly += df_hourly['MW_GRANTED'][i] * (22-(df_hourly['START_TIME'][i].hour)) # 22- startime is on peak multipler 
        elif df_hourly['START_TIME'][i].hour > 6 and df_hourly['STOP_TIME'][i].hour in range(7,23): #conditions of 0700 - 2200
            mw_onpeak=df_hourly['MWHr'][i] #MW generated PER HOUR
            total_mw_onpeak_hourly += mw_onpeak 
        elif df_hourly['START_TIME'][i].hour >= 22 and df_hourly['STOP_TIME'][i].hour < 7: #conditions of 2300 - 0600
            mw_offpeak_multipler =  (24 - df_hourly['START_TIME'][i].hour) + df_hourly['STOP_TIME'][i].hour 
            total_mw_offpeak_hourly += mw_offpeak_multipler * df_hourly["MW_GRANTED"][i] 
        elif df_hourly['START_TIME'][i].hour < 6 and df_hourly['STOP_TIME'][i].hour < 7: # conditions of 0000-0100
            total_mw_offpeak_hourly += df_hourly['MWHr'][i]
        #elif df_hourly['START_TIME'][i].hour > 22 and df_hourly['STOP_TIME'][i].hour < 7
            
    #hourly_sched 1 and 2
    schedule_1_hourly_op = total_mw_onpeak_hourly * Hourly_Service_OP['Schedule 1']
    schedule_2_hourly_op = total_mw_onpeak_hourly * Hourly_Service_OP['Schedule 2']
    schedule_1_hourly_offp = total_mw_offpeak_hourly * Hourly_Service_OFFP['Schedule 1']
    schedule_2_hourly_offp = total_mw_offpeak_hourly * Hourly_Service_OFFP['Schedule 2']

    #hourly_sched 3
    schedule_3_hourly_op = total_mw_onpeak_hourly * Hourly_Service_OP['Schedule 3']
    schedule_3_hourly_offp = total_mw_offpeak_hourly * Hourly_Service_OFFP['Schedule 3']

    #hourly_sched 5
    schedule_5_hourly_op = total_mw_onpeak_hourly * Hourly_Service_OP['Schedule 5']
    schedule_5_hourly_offp = total_mw_offpeak_hourly * Hourly_Service_OFFP['Schedule 5']

    #hourly_sched 6
    schedule_6_hourly_op = total_mw_onpeak_hourly * Hourly_Service_OP['Schedule 6']
    schedule_6_hourly_offp = total_mw_offpeak_hourly * Hourly_Service_OFFP['Schedule 6']

    #hourly_sched 10
    schedule_10_hourly_op = total_mw_onpeak_hourly * Hourly_Service_OP['Schedule 10']
    schedule_10_hourly_offp = total_mw_offpeak_hourly * Hourly_Service_OFFP['Schedule 10']


    
    
    if schedule_3_bool and schedule_5_bool and schedule_10_bool:
        total_ancillary_hourly_op = schedule_1_hourly_op + schedule_2_hourly_op + schedule_5_hourly_op + schedule_6_hourly_op + schedule_10_hourly_op #prices
        total_ancillary_hourly_offp = schedule_1_hourly_offp + schedule_2_hourly_offp + schedule_5_hourly_offp + schedule_6_hourly_offp + schedule_10_hourly_offp  #prices
        total_ancillary_hourly = total_ancillary_hourly_op + total_ancillary_hourly_offp #prices
        total_ancillary_hourly.round(2)
        print_hourly = f'''
        Hourly:
    
        On Peak: {total_mw_onpeak_hourly}MW                           
        Schedule 1: ${schedule_1_hourly_op}
        Schedule 2: ${schedule_2_hourly_op}
        Schedule 5: ${schedule_5_hourly_op}
        Schedule 6: ${schedule_6_hourly_op}
        Schedule 10: ${schedule_10_hourly_op}
        
        Off Peak: {total_mw_offpeak_hourly}MW
        Schedule 1: ${schedule_1_hourly_offp}
        SChedule 2: ${schedule_2_hourly_offp}
        Schedule 5: ${schedule_5_hourly_offp}
        Schedule 6: ${schedule_6_hourly_offp}
        Schedule 10: ${schedule_10_hourly_offp}

        Total Ancillary Hourly = ${round(total_ancillary_hourly,2)}
        '''
        


    
    
    elif schedule_10_bool and schedule_3_bool and not schedule_5_bool:
        total_ancillary_hourly_op = schedule_1_hourly_op + schedule_2_hourly_op + schedule_3_hourly_op + schedule_10_hourly_op # no sched 5
        total_ancillary_hourly_offp = schedule_1_hourly_offp + schedule_2_hourly_offp + schedule_3_hourly_offp + schedule_10_hourly_offp #no sched 5
        total_ancillary_hourly = total_ancillary_hourly_op + total_ancillary_hourly_offp
        print_hourly = f'''
        Hourly:
    
        On Peak: {total_mw_onpeak_hourly}MW                           
        Schedule 1: ${schedule_1_hourly_op}
        Schedule 2: ${schedule_2_hourly_op}
        Schedule 3: ${schedule_3_hourly_op}
        Schedule 10: ${schedule_10_hourly_op}
        
        Off Peak: {total_mw_offpeak_hourly}MW
        Schedule 1: ${schedule_1_hourly_offp}
        SChedule 2: ${schedule_2_hourly_offp}
        Schedule 3: ${schedule_3_hourly_offp}
        Schedule 10: ${schedule_10_hourly_offp}

        Total Ancillary Hourly = ${round(total_ancillary_hourly,2)}
        '''
    elif not schedule_3_bool and schedule_5_bool and schedule_10_bool:
        total_ancillary_hourly_op = schedule_1_hourly_op + schedule_2_hourly_op + schedule_5_hourly_op + schedule_6_hourly_op + schedule_10_hourly_op
        total_ancillary_hourly_offp = schedule_1_hourly_offp + schedule_2_hourly_offp + schedule_5_hourly_offp + schedule_6_hourly_offp + schedule_10_hourly_offp 
        total_ancillary_hourly = total_ancillary_hourly_op + total_ancillary_hourly_offp
        print_hourly = f'''
        Hourly:
    
        On Peak: {total_mw_onpeak_hourly}MW                           
        Schedule 1: ${schedule_1_hourly_op}
        Schedule 2: ${schedule_2_hourly_op}
        Schedule 5: ${schedule_5_hourly_op}
        Schedule 6: ${schedule_6_hourly_op}
        Schedule 10: ${schedule_10_hourly_op}
        
        Off Peak: {total_mw_offpeak_hourly}MW
        Schedule 1: ${schedule_1_hourly_offp}
        SChedule 2: ${schedule_2_hourly_offp}
        Schedule 5: ${schedule_5_hourly_offp}
        Schedule 6: ${schedule_6_hourly_offp}
        Schedule 10: ${schedule_10_hourly_offp}

        Total Ancillary Hourly = ${round(total_ancillary_hourly,2)}
        '''
    else:
        total_ancillary_hourly_op = schedule_1_hourly_op + schedule_2_hourly_op 
        total_ancillary_hourly_offp = schedule_1_hourly_offp + schedule_2_hourly_offp
        total_ancillary_hourly = total_ancillary_hourly_op + total_ancillary_hourly_offp
        print_hourly = f'''
        Hourly:
    
        On Peak: {total_mw_onpeak_hourly}MW                           
        Schedule 1: ${schedule_1_hourly_op}
        Schedule 2: ${schedule_2_hourly_op}
        
        Off Peak: {total_mw_offpeak_hourly}MW
        Schedule 1: ${schedule_1_hourly_offp}
        SChedule 2: ${schedule_2_hourly_offp}

        Total Ancillary Hourly = ${round(total_ancillary_hourly,2)}
        '''

    

    print(print_hourly) 






#show Power Losses
#POWER LOSSES = LMP * %PATHLOSS * TOTAL MW
#def power_losses(company):
    #we are gonna have to import in the path losses
 #   df_path_losses= pd.read_xml(r"YOUR PATH TO XML LOSSES FILE") #path losses xml file
  #  df_path_losses=df_path_losses.drop(columns=["Identity"]) #drop identity column 
   # df_path_losses=df_path_losses.drop(0) #drop first row 
    #import LMP FINAL FOR MONTH or CAISO_LAP_RE
    #df_LMP=pd.read_csv(r"YOUR PATH TO SP_15 LMP CSV OR CAISO LMP PRICES") #path to caiso_lap_re_csv

    #import Billing_Schedule csv for the month
    #df_bill_sched = pd.read_csv(r"PATH TO BILLING SCHEDU")#pull billing schedule csv for month, after validated 
    #df_bill_sched.reset_index(inplace=True) #reset index




if __name__ == '__main__':
    main() 
