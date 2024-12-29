import requests
import os
import pytest

log_dir = '/var/log'
test_file_path = os.path.join(log_dir, 'test.log')
large_test_file_path = os.path.join(log_dir, 'large_test.log')

@pytest.fixture(scope='module', autouse=True)
def setup_and_teardown():
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(test_file_path, 'w') as f:
        for i in range(1, 12):
            f.write(f'Line {i}\n')

    with open(large_test_file_path, 'w') as f:
        for i in range(1, 1000001):
            f.write(f'Line {i}\n')

    yield

    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    if os.path.exists(large_test_file_path):
        os.remove(large_test_file_path)

def test_get_log():
    response = requests.get('http://localhost:5000/test.log')
    assert response.status_code == 200
    assert len(response.json()['lines']) == 11
    assert response.json()['lines'] == [
        'Line 11\n',
        'Line 10\n',
        'Line 9\n',
        'Line 8\n',
        'Line 7\n',
        'Line 6\n',
        'Line 5\n',
        'Line 4\n',
        'Line 3\n',
        'Line 2\n',
        'Line 1\n'
    ]

def test_get_nonexistent_log():
    response = requests.get('http://localhost:5000/nonexistent.log')
    assert response.status_code == 404
    assert 'File not found' in response.text

def test_keyword_search():
    response = requests.get('http://localhost:5000/test.log?keyword=Line 1')
    assert response.status_code == 200
    assert len(response.json()['lines']) == 3
    assert response.json()['lines'] == ['Line 11\n', 'Line 10\n', 'Line 1\n']

def test_number_of_matches():
    response = requests.get('http://localhost:5000/test.log?n=5')
    assert response.status_code == 200
    assert len(response.json()['lines']) == 5
    assert response.json()['lines'] == [
        'Line 11\n',
        'Line 10\n',
        'Line 9\n',
        'Line 8\n',
        'Line 7\n'
    ]

def test_keyword_and_number_of_matches():
    response = requests.get('http://localhost:5000/test.log?keyword=Line&n=5')
    assert response.status_code == 200
    assert len(response.json()['lines']) == 5
    print(response.json()['lines'])
    assert response.json()['lines'] == [
        'Line 11\n',
        'Line 10\n',
        'Line 9\n',
        'Line 8\n',
        'Line 7\n'
    ]

def test_invalid_filename():
    response = requests.get('http://localhost:5000/invalid*filename.log')
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid filename format'

def test_invalid_keyword():
    response = requests.get('http://localhost:5000/test.log?keyword=invalid*keyword')
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid keyword format'

def test_invalid_number_of_lines():
    response = requests.get('http://localhost:5000/test.log?n=invalid')
    assert response.status_code == 400
    assert response.json()['error'] == 'Number of lines must be a valid number'

def test_read_large_file():
    response = requests.get('http://localhost:5000/large_test.log?n=1000')
    assert response.status_code == 200
    assert len(response.json()['lines']) == 1000
    print(response.json()['lines'])
    assert response.json()['lines'] == [f'Line {i}' for i in range(1000000, 999000, -1)]
