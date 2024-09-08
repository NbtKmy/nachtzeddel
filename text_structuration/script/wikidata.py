import os
import re
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import time

start = time.time()

titles = ['Hr', 'Mr', 'Fr', 'Herr', 'Monsieur', 'Frau', 'Madame', 'Jkr', 'Madm', 'Pfr', 'Pr']

def get_wiki_hits(name):
    url = "https://de.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": name,
        "format": "json"
    }
    hits = []
    if len(name) > 0:
        r = requests.get(url=url, params=params)
        results = r.json()
        hits = results[3]
    return hits

def get_name_hits(name):
    links = []
    hits = get_wiki_hits(name)
    #print(hits)
    if len(hits) > 0:
        links.append(name + " (" + str(' '.join(hits)) + ")")

    # check hits without title
    for title in titles:
        title_with_period = title + '. '
        if title_with_period in name:
            hits = []
            name = name.replace(title_with_period, '')
            hits = get_wiki_hits(name)
            if len(hits) > 0:
                links.append(name + " (" + str(' '.join(hits)) + ")")
        
    # check hits without von something
    if ' von ' in name:
        hits = []
        name = name[slice(0, name.index(' von '))]
        hits = get_wiki_hits(name)
        if len(hits) > 0:
            links.append(name + " (" + str(' '.join(hits)) + ")")

    # check hits without aus something
    if ' aus ' in name:
        hits = []
        name = name[slice(0, name.index(' aus '))]
        hits = get_wiki_hits(name)
        if len(hits) > 0:
            links.append(name + " (" + str(' '.join(hits)) + ")")

    # check hits without de something
    if ' de ' in name:
        hits = []
        name = name[slice(0, name.index(' de '))]
        hits = get_wiki_hits(name)
        if len(hits) > 0:
            links.append(name + " (" + str(' '.join(hits)) + ")")

    # check hits without d' something
    if ' d\'' in name:
        hits = []
        name = name[slice(0, name.index(' d\''))]
        hits = get_wiki_hits(name)
        if len(hits) > 0:
            links.append(name + " (" + str(' '.join(hits)) + ")")

    # check hits without D' something
    if ' D\'' in name:
        hits = []
        name = name[slice(0, name.index(' D\''))]
        hits = get_wiki_hits(name)
        if len(hits) > 0:
            links.append(name + " (" + str(' '.join(hits)) + ")")

    return links

# Inns to look for in the text
inns = ['SCHWERDT', 'STORCHEN', 'STÖRCHEN', 'STOKCHEN', 'ADLER', 'HIRSCHEN', 'RAABEN', 'RABEN', 'LEUEN', 'LEUWEN', 'LUEN', 'ROESSL', 'ROESSLI', 'ROESSLE', 'ROEFSLI', 'ROESSEL', 'SCHWANEN', 'ROTHHAUS', 'ROTHAUS', 'ROTHUS', 'HAAREN', 'KUTSCHEN', 'SCHEHAUS']

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

