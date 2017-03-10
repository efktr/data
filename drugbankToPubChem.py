# Current Drugbank Mapping TSV file address: https://www.drugbank.ca/releases/5-0-5/downloads/all-drugbank-vocabulary

from __future__ import print_function
import pubchempy
import os
import pycurl
import zipfile
import csv
import json
import re

source_zip_url = 'https://www.drugbank.ca/releases/5-0-5/downloads/all-drugbank-vocabulary'
temp_folder = './temp'
data_folder = './data'
scope_name = 'drugbank'
temp_file = os.path.join(temp_folder, scope_name, 'drugbankToPubChem.zip')
use_cache_only = False

if not os.path.isdir(temp_folder):
    os.makedirs(temp_folder)

if not os.path.isdir(os.path.join(temp_folder, scope_name)):
    os.makedirs(os.path.join(temp_folder, scope_name))

if not os.path.isfile(temp_file):
    print("Downloading file ...")
    try:
        with open(temp_file, 'wb') as current_file:
            c = pycurl.Curl()
            c.setopt(c.FOLLOWLOCATION, 1L)
            c.setopt(c.URL, source_zip_url)
            c.setopt(c.WRITEDATA, current_file)
            c.perform()
            c.close()
    except IOError, e:
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

if not os.path.isdir(os.path.join(temp_folder, scope_name, "cache")):
    os.makedirs(os.path.join(temp_folder, scope_name, "cache"))

# Filter out data that has already been downloaded
cached_files = [f.replace(".json", "") for f in os.listdir(os.path.join(temp_folder, scope_name, "cache")) if os.path.isfile(os.path.join(temp_folder, scope_name, "cache", f))]
data = [item for item in data if item["drugbankId"] not in cached_files]

if not use_cache_only:
    print("Getting pubChemIds for", len(data), "items")

    # map DrugBank compounds to pubchem using InChI
    for row in data:
        try:
            compounds = pubchempy.get_compounds(row['inChi'], namespace='inchikey')
            compounds = [compound.cid for compound in compounds]
            if len(compounds) > 0:
                row['pubChemIds'] = compounds
                print(row['drugbankId'], "-->", row['pubChemIds'])
                with open(os.path.join(temp_folder, scope_name, "cache", row['drugbankId'] + ".json"), 'wb') as out:
                    out.write(json.dumps(row))
                    out.close()
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
cached_files = [f for f in os.listdir(os.path.join(temp_folder, scope_name, "cache")) if os.path.isfile(os.path.join(temp_folder, scope_name, "cache", f))]
for f in cached_files:
    with open(os.path.join(temp_folder, scope_name, "cache", f)) as current:
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
