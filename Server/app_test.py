import requests
import os

def test_get_log():
    log_dir = '/var/log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'test.log'), 'w') as f:
        for i in range(1, 12):
            f.write(f'Line {i}\n')

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

    os.remove(os.path.join(log_dir, 'test.log'))

def test_get_nonexistent_log():
    response = requests.get('http://localhost:5000/nonexistent.log')
    assert response.status_code == 500
    assert 'No such file or directory' in response.text

def test_keyword_search():
    log_dir = '/var/log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'test.log'), 'w') as f:
        for i in range(1, 12):
            f.write(f'Line {i}\n')

    response = requests.get('http://localhost:5000/test.log?keyword=Line 1')
    assert response.status_code == 200
    assert len(response.json()['lines']) == 3
    assert response.json()['lines'] == ['Line 11\n', 'Line 10\n', 'Line 1\n']

    os.remove(os.path.join(log_dir, 'test.log'))

def test_number_of_matches():
    log_dir = '/var/log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'test.log'), 'w') as f:
        for i in range(1, 12):
            f.write(f'Line {i}\n')

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

    os.remove(os.path.join(log_dir, 'test.log'))

def test_keyword_and_number_of_matches():
    log_dir = '/var/log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'test.log'), 'w') as f:
        for i in range(1, 12):
            f.write(f'Line {i}\n')

    response = requests.get('http://localhost:5000/test.log?keyword=Line&n=5')
    assert response.status_code == 200
    assert len(response.json()['lines']) == 5
    assert response.json()['lines'] == [
        'Line 11\n',
        'Line 10\n',
        'Line 9\n',
        'Line 8\n',
        'Line 7\n'
    ]

    os.remove(os.path.join(log_dir, 'test.log'))
