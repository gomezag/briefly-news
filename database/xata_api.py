from xata.client import XataClient
from database.exceptions import OperationError
import os
from dotenv import load_dotenv
from .utils import get_project_root

env_file = os.path.join(get_project_root(), '.env')

load_dotenv(env_file)

XATA_API_KEY = os.getenv('XATA_API_KEY')
XATA_DB_URL = os.getenv('XATA_DB_URL')


class XataAPI(object):
    def __init__(self, *args, **kwargs):
        self.branch = kwargs.pop('branch', 'main')
        self.client = XataClient(api_key=XATA_API_KEY, db_url=f"{XATA_DB_URL}:{self.branch}")

    def process_parms(self, params):
        """
        Takes an object dictionary and returns a proper Xata query dictionary.
        Handles a list by setting the query key $includesAll, and $is
        :param params:
        :return:
        """
        if type(params) == list:
            r = dict()
            query = {}
            for p in params:
                query.update({'$is': p})
            r['$includesAll'] = query
            return r
        elif type(params) == dict:
            r = dict()
            for key, value in params.items():
                r[key] = self.process_parms(value)
            return r
        else:
            return params

    def query(self, table, **params):
        try:
            process_params = self.process_parms(params)
            print(process_params)
            records = self.client.query(table, **process_params)
            if not records.get('message', None):
                return records['records']
            else:
                raise FileNotFoundError('Record not found')
        except Exception as e:
            raise OperationError(e)

    def create(self, table, record_dict):
        created_record = self.client.records().insertRecord(table, record_dict).json()
        if created_record.get('message', None):
            raise OperationError(f"{created_record.get('message')}")

        r = record_dict.copy()
        r.update({"id": created_record['id']})
        return r

    def read(self, table, record_id):
        record = self.client.records().getRecord(table, record_id)
        if record:
            return record.json()

        return None

    def update(self, table, record_id, record):
        try:
            res = self.client.records().updateRecordWithID(table, record_id, record)
        except Exception as e:
            raise OperationError(e)
        if res:
            r = record.copy()
            r.update(res.json())
        return r

    def delete(self, table, record_id):
        r = self.client.records().deleteRecord(table, record_id)
        if r.status_code != 204:
            raise OperationError(r.json()['message'])
        return r

    def get_or_create(self, table, record_dict):
        try:
            record = self.query(table, filter=record_dict)
            if len(record) > 1:
                raise OperationError('There is more than one matching record.')
            record = record[0]
            created = False

        except (FileNotFoundError, IndexError):
            record = self.create(table, record_dict)
            created = True
        
        return record, created
