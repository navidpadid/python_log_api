from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/<filename>', methods=['GET'])
def get_log(filename):
    keyword = request.args.get('keyword', '')
    n = int(request.args.get('n', 100))
    file_path = os.path.join('/var/log', filename)
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            matching_lines = [line for line in lines if keyword in line]
            last_n_lines = matching_lines[-n:][::-1]  
        return jsonify({'lines': last_n_lines})
    except Exception as e:
        return str(e), 500

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