confusing_count = 0
def parse_visitor_line(record):
    global confusing_count
    # clean the record
    for title in titles:
        if record == title:
            return ''
    record = record.replace(' f. 1.', '.')
    record = record.replace(' f. 2.', '.')
    record = record.replace(' ſ. 2.', '.')
    record = record.replace(' f. 3.', '.')
    record = record.replace(' f. 4.', '.')
    record = record.replace(' f. 5.', '.')
    record = record.replace(' f. 6.', '.')
    record = record.replace(' f. 7.', '.')
    record = record.replace(' f. 8.', '.')
    record = record.replace(' f. 1', '')
    record = record.replace(' f. 2', '')
    record = record.replace(' f. 3', '')
    record = record.replace(' f. 4', '')
    record = record.replace(' f. 5', '')
    record = record.replace(' f. 6', '')
    record = record.replace(' f. 7', '')
    record = record.replace(' f. 8', '')
    record = record.replace('Mr-', 'Mr.')
    record = record.replace('Mr ', 'Mr.')
    record = record.replace('Hr ', 'Hr.')
    record = record.replace('Landl-', 'Landl')
    record = record.replace('-Herr', '. Herr')
    record = record.replace(' u. ', ' und ')
    record = record.replace(' und ', ' & ')
    record = record.replace(' v. ', ' von ')
    record = record.replace('& 1', '. 1')
    record = record.replace('& 2', '. 2')
    record = record.replace('& 3', '. 3')
    record = record.replace('& 4', '. 4')
    record = record.replace('& 5', '. 5')
    record = record.replace('& 6', '. 6')
    record = record.replace('& 7', '. 7')
    record = record.replace('& 8', '. 8')
    record = record.replace(' be ', ' de ')
    record = record.replace('St. ', 'Sankt ')
    record = record.replace('St ', 'Sankt ')
    record = record.replace('Tfch', 'Tsch')
    record = record.replace('tfch', 'tsch')
    #record = record.replace(' & Frau', '')
    record = record.strip(' ')
    record = record.strip('-')
    record = record.strip(',')
    record = record.strip('&')
    record = record.strip(' ')

    # stop on confusion
    confusing = False
    if ':' in record:
        confusing = True
    if '-' in record and not "Portrait-Mahler" in record and not "Glas-händler" in record and not "Capaunen-händler" in record:
        confusing = True
    if '&' in record:
        confusing = True
    if '}' in record:
        confusing = True
    if confusing:
        print("confusing: " + record)
        confusing_count += 1
        return "UNABLE TO PARSE", ""
    
    # parse record
    visitor_list = record.split('.')
    record = ''
    visitor_list_names = []
    new_name = False
    for index, piece in enumerate(visitor_list):
        # clean up piece
        piece = piece.strip(' ')
        if len(piece) >= 2 and piece[slice(len(piece)-2, len(piece))] == ' f':
            piece = piece[:len(piece)-2]

        # ignore lower class counts
        if not piece or piece[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            continue
        if piece[slice(0, 4)] == 'Ein ':    
            continue
        if piece[slice(0, 5)] == 'Eine ':    
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
            if len(visitor_list_names) > 0:
                visitor_list_names[-1] += '. ' + piece
                new_name = True
            else:
                visitor_list_names.append(piece)
                new_name = True

    links = []
    for name in visitor_list_names:
        hits = get_name_hits(name)
        links.append(str(' '.join(hits)))
    joined_names = ', '.join(visitor_list_names)
    joined_links = ', '.join(links)
    #print(joined_links)
    return joined_names, joined_links

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
    visitor_lines = []
    lines = content.splitlines()
    for line in lines:
        if inn_in_line(line):
            #print(line)
            if inn:
                inn_data[inn] = visitor_lines
            # Start a new key and reset the list
            inn = inn_in_line(line)
            visitor_lines = []
        else:
            # Add non-inn lines to the current list
            if inn and len(line) > 0:
                joined_names, joined_links = parse_visitor_line(line)
                visitor_lines.append( { "raw_line" : line, "processed_line" : joined_names, "links": joined_links } )
        #print(inn_data)
    return historical_date, modern_date, inn_data

# Initialize an empty list to hold the structured data
structured_data = []

# Initialize counters for visit and guest IDs
visit_id = 1

# Get all files in the directory and sort them alphanumerically
files = []
txt_directory = '../../ideas/ocr_mit_claude'
#print(os.walk(txt_directory))
for x in os.walk(txt_directory):
    #print(x)
    files += sorted([x[0] + '/' + f for f in os.listdir(x[0]) if f.endswith(".txt")])

# Iterate over all text files in the directory, in sequential order
line_limit_count = 0
for filename in files:
    #print(filename)
    filepath = os.path.join(txt_directory, filename)
    #print(filepath)
    historical_date, modern_date, inn_data = parse_file(filepath)
    if historical_date and modern_date and inn_data:
        # Iterate over each inn and process visitors
        for inn, visitor_lines in inn_data.items():
            if visitor_lines:  # If there are visitors listed for the inn
                #visitor_list = visitors.split(', ')  # Separate individual visitors
                for line in visitor_lines:
                        line_limit_count += 1
                        if line_limit_count > 1000000:
                            break
                    #print(visitor)
                    #if visitor:
                        # Add the structured data for each individual visitor
                        structured_data.append({
                            'Visit_ID': visit_id,  # Unique visit event ID
                            'Historical Date': historical_date,
                            'Modern Date': modern_date,
                            'Inn': inn,
                            'Raw Line': line["raw_line"],
                            'Visitor': line["processed_line"],
                            'Links': line["links"],
                            'Filename': filename
                        })
                        visit_id += 1  # Increment visit ID
                else:
                    continue
                break
        else:
            continue
        break
# Convert the structured data into a DataFrame
df_structured = pd.DataFrame(structured_data)

# Step 1: Assign a unique ID to each inn and place the 'Inn_ID' column next to the 'Inn' column
inn_unique_ids = {inn: idx + 1 for idx, inn in enumerate(df_structured['Inn'].unique())}
df_structured['Inn_ID'] = df_structured['Inn'].map(inn_unique_ids)

# Reorder columns to place 'Inn_ID' next to 'Inn'
df_structured = df_structured[['Visit_ID', 'Historical Date', 'Modern Date', 'Inn', 'Inn_ID', 'Raw Line', 'Visitor', 'Links', 'Filename']]

# Display the structured DataFrame with the new Inn_ID column next to Inn
#print(df_structured.head())

# Save the structured DataFrame to a new CSV file with UTF-8 encoding
df_structured.to_csv('structured_guests_with_inn_ids_bradley.csv', index=False, encoding='utf-8')

print("confusing_count: " + str(confusing_count))

end = time.time()
print('Runtime: ' + str(end - start))