import flask
from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required

from kontainer.admin.auth import validate_admin_credentials_from_file

auth_api_bp = flask.Blueprint('auth_api', __name__, url_prefix='/api/auth')


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@auth_api_bp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    print("login", username, password)

    try:
        #if not validate_admin_credentials_simple(username, password):
        #    return jsonify(error="Bad username or password"), 401
        if not validate_admin_credentials_from_file(username, password):
            return jsonify(error="Bad username or password"), 401
    except Exception as e:
        print(e)
        return jsonify(error="Login Error:" + str(e)), 500

    # additional_claims = {
    #     "role": "admin"
    # }
    access_token = create_access_token(identity=username)
    print("login successful", username, access_token)
    return jsonify(access_token=access_token)


@auth_api_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify(message="logout"), 200


@auth_api_bp.route("/whoami", methods=["GET"])
@jwt_required()
def get_user_session():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200



# @auth_api_bp.route("/login", methods=["POST"])
# def login():
#     username = request.json.get("username", None)
#     password = request.json.get("password", None)
#
#     user = User.query.filter_by(username=username).one_or_none()
#     if not user or not user.check_password(password):
#         return jsonify("Wrong username or password"), 401
#
#     # Notice that we are passing in the actual sqlalchemy user object here
#     access_token = create_access_token(identity=user)
#     return jsonify(access_token=access_token)
#
#
# @auth_api_bp.route("/who_am_i", methods=["GET"])
# @jwt_required()
# def protected():
#     # We can now access our sqlalchemy User object via `current_user`.
#     return jsonify(
#         id=current_user.id,
#         full_name=current_user.full_name,
#         username=current_user.username,
#     )



