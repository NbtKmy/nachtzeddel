import pandas as pd
#from wikidata.client import Client

# Create a Wikidata client
#client = Client()

# import CSV of nachtzeddel
records = pd.read_csv('structured_guests_with_inn_ids.csv', header=0)
names_column = []
confusing_records = []
confusing_count = 0
for record in records['Visitor']:
    #print("rec: " + record)
    names = []

    # stop on confusion
    confusing = False
    if ':' in record:
        confusing = True
    if 'und' in record:
        confusing = True
    if '-' in record and "Portrait-Mahler" not in piece and "Comödien-Director" not in piece:
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


            if 0 == index:
                visitor_list_names.append(piece)
            elif new_name:
                visitor_list_names.append(piece)
                if ' ' not in piece:
                    new_name = False
            elif piece in ['Hr', 'Mr', 'Fr', 'Herr', 'Monsieur', 'Frau', 'Madame', 'Jkr']:
                visitor_list_names.append(piece)
            elif piece in ['Cath', 'Jof', 'Joh', 'Bapt', 'Jac']:
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
    #print(names)  
    names_column.append(', '.join(names))
print("confusing_count: " + str(confusing_count))

# add names to records
records['Names'] = names_column

# save records
records.to_csv('hotels_with_names_extracted.csv', index=False, encoding='utf-8')

#for name in names:
#    print(name)
    # Search for the name in Wikidata
    #results = client.search(name)
    #for result in results:
    #    print(result.description)
    #    print(result.label)
    #    print(result.id)
    #    print(result.concept_uri)
    #    print(result.description)
    #    print(result.aliases)
