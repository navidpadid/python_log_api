import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from lib.log_viewer import LogViewer

app = Flask(__name__)
CORS(app)

@app.route('/<filename>', methods=['GET'])
def get_log(filename):
    keyword = request.args.get('keyword', '')
    n = request.args.get('n', '10000')

    if not n.isdigit():
        return jsonify({'error': 'Number of lines must be a valid number'}), 400

    n = int(n)
    if n > 100000:
        n = 100000

    log_viewer = LogViewer(filename, keyword, int(n))

    if not log_viewer.is_valid_filename():
        return jsonify({'error': 'Invalid filename format'}), 400

    if not log_viewer.is_valid_keyword():
        return jsonify({'error': 'Invalid keyword format'}), 400

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
                "n": "Number of matching entries to return (optional, default: 10000 lines)"
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
                "n": "Number of matching entries to return (optional, default: 10000 lines)"
            },
            "example": "/test.log?keyword=error&n=50"
        }
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
