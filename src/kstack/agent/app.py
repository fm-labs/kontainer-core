from flask import Flask, jsonify
from flask_cors import CORS

from . import settings
from .server.middleware import auth_token_middleware

app = Flask(__name__)

app.config['DATA_DIR'] = settings.AGENT_DATA_DIR
app.config['STACKS_DIR'] = f"{settings.AGENT_DATA_DIR}/stacks"
app.config['REPOS_DIR'] = f"{settings.AGENT_DATA_DIR}/repos"
app.config['UPLOAD_DIR'] = f"{settings.AGENT_DATA_DIR}/uploads"
app.config['AUTH_TOKEN'] = settings.AGENT_AUTH_TOKEN

CORS(app,
     allow_headers=["x-api-key", "x-csrf-token", "content-type"],
     methods=["GET", "POST", "OPTIONS"],
     origins=["*"])
auth_token_middleware(app)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
