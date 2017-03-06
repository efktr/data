# You need to download the full drugbank database and unzip it!

import xmltodict
import json
import os

temp_folder = './temp'
data_folder = './data'
scope_name = 'drugbank'

source_zip_location = os.path.join(data_folder, scope_name, "drugbank-full.xml")

print("Opening XML database dump")
with open(source_zip_location) as f:
    print("Opened XML database dump")

    print("Parsing XML into dictionaries.. This will take a while!")
    d = xmltodict.parse(f, xml_attribs=True)
    print("Parsed XML into dictionaries")

    with open(os.path.join(data_folder, scope_name + 'drugbank.json'), 'wb') as out:
        print("Writing JSON representation of database and filtering only wanted fields")

        result = []

        for drug in d['drugbank']['drug']:
            current = {'name': drug['name']}

            if isinstance(drug['drugbank-id'], list):
                current['id'] = [e['#text'] for e in drug['drugbank-id'] if isinstance(e, dict) and e['@primary'] == 'true'][0]
            else:
                current['id'] = drug['drugbank-id']['#text']

            if drug['synonyms'] is None:
                current['synonyms'] = None
            elif isinstance(drug['synonyms']['synonym'], list):
                current['synonyms'] = list(set([e['#text'] for e in drug['synonyms']['synonym'] if e['#text'] is not None]))
            else:
                current['synonyms'] = drug['synonyms']['synonym']['#text']

            if drug['products'] is None:
                current['products'] = None
            elif isinstance(drug['products']['product'], list):
                current['products'] = list(set([e['name'] for e in drug['products']['product'] if e['name'] is not None]))
            else:
                current['products'] = drug['products']['product']['name']

            result.append(current)

        out.write(json.dumps(result))
        out.close()

print("Done.")