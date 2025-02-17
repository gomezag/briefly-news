import json
import os
import sys

# Add the parent directory to the sys.path to import the database module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.xata_api import XataAPI


xata_api = XataAPI(branch='main')

with open('database/schema.json', 'r') as f:
    structure = json.loads(f.read())

for table in structure['tables']:
    schema = xata_api.get_table_schema(table['name'])
    if schema is None:
        xata_api.create_table(table['name'])
        for column in table['columns']:
            xata_api.add_table_column(table['name'], column)