This tool parses Telegram-exported result.json chat logs, detects English entities using Amazon Comprehend, and enriches credit card data using the BINChecker API. Results are saved in .xlsx files.

Setup Guide
1. Set up a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   #Use ‘venv\Scripts\activate’ on Windows
2. Install required packages
Run this command in your terminal:
pip install boto3 requests openpyxl pandas tqdm ftfy python-dateutil langdetect

API Requirements
1.	Amazon Comprehend
	- You must configure AWS CLI with your credentials:
		aws configure
	- You’ll be prompted to enter:
    	AWS Access Key ID	
    	AWS Secret Access Key
		Default region name (e.g., us-east-1)
    	Output format (you can just hit Enter)
	- Alternatively, you can export them as environment variables:
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
2.	BINChecker API
	- Sign up at https://apilayer.com/marketplace/bincheck-api
	- Get your API key and paste it into the script where it says:
		"apikey": "YOUR_API_KEY"

File Structure Requirements
- Place your Telegram result.json files in a folder of your choice.
- Update this line in the script with the full path to that folder:
	Main_Folder = 'PATH'
- Each processed .json file will generate a corresponding .xlsx file.

Supported file structure:
- Telegram result.json format (from the export chat function)

Notes:
- Currently supports only Telegram .json exports.
- Other formats will be supported in future versions.
- The script filters for English and ignores non-English text (especially Russian).
- CVV, names, addresses, and other PII are categorized using Comprehend + heuristics.

