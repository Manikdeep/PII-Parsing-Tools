#-------------------------------------------------------------------------------------- Comprehend Code --------------------------------------------------------------------------------------#
# Import necessary libraries
from multiprocessing import Process, Manager
import os
import sys
import boto3
import requests
from collections import Counter
from openpyxl import Workbook
import json
from collections import OrderedDict
from tqdm import tqdm
import pandas as pd
import pathlib
import io
import ftfy
from functools import lru_cache
from dateutil.parser import parse
from langdetect import detect
from datetime import datetime
import re

# for semaphore
import threading


# Set encoding for stdin and stdout to utf-8
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

# Set AWS region
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
# Initialize Comprehend client
comprehend = boto3.client('comprehend')

# Initialize user list and count
userlist = []

# create a semaphore object
# The value should ideally be less than or equal to the number of cores you have on your CPU
# For a Ryzen 5 5600x, which has 6 cores, you can safely set the semaphore value to 6
# If you're on a lower-end system, consider lowering this number to match your available cores
semaphore = threading.Semaphore(6)

#Change max size according to RAM on your computer
@lru_cache(maxsize=10000)
def bincheck(bin):
    semaphore.acquire()
    url = "https://api.apilayer.com/bincheck/" + str(bin)

    payload = {}
    headers= {
    #new key
    "apikey": "YOUR_API_KEY" #Add your API Key Here
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    semaphore.release()

    result = response.json()

    return str(result.get('scheme', None)) , str(result.get('bank_name', None)) , str(result.get('country', None)), str(result.get('type', None)), str(result.get('url', None))


# Define the main folder and get its name
Main_Folder = 'PATH'
main_folder_name = os.path.basename(Main_Folder)

# Initialize the json files list
json_files = []

# Walk through all files in the main folder
for root, dirs, files in os.walk(Main_Folder):
    for file in files:
        if file.endswith('.json'):
            subfolder_name = os.path.basename(root)
            json_files.append(os.path.join(root, file))


# Loop through all json files
for file_index, file_path in enumerate(tqdm(json_files, desc="\nProcessing JSON Files")):
    tqdm.write(f'Start processing file {file_index + 1}/{len(json_files)}: {file_path}')  # Print the start of processing of the current file
    # Load JSON data from the file
    try:
        with open(file_path, 'r', encoding='utf-8') as file_content:
            json_data = json.load(file_content)

        if not json_data:
            raise ValueError("File is empty")

    except ValueError as e:
        print(f"Skipping file {file_path} due to error: {e}")
        continue

    # Extract the folder name
    folder_name = os.path.basename(os.path.dirname(file_path))
    new_file_name = folder_name + ".xlsx"

    #This gets all of the text
    Total_Text_list = []

    if "result.json" in file_path.lower():
        for i in json_data["messages"]: 
            if "text" in i:
                if (isinstance(i['text'], list)):
                    for j in i['text']:
                        if isinstance(j, dict):
                            String = j['text']
                            Total_Text_list.append(String)
                        elif isinstance(j, str):
                            if not j == " ":
                                Total_Text_list.append(j)
                else:
                    if (isinstance(i['text'], str)):
                        if  not len(i['text']) == 0:
                            STRING = i['text']
                            Total_Text_list.append(STRING)

            if "text_entities" in i:
                if (isinstance(i['text_entities'], list)):
                    for j in i['text_entities']:
                        if isinstance(j, dict):
                            String_entitiy = j['text']
                            Total_Text_list.append(String_entitiy)
                        elif isinstance(j, str):
                            if not j == " ":
                                Total_Text_list.append(j)
                else:
                    if (isinstance(i['text_entities'], str)):
                        if  not len(i['text_entities']) == 0:
                            STRING_string = i['text_entities']
                            Total_Text_list.append(STRING_string)

    elif "messages.json" in file_path.lower():
        for i in json_data:
            # Handle "text"
            if "text" in i and isinstance(i["text"], str) and i["text"].strip():
                words = i["text"].split()
                for word in words:
                    Total_Text_list.append(word)

            # Handle "text_entities"
            if "text_entities" in i:
                if isinstance(i["text_entities"], list):
                    for entity in i["text_entities"]:
                        if isinstance(entity, dict) and "text" in entity:
                            words = entity["text"].split()
                            for word in words:
                                Total_Text_list.append(word)
                        elif isinstance(entity, str):
                            words = entity.split()
                            for word in words:
                                Total_Text_list.append(word)
                elif isinstance(i["text_entities"], str):
                    words = i["text_entities"].split()
                    for word in words:
                        Total_Text_list.append(word)


    unique_words = list(OrderedDict.fromkeys(Total_Text_list))

    dfs = []  # Initialise an empty list to hold all the dataframes
    for p in unique_words:
        text = p
        if len(text) == 0:
            text = 'null'
        
        
        if text.isnumeric():
            language_code = 'en'
        else:
            try:
                language_code = detect(text)
            except:
                language_code = None
        #filters the language to english because the russian in the files is overwhelming
        if language_code == 'en':
            
            #The process with DetectEntitiestext and the PIItext is it takes the text from the list and runs it through the api through two methods
            #Two methods is necessary because it won't pick up everything and some things will show up categorized.
            DetectEntitiestext = text
            resp = (json.dumps(comprehend.detect_entities(Text=DetectEntitiestext, LanguageCode='en'), sort_keys=True, indent=4))
            respJ = json.loads(resp)

            DetectPIItext = text
            requestPII = (json.dumps(comprehend.detect_pii_entities(Text=DetectPIItext, LanguageCode='en')))
            respPII = json.loads(requestPII)

            #This takes the the two lists made by comprehend and combines them
            list1 = []
            list2 = []

            i = 0
            while not (len(respJ['Entities']) - 1 < i):

                boff = int(respJ['Entities'][i]['BeginOffset'])
                eoff = int(respJ['Entities'][i]['EndOffset'])

                list1.append((str(respJ['Entities'][i]['Type']) + ': ' + text[boff:eoff]))
                i += 1

            i = 0
            while not (len(respPII['Entities']) - 1 < i):

                boff = int(respPII['Entities'][i]['BeginOffset'])
                eoff = int(respPII['Entities'][i]['EndOffset'])

                list2.append((str(respPII['Entities'][i]['Type']) + ': ' + text[boff:eoff]))
                i += 1

            #cross references the lists to delete duplicates
            #There could be many duplicates and this just checks it just in case

            def find_duplicates(list1,list2):
                endlist = []
                for i in list1:
                    for j in list2:
                        if i[i.index(':'):len(i)] != j[j.index(':'):len(i)]:
                            endlist.append(i)
                            break
                
                return endlist
                    
            #find duplicates in list1
            endlist = find_duplicates(list1,list2)

            def check_date_format(date_string):
                for fmt in ('%Y%m%d', '%d%m%Y', '%m%d%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y', '%Y'):
                    try:
                        datetime.strptime(date_string, fmt)
                        return True
                    except ValueError:
                        pass
                return False

            if len(endlist) != 0:
                #Declaring variables
                address = ''
                cvv = ''
                expiry = ''
                ccnum = ''
                cc_type =''
                name = ''
                gender = ''
                email = ''
                phone = ''
                bank = ''
                scheme = ''
                country = ''
                organization = ''
                url = ''
                dob = ''
                ssn = ''
                extradata = ''

                #Appending list2 to endlist
                for i in list2:
                    endlist.append(i)

                #looping through the entities found and assigns the value to the correct variable
                for i in endlist:
                    # Extract key and word
                    key = i[:i.index(':')]
                    word = i[i.index(':')+2:]

                    # Category assignment
                    
                    #Phone
                    import re

                    if (word not in phone and (word.isdigit() and len(word) > 9 and len(word) < 15) or (("OTHER" in key or "PHONE" in key) and 
                                            ((len(word.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')) == 10 and word.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit()) or 
                                            (len(word.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')) == 12 and word.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')[0] == '1' and word.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')[1:].isdigit()) or
                                            (len(word.replace(' ', '').replace('-', '').replace('(', '').replace('(', '').replace(')', '')) == 14 and word.replace(' ', '').replace('-', '').replace('(', '').replace('(', '').replace(')', '')[0:3] == '+1' and word.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')[3:].isdigit()) or
                                            (re.match(r"\b\d{3}-\d{3}-\d{4}\b", word.replace(' ', '')) is not None) or
                                            (re.match(r"\+\d\s\d{3}\s\d{3}\s\d{4}", word) is not None) or
                                            (len(word.replace(' ', '')) == 12 and word.count(' ') == 2 and word.replace(' ', '').isdigit()) or
                                            (len(word) == 10 and word.isdigit())) or
                                            (re.match(r"\+\d\s\(\d{3}\)\s\d{3}‑\d{4}", word) is not None))):
                                            phone += word + ' '

                    
                    #Address used to contain "or "ADDRESS" in key" but caused duplication of phone numbers in address box
                    elif ("LOCATION" in key ): 
                        address += word + ' '

                    #CVV
                    elif ("CREDIT_DEBIT_CVV" in key or "OTHER" in key or "QUANTITY" in key) and (len(word) == 3 or "CVV" in word.lower()) and word.isdigit():
                        cvv += word[word.index("CVV") + 4:] if "CVV" in word else word + ', '
                    
                    #DOB & Expiry
                    elif "DATE" in key or "OTHER" in key:
                         if len(word) in (4, 8, 10) and check_date_format(word):  # Update length check to include 4 for year-only format
                            for fmt in ('%Y%m%d', '%d%m%Y', '%m%d%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y', '%Y'):
                                try:
                                    parsed_date = datetime.strptime(word, fmt)
                                    if len(word) == 4:  # For year-only format, we can't decide if it's dob or expiry. Add it to both or decide based on your criteria.
                                        if word not in dob:
                                            dob += word + ' '
                                        if word not in expiry:
                                            expiry += word + ' '
                                    elif parsed_date.year < 2006 and parsed_date.year > 1920:  # Date of Birth
                                        if word not in dob:
                                            dob += word + ' '
                                    else:  # Expiry Date
                                        if word not in expiry:
                                            expiry += word + ' '
                                    break  # Break once we successfully parse the date with a valid format
                                except ValueError:
                                    pass


                    #Credit Card Number
                    elif ("OTHER" in key or "CREDIT_DEBIT_NUMBER" in key) and (len(word) in [15, 16]):
                        ccnum += word + ' '
                        try:
                            scheme, bank, country, cc_type, url = bincheck(word[:6])
                        except:
                            pass
                    
                    #Name
                    elif "PERSON" in key and word != '':
                        name += word + ' '
                    
                    #Email
                    elif "OTHER" in key and ('mail' in word.lower() or '@' in word):
                        email += word + ' '
                    
                    
                    #Organization
                    elif "ORGANIZATION" in key:
                        organization += word + ' '
                    
                    #SSN
                    elif len(word) > 8 and ("SSN" in key or ("OTHER" in key and word.replace('-', '').isdigit() and ((len(word.replace('-', '')) == 9 and word.count('-') == 2 and word[3] == '-' and word[6] == '-') or (len(word) == 9)))):
                        ssn += word + ' '

                    #Extra data
                    else:
                        extradata += word + ' '

                
                # Appending to the DataFrame
                user = {'Name': name, 'Phone': phone,'Email': email, 'DOB': dob, 'Address': address, 'Gender': gender, 'Organization': organization,
                            'CC Type': cc_type, 'CC Number': ccnum, 'CVV': cvv, 'Expiry Date': expiry, 'Bank Name': bank, 'Scheme': scheme, 'Country': country, 'Url': url, 'SSN': ssn, 'Extra data': extradata}

                # Append each user dictionary to a list of dataframes
                dfs.append(pd.DataFrame([user]))

    # Concatenate all dataframes in the list
    try:
        df = pd.concat(dfs, ignore_index=True)
    except ValueError as e:
        print(f" Skipping file {file_path} due to error: {e}")
        continue

    # Filter rows containing '$'
    df = df[~df.apply(lambda row: row.astype(str).str.contains('\$').any(), axis=1)]
    
    # Write the DataFrame to a new Excel file
    df.to_excel(r"PATH/{new_file_name}".format(new_file_name=new_file_name), index = False) #Provide the path to save the excel file
    tqdm.write(f'Finished processing file {file_index + 1}/{len(json_files)}: {file_path}\n')  # Print the completion of processing of the current file
