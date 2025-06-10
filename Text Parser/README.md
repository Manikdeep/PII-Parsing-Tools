This tool parses Telegram-exported result.json chat logs, detects English entities using Amazon Comprehend, and enriches credit card data using the BINChecker API. Results are saved in .xlsx files.

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
