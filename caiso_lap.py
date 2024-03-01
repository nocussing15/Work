import pandas as pd
import requests
from zipfile import ZipFile
import os
from urllib.parse import urlsplit
from pathlib import Path 



def main():
     lap_csv()
     convert_caiso()





#get zip filename
def get_filename_from_url(url):
     path=urlsplit(url).path
     filename = os.path.basename(path)
     return filename 
#return the latest uploaded CAISO CSV FILE 
def get_latest_csv_file(folder_path):
    all_files = os.listdir(folder_path)
    csv_files = [file for file in all_files if file.lower().endswith(".csv")]
    csv_files.sort(reverse=True)
    if not csv_files:
        return None
    else:
        return csv_files[0] #returns name of CSV FILE 


# make LAP CSV
def lap_csv():
        # Specify the URL you want to open
        #change the dates to beginning of month to end of month.
        while True:
            try:
                start_date = input("Please Enter a Start Date (ex:20240101) :") #beginning of month
                end_date = input("Please Enter an End Date(ex:20240201):") #beginning of next month
                if not int(start_date) and not int(end_date):
                     raise ValueError
                else:
                     break
                
            except ValueError:
                 print("Please enter a date in format YEARMONTHDAY")
                 

        url = f"http://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_RTM_LAP&version=6&startdatetime={start_date}T08:00-0000&enddatetime={end_date}T08:00-0000&market_run_id=RTM&node=ELAP_LADWP-APND"

        # Specify the path where you want to save the downloaded zip file
        download_path = r"C:\Users\pnguy1\downloads"

        # Specify the path where you want to extract the contents of the zip file
        extract_path = r"C:\Users\pnguy1\Desktop\Python Programs\LAP_Prices\CAISO_LAP_UNZIP"

        # Make a request to the URL to get the content
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Get the downloaded file name
            zip_file_name = get_filename_from_url(url)
            # Specify the full path of the downloaded zip file
            zip_file_path = os.path.join(download_path, zip_file_name)

            # Save the content to the zip file
            with open(zip_file_path, 'wb') as zip_file:
                zip_file.write(response.content)

            # Extract the contents of the zip file
            with ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Remove the downloaded zip file if needed
            os.remove(zip_file_path)

        else:
            print(f"Failed to download the file. Status code: {response.status_code}")





#convert CAISO LAP CSV TO DATAFRAME, remodel in dataframe, convert back to csv
def convert_caiso():
     folder_path = r"C:\Users\pnguy1\Desktop\Python Programs\LAP_Prices\CAISO_LAP_UNZIP"
     caiso_csv_file = get_latest_csv_file(folder_path) #gives caiso_csv_file NAME
     print(caiso_csv_file)
     df_caiso_lap=pd.read_csv(fr"C:\Users\pnguy1\Desktop\Python Programs\LAP_Prices\CAISO_LAP_UNZIP\{caiso_csv_file}") #read in caiso csv
     
     df_lmp_prc = df_caiso_lap[df_caiso_lap["DATA_ITEM"] == "LMP_PRC"] #filter for LMP_PRC ONLY
     df_lmp = df_lmp_prc[["OPR_DATE","INTERVAL_NUM","VALUE"]]# recreate dataframe for only date, hour interval, and price
     df_lmp = df_lmp.rename(columns={"OPR_DATE":"DATE"}).sort_values(by=["DATE","INTERVAL_NUM"]).reset_index(drop=True) #rename columns, reset index
     df_lmp = df_lmp.pivot(index="DATE",columns="INTERVAL_NUM",values="VALUE").reset_index().rename_axis(None,axis=1) #relocates interval column to become header, plug in "VALUE" as values 
     df_lmp = df_lmp.set_index("DATE")
     os.makedirs(r'C:\Users\pnguy1\Desktop\Python Programs\LAP_Prices\CAISO_LAP_RE',exist_ok=True) #does new folder exist?
     df_lmp.to_csv(fr"C:\Users\pnguy1\Desktop\Python Programs\LAP_Prices\CAISO_LAP_RE\{caiso_csv_file}") #drop newly made csv file into the remodel csv folder, this folder is different from unzip 










if __name__ == '__main__':
    main() 