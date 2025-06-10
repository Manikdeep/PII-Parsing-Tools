import pandas as pd

# Load the Excel file
input_file = "PATH/ExcelResults/ExcelFile<MONTH>/<MONTH>.xlsx"  # Replace with the path to your file
output_file = "PATH/ExcelResults/ExcelFile<MONTH>/<MONTH>FilteredAddresses.xlsx"  # Output file to store rows with addresses
address_column = "Address"  # Replace with the name of your address column

# Read the input Excel file
df = pd.read_excel(input_file)

# Filter rows where the Address column is not empty or NaN
filtered_df = df[df[address_column].notnull() & (df[address_column] != '')]

# Write the filtered data to a new Excel file
filtered_df.to_excel(output_file, index=False)

print(f"Filtered rows with addresses have been saved to {output_file}")
