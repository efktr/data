# Data from FDA: drug names
# https://www.fda.gov/downloads/Drugs/InformationOnDrugs/UCM527389.zip

import urllib2
import zipfile
import os
import csv
from sets import Set


source_zip_url = 'https://www.fda.gov/downloads/Drugs/InformationOnDrugs/UCM527389.zip'
download = False
temp_folder = './temp'
data_folder = './data'
file_name = 'fda-drugs'
temp_file = os.path.join(temp_folder, file_name + '.zip')
data_file = os.path.join(data_folder, file_name + '.json')

if not os.path.isdir(temp_folder):
    os.makedirs(temp_folder)

if not os.path.isdir(data_folder):
    os.makedirs(data_folder)

if download:
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

drugs = Set()
drugs_to_Ingredient = Set()
ingredients = Set()


with open(os.path.join(temp_folder, file_name, 'Products.txt')) as csv_file:
    reader = csv.DictReader(csv_file, delimiter='\t')
    for row in reader:
        drug_name = row['DrugName'].lower()
        ing_list = row['ActiveIngredient'].lower().split("; ")

        drugs.add(drug_name)
        for ingredient in ing_list:
            ingredients.add(ingredient)
        # drugs_to_Ingredient.add((drug_name, ing_list))
        print(drug_name, ing_list)

quit()
