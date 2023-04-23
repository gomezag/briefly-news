from xata.client import XataClient
from database.exceptions import OperationError
import os
from dotenv import load_dotenv
from .utils import get_project_root

env_file = os.path.join(get_project_root(), '.env')

load_dotenv(env_file)

XATA_API_KEY = os.getenv('XATA_API_KEY')
XATA_DB_URL = os.getenv('XATA_DB_URL')


class XataAPI:
    def __init__(self):
        self.client = XataClient(api_key=XATA_API_KEY, db_url=XATA_DB_URL)

    def create(self, table, record_dict):
        created_record = self.client.records().insertRecord(table, record_dict).json()
        if created_record.get('message', None):
            raise OperationError(f"{created_record.get('message')}")
        record_dict.update({"id": created_record['id']})
        return record_dict

    def read(self, table, record_id):
        record = self.client.records().getRecord(table, record_id)
        if record:
            return record.json()

        return None

    def query(self, table, **parms):
        try:
            records = self.client.query(table, **parms)
            if not records.get('message', None):
                return records['records']
            else:
                raise FileNotFoundError('Registro no encontrado')
        except Exception as e:
            raise OperationError(e)

    def update(self, table, record_id, record):
        try:
            r = self.client.records().updateRecordWithID(table, record_id, record)
        except Exception as e:
            raise OperationError(e)
        return r

    def delete(self, table, record_id):
        r = self.client.records().deleteRecord(table, record_id)
        if r.status_code != 204:
            raise OperationError(r.json()['message'])
        return r
