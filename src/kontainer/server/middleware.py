from flask import request, jsonify, g, abort
#from flask_jwt_extended import verify_jwt_in_request

from kontainer.docker.service import DockerService


# Middleware to check API key presence
# Deprecated: Use JWT instead
def auth_token_middleware(app):

    def __init__(self):
        if app.config['API_KEY'] is None:
            raise Exception("API_KEY is not set in the app configuration")

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

        required_value = app.config['API_KEY']
        if api_key != required_value:
            return False

        return True


# # Middleware to check JWT presence
# def check_jwt_middleware(app):
#
#     @app.before_request
#     def before_request():
#         # Bypass JWT check for login route
#         if request.endpoint == "login":
#             return
#
#         try:
#             # Attempt to verify the JWT
#             verify_jwt_in_request()
#         except Exception as e:
#             return jsonify({"error": "Missing or invalid token", "message": str(e)}), 401


def docker_service_middleware(app):
    @app.before_request
    def inject_docker_service():
        # Check if the request is an OPTIONS request
        if request.method == "OPTIONS":
            return

        docker_ctxid = request.headers.get('X-Docker-Context')
        if not docker_ctxid:
            # abort(400, description="Missing required header: X-Docker-Context")
            return jsonify({"error": "Missing required header: X-Docker-Context"}), 401

        # # validate format
        # try:
        #     docker_ctxid = int(docker_ctxid)
        # except ValueError:
        #     # abort(400, description="Invalid X-Docker-Context: must be an integer")
        #     return jsonify({"error": "Invalid X-Docker-Context: must be an integer"}), 400

        g.dkr_ctx_id = docker_ctxid
        g.dkr = DockerService(docker_ctxid).dkr
        return None
