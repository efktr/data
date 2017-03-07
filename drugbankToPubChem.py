# Current Drugbank Mapping TSV file address: https://www.drugbank.ca/releases/5-0-5/downloads/all-drugbank-vocabulary

from __future__ import print_function
import pubchempy
import os
import urllib2
import pandas
import zipfile
import csv
import json
import re

source_zip_url = 'https://www.drugbank.ca/releases/5-0-5/downloads/all-drugbank-vocabulary'
temp_folder = './temp'
data_folder = './data'
scope_name = 'drugbank'
temp_file = os.path.join(temp_folder, scope_name + '.zip')
use_cache_only = False

if not os.path.isdir(temp_folder):
    os.makedirs(temp_folder)

if not os.path.isfile(temp_file):
    print("Downloading file ...")
    try:
        response = urllib2.urlopen(source_zip_url).read()
    except IOError, e:
        print("Can't retrieve %r to %r: %s" % (source_zip_url, temp_folder, e))
        quit()

    try:
        with open(temp_file, 'w') as f:
            f.write(response)
            f.close()
    except:
        print("Could not write zipfile to temp_dir")
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
except zipfile.error, e:
    print("Bad zipfile (from %r): %s" % (source_zip_url, e))
    quit()

print("Reading data ...")
data = []
reg_split_no_esc = re.compile('[\s]?\|[\s]?')
with open(os.path.join(temp_folder, scope_name, "drugbank vocabulary.csv")) as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        # Fields: DrugBank ID,Accession Numbers,Common name,CAS,UNII,Synonyms,Standard InChI Key
        drugbankId = row['DrugBank ID']
        commonName = row['Common name']
        synonyms = re.split(reg_split_no_esc, row['Synonyms'])
        inChi = row['Standard InChI Key']


        current = {
            "drugbankId": drugbankId,
            "commonName": commonName,
            "synonyms": synonyms,
            "inChi": inChi
        }

        if current['inChi'] is not None and current['inChi'] is not "":
            data.append(current)

if not os.path.isdir(os.path.join(temp_folder, scope_name, "temp")):
    os.makedirs(os.path.join(temp_folder, scope_name, "temp"))

# Filter out data that has already been downloaded
cached_files = [f.replace(".json", "") for f in os.listdir(os.path.join(temp_folder, scope_name, "temp")) if os.path.isfile(os.path.join(temp_folder, scope_name, "temp", f))]
data = [item for item in data if item["drugbankId"] not in cached_files]

if not use_cache_only:
    print("Getting pubChemIds for", len(data), "items")

    # Read DrugBank compounds
    drugbank_df = pandas.DataFrame(data)
    # map DrugBank compounds to pubchem using InChI
    rows = list()
    for i, row in drugbank_df.iterrows():
        try:
            compounds = pubchempy.get_compounds(row.inChi, namespace='inchikey')
            compounds = [compound.cid for compound in compounds]
            if len(compounds) > 0:
                row['pubChemIds'] = compounds
                print(row['drugbankId'], "-->", row['pubChemIds'])
                rows.append(row)
                row.to_json(os.path.join(temp_folder, scope_name, "temp", row['drugbankId'] + ".json"))
            else:
                print(row['drugbankId'], "-->", "NO HIT")
        except pubchempy.BadRequestError:
            print(row['drugbankId'], "-->", "Bad Request!")
            continue
        except pubchempy.ServerError:
            print(row['drugbankId'], "-->", "Server Error!")
            continue
        except:
            print("Unknown exception")
            continue

print("Writing data...")

if not os.path.isdir(os.path.join(data_folder, scope_name)):
    os.makedirs(os.path.join(data_folder, scope_name))

inChiToPubChemIds = []
cached_files = [f for f in os.listdir(os.path.join(temp_folder, scope_name, "temp")) if os.path.isfile(os.path.join(temp_folder, scope_name, "temp", f))]
for f in cached_files:
    with open(os.path.join(temp_folder, scope_name, "temp", f)) as current:
        inChiToPubChemIds.append(json.loads(current.read()))
        current.close()

with open(os.path.join(data_folder, scope_name, "inChiToPubChemIds.json"), 'wb') as out:
    out.write(json.dumps(inChiToPubChemIds))
    out.close()

drugbankToPubChem = [{"drugbankId": e['drugbankId'], "pubChemIds": e['pubChemIds']} for e in inChiToPubChemIds]
with open(os.path.join(data_folder, scope_name, "drugbankToPubChem.json"), 'wb') as out:
    out.write(json.dumps(drugbankToPubChem))
    out.close()

with open(os.path.join(data_folder, scope_name, "pubChemToDrugbankDictionary.json"), 'wb') as out:
    result = []
    for item in drugbankToPubChem:
        for pubChemId in item["pubChemIds"]:
            result.append({"drugbankId": item['drugbankId'], "pubChemId": pubChemId})
    out.write(json.dumps(result))
    out.close()

quit()