from flask import jsonify

from kstack.agent.app import app

from .server.engine_api import engine_api_bp
from .server.container_api import container_api_bp
from .server.environments_api import environments_api_bp
from .server.images_api import images_api_bp
from .server.networks_api import networks_api_bp
from .server.stacks_api import stacks_api_bp
from .server.tasks_api import tasks_api_bp
from .server.templates_api import templates_api_bp
from .server.volumes_api import volumes_api_bp
#from .server.kube_namespaces_api import kube_namespaces_api_bp
#from .server.kube_pods_api import kube_pods_api_bp

from .stacks.stacksmanager import StacksManager

StacksManager.enumerate()

@app.route('/', methods=["GET"])
def index():
    status_data = {
        "status": "OK"
    }
    return jsonify(status_data)

# Admin API
app.register_blueprint(environments_api_bp)
# app.register_blueprint(system_api_bp)
app.register_blueprint(tasks_api_bp)
app.register_blueprint(templates_api_bp)

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