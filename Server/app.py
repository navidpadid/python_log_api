from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)

def is_valid_filename(filename):
    return re.match(r'^[\w,\s-]+\.[A-Za-z]{3}$', filename) is not None

def is_valid_keyword(keyword):
    return re.match(r'^[\w\s-]*$', keyword) is not None

@app.route('/<filename>', methods=['GET'])
def get_log(filename):
    keyword = request.args.get('keyword', '')
    n = request.args.get('n', '100')

    if not is_valid_filename(filename):
        return jsonify({'error': 'Invalid filename format'}), 400

    if not is_valid_keyword(keyword):
        return jsonify({'error': 'Invalid keyword format'}), 400

    if not n.isdigit():
        return jsonify({'error': 'Number of lines must be a valid number'}), 400

    n = int(n)

    if n > 5000:
        n = 2000

    file_path = os.path.join('/var/log', filename)
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            matching_lines = [line for line in lines if keyword in line]
            last_n_lines = matching_lines[-n:][::-1] 
        return jsonify({'lines': last_n_lines})
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
