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

auth_token_middleware(app)
CORS(app,
     allow_headers=["x-api-key", "x-csrf-token", "content-type"],
     methods=["GET", "POST", "OPTIONS"],
     origins=["*"])

# Celery configuration
# https://docs.celeryq.dev/en/stable/userguide/configuration.html
app.config['CELERY_BROKER_URL'] = settings.CELERY_BROKER_URL
#app.config['CELERY_RESULT_BACKEND'] = settings.CELERY_RESULT_BACKEND
app.config['result_backend'] = settings.CELERY_RESULT_BACKEND
app.config['result_expires'] = settings.CELERY_RESULT_EXPIRES
app.config['task_time_limit'] = settings.CELERY_TASK_TIME_LIMIT
app.config['task_soft_time_limit'] = int(settings.CELERY_TASK_TIME_LIMIT * 0.9)
