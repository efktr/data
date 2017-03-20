# Data taken from http://stitch.embl.de/download/chemicals.inchikeys.v5.0.tsv.gz


import json
import csv
import os
import gzip
import pycurl

temp_folder = './temp'
data_folder = './data'
scope_name = 'stitch'


source_zip_url = 'http://stitch.embl.de/download/chemicals.inchikeys.v5.0.tsv.gz'

temp_file = os.path.join(temp_folder, scope_name, "stitch_chemichal_inchi.tsv.gz")

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
with gzip.open(os.path.join(temp_folder, scope_name, "stitch_chemichal_inchi.tsv.gz"), 'rb') as f:
    stitch_chemichal_inchi_content = f.read()
    f.close()

print("Reading data ...")
stitch_to_umls = {}
umls_dictionary = set()
reader = csv.DictReader(stitch_chemichal_inchi_content.split("\n"), delimiter='\t',
                        fieldnames=[
                            'flat_chemical_id',
                            'stereo_chemical_id',
                            'placebo',
                            'inchikey'])

with open(os.path.join(data_folder, "sider", "stitchToUmls.json")) as data_file:
    data = json.load(data_file)
    data_file.close()

# TODO - Map stich id's from sider to the ones from stitch and save inChi to document