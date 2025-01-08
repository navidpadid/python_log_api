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
    """
    Fixture to set up and tear down test environment.
    
    Steps:
    1. Create log directory if it doesn't exist.
    2. Create test log files with sample data.
    3. Yield control to the test functions.
    4. Remove test log files after tests are done.
    """
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
    """
    Function to append logs to a file until a stop event is set.
    
    Arguments:
    - file_path (str): Path to the log file.
    - stop_event (threading.Event): Event to signal when to stop appending logs.
    
    Steps:
    1. Open the log file in append mode.
    2. Continuously write new log lines until the stop event is set.
    """
    with open(file_path, 'a') as f:
        i = 1
        while not stop_event.is_set():
            time.sleep(0.0001)
            f.write(f'Appended Line {i}\n')
            i += 1

def test_get_nonexistent_log():
    """
    Test to verify that requesting a nonexistent log file returns a 404 error.
    
    Steps:
    1. Send a GET request to a nonexistent log file.
    
    Assertions:
    - Response status code should be 404.
    - Response JSON should contain 'File not found' error.
    """
    response = requests.get('http://localhost:5000/nonexistent.log')
    assert response.status_code == 404
    assert response.json()['error'] == 'File not found'

def test_invalid_filename():
    """
    Test to verify that requesting a log file with an invalid filename format returns a 400 error.
    
    Steps:
    1. Send a GET request with an invalid filename format.
    
    Assertions:
    - Response status code should be 400.
    - Response JSON should contain 'Invalid filename format' error.
    """
    response = requests.get('http://localhost:5000/invalid*filename.log')
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid filename format'

def test_invalid_keyword():
    """
    Test to verify that requesting a log file with an invalid keyword format returns a 400 error.
    
    Steps:
    1. Send a GET request with an invalid keyword format.
    
    Assertions:
    - Response status code should be 400.
    - Response JSON should contain 'Invalid keyword format' error.
    """
    response = requests.get('http://localhost:5000/test.log?keyword=invalid*keyword')
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid keyword format'

def test_invalid_number_of_lines():
    """
    Test to verify that requesting a log file with an invalid number of lines returns a 400 error.
    
    Steps:
    1. Send a GET request with an invalid number of lines.
    
    Assertions:
    - Response status code should be 400.
    - Response JSON should contain 'Number of lines must be a valid number' error.
    """
    response = requests.get('http://localhost:5000/test.log?n=invalid')
    assert response.status_code == 400
    assert response.json()['error'] == 'Number of lines must be a valid number'

def test_get_log():
    """
    Test to verify that requesting a log file returns the correct content.
    
    Steps:
    1. Send a GET request to the log file.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain 11 lines in reverse order.
    """
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
    """
    Test to verify that requesting a log file with streaming enabled returns the correct content.
    
    Steps:
    1. Send a GET request to the log file with streaming enabled.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain 11 lines in reverse order.
    """
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
    """
    Test to verify that searching for a keyword in a log file returns the correct content.
    
    Steps:
    1. Send a GET request to the log file with a keyword.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain lines with the keyword in reverse order.
    """
    response = requests.get('http://localhost:5000/test.log?keyword=Line 1')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 3
    assert lines == ['Line 11', 'Line 10', 'Line 1']

def test_keyword_search_stream():
    """
    Test to verify that searching for a keyword in a log file with streaming enabled returns the correct content.
    
    Steps:
    1. Send a GET request to the log file with a keyword and streaming enabled.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain lines with the keyword in reverse order.
    """
    response = requests.get('http://localhost:5000/test.log?keyword=Line 1&stream=true')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 3
    assert lines == ['Line 11', 'Line 10', 'Line 1']

def test_number_of_matches():
    """
    Test to verify that requesting a specific number of lines from a log file returns the correct content.
    
    Steps:
    1. Send a GET request to the log file with a specific number of lines.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain the specified number of lines in reverse order.
    """
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
    """
    Test to verify that requesting a specific number of lines from a log file with streaming enabled returns the correct content.
    
    Steps:
    1. Send a GET request to the log file with a specific number of lines and streaming enabled.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain the specified number of lines in reverse order.
    """
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
    """
    Test to verify that searching for a keyword and requesting a specific number of lines from a log file returns the correct content.
    
    Steps:
    1. Send a GET request to the log file with a keyword and a specific number of lines.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain the specified number of lines with the keyword in reverse order.
    """
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
    """
    Test to verify that searching for a keyword and requesting a specific number of lines from a log file with streaming enabled returns the correct content.
    
    Steps:
    1. Send a GET request to the log file with a keyword and a specific number of lines, with streaming enabled.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain the specified number of lines with the keyword in reverse order.
    """
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
    """
    Test to verify that requesting a large number of lines from a large log file (loading file by chunks into memory) returns the correct content.
    
    Steps:
    1. Send a GET request to the large log file with a specific number of lines.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain the specified number of lines in reverse order.
    """
    response = requests.get('http://localhost:5000/large_test.log?n=1000')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 1000
    assert lines == [f'Line {i}' for i in range(1000000, 999000, -1)]

def test_read_large_file_stream():
    """
    Test to verify that requesting a large number of lines from a large log file (loading file by chunks into memory) with streaming enabled returns the correct content.
    
    Steps:
    1. Send a GET request to the large log file with a specific number of lines, with streaming enabled.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain the specified number of lines in reverse order.
    """
    response = requests.get('http://localhost:5000/large_test.log?n=1000&stream=true')
    assert response.status_code == 200
    lines = response.text.strip().split('\n')
    assert len(lines) == 1000
    assert lines == [f'Line {i}' for i in range(1000000, 999000, -1)]

def test_read_large_file_stream_append():
    """
    Test to verify that requesting a large number of lines from a large log file with streaming enabled returns the correct content while logs are being appended.
    
    Steps:
    1. Start a thread to append logs to the large log file.
    2. Send a GET request to the large log file with a specific number of lines, with streaming enabled.
    3. Stop the log appending thread.
    
    Assertions:
    - Response status code should be 200.
    - Response text should contain the specified number of lines in reverse order.
    """
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
