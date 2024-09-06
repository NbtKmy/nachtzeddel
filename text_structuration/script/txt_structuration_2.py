# -------------------------- #
# Code Description:
# -------------------------- #
# This script processes nightly visitor data from Zürich's inns, extracting 
# and structuring information such as visit dates, guest names, and inns where they stayed.
# The script assigns unique Visit_IDs, Guest_IDs, and Inn_IDs for each record.
# -------------------------- #

import os
import re
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# Define the directory containing your text files
txt_directory = 'txt/'

# Inns to look for in the text
inns = ['SCHWERDT', 'STORCHEN', 'ADLER', 'HIRSCHEN', 'RAABEN', 'LEUEN', 'ROESSLI', 'SCHWANEN']

# Define the month mapping for Latinized month names
month_mapping = {
    'Januarii': '01',
    'Februarii': '02',
    'Martii': '03',
    'Aprilis': '04',
    'Maii': '05',
    'Junii': '06',
    'Julii': '07',
    'Augusti': '08',
    'Septembris': '09',
    'Octobris': '10',
    'Novembris': '11',
    'Decembris': '12'
}

# Function to convert historical date format to modern date format (YYYY-MM-DD)
def convert_to_modern_date(historical_date):
    day, month, year = historical_date.split()
    month_numeric = month_mapping.get(month, '01')  # Default to January if the month is not found
    modern_date_str = f"{year}-{month_numeric}-{day.zfill(2)}"
    return modern_date_str

# Function to parse a single file
def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    # Extract the date (assuming it follows the pattern "FREYTAGS, den 28 Julii 1780")
    date_match = re.search(r'\b(\d{1,2} \w+ \d{4})\b', content)
    if date_match:
        historical_date = date_match.group(1)
        modern_date = convert_to_modern_date(historical_date)
    else:
        return None, None, None  # If no date is found, skip the file


    '''
    # Extract data for each inn
    inn_data = {inn: [] for inn in inns}
    for inn in inns:
        # Use regex to extract the text under each inn
        inn_match = re.search(rf'{inn}[-.]\s*(.*?)(?=\n[A-Z]+\.|\Z)', content, re.DOTALL)
        if inn_match:
            # Clean up the text (remove newlines and extra spaces)
            visitors = inn_match.group(1).strip().split('\n')
            visitors = [v.strip() for v in visitors]
            inn_data[inn] = visitors
    print(inn_data)
    '''
    inn_data = {}
    inn = None
    visitors = []
    lines = content.splitlines()[2:]
    for line in lines:
        if line.isupper():
            print(line)
            if inn:
                inn_data[inn] = visitors
            # Start a new key and reset the list
            inn = re.sub(r'[^A-Z]+$', '', line.strip())
            visitors = []
        else:
            # Add non-uppercase lines to the current list
            if inn and len(line) > 0:
                visitors.append(line.strip())
    
        # Add the last collected key-value pair to the dictionary
        if inn:
            inn_data[inn] = visitors

        print(inn_data)
    return historical_date, modern_date, inn_data

# Initialize an empty list to hold the structured data
structured_data = []

# Initialize counters for visit and guest IDs
visit_id = 1
guest_id = 1

# Get all files in the directory and sort them alphanumerically
files = sorted([f for f in os.listdir(txt_directory) if f.endswith(".txt")])

# Iterate over all text files in the directory, in sequential order
for filename in files:
    filepath = os.path.join(txt_directory, filename)
    historical_date, modern_date, inn_data = parse_file(filepath)
    if historical_date and modern_date and inn_data:
        # Iterate over each inn and process visitors
        for inn, visitors in inn_data.items():
            if visitors:  # If there are visitors listed for the inn
                #visitor_list = visitors.split(', ')  # Separate individual visitors
                for visitor in visitors:
                    print(visitor)
                    if visitor:
                        # Add the structured data for each individual visitor
                        structured_data.append({
                            'Visit_ID': visit_id,  # Unique visit event ID
                            'Historical Date': historical_date,
                            'Modern Date': modern_date,
                            'Inn': inn,
                            'Visitor': visitor,
                            'Guest_ID': guest_id,
                            'Filename': filename
                        })
                        visit_id += 1  # Increment visit ID
                        guest_id += 1  # Increment guest ID

# Convert the structured data into a DataFrame
df_structured = pd.DataFrame(structured_data)

# Step 1: Assign a unique ID to each inn and place the 'Inn_ID' column next to the 'Inn' column
inn_unique_ids = {inn: idx + 1 for idx, inn in enumerate(df_structured['Inn'].unique())}
df_structured['Inn_ID'] = df_structured['Inn'].map(inn_unique_ids)

# Reorder columns to place 'Inn_ID' next to 'Inn'
df_structured = df_structured[['Visit_ID', 'Historical Date', 'Modern Date', 'Inn', 'Inn_ID', 'Visitor', 'Guest_ID', 'Filename']]

# Display the structured DataFrame with the new Inn_ID column next to Inn
print(df_structured.head())

# Save the structured DataFrame to a new CSV file with UTF-8 encoding
df_structured.to_csv('structured_guests_with_inn_ids_sarah.csv', index=False, encoding='utf-8')

