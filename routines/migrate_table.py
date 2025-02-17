import os
import sys

# Add the parent directory to the sys.path to import the database module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.xata_api import OperationError, XataAPI

from time import sleep
import datetime as dt
import csv

if __name__=='__main__':

    table = sys.argv[1]

    src = XataClient(api_key=os.getenv('XATA_KEY'), db_url='https://whatsgoingon-024tih.us-east-1.xata.sh/db/xata-test')
    dest = XataClient(api_key=os.getenv('XATA_KEY'), db_url='https://whatsgoingon-54qsjf.us-east-1.xata.sh/db/paraguay')

    assert src.migrate_table(dest, table), 'Error'
    #src.delete_all_records(table)
