import pandas as pd

# Load the data
input_file = "PATH/ExcelResults/ExcelFile<MONTH>/<MONTH>GeocodedAddresses.xlsx"  # Replace with your file name
output_file = "PATH/ExcelResults/ExcelFile<MONTH>/<MONTH>GeocodedAddressesFinal.xlsx"

# Read the Excel file
data = pd.read_excel(input_file)

# Filter rows where ZIP column has a value (non-empty and non-NaN)
filtered_data = data[data['ZIP'].notnull()]

# Save the filtered data to a new Excel file
filtered_data.to_excel(output_file, index=False)

print(f"Filtered rows with ZIP have been saved to '{output_file}'.")
