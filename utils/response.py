from flask import jsonify


def generate_response(code, **kwargs):
    return jsonify({'status_code': code, 'success': code == 200, **kwargs}), code
