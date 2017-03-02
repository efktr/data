# Current Drugbank Mapping TSV file address: https://www.drugbank.ca/releases/5-0-5/downloads/all-drugbank-vocabulary

from __future__ import print_function
import pubchempy
import os
import urllib2
import pandas
import zipfile
import csv
import json

source_zip_url = 'https://www.drugbank.ca/releases/5-0-5/downloads/all-drugbank-vocabulary'
temp_folder = './temp'
data_folder = './data'
scope_name = 'drugbank'
temp_file = os.path.join(temp_folder, scope_name + '.zip')

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

with open(os.path.join(temp_folder, scope_name, "drugbank vocabulary.csv")) as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        # Fields: DrugBank ID,Accession Numbers,Common name,CAS,UNII,Synonyms,Standard InChI Key
        drugbankId = row['DrugBank ID']
        commonName = row['Common name']
        synonyms = row['Synonyms']
        inChi = row['Standard InChI Key']


        current = {
            "drugbankId": drugbankId,
            "commonName": commonName,
            "synonyms": synonyms,
            "inChi": inChi
        }

        if current['inChi'] is not None and current['inChi'] is not "":
            data.append(current)

# Read DrugBank compounds
drugbank_df = pandas.DataFrame(data)

if not os.path.isdir(os.path.join(data_folder, scope_name)):
    os.makedirs(os.path.join(data_folder, scope_name))

if not os.path.isdir(os.path.join(data_folder, scope_name, "temp")):
    os.makedirs(os.path.join(data_folder, scope_name, "temp"))

# map DrugBank compounds to pubchem using InChI
rows = list()
for i, row in drugbank_df.iterrows():
    try:
        compounds = pubchempy.get_compounds(row.inChi, namespace='inchikey')
        compounds = [compound.cid for compound in compounds]
        if len(compounds) > 0:
            row['pubChemIds'] = compounds
            print(row['inChi'], "-->", row['pubChemIds'])
            rows.append(row)
        with open(os.path.join(data_folder, scope_name, "temp", row['drugbankId'] + ".json"), 'wb') as out:
            out.write(json.dumps(row))
            out.close()
    except pubchempy.BadRequestError:
        continue
    except pubchempy.ServerError:
        continue
    except:
        continue

# mapped_df = pandas.DataFrame(rows)
# mapping_df = mapped_df[['drugbankId', 'pubChemIds']].dropna()


print("Writing data...")

if not os.path.isdir(os.path.join(data_folder, scope_name)):
    os.makedirs(os.path.join(data_folder, scope_name))

with open(os.path.join(data_folder, scope_name, "inChiToPubChemIds.json"), 'wb') as out:
    out.write(json.dumps(rows))
    out.close()

    # Save mapping
    # mapping_df.to_json(os.path.join(data_folder, scope_name, "pubChemToDrugbank.json"))