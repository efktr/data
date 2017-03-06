# Data from FDA: drug names
# https://www.fda.gov/downloads/Drugs/InformationOnDrugs/UCM527389.zip

import urllib2
import zipfile
import os
import csv
import re
import json


source_zip_url = 'https://www.fda.gov/downloads/Drugs/InformationOnDrugs/UCM527389.zip'
temp_folder = './temp'
data_folder = './data'
file_name = 'fda-drugs'
temp_file = os.path.join(temp_folder, file_name + '.zip')

if not os.path.isdir(temp_folder):
    os.makedirs(temp_folder)

if not os.path.isfile(temp_file):
    print "Downloading file ..."
    try:
        response = urllib2.urlopen(source_zip_url)
        zipcontent = response.read()
    except IOError, e:
        print "Can't retrieve %r to %r: %s" % (source_zip_url, temp_folder, e)
        quit()

    try:
        with open(temp_file, 'w') as f:
            f.write(zipcontent)
            f.close()
    except e:
        print "Could not write zipfile to temp_dir"
        quit()

print "Unzipping file ..."
try:
    with zipfile.ZipFile(temp_file) as fdazip:
        for n in fdazip.namelist():
            destination = os.path.join(temp_folder, file_name, n)
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
    print "Bad zipfile (from %r): %s" % (source_zip_url, e)
    quit()

print "Reading data ..."
drugs = set()
ingredients = set()
forms = set()
products = []
reg_split_no_esc = re.compile(';[\s]?')

with open(os.path.join(temp_folder, file_name, 'Products.txt')) as csv_file:
    reader = csv.DictReader(csv_file, delimiter='\t')
    for row in reader:
        drug_name = row['DrugName'].lower()
        ing_list = re.split(reg_split_no_esc, row['ActiveIngredient'].lower())
        forms_list = re.split(reg_split_no_esc, row['Form'].lower())
        strength = row['Strength'].lower()

        drugs.add(drug_name)
        for ingredient in ing_list:
            ingredients.add(ingredient)

        for form in forms_list:
            forms.add(form)

        current = {
            "drugName": drug_name,
            "activeIngradients": ing_list,
            "form": forms_list,
            "strength": strength
        }

        products.append(current)

print "Writing data ..."
if not os.path.isdir(data_folder):
    os.makedirs(data_folder)

if not os.path.isdir(os.path.join(data_folder, file_name)):
    os.makedirs(os.path.join(data_folder, file_name))

with open(os.path.join(data_folder, file_name, "drugs.json"), 'wb') as out:
    out.write(json.dumps(list(drugs)))
    out.close()

with open(os.path.join(data_folder, file_name, "ingredients.json"), 'wb') as out:
    out.write(json.dumps(list(ingredients)))
    out.close()

with open(os.path.join(data_folder, file_name, "forms.json"), 'wb') as out:
    out.write(json.dumps(list(forms)))
    out.close()

with open(os.path.join(data_folder, file_name, "products.json"), 'wb') as out:
    out.write(json.dumps(products))
    out.close()

print "Done."
quit()
