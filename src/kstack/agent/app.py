#from hmac import compare_digest

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended.jwt_manager import JWTManager
#from flask_sqlalchemy import SQLAlchemy

from . import settings
from .admin.auth import init_admin_credentials_file

#from .server.middleware import auth_token_middleware

app = Flask(__name__)

# App configuration
app.config['DATA_DIR'] = settings.AGENT_DATA_DIR
app.config['STACKS_DIR'] = f"{settings.AGENT_DATA_DIR}/stacks"
app.config['REPOS_DIR'] = f"{settings.AGENT_DATA_DIR}/repos"
app.config['UPLOAD_DIR'] = f"{settings.AGENT_DATA_DIR}/uploads"
app.config['API_KEY'] = settings.AGENT_API_KEY


# JWT (Flask-JWT-Extended)
# Using defaults for now
# https://flask-jwt-extended.readthedocs.io/en/stable/options.html
app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_JSON_KEY"] = "access_token"
app.config["JWT_REFRESH_JSON_KEY"] = "access_token"

# Celery
# https://docs.celeryq.dev/en/stable/userguide/configuration.html
#app.config['CELERY_RESULT_BACKEND'] = settings.CELERY_RESULT_BACKEND
app.config['CELERY_BROKER_URL'] = settings.CELERY_BROKER_URL
app.config['result_backend'] = settings.CELERY_RESULT_BACKEND
app.config['result_expires'] = settings.CELERY_RESULT_EXPIRES
app.config['task_time_limit'] = settings.CELERY_TASK_TIME_LIMIT
app.config['task_soft_time_limit'] = int(settings.CELERY_TASK_TIME_LIMIT * 0.9)
app.config['broker_connection_retry_on_startup'] = True

# Middleware
CORS(app,
     allow_headers=["x-api-key", "x-csrf-token", "content-type", "authorization"],
     methods=["OPTIONS", "GET", "POST", "DELETE"],
     origins=["*"])

#auth_token_middleware(app)
jwt = JWTManager(app)

init_admin_credentials_file()


# # Database
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)
# db.init_app(app)
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.Text, nullable=False, unique=True)
#     full_name = db.Column(db.Text, nullable=False)
#
#     # NOTE: In a real application make sure to properly hash and salt passwords
#     def check_password(self, password):
#         return compare_digest(password, "password")
#
#
# # Register a callback function that takes whatever object is passed in as the
# # identity when creating JWTs and converts it to a JSON serializable format.
# @jwt.user_identity_loader
# def user_identity_lookup(user):
#     return user.id
#
#
# # Register a callback function that loads a user from your database whenever
# # a protected route is accessed. This should return any python object on a
# # successful lookup, or None if the lookup failed for any reason (for example
# # if the user has been deleted from the database).
# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     identity = jwt_data["sub"]
#     return User.query.filter_by(id=identity).one_or_none()
#
#
# # Using the additional_claims_loader, we can specify a method that will be
# # called when creating JWTs. The decorated method must take the identity
# # we are creating a token for and return a dictionary of additional
# # claims to add to the JWT.
# @jwt.additional_claims_loader
# def add_claims_to_access_token(identity):
#     return {
#         #"aud": "some_audience",
#         #"foo": "bar",
#         #"upcase_name": identity.upper(),
#     }