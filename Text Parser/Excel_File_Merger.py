import pandas as pd
import os
from tqdm import tqdm

# specify the directory you're working from
path = 'PATH/ExcelResults/ExcelFile<MONTH>'

files = os.listdir(path)

# filter out any non-xlsx files or any files you aren't interested in
excel_files = [file for file in files if file.endswith('.xlsx')]

# create a list to hold the dataframes
dfs = []

# read them in
for excel in tqdm(excel_files, desc="Merging Files", unit="file"):
    df = pd.read_excel(path + '/' + excel)
    dfs.append(df)

# concatenate them together
combined = pd.concat(dfs)

# write it out
output_path = path + ".xlsx"
combined.to_excel(output_path, index=False)
