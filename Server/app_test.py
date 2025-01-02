import requests
import os
import pytest
import threading
import time

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

def append_logs(file_path, stop_event):
    with open(file_path, 'a') as f:
        i = 1
        while not stop_event.is_set():
            time.sleep(0.0001)
            f.write(f'Appended Line {i}\n')
            i += 1

def test_get_nonexistent_log():
    response = requests.get('http://localhost:5000/nonexistent.log')
    assert response.status_code == 404
    assert response.json()['error'] == 'File not found'

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


def test_get_log():
    response = requests.get('http://localhost:5000/test.log')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 11
    assert lines == [
        'Line 11',
        'Line 10',
        'Line 9',
        'Line 8',
        'Line 7',
        'Line 6',
        'Line 5',
        'Line 4',
        'Line 3',
        'Line 2',
        'Line 1'
    ]

def test_get_log_stream():
    response = requests.get('http://localhost:5000/test.log?stream=true')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 11
    assert lines == [
        'Line 11',
        'Line 10',
        'Line 9',
        'Line 8',
        'Line 7',
        'Line 6',
        'Line 5',
        'Line 4',
        'Line 3',
        'Line 2',
        'Line 1'
    ]

def test_keyword_search():
    response = requests.get('http://localhost:5000/test.log?keyword=Line 1')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 3
    assert lines == ['Line 11', 'Line 10', 'Line 1']

def test_keyword_search_stream():
    response = requests.get('http://localhost:5000/test.log?keyword=Line 1&stream=true')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 3
    assert lines == ['Line 11', 'Line 10', 'Line 1']

def test_number_of_matches():
    response = requests.get('http://localhost:5000/test.log?n=5')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 5
    assert lines == [
        'Line 11',
        'Line 10',
        'Line 9',
        'Line 8',
        'Line 7'
    ]

def test_number_of_matches_stream():
    response = requests.get('http://localhost:5000/test.log?n=5&stream=true')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 5
    assert lines == [
        'Line 11',
        'Line 10',
        'Line 9',
        'Line 8',
        'Line 7'
    ]

def test_keyword_and_number_of_matches():
    response = requests.get('http://localhost:5000/test.log?keyword=Line&n=5')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 5
    assert lines == [
        'Line 11',
        'Line 10',
        'Line 9',
        'Line 8',
        'Line 7'
    ]

def test_keyword_and_number_of_matches_stream():
    response = requests.get('http://localhost:5000/test.log?keyword=Line&n=5&stream=true')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 5
    assert lines == [
        'Line 11',
        'Line 10',
        'Line 9',
        'Line 8',
        'Line 7'
    ]

def test_read_large_file():
    response = requests.get('http://localhost:5000/large_test.log?n=1000')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 1000
    assert lines == [f'Line {i}' for i in range(1000000, 999000, -1)]

def test_read_large_file_stream():
    response = requests.get('http://localhost:5000/large_test.log?n=1000&stream=true')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 1000
    assert lines == [f'Line {i}' for i in range(1000000, 999000, -1)]


def test_read_large_file_stream_append():
    stop_event = threading.Event()
    append_thread = threading.Thread(target=append_logs, args=(large_test_file_path, stop_event))
    append_thread.start()

    try:
        response = requests.get('http://localhost:5000/large_test.log?n=1000&stream=true')
        assert response.status_code == 200
        lines = response.text.strip().split('\n')
        assert len(lines) == 1000
        assert lines == [f'Line {i}' for i in range(1000000, 999000, -1)]
    finally:
        stop_event.set()
        append_thread.join()
