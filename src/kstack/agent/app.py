from flask import Flask, jsonify
from flask_cors import CORS

from .server.container_api import container_api
from .server.engine_api import engine_api
from .server.images_api import images_api
from .server.networks_api import networks_api
from .server.stacks_api import stacks_api
from .server.system_api import system_api
from .server.volumes_api import volumes_api
from .stacks.stacksmanager import StacksManager

# CLASSES

StacksManager.enumerate()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./data/uploads"
CORS(app)

@app.route('/', methods=["GET"])
def index():
    status_data = {
        "version": "1.0.0",
        "status": "OK"
    }
    return jsonify(status_data)

engine_api(app)
container_api(app)
images_api(app)
networks_api(app)
volumes_api(app)
stacks_api(app)
system_api(app)