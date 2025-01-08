import os
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from lib.log_viewer import LogViewer

DEFAULT_NUM_LINES = 10000
MAX_NUM_LINES = 10000000
LOG_DIR = '/var/log'
CHUNK_SIZE = MAX_NUM_LINES // 100
""" sending CHUNK_SIZE amount of lines for the streaming option """

app = Flask(__name__)
CORS(app)

@app.route('/<filename>', methods=['GET'])
def get_log(filename):
    """
    Retrieve log file content with optional keyword filtering, line limit, and can return the content as a streaming response if requested.

    Arguments:
    - filename (str): The name of the log file.

    Returns:
    - Response: The log file content or an error message.
    """
    keyword = request.args.get('keyword', '')
    n = request.args.get('n', str(DEFAULT_NUM_LINES))
    stream = request.args.get('stream', 'false').lower() == 'true'

    if not n.isdigit():
        return jsonify({'error': 'Number of lines must be a valid number'}), 400

    n = int(n)
    if n > MAX_NUM_LINES:
        n = MAX_NUM_LINES

    file_path = os.path.join(LOG_DIR, filename)
    log_viewer = LogViewer(filename, file_path, keyword, n)

    if not log_viewer.is_valid_filename():
        return jsonify({'error': 'Invalid filename format'}), 400

    if not log_viewer.is_valid_keyword():
        return jsonify({'error': 'Invalid keyword format'}), 400
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        if stream:
            def generate():
                chunk = []
                for line in log_viewer.get_lines_generator():
                    chunk.append(f"{line.strip()}\n")
                    if len(chunk) >= CHUNK_SIZE:
                        yield ''.join(chunk)
                        chunk = []
                if chunk:
                    yield ''.join(chunk)
            return Response(generate(), content_type='text/plain')
        else:
            lines = log_viewer.get_lines()
            return Response(''.join(lines), content_type='text/plain')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """
    Display a welcome message and usage instructions for the Log Viewer API.

    Returns:
    - Response: A JSON response with a welcome message and usage instructions.
    """
    return jsonify({
        "message": "Welcome to the Log Viewer API!",
        "usage": {
            "endpoint": "/<filename>",
            "parameters": {
                "filename": "The name of the log file (required)",
                "keyword": "Text/keyword to filter log lines (optional, default: any text/keyword)",
                "n": f"Number of matching entries to return (optional, default: {DEFAULT_NUM_LINES} lines)",
                "stream": "Whether to stream the response (optional, default: false)"
            },
            "example": f"/test.log?keyword=error&n=50&stream=true"
        }
    })

@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors by displaying a welcome message and usage instructions.

    Args:
    - e (Exception): The exception that triggered the error handler.

    Returns:
    - Response: A JSON response with a welcome message and usage instructions.
    """
    return jsonify({
        "message": "Welcome to the Log Viewer API!",
        "usage": {
            "endpoint": "/<filename>",
            "parameters": {
                "filename": "The name of the log file (required)",
                "keyword": "Text/keyword to filter log lines (optional, default: any text/keyword)",
                "n": f"Number of matching entries to return (optional, default: {DEFAULT_NUM_LINES} lines)",
                "stream": "Whether to stream the response (optional, default: false)"
            },
            "example": f"/test.log?keyword=error&n=50&stream=true"
        }
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
