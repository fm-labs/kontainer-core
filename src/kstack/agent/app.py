from flask import Flask, jsonify
from flask_cors import CORS

from .server.engine_api import engine_api_bp
from .server.container_api import container_api_bp
from .server.images_api import images_api_bp
from .server.networks_api import networks_api_bp
from .server.stacks_api import stacks_api_bp
from .server.system_api import system_api_bp
from .server.volumes_api import volumes_api_bp
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


app.register_blueprint(engine_api_bp)
app.register_blueprint(container_api_bp)
app.register_blueprint(images_api_bp)
app.register_blueprint(networks_api_bp)
app.register_blueprint(stacks_api_bp)
app.register_blueprint(system_api_bp)
app.register_blueprint(volumes_api_bp)
