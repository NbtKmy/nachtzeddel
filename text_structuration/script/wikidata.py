import pandas as pd
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
