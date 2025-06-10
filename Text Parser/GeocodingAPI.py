import pandas as pd
import requests

# Function to clean and get structured address details using Google Maps API
def get_address_details(address, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            result = data['results'][0]
            formatted_address = result.get("formatted_address", "")
            address_components = result.get("address_components", [])
            
            # Extract ZIP and State
            zip_code = next((item['long_name'] for item in address_components if 'postal_code' in item['types']), "")
            state = next((item['short_name'] for item in address_components if 'administrative_area_level_1' in item['types']), "")
            
            return formatted_address, zip_code, state
    return None, None, None

# Load the Excel file
input_file = "PATH/ExcelResults/ExcelFile<MONTH>/<MONTH>.xlsx"  # Replace with your file path
output_file = "PATH/ExcelResults/ExcelFile<MONTH>/<MONTH>GeocodedAddresses.xlsx"  # Output file
api_key = "YOUR API KEY"  # Replace with your actual API key

# Read the input file
df = pd.read_excel(input_file)

# Add new columns for cleaned address, ZIP, and state
df['Cleaned Address'] = ''
df['ZIP'] = ''
df['State'] = ''

# Iterate over rows to populate new columns
for index, row in df.iterrows():
    address = row['Address']
    if pd.notna(address):
        try:
            formatted_address, zip_code, state = get_address_details(address, api_key)
            df.at[index, 'Cleaned Address'] = formatted_address
            df.at[index, 'ZIP'] = zip_code
            df.at[index, 'State'] = state
        except Exception as e:
            print(f"Error processing row {index}: {e}")

# Save the updated DataFrame
df.to_excel(output_file, index=False)
print(f"Geocoded addresses saved to {output_file}")
