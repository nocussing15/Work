import os
import PyPDF2

def search_for_number_in_folder(folder_path, target_number):
    # Iterate through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)

            # Open the PDF file
            with open(pdf_path, 'rb') as file:
                # Create a PDF reader object
                pdf_reader = PyPDF2.PdfFileReader(file)

                # Iterate through each page in the PDF
                for page_num in range(pdf_reader.numPages):
                    # Extract text from the page
                    page = pdf_reader.getPage(page_num)
                    page_text = page.extractText()

                    # Check if the target number is present in the extracted text
                    if target_number in page_text:
                        print(f"Number {target_number} found in {pdf_path}, page {page_num + 1}")
                    
                    

if __name__ == "__main__":
    # Specify the path to the folder containing PDF files and the target number
    folder_path = r"O:\Billing\OASIS Invoices\2023\2023-11\Final" #note had to add extra double slashes
    target_number = "$194.00"

    # Call the search function
    search_for_number_in_folder(folder_path, target_number)
