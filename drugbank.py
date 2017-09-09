# Currently get full xml drugbank db as: curl -L -o filename.zip -u EMAIL:PASSWORD https://www.drugbank.ca/releases/5-0-5/downloads/all-full-database

import xmltodict
import json
import os
import zipfile
import pycurl

temp_folder = './temp'
data_folder = './data'
scope_name = 'drugbank'

USERNAME = os.environ['DRUGBANK_USER']
PASSWORD = os.environ['DRUGBANK_PASSWORD']

source_zip_url = 'https://www.drugbank.ca/releases/5-0-5/downloads/all-full-database'
temp_file = os.path.join(temp_folder, scope_name, "drugbank-full.zip")

if not os.path.isdir(temp_folder):
    os.makedirs(temp_folder)

if not os.path.isdir(os.path.join(temp_folder, scope_name)):
    os.makedirs(os.path.join(temp_folder, scope_name))

if not os.path.isfile(temp_file):
    print("Downloading file ...")
    try:
        with open(temp_file, 'wb') as current_file:
            c = pycurl.Curl()
            c.setopt(c.USERPWD, '%s:%s' % (USERNAME, PASSWORD))
            c.setopt(c.FOLLOWLOCATION, 1)
            c.setopt(c.URL, source_zip_url)
            c.setopt(c.WRITEDATA, current_file)
            c.perform()
            c.close()
    except IOError as e:
        print("Can't retrieve %r to %r: %s" % (source_zip_url, temp_folder, e))
        quit()

print("Unzipping file ...")
try:
    with zipfile.ZipFile(temp_file) as fdazip:
        for n in fdazip.namelist():
            destination = os.path.join(temp_folder, scope_name, n)
            destination_dir = os.path.dirname(destination)
            if not os.path.isdir(destination_dir):
                os.makedirs(destination_dir)
            with fdazip.open(n) as file:
                with open(destination, 'w') as f:
                    f.write(file.read())
                    f.close()
                file.close()
        fdazip.close()
except zipfile.error as e:
    print("Bad zipfile (from %r): %s" % (source_zip_url, e))
    quit()

print("Opening XML database dump")
with open(os.path.join(temp_folder, scope_name, "full database.xml")) as f:
    print("Opened XML database dump")

    print("Parsing XML into dictionaries.. This will take a while!")
    d = xmltodict.parse(f, xml_attribs=True)
    print("Parsed XML into dictionaries")

    if not os.path.isdir(data_folder):
        os.makedirs(data_folder)

    if not os.path.isdir(os.path.join(data_folder, scope_name)):
        os.makedirs(os.path.join(data_folder, scope_name))

    with open(os.path.join(data_folder, scope_name, 'drugbank.json'), 'wb') as out:
        print("Writing JSON representation of database and filtering only wanted fields")

        result = []

        for drug in d['drugbank']['drug']:
            current = {'name': drug['name']}

            if isinstance(drug['drugbank-id'], list):
                current['drugbankId'] = [e['#text'] for e in drug['drugbank-id'] if isinstance(e, dict) and e['@primary'] == 'true'][0]
                current['otherIds'] = [e['#text'] for e in drug['drugbank-id'] if isinstance(e, dict) and e['@primary'] != 'true']

                print(current)
                quit()
            else:
                current['drugbankId'] = drug['drugbank-id']['#text']

            if drug['synonyms'] is None:
                current['synonyms'] = None
            elif isinstance(drug['synonyms']['synonym'], list):
                current['synonyms'] = list(set([e['#text'] for e in drug['synonyms']['synonym'] if e['#text'] is not None]))
            else:
                current['synonyms'] = [drug['synonyms']['synonym']['#text']]

            if drug['products'] is None:
                current['products'] = None
            elif isinstance(drug['products']['product'], list):
                current['products'] = list(set([e['name'] for e in drug['products']['product'] if e['name'] is not None]))
            else:
                current['products'] = [drug['products']['product']['name']]

            result.append(current)

        out.write(json.dumps(result))
        out.close()

print("Done.")