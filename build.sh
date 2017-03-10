echo "Running python scripts to collect data and fill the database"

echo "Collecting sider data"
python sider.py

echo "Collecting drugbank data to create drugbank-pubchem mapping"
python drugbanckToPubChem.py

echo "Collecting drugbank data"
python drugbank.py

exit 0