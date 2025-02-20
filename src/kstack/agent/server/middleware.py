import hashlib

from flask import request, jsonify

def auth_token_middleware(app):

    @app.before_request
    def before_request():

        # Check if the request is an OPTIONS request
        if request.method == "OPTIONS":
            return

        # Check if the request is an GET request and the path is / or /health
        if request.method == "GET" and request.path == "/":
            return
        if request.method == "GET" and request.path == "/health":
            return

        # Extract the API key from the request headers
        required_key = "x-api-key"
        headers = {k.lower(): v for k, v in request.headers.items()}
        api_key = headers.get(required_key)
        if not api_key:
            return jsonify({"error": "Unauthorized"}), 401

        # Validate the API key
        if not validate_api_key(api_key):
            return jsonify({"error": "Unauthorized"}), 401  # Unauthorized response


    def validate_api_key(api_key):
        # hasher = hashlib.sha256()
        # hasher.update(api_key.encode())
        # hasher.update(app.config['SECRET_KEY'].encode())
        # return hasher.hexdigest()

        required_value = app.config['AUTH_TOKEN']
        if api_key != required_value:
            return False

        return True