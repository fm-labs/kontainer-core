import os
import json

from flask import Flask, jsonify
from flask_cors import CORS

from dockerhttp.projects.projectmanager import ProjectManager, DockerComposeProject
from dockerhttp.docker.client import DockerMgmtClient
from dockerhttp.server.settings import DOCKERHTTP_COMPOSE_DIR

# CLASSES
docker_host = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
dk = DockerMgmtClient(docker_host)

# Init project manager
# scan for directories in DOCKER_PROJECTS_DIR and check if they have a project.json or a docker-compose.yml file
# if they have a project.json file, load the project from the file
# if they have a docker-compose.yml file, create a project from the file
# if they have both, load the project from the project.json file and update it with the docker-compose.yml file
# if they have neither, ignore the directory
os.makedirs(DOCKERHTTP_COMPOSE_DIR, exist_ok=True)
for project in os.listdir(DOCKERHTTP_COMPOSE_DIR):
    project_dir = os.path.join(DOCKERHTTP_COMPOSE_DIR, project)
    if os.path.isdir(project_dir):
        project_json = os.path.join(project_dir, "project.json")
        docker_compose = os.path.join(project_dir, "docker-compose.yml")
        if os.path.exists(project_json):
            with open(project_json, "r") as f:
                project_data = json.load(f)
                p = DockerComposeProject(**project_data)
                ProjectManager.add(p)
        elif os.path.exists(docker_compose):
            p = DockerComposeProject.from_docker_compose(project, docker_compose)
            ProjectManager.add(p)
            pass
        else:
            print(f"Skipping {project_dir}")

app = Flask(__name__)
CORS(app)

from dockerhttp.server.container_api import *
from dockerhttp.server.images_api import *
from dockerhttp.server.volumes_api import *
from dockerhttp.server.networks_api import *
from dockerhttp.server.projects_api import *

@app.route('/', methods=["GET"])
def index():
    status_data = {
        "version": "1.0.0",
        "status": "OK"
    }
    return jsonify(status_data)
