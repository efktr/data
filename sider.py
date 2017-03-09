# Import data from SIDER
# Current url for latest: ftp://xi.embl.de/SIDER/latest/

from __future__ import print_function
from ftplib import FTP
import gzip
import os
import csv
import json

source_domain = 'xi.embl.de'
source_folder = '/SIDER/latest/'
temp_folder = './temp'
data_folder = './data'
scope_name = 'sider'

if not os.path.isdir(temp_folder):
    os.makedirs(temp_folder)


# Utils
def stitch_flat_to_pubchem(cid):
    assert cid.startswith('CID')
    return int(cid[3:]) - 1e8


def stitch_stereo_to_pubchem(cid):
    assert cid.startswith('CID')
    return int(cid[3:])


# END Utils

if not os.path.isfile(os.path.join(temp_folder, scope_name, "meddra_freq.tsv.gz")):
    print("Connecting to FTP server and collecting data...")

    ftp = FTP(source_domain)
    ftp.login('anonymous', 'anonymous')
    ftp.cwd(source_folder)

    filenames = ftp.nlst()

    if not os.path.isdir(os.path.join(temp_folder, scope_name)):
        os.makedirs(os.path.join(temp_folder, scope_name))

    for filename in filenames:
        local_filename = os.path.join(temp_folder, scope_name, filename)
        if not filename.startswith("."):
            print("Writing file", filename)
            current = open(local_filename, 'wb')
            ftp.retrbinary('RETR ' + filename, current.write)
            current.close()
    ftp.quit()

print("Unzipping file ...")
with gzip.open(os.path.join(temp_folder, scope_name, "meddra_freq.tsv.gz"), 'rb') as f:
    sider_freq_content = f.read()
    f.close()

print("Reading data ...")
stitch_to_umls = {}
umls_dictionary = set()
reader = csv.DictReader(sider_freq_content.split("\n"), delimiter='\t',
                        fieldnames=[
                            'stitch_id_flat',
                            'stitch_id_stereo',
                            'umls_cui_from_label',
                            'placebo',
                            'frequency',
                            'lower',
                            'upper',
                            'meddra_type',
                            'umls_cui_from_meddra',
                            'side_effect_name'])
for row in reader:
    umls_cui = row["umls_cui_from_meddra"] if row["umls_cui_from_meddra"] is not None and row["umls_cui_from_meddra"] != '' else row["umls_cui_from_label"]

    if umls_cui is not None and umls_cui != '':
        umls_dictionary.add((umls_cui, row['side_effect_name']))

        if not row["stitch_id_stereo"] in stitch_to_umls:
            stitch_to_umls[row["stitch_id_stereo"]] = {
                "stitchId": row["stitch_id_stereo"],
                "stitchIdFlat": row["stitch_id_flat"],
                "pubChemId": stitch_stereo_to_pubchem(row["stitch_id_stereo"]),
                "adverseReactions": {
                    umls_cui: {
                        "umlsId": umls_cui,
                        "lower": float(row["lower"]),
                        "upper": float(row["upper"]),
                        "count": 1.0
                    }
                }
            }
        else:
            if not umls_cui in stitch_to_umls[row["stitch_id_stereo"]]['adverseReactions']:
                stitch_to_umls[row["stitch_id_stereo"]]['adverseReactions'][umls_cui] = {
                    "umlsId": umls_cui,
                    "lower": float(row["lower"]),
                    "upper": float(row["upper"]),
                    "count": 1.0
                }
            else:
                stitch_to_umls[row["stitch_id_stereo"]]['adverseReactions'][umls_cui]["count"] += 1.0
                current = stitch_to_umls[row["stitch_id_stereo"]]['adverseReactions'][umls_cui]
                stitch_to_umls[row["stitch_id_stereo"]]['adverseReactions'][umls_cui]['lower'] = current['lower'] + (1 / current['count']) * (float(row["lower"]) - current['lower'])
                stitch_to_umls[row["stitch_id_stereo"]]['adverseReactions'][umls_cui]['upper'] = current['upper'] + (1 / current['count']) * (float(row["upper"]) - current['upper'])
    else:
        print("Lost one dictionary item")


print("Writing data ...")
if not os.path.isdir(data_folder):
    os.makedirs(data_folder)

if not os.path.isdir(os.path.join(data_folder, scope_name)):
    os.makedirs(os.path.join(data_folder, scope_name))

with open(os.path.join(data_folder, scope_name, "umlsDictionary.json"), 'wb') as out:
    out.write(json.dumps(list([{"umlsId": e[0], "name": e[1]} for e in umls_dictionary])))
    out.close()

with open(os.path.join(data_folder, scope_name, "stitchToUmls.json"), 'wb') as out:
    result = stitch_to_umls.values()
    for e in result:
        e['adverseReactions'] = e['adverseReactions'].values()
    out.write(json.dumps(result))
    out.close()

print("Done.")
quit()