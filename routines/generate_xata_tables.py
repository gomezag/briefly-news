from database.xata_api import XataAPI
import json

client = XataAPI(branch='main').client

with open('database/schema.json', 'r') as f:
    structure = json.loads(f.read())

for table in structure['tables']:
    res = client.table().getTableSchema(table['name'])
    if res.status_code == 404:
        res = client.table().createTable(table['name'])
        assert res.status_code == 201, f'Status {res.status_code} when creating the table. {res.text}'
        for column in table['columns']:
            res = client.table().addTableColumn(table['name'], payload=column)
