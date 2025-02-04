from flask import Flask, jsonify
from flask_cors import CORS

from .server.container_api import container_api
from .server.images_api import images_api
from .server.networks_api import networks_api
from .server.projects_api import projects_api
from .server.volumes_api import volumes_api
from .projects.projectmanager import ProjectManager

# CLASSES

ProjectManager.init()

app = Flask(__name__)
CORS(app)

@app.route('/', methods=["GET"])
def index():
    status_data = {
        "version": "1.0.0",
        "status": "OK"
    }
    return jsonify(status_data)


container_api(app)
images_api(app)
networks_api(app)
volumes_api(app)
projects_api(app)
