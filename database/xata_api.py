from xata.client import XataClient
from xata.helpers import BulkProcessor
from database.exceptions import OperationError
import os
from dotenv import load_dotenv
from .utils import get_project_root
from xata.helpers import to_rfc339
import datetime

env_file = os.path.join(get_project_root(), '.env')

load_dotenv(env_file)

XATA_API_KEY = os.getenv('XATA_API_KEY')
XATA_DB_URL = os.getenv('XATA_DB_URL')


class XataAPI(object):
    def __init__(self, *args, **kwargs):
        self.branch = kwargs.pop('branch', 'main')
        self.client = None
        if kwargs.get('xata_url') and kwargs.get('xata_key'):
            self.login(kwargs.get('xata_key'), kwargs.get('xata_url'))
        elif XATA_API_KEY and XATA_DB_URL:
            self.login(XATA_API_KEY, XATA_DB_URL)

    def login(self, key, url):
        self.client = XataClient(api_key=key, db_url=f"{url}:{self.branch}")

    @property
    def is_log_in(self):
        return self.client is not None

    def process_parms(self, params):
        """
        Takes an object dictionary and returns a proper Xata query dictionary.
        Handles a list by setting the query key $includesAll, and $is
        :param params:
        :return:
        """
        if isinstance(params, list):
            if not params:
                return None
            query = {'$includes': {'$contains': p} for p in params}
            return query
        elif isinstance(params, dict):
            return {key: self.process_parms(value) for key, value in params.items()}
        elif isinstance(params, (datetime.datetime, datetime.date)):
            return to_rfc339(params)
        else:
            return params

    def query(self, table, **params):
        try:
            process_params = self.process_parms(params)
            records = self.client.data().query(table, process_params)
            if records.status_code == 200:
                return records.json()
            elif records.status_code == 404:
                raise FileNotFoundError('Record not found')
            else:
                raise OperationError(records.status_code, records)
        except Exception as e:
            raise OperationError(e)

    def create(self, table, record_dict):
        created_record = self.client.records().insert(table, record_dict).json()
        if created_record.get('message', None):
            raise OperationError(f"{created_record.get('message')}")

        r = record_dict.copy()
        r.update({"id": created_record['id']})
        return r

    def read(self, table, record_id):
        record = self.client.data().get(table, record_id)
        if record:
            return record.json()

        return None

    def update(self, table, record_id, record):
        try:
            res = self.client.records().update(table, record_id, record)
        except Exception as e:
            raise OperationError(e)

        if res.status_code == 400:
            raise OperationError(res.message)

        if res:
            r = record.copy()
            r.update(res.json())
        return r

    def delete(self, table, record_id):
        r = self.client.records().delete(table, record_id)
        if r.status_code != 204:
            raise OperationError(r.json()['message'])
        return r

    def get_or_create(self, table, record_dict):
        try:
            record_dict = {k: v for k, v in record_dict.items() if v}
            record = self.query(table, filter=record_dict)['records']
            if len(record) > 1:
                raise OperationError('There is more than one matching record.')
            record = record[0]
            created = False

        except (FileNotFoundError, IndexError):
            record = self.create(table, record_dict)
            created = True
        
        return record, created

    def get_table_schema(self, table_name):
        res = self.client.table().get_schema(table_name)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 404:
            return None
        else:
            raise OperationError(res)

    def create_table(self, table_name):
        res = self.client.table().create(table_name)
        if res.status_code == 201:
            return res.json()
        else:
            raise OperationError(res, res.status_code)

    def add_table_column(self, table_name, column):
        res = self.client.table().add_column(table_name, column)
        if res.status_code == 200:
            return res.json()
        else:
            raise OperationError(res)

    def delete_all_records(self, table):
        res = self.client.data().query(table, {'page': {'size': 200}})
        i = 0
        while res.status_code == 200:
            for article in res.json()['records']:
                id = article['id']
                self.client.data().delete(table, id)
                i += 1
                if i % 100 == 5:
                    print(f'{datetime.datetime.now()} - Deleted {i} articles.')
            res = self.client.data().query(table, {'page': {'size': 200}})
        return True

    def migrate_table(self, dest, table):
        if (self.branch == dest.branch and 
            self.client.workspace_id == dest.client.workspace_id and 
            self.client.branch().get_details().get('databaseName') == dest.client.branch().get_details().get('databaseName')):
            raise OperationError('Source and destination branches are the same!')
        bp = BulkProcessor(dest.client)
        more = True
        i = 0
        all_data = []
        errors = []
        query = dict(
            filter={},
            sort={'xata.createdAt': 'desc'},
            page={'size': 200}
        )

        while more:
            res = self.client.data().query(table, query)
            if res.status_code == 200:
                res = res.json()
                meta = res['meta']['page']
                more = meta['more']
                i += 200
                data = res['records']
                all_data.extend(data)
                for d in data:
                    d.pop('xata')
                    d.pop('process_time', None)
                query['page'].update({'after': meta['cursor']})
                query.pop('filter', None)
                query.pop('sort', None)
            else:
                print(f'Response: {res} from server')
                break
            print(f'{datetime.datetime.now()} - Fetched {i} articles. New articles: {len(all_data)}')
        print(f'Total retrieved: {len(all_data)}')
        print(f'With errors: {len(errors)}')

        bp.put_records(table, all_data)
        bp.flush_queue()
        return all_data