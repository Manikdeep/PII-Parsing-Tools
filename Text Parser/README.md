### PII Text Parsing

This tool (PII_TextParser.py) parses Telegram-exported result.json chat logs, detects English entities using Amazon Comprehend, and enriches credit card data using the BINChecker API. Results are saved in .xlsx files.

### Setup Guide

1. Download Python and add Python to PATH variables.

2. Create your project folder which includes scraped .JSON files and the parser script.
	Example folder structure:
  	```
	PII_Tool/
	├── Channel1/
	│   └── result.json
	├── Channel2/
	│   └── result.json
	├── main_script.py
	```
  
3. Set up a Python environment
   In a terminal, go into your project folder and run the follwoing command:
   ``` python -m venv venv ```
   To activate environment, run:
	   On Mac/Linux:
	   ``` source venv/bin/activate ```
	   On Windows:
	   ``` venv\Scripts\activate ```

4. Install required packages
   ``` pip install boto3 requests openpyxl pandas tqdm ftfy python-dateutil langdetect ```

6. Set Up AWS and add your API Keys

   Amazon Comprehend Setup:
   - Go to aws.amazon.com and log in or create a free account.
   - Click on your Username > My Security Credentials.
   - Under Access Keys, click Create Access Key.
   - You will receive:
		- Access Key ID (e.g., AKIAIOSFODNN7EXAMPLE)
		- Secret Access Key (a long string like wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY)
   - Save both keys safely. You’ll only see the secret key once!
   - Then, in your terminal, run:
		``` aws configure ```
	- Provide the following user input:
   		```
	  	AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
		AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
		Default region name [None]: us-east-1
		Default output format [None]: json
     	```
 
   BINChecker API Setup:

   Go to apilayer.com/marketplace/bincheck-api, sign up, and get your API key. Paste it into the script where it says:
   ```
   "apikey": "YOUR_API_KEY"
   ```

8. How to Use the Script
	- Set the JSON Source Path:
   		In the parser script replace the PATH in ``` Main_Folder = 'PATH' ``` with your full path to the project folder.
     	Example:
		``` Main_Folder = r"C:\Users\YourName\Desktop\PII_Tool" ```
	- Replace the Output PATH ``` r"PATH/{new_file_name}" ``` with a PATH to an existing folder where you want the Excel files to be saved.
		Example:
		``` r"C:\Users\YourName\Desktop\PII_Tool\ExcelOutput\{new_file_name}" ```

10. Output file includes:
    - Name
	- Phone
	- Address
	- Email
	- Credit card type, number, CVV, expiry
	- SSN, DOB, organization

11. Key AWS Terms in the Code
	- comprehend.detect_entities: finds general things like names and orgs
	- comprehend.detect_pii_entities: finds private stuff like SSNs, phone numbers
	- semaphore: controls how many things run at once (helps your CPU breathe)

---

### Post Parsing Workflow

Once the parser is done and you've got a bunch of Excel files with categorized data, here's what to do next. These steps clean up the info even more so you only keep the good stuff:

1. Excel File Merger\
   This script combines all your Excel files into one big file.
   
   Requirements:
   - A folder with all the Excel files you want to merge (they should end in .xlsx).
   - Update the path in the script so it knows where your folder is.
     
   To run:
   - Open Excel_File_Merger.py.
   - Make sure the folder path is correct.
   - Run the script.
   
   Use:
   - It reads every Excel file in that folder.
   - It stacks all the data together into one big Excel file.
   - It saves that file as a single .xlsx file in the same location.

3. Extract Addresses\
   This script pulls out only the non-empty rows of the "Address" column.

   To run:
   - Open Extract_Addresses.py.
   - Make sure the input_file path points to the file you got from the merger step.
   - Run the script.
   
   Use:
   - Checks each row to see if there's an address.
   - If there is, it keeps the row.
   - If there's no address, it gets rid of it.
   - Saves the cleaned-up file with a new name.

5. Geocoding API\
   This API looks up the address online to fill in missing or incorrect details like ZIP Code or State.

   To run:
   - Open GeocodingAPI.py.
   - Change the file path so it points to the filtered address file from the last step.
   - Run the script (requires Internet).
   
   Use:
   - Sends each address to Google's Geocoding API.
   - Gets back a clean, full address.
   - Adds ZIP codes and states into new columns.
   - Saves the new version of the file.

7. Extract ZIP Codes\
   This script keeps only the rows that have valid ZIP codes.

   To run:
   - Open Extract_ZIP_Codes.py.
   - Make sure the path points to the file from the geocode step.
   - Run the script.
   
   Use:
   - Looks at the ZIP column.
   - Keeps rows that have ZIP codes.
   - Deletes rows that don’t.
   - Saves the final cleaned file.
