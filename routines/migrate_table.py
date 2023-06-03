from database.exceptions import OperationError
from xata import XataClient
from xata.helpers import BulkProcessor
import os
import sys
from time import sleep
import datetime as dt
import csv


def migrate_table(source, dest, table):
    if source.branch == dest.branch and source.workspace_id == dest.workspace_id:
        raise OperationError('Source and destination branches are the same!')
    bp = BulkProcessor(dest)
    more = True
    i = 0
    all_data = []
    errors = []
    query = dict(
        filter={},
        sort={'date':'desc'},
        page={'size': 200}
    )

    while more:
        res = source.search_and_filter().queryTable(table, query)
        if res.status_code == 200:
            res = res.json()
            meta = res['meta']['page']
            more = meta['more']
            i += 200
            data = res['records']
            all_data.extend(data)
            for d in data:
                d.pop('xata')
                #d.pop('id')
                d.pop('process_time', None)
                d['publisher'] = d['publisher']['id']
            query['page'].update({'after': meta['cursor']})
            query.pop('filter', None)
            query.pop('sort', None)
        else:
            print(f'Response: {res.text} from server')
            break
        print(f'{dt.datetime.now()} - Fetched {i} articles. New articles: {len(all_data)}')
    print(f'Total retrieved: {len(all_data)}')
    print(f'With errors: {len(errors)}')

    # with open('data/articles.bk', 'w') as f:
    #     writer = csv.writer(f, delimiter=',')
    #     writer.writerows(all_data)
    # with open('data/errros.bk', 'w') as f:
    #     writer = csv.writer(f, delimiter=',')
    #     writer.writerows(errors)

    bp.put_records(table, all_data)
    bp.flush_queue()
    return True


def delete_all_records(xata: XataClient, table):
    res = xata.search_and_filter().queryTable(table, {'page':{'size': 200}})
    i = 0
    while res.status_code == 200:
        for article in res.json()['records']:
            id = article['id']
            xata.records().deleteRecord(table, id)
            i+=1
            if i%100 == 5:
                print(f'{dt.datetime.now()} - Deleted {i} articles.')
        res = xata.search_and_filter().queryTable(table, {'page': {'size': 200}})
    return True


if __name__=='__main__':

    table = sys.argv[1]

    src = XataClient(api_key=os.getenv('XATA_KEY'), db_url='https://whatsgoingon-024tih.us-east-1.xata.sh/db/xata-test')
    dest = XataClient(api_key=os.getenv('XATA_KEY'), db_url='https://whatsgoingon-54qsjf.us-east-1.xata.sh/db/paraguay')

    assert migrate_table(src, dest, table), 'Error'
    #delete_all_records(dest, table)
