import psycopg2
import psycopg2.extras
import os
import json

if "DBURI" in os.environ:
    connection_string = os.environ['DBURI']
else:
    connection = {
        "dbname": os.environ['dbname'] if "dbname" in os.environ is not None else "efktr",
        "user": os.environ['user'] if "user" in os.environ is not None else "postgres",
        "password": os.environ['password'] if "password" in os.environ else "postgres",
        "host": os.environ['host'] if "host" in os.environ is not None else "127.0.0.1",
        "port": os.environ['port'] if "port" in os.environ is not None else "32768"
    }

    connection_string = ("dbname=" + connection['dbname'] +
                             " user=" + connection['user'] +
                             " host=" + connection['host'] +
                             " port=" + connection['port'] +
                             " password=" + connection['password'])

# Try to connect to db
try:
    print(connection_string)

    conn = psycopg2.connect(connection_string)
except:
    print "I am unable to connect to the database"

cursor = conn.cursor()

# Insert drugbank data
drugbank_data = os.path.join("data", "drugbank", "drugbank.json")
drugbank_file = open(drugbank_data)
drugbank = json.loads(drugbank_file.read())
drugbank_file.close()

drugbank_table = []
drugbank_synonyms_table = []
drugbank_products_table = []

for element in drugbank:
    c = cursor.mogrify('(%s, %s, %s)', (element['name'], element['drugbankId'], element['otherIds'] if "otherIds" in element is not None else None))
    drugbank_table.append(c)
    if element['synonyms'] is not None:
            for synonym in element['synonyms']:
                drugbank_synonyms_table.append(cursor.mogrify('(%s, %s)', (synonym, element['drugbankId'])))
    if element['products'] is not None:
        for product in element['products']:
            drugbank_products_table.append(cursor.mogrify('(%s, %s)', (product, element['drugbankId'])))

drugbank_table = psycopg2.extensions.AsIs(','.join(drugbank_table))
drugbank_synonyms_table = psycopg2.extensions.AsIs(','.join(drugbank_synonyms_table))
drugbank_products_table = psycopg2.extensions.AsIs(','.join(drugbank_products_table))

insert_drugbank_table = 'insert into drugbank ("name", "drugbank_id", "other_ids") values %s'
insert_drugbank_synonyms_table = 'insert into drugbank_synonyms ("synonym", "drugbank_id") values %s on conflict do nothing'
insert_drugbank_products_table = 'insert into drugbank_products ("product", "drugbank_id") values %s on conflict do nothing'

try:
    cursor.execute(insert_drugbank_table, [drugbank_table])
    cursor.execute(insert_drugbank_synonyms_table, [drugbank_synonyms_table])
    cursor.execute(insert_drugbank_products_table, [drugbank_products_table])
except psycopg2.ProgrammingError as error:
    print error
except psycopg2.IntegrityError as error:
    print error

# Insert UMLS data
umls_dictionary_data = os.path.join("data", "sider", "umlsDictionary.json")

umls_dictionary_file = open(umls_dictionary_data)
umls_dictionary = json.loads(umls_dictionary_file.read())
umls_dictionary_file.close()

umls_dictionary_table = [cursor.mogrify('(%s, %s)', (element['umlsId'], element['name'])) for element in umls_dictionary]
umls_dictionary_table = psycopg2.extensions.AsIs(','.join(umls_dictionary_table))

insert_umls_dictionary_table = 'insert into umls_dictionary ("umls_id", "name") values %s'

try:
    cursor.execute(insert_umls_dictionary_table, [umls_dictionary_table])
except psycopg2.ProgrammingError as error:
    print error

# Insert data from sider...
sider_data = os.path.join("data", "sider", "stitchToUmls.json")
# ... but only insert the data that has drugbank_ids mapped to pubchem_ids. The rest is useless (for now!!)
pubchem_to_drugbank_data = os.path.join("data", "drugbank", "pubChemToDrugbankDictionary.json")

sider_data_file = open(sider_data)
sider_data = json.loads(sider_data_file.read())
sider_data_file.close()

pubchem_to_drugbank_file = open(pubchem_to_drugbank_data)
pubchem_to_drugbank_data = json.loads(pubchem_to_drugbank_file.read())
pubchem_to_drugbank_file.close()

pubchem_table = []
adr_table = []

mapped_pubchem_ids = set([e['pubChemId'] for e in pubchem_to_drugbank_data])
pubchem_ids_in_sider = []

for element in sider_data:
    if element['pubChemId'] in mapped_pubchem_ids:

        pubchem_ids_in_sider.append(element['pubChemId'])

        pubchem_table.append(cursor.mogrify('(%s, %s, %s)', (element['pubChemId'], element['stitchId'], element['stitchIdFlat'])))
        for adr in element['adverseReactions']:
            # !! ODER COUNTS!!
            current_ard = [element['pubChemId']]
            current_ard.append(adr['umlsId'])
            if adr['lower'] > adr['upper']:
                print element['pubChemId'], adr['umlsId'], "has lower bound higher than upper bound. Inverting."
                current_ard.append(psycopg2.extras.NumericRange(lower=adr['upper'], upper=adr['lower']))
            elif adr['lower'] == adr['upper']:
                # Uncomment following line to log when 0.0001 is added to upper to render range not-empty
                # print element['pubChemId'], adr['umlsId'], "has lower bound equal to upper bound. Adding 0.0001 to upper so to render the range non-empty."
                current_ard.append(psycopg2.extras.NumericRange(lower=adr['lower'], upper=adr['upper'] + 0.0001))
            else:
                current_ard.append(psycopg2.extras.NumericRange(lower=adr['lower'], upper=adr['upper']))
            current_ard.append(adr['count'])

            adr_table.append(cursor.mogrify('(%s, %s, %s, %s)', current_ard))
    # Uncomment following lines to log which pubchem ids have no drugbank mapping
    # else:
        # print element['pubChemId'], "has no mapping."

pubchem_to_drugbank_table = [cursor.mogrify('(%s, %s)', (element['pubChemId'], element['drugbankId'])) for element in pubchem_to_drugbank_data if element['pubChemId'] in pubchem_ids_in_sider]
pubchem_to_drugbank_table = psycopg2.extensions.AsIs(','.join(pubchem_to_drugbank_table))
insert_pubchem_to_drugbank_table = 'insert into pubchem_to_drugbank ("pubchem_id", "drugbank_id") values %s on conflict do nothing'


pubchem_table = psycopg2.extensions.AsIs(','.join(pubchem_table))
adr_table = psycopg2.extensions.AsIs(','.join(adr_table))

insert_pubchem_table = 'insert into pubchem ("pubchem_id", "stitch_id", "stitch_id_flat") values %s'
insert_adr_table = 'insert into adverse_drug_reactions ("pubchem_id", "umls_id", "range", "support") values %s'

try:
    cursor.execute(insert_pubchem_table, [pubchem_table])
    cursor.execute(insert_adr_table, [adr_table])
    cursor.execute(insert_pubchem_to_drugbank_table, [pubchem_to_drugbank_table])
except psycopg2.ProgrammingError as error:
    print error

try:
    conn.commit()
    cursor.close()
    conn.close()
except:
    print "Cannot commit and close connection"