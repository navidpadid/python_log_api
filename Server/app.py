from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import re
from collections import deque

class LogViewer:
    def __init__(self, file_path, keyword, num_lines):
        self.file_path = file_path
        self.keyword = keyword
        self.num_lines = num_lines
        self.lines = deque(maxlen=num_lines)

    def is_valid_filename(self):
        return re.match(r'^[\w,\s-]+\.[A-Za-z]{3}$', self.file_path) is not None

    def is_valid_keyword(self):
        return re.match(r'^[\w\s-]*$', self.keyword) is not None

    def read_small_file(self):
        with open(self.file_path, 'r') as file:
            read_lines = file.readlines()
            if self.keyword == '':
                self.lines = read_lines[-1:-(self.num_lines+1):-1]
            else:
                cntr = 0
                for line in reversed(read_lines):
                    if cntr == self.num_lines:
                        break
                    if self.keyword in line:
                        self.lines.append(line)
                        cntr += 1

    def read_large_file(self):
        with open(self.file_path, 'rb') as file:
            file.seek(0, os.SEEK_END)
            buffer_size = 500 * 1024  # Read in chunks of 500 lines (approx. 500 KB)
            buffer = b''
            position = file.tell()

            while position > 0 and len(self.lines) < self.num_lines:
                position = max(0, position - buffer_size)
                file.seek(position)
                buffer = file.read(buffer_size) + buffer
                cur_lines = buffer.split(b'\n')
                buffer = cur_lines.pop(0)  # Keep the last partial line for the next read

                for line in reversed(cur_lines):
                    if self.keyword.encode() in line:
                        self.lines.append(line.decode().strip())
                        if len(self.lines) == self.num_lines:
                            break

    def get_lines(self):
        file_size = os.path.getsize(self.file_path)
        if file_size <= 50 * 1024 * 1024:  # 50 MB
            self.read_small_file()
        else:
            self.read_large_file()
        return list(self.lines)

app = Flask(__name__)
CORS(app)

@app.route('/<filename>', methods=['GET'])
def get_log(filename):
    keyword = request.args.get('keyword', '')
    n = request.args.get('n', '100')

    log_viewer = LogViewer(filename, keyword, int(n))

    if not log_viewer.is_valid_filename():
        return jsonify({'error': 'Invalid filename format'}), 400

    if not log_viewer.is_valid_keyword():
        return jsonify({'error': 'Invalid keyword format'}), 400

    if not n.isdigit():
        return jsonify({'error': 'Number of lines must be a valid number'}), 400

    n = int(n)

    if n > 5000:
        n = 2000

    try:
        file_path = os.path.join('/var/log', filename)
        log_viewer.file_path = file_path
        lines = log_viewer.get_lines()
        return jsonify({'lines': lines})
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to the Log Viewer API!",
        "usage": {
            "endpoint": "/<filename>",
            "parameters": {
                "filename": "The name of the log file (required)",
                "keyword": "Text/keyword to filter log lines (optional, default: any text/keyword)",
                "n": "Number of matching entries to return (optional, default: 100 lines)"
            },
            "example": "/test.log?keyword=error&n=50"
        }
    })

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        "message": "Welcome to the Log Viewer API!",
        "usage": {
            "endpoint": "/<filename>",
            "parameters": {
                "filename": "The name of the log file (required)",
                "keyword": "Text/keyword to filter log lines (optional, default: any text/keyword)",
                "n": "Number of matching entries to return (optional, default: 100 lines)"
            },
            "example": "/test.log?keyword=error&n=50"
        }
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
