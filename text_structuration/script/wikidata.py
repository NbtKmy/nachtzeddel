import os
import re
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import requests

titles = ['Hr', 'Mr', 'Fr', 'Herr', 'Monsieur', 'Frau', 'Madame', 'Jkr', 'Madm']

def get_wiki_hits(name):
    prefix = "https://de.wikipedia.org/w/api.php?action=opensearch&format=json&search="
    hits = []
    if len(name) > 0:
        r = requests.get(prefix + name)
        results = r.json()
        hits = results[3]
    return hits

# Inns to look for in the text
inns = ['SCHWERDT', 'STORCHEN', 'ADLER', 'HIRSCHEN', 'RAABEN', 'LEUEN', 'ROESSLI', 'SCHWANEN']

def inn_in_line(line):
    for inn in inns:
        if inn in line:
            return inn
    return False

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

    inn_data = {}
    inn = None
    visitors = ''
    lines = content.splitlines()
    for line in lines:
        if inn_in_line(line):
            #print(line)
            if inn:
                inn_data[inn] = visitors
            # Start a new key and reset the list
            inn = re.sub(r'[^A-Z]+$', '', line.strip())
            visitors = ''
        else:
            # Add non-uppercase lines to the current list
            if inn and len(line) > 0:
                visitors += line + ' '
        #print(inn_data)
    return historical_date, modern_date, inn_data

# Initialize an empty list to hold the structured data
structured_data = []

# Initialize counters for visit and guest IDs
visit_id = 1
guest_id = 1

# Get all files in the directory and sort them alphanumerically
files = []
txt_directory = '../../ideas/ocr_mit_claude'
#print(os.walk(txt_directory))
for x in os.walk(txt_directory):
    #print(x)
    files += sorted([x[0] + '/' + f for f in os.listdir(x[0]) if f.endswith(".txt")])

# Iterate over all text files in the directory, in sequential order
for filename in files:
    #print(filename)
    filepath = os.path.join(txt_directory, filename)
    #print(filepath)
    historical_date, modern_date, inn_data = parse_file(filepath)
    if historical_date and modern_date and inn_data:
        # Iterate over each inn and process visitors
        for inn, visitors in inn_data.items():
            if visitors:  # If there are visitors listed for the inn
                #visitor_list = visitors.split(', ')  # Separate individual visitors
                #for visitor in visitors:
                    #print(visitor)
                    #if visitor:
                        # Add the structured data for each individual visitor
                        structured_data.append({
                            'Visit_ID': visit_id,  # Unique visit event ID
                            'Historical Date': historical_date,
                            'Modern Date': modern_date,
                            'Inn': inn,
                            'Visitor': visitors,
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
#print(df_structured.head())

# Save the structured DataFrame to a new CSV file with UTF-8 encoding
df_structured.to_csv('structured_guests_with_inn_ids_sarah.csv', index=False, encoding='utf-8')

# import CSV of nachtzeddel
records = pd.read_csv('structured_guests_with_inn_ids.csv', header=0)
names_column = []
hits_column = []
confusing_records = []
confusing_count = 0
for record in records['Visitor']:
    #print("rec: " + record)
    names = []
    hit_names = []

    # clean the record
    for title in titles:
        if record == title:
            continue
    record = record.replace(' f. 1.', '.')
    record = record.replace(' f. 2.', '.')
    record = record.replace(' ſ. 2.', '.')
    record = record.replace(' f. 3.', '.')
    record = record.replace(' f. 4.', '.')
    record = record.replace('Mr-', 'Mr.')
    record = record.replace('Mr ', 'Mr.')
    record = record.replace('Hr ', 'Hr.')
    record = record.replace('Landl-', 'Landl')
    record = record.replace('-Herr', '. Herr')
    record = record.replace(' und ', ' & ')
    record = record.replace('& 1', '. 1')
    record = record.replace('& 2', '. 2')
    record = record.replace('& 3', '. 3')
    record = record.replace('& 4', '. 4')
    record = record.replace(' & Frau', '')

    # stop on confusion
    confusing = False
    if ':' in record:
        confusing = True
    if '-' in record:
        confusing = True
    if '&' in record:
        confusing = True
    if confusing:
        names.append("UNABLE TO PARSE")
        print("confusing: " + record)
        confusing_count += 1
    else:
        # parse record
        visitor_list = record.split('.')
        visitor_list_names = []
        next_no_period = False
        new_name = False
        for index, piece in enumerate(visitor_list):
            # clean up piece
            piece = piece.strip(' ')
            if len(piece) >= 2 and piece[slice(len(piece)-2, len(piece))] == ' f':
                piece = piece[:len(piece)-2]
            #print(piece)

            # ignore lower class counts
            if not piece or piece[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                continue
            if piece[slice(0, 4)] == 'Ein ':    
                continue

            if 0 == index:
                visitor_list_names.append(piece)
            elif new_name:
                visitor_list_names.append(piece)
                if ' ' not in piece:
                    new_name = False
            elif piece in titles:
                visitor_list_names.append(piece)
            elif piece in ['Cath', 'Jof', 'Joh', 'Bapt', 'Jac', 'Casp']:
                visitor_list_names[-1] += '. ' + piece
            else:
                if next_no_period:
                    visitor_list_names[-1] += piece
                    next_no_period = False
                    new_name = True
                elif len(visitor_list_names) > 0:
                    visitor_list_names[-1] += '. ' + piece
                    new_name = True
                else:
                    visitor_list_names.append(piece)
                    new_name = True
            if piece[-1] in ['v', 'v']:
                #print("!!!!" + piece)
                visitor_list_names[-1] += 'on '
                next_no_period = True
                new_name = False
        for name in visitor_list_names:
            names.append(name)
            """
            hits = get_wiki_hits(name)
            #print(hits)
            if len(hits) > 0:
                hit_names.append(name + " (" + str(' '.join(hits)) + ")")

            # check hits without title
            for title in titles:
                if title in name:
                    hits = []
                    name = name.replace(title, '')
                    hits = get_wiki_hits(name)
                    if len(hits) > 0:
                        hit_names.append(name + " (" + str(' '.join(hits)) + ")")
            
            # check hits without von something
            if 'von' in name:
                hits = []
                name = name[slice(0, name.index('von'))]
                hits = get_wiki_hits(name)
                if len(hits) > 0:
                    hit_names.append(name + " (" + str(' '.join(hits)) + ")")
                    """
    #print(names)

    names_column.append(', '.join(names))
    hits_column.append(', '.join(hit_names))
print("confusing_count: " + str(confusing_count))

# add names to records
records['Names'] = names_column
records['Hits'] = hits_column

# save records
records.to_csv('hotels_with_names_extracted.csv', index=False, encoding='utf-8')
