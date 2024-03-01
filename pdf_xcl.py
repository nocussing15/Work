import tabula
import pandas as pd


pdf_path = 'PWX_PRELIM.pdf'
template_path = 'TEST_PDF.tabula-template (1).json'
#headers=['AREF','INCREMENT','MW GRANTED', 'MWHr', 'Billing Rate', 'PRICE Units', 'TRANS Charge', 'Start Time', 'Stop Time', 'POR', 'POD', 'REQUEST TYPE']
#df=tabula.read_pdf(pdf_path,pages='2',stream=True)
df = tabula.read_pdf_with_template(pdf_path,template_path,pages='2')
#df1 = df[0]
#file_name = pdf_path.replace('.pdf','.xlsx')
#df.to_excel(file_name)
#df1.columns=headers

print(df)





