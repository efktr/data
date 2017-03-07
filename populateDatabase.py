import psycopg2
import os
import json
import re

connection = {
    "dbname": os.environ['dbname'] if "dbname" in os.environ is not None else "efktr",
    "user": os.environ['user'] if "user" in os.environ is not None else "postgres",
    "password": os.environ['password'] if "password" in os.environ else "postgres",
    "host": os.environ['host'] if "host" in os.environ is not None else "127.0.0.1",
    "port": os.environ['port'] if "port" in os.environ is not None else "32768"
}

drugbank_data = os.path.join("data", "drugbank", "drugbank.json")
pubchem_to_drugbank_data = os.path.join("data", "drugbank", "pubChemToDrugbankDictionary.json")

# Try to connect to db
try:
    connection_string = ("dbname=" + connection['dbname'] +
                         " user=" + connection['user'] +
                         " host=" + connection['host'] +
                         " port=" + connection['port'] +
                         " password=" + connection['password'])

    print(connection_string)

    conn = psycopg2.connect(connection_string)
except:
    print "I am unable to connect to the database"

cursor = conn.cursor()

# Insert drugbank data
drugbank_file = open(drugbank_data)
drugbank = json.loads(drugbank_file.read())
drugbank_file.close()

drugbank_table = []
drugbank_synonyms_table = []
drugbank_products_table = []

for element in drugbank:
    drugbank_table.append(cursor.mogrify('(%s, %s)', (element['name'], element['drugbankId'])))
    if element['synonyms'] is not None:
            for synonym in element['synonyms']:
                drugbank_synonyms_table.append(cursor.mogrify('(%s, %s)', (synonym, element['drugbankId'])))
    if element['products'] is not None:
        for product in element['products']:
            drugbank_products_table.append(cursor.mogrify('(%s, %s)', (product, element['drugbankId'])))

drugbank_table = psycopg2.extensions.AsIs(','.join(drugbank_table))
drugbank_synonyms_table = psycopg2.extensions.AsIs(','.join(drugbank_synonyms_table))
drugbank_products_table = psycopg2.extensions.AsIs(','.join(drugbank_products_table))

insert_drugbank_table = 'insert into drugbank ("name", "drugbank_id") values %s'
insert_drugbank_synonyms_table = 'insert into drugbank_synonyms ("synonym", "drugbank_id") values %s  on conflict do nothing'
insert_drugbank_products_table = 'insert into drugbank_products ("product", "drugbank_id") values %s  on conflict do nothing'

try:
    cursor.execute(insert_drugbank_table, [drugbank_table])
    cursor.execute(insert_drugbank_synonyms_table, [drugbank_synonyms_table])
    cursor.execute(insert_drugbank_products_table, [drugbank_products_table])
except psycopg2.ProgrammingError as error:
    print error

# Insert Sider data

try:

    conn.commit()
    cursor.close()
    conn.close()
except:
    print "Cannot commit and close connection"