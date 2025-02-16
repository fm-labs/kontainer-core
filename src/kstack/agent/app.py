from flask import Flask, jsonify
from flask_cors import CORS

from . import settings
from .server.engine_api import engine_api_bp
from .server.container_api import container_api_bp
from .server.environments_api import environments_api_bp
from .server.images_api import images_api_bp
from .server.middleware import auth_token_middleware
#from .server.kube_namespaces_api import kube_namespaces_api_bp
#from .server.kube_pods_api import kube_pods_api_bp
from .server.networks_api import networks_api_bp
from .server.stacks_api import stacks_api_bp
from .server.system_api import system_api_bp
from .server.volumes_api import volumes_api_bp
from .stacks.stacksmanager import StacksManager

# CLASSES

StacksManager.enumerate()

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

@app.route('/', methods=["GET"])
def index():
    status_data = {
        "version": "1.0.0",
        "status": "OK"
    }
    return jsonify(status_data)

# Admin API
app.register_blueprint(environments_api_bp)
# app.register_blueprint(system_api_bp)

# Docker API
app.register_blueprint(engine_api_bp)
app.register_blueprint(container_api_bp)
app.register_blueprint(images_api_bp)
app.register_blueprint(networks_api_bp)
app.register_blueprint(stacks_api_bp)
app.register_blueprint(volumes_api_bp)

# Kubernetes API
#app.register_blueprint(kube_namespaces_api_bp)
#app.register_blueprint(kube_pods_api_bp)