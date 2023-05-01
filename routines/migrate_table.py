from database.xata_api import XataAPI
from database.exceptions import OperationError


def migrate_table(source: XataAPI, dest: XataAPI, table: str):
    if source.branch == dest.branch:
        raise OperationError('Source and destination branches are the same!')
    records = source.query(table, filter={})
    print(records)
    for record in records:
        record.pop('id')
        record.pop('xata')
        print(record)
        [record.pop(key) for key in record.keys() if key.startswith('publisher.')]
        print(record)
        dest.create(table, record)
