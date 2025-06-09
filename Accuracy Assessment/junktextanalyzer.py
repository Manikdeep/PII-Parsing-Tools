import json
from collections import defaultdict
import pandas as pd

# Load Amazon Comprehend output from JSON
json_path = 'PATH/comprehend_raw_log.json' #Your path
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Load expected values from original clean file
clean_df = pd.read_excel('PATH/GroundTruthSet.xlsx').iloc[:2500] #Your path

# Junk indicator patterns
junk_indicators = [
    'junk', 'not_a_real_value', 'encoded_xyz', 'nullnullnull',
    '123fakeinfo321', 'xxx@zzz', 'check_this_later', '!!donotread!!',
    '###confidential###', '>>start>>'
]

# Track results
full_data_covered = 0
exact_matches = 0
matched_with_junk_count = 0
junk_only_rows = 0
partial_matches_with_junk = 0
junk_entities_total = 0
junk_rows = defaultdict(list)
perfect_rows = []
covered_rows = []
wrong_rows = []

row_details = {}

from tqdm import tqdm

print("Loading noised source file...")
noised_df = pd.read_excel('PATH/Final_Noised_Stage1_Easy.xlsx') #Your path
print("Analyzing Amazon Comprehend output row-by-row...")
for row in tqdm(data, desc="Processing Rows"):
    idx = row['row_index']
    detected_entities = [ent.get("Text", "").strip().lower() for ent in row.get("entities", []) if ent.get("Text", "").strip()]
    expected_row = clean_df.iloc[idx]
    expected_values = [str(expected_row[col]).strip().lower() for col in clean_df.columns if pd.notna(expected_row[col])]

    correctly_matched_values = [val for val in expected_values if any(val.lower() in det.lower() for det in detected_entities)]
    matched_all = len(correctly_matched_values) == len(expected_values)
    matched_exact = len(correctly_matched_values) == len(expected_values) and not any(det for det in detected_entities if det.lower() not in [val.lower() for val in expected_values])

    extra = [det for det in detected_entities if det not in expected_values]
    junk = [j for j in extra if any(junk_tag in j for junk_tag in junk_indicators)]
    semi_valid_extra = [j for j in extra if j not in junk]

    if matched_all:
        full_data_covered += 1
        if matched_exact:
            exact_matches += 1
            perfect_rows.append(idx)
        else:
            partial_matches_with_junk += 1
            covered_rows.append(idx)
            if junk:
                matched_with_junk_count += 1
    else:
        wrong_rows.append(idx)
        if junk:
            junk_only_rows += 1

    for j in junk:
        junk_rows[idx].append(j)
        junk_entities_total += 1

    
    original_row_data = str(noised_df.iloc[idx].to_dict())

    row_details[idx] = {
        "original_row": original_row_data,
        "expected": expected_values,
        "detected": detected_entities,
        "junk": junk,
        "semi_valid_extra": semi_valid_extra,
        
        "matched_count": "",
        "expected_count": ""
    }

# Generate report
summary_lines = []
summary_lines.append("=== Junk Detection and Entity Accuracy Report ===")
summary_lines.append("Files Used:")
summary_lines.append("- Clean Ground Truth File: GroundTruthSet.xlsx")
summary_lines.append("- Noised Input File: Final_Noised_Stage3_Hard.xlsx")
summary_lines.append("This analysis is designed to evaluate Amazon Comprehend's ability to extract expected values from structured text with varying levels of noise.\n")
summary_lines.append("Goals of this analysis:")
summary_lines.append("- Confirm that Comprehend eventually finds all valid data (data coverage)")
summary_lines.append("- Identify perfect matches with no extra detected data")
summary_lines.append("- Report where Comprehend picked up extra junk but still got the right stuff")
summary_lines.append("- Flag rows where the output was flat-out incorrect")
summary_lines.append("- Break down junk detected and extra noise returned\n")



summary_lines.append("=== Detailed Row Breakdown === (Per Row Counts Included)")
for idx in sorted(row_details):
    details = row_details[idx]
    summary_lines.append(f"\n=== Row {idx + 1} ===")
    summary_lines.append(f"Original Row:\n  {details['original_row']}\n")
    summary_lines.append(f"Expected Values:\n  {details['expected']}\n")
    summary_lines.append(f"Detected Entities:\n  {details['detected']}\n")
    summary_lines.append(f"Extra Junk Detected:\n  {details['junk']}\n")
    summary_lines.append(f"Other Non-Junk Extras:\n  {details['semi_valid_extra']}\n")
    summary_lines.append(f"Matched Values:  / ")
    summary_lines.append(f"Exact Match Count (no junk + full match): ")
    summary_lines.append(f"Correct With Junk Count: ")
    summary_lines.append(f"Junk Only Count: ")

# Save report
report_path = 'PATH/comprehend_junk_breakdown_summary.txt' #Your path
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(summary_lines))

print("Comprehend accuracy and junk analysis complete. Summary saved to:", report_path)
