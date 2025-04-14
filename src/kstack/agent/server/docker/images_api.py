from flask import jsonify, Blueprint, g
from flask_jwt_extended.view_decorators import jwt_required

from kstack.agent.server.middleware import docker_service_middleware

images_api_bp = Blueprint('images_api', __name__, url_prefix='/api/docker/images')
docker_service_middleware(images_api_bp)

@images_api_bp.route('', methods=["GET"])
@jwt_required()
def list_images():
    images = g.dkr.list_images()
    mapped = list(map(lambda x: x.attrs, images))
    return jsonify(mapped)
