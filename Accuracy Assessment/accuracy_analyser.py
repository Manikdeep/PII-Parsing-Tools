import pandas as pd
import boto3
import time
import os
import re
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from collections import defaultdict

# AWS Comprehend setup
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
comprehend = boto3.client('comprehend')

# Load file
file_path = 'PATH/Final_Noised_Stage1_Easy.xlsx' #Your path
df = pd.read_excel(file_path)

# Logging
missed = []
raw_comprehend_outputs = []
found_total = 0
expected_total = 0
field_type_stats = defaultdict(lambda: {"correct_type": 0, "other_type": 0, "not_found": 0})

# Fields to validate
field_to_expected_type = {
    'Name': ['PERSON'],
    'Phone': ['PHONE', 'PHONE_NUMBER'],
    'Email': ['EMAIL'],
    'DOB': ['DATE_TIME', 'DATE'],
    'Address': ['LOCATION'],
    'Organization': ['ORGANIZATION'],
    'CC Number': ['CREDIT_DEBIT_NUMBER'],
    'CVV': ['CREDIT_DEBIT_CVV'],
    'Expiry Date': ['DATE_TIME', 'DATE'],
    'Bank Name': ['BANK_NAME', 'ORGANIZATION'],
    'Scheme': [],
    'Country': ['LOCATION'],
    'Url': ['URL'],
    'SSN': ['SSN']
}

print("Starting Amazon Comprehend Accuracy Check...")
print("Passing each row to Amazon Comprehend for entity recognition...")

# Comprehend entity detection
def detect_entities(text):
    try:
        entities = comprehend.detect_entities(Text=text, LanguageCode='en')['Entities']
        pii = comprehend.detect_pii_entities(Text=text, LanguageCode='en')['Entities']
        return entities + pii
    except Exception as e:
        print(f"Error calling Comprehend: {e}")
        return []

# Enhanced matching: text and type awareness
def match_found(field, value, entities):
    value = str(value).strip().lower()
    if not value:
        return True
    found = False
    matched_type = None
    for ent in entities:
        ent_text = ent.get('Text', '').strip().lower()
        ent_type = ent.get('Type', '')
        if value in ent_text or ent_text in value:
            found = True
            matched_type = ent_type
            break

    if not found:
        field_type_stats[field]['not_found'] += 1
        return False
    elif matched_type in field_to_expected_type.get(field, []):
        field_type_stats[field]['correct_type'] += 1
    else:
        field_type_stats[field]['other_type'] += 1
    return True

# Row processor
def process_row(index, row):
    local_missed = []
    combined_text = " ".join([str(row[col]) for col in field_to_expected_type if col in df.columns and pd.notna(row[col])])
    detected = detect_entities(combined_text)

    raw_comprehend_outputs.append({
        "row_index": index,
        "original_text": combined_text,
        "entities": detected
    })

    for field in field_to_expected_type:
        if field in df.columns:
            val = row[field]
            if not match_found(field, val, detected):
                local_missed.append({"row": index + 1, "field": field, "value": val})
    return local_missed

# Multi-threaded execution with progress bar
try:
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_row, idx, row): idx for idx, row in df.iterrows()}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Rows"):
            result = future.result()
            missed.extend(result)
except KeyboardInterrupt:
    print("Interrupted by user. Saving partial results...")

# Final accuracy
expected_total = len(df) * len(field_to_expected_type)
found_total = expected_total - len(missed)
accuracy = found_total / expected_total * 100 if expected_total else 0

# Save missed log
with open("PATH/comprehend_missed_log.txt", "w", encoding='utf-8') as f:
    for item in missed:
        f.write(f"Row {item['row']}, Field: {item['field']}, Value: {item['value']}\n")
    f.write(f"\nOverall Accuracy: {accuracy:.2f}%\n")

    f.write("\nField Type Detection Summary:\n")
    for field, stats in field_type_stats.items():
        f.write(f"{field} - Correct Type: {stats['correct_type']}, Other Type: {stats['other_type']}, Not Found: {stats['not_found']}\n")

# Save raw output
with open("PATH/comprehend_raw_log.json", "w", encoding='utf-8') as f: #Your path
    json.dump(raw_comprehend_outputs, f, indent=2)

print(f"Done. Accuracy: {accuracy:.2f}%")
print("Missed items saved to 'comprehend_missed_log.txt'")
print("Raw Comprehend responses saved to 'comprehend_raw_log.json'")
