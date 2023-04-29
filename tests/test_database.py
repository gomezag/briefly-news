import pytest
import random
import string

from database.exceptions import OperationError


@pytest.fixture
def created_record_id(created_record):
    return created_record['id']


@pytest.fixture
def created_record(xata_api):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    created_record = xata_api.create('test_table', {'name': 'test-'+random_string})
    assert created_record['id'] is not None

    try:
        yield created_record

    finally:
        res = xata_api.delete('test_table', created_record['id'])
        assert res.status_code == 204


def test_read(xata_api, created_record_id):
    res = xata_api.read('test_table', created_record_id)
    assert res['id'] == created_record_id


def test_get_or_create(xata_api, created_record):
    table = 'test_table'
    same_dict = {key: value for key, value in created_record.items() if key not in ['id', 'xata']}
    record, c = xata_api.get_or_create(table, same_dict)
    assert c == 0
    assert record['id'] == created_record['id']
    try:
        dup_record = xata_api.create(table, same_dict)
        assert dup_record['id'] != created_record['id']
        assert dup_record['name'] == created_record['name']
        pytest.raises(OperationError, xata_api.get_or_create, table, same_dict)
    finally:
        xata_api.delete(table, dup_record['id'])

