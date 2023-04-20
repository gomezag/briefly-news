from xata.client import XataClient
import config
import os
from .utils import get_project_root

env_file = os.path.join(get_project_root(), '.env')

cfg = config.Config(env_file)

XATA_API_KEY = cfg.get('XATA_API_KEY')
DB_URL = cfg.get('XATA_DB_URL')

class XataAPI:
    def __init__(self):
        self.client = XataClient(api_key=XATA_API_KEY, db_url=DB_URL)


    def create(self, table, record_dict):
        created_record = self.client.records().insertRecord(table, record_dict).json()
        record_dict.update({"id": created_record['id']})

        return record_dict


    def read(self, table, record_id):
        record = self.client.records().getRecord(table, record_id)
        if record:
            return record.json()

        return None
    
    
    def delete(self, table, record_id):
        return self.client.records().deleteRecord(table, record_id)