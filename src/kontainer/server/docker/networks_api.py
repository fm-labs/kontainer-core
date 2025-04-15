from flask import jsonify, Blueprint, g
from flask_jwt_extended.view_decorators import jwt_required

from kontainer.server.middleware import docker_service_middleware

networks_api_bp = Blueprint('networks_api', __name__, url_prefix='/api/docker/networks')
docker_service_middleware(networks_api_bp)

@networks_api_bp.route('', methods=["GET"])
@jwt_required()
def list_networks():
    networks = g.dkr.list_networks()
    mapped = list(map(lambda x: x.attrs, networks))
    return jsonify(mapped)
