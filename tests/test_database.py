from database.xata_api import XataAPI
import pytest


@pytest.fixture
def xata_api():
    return XataAPI()


@pytest.fixture
def created_record(xata_api):
    created_record = xata_api.create('test_table', {'name': 'test_name'})
    assert created_record['id'] is not None
    
    yield created_record['id']
    
    xata_api.delete('test_table', created_record)
    

def test_read(xata_api, created_record):
    res = xata_api.read('test_table', created_record)
    assert res['id'] == created_record


def test_delete(xata_api, created_record):
    res = xata_api.delete('test_table', created_record)
    assert res.status_code == 204