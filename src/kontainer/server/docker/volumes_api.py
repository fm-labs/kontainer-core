import flask
from flask import jsonify, g
from flask_jwt_extended.view_decorators import jwt_required

from kontainer.server.middleware import docker_service_middleware

volumes_api_bp = flask.Blueprint('volumes_api', __name__, url_prefix='/api/docker/volumes')
docker_service_middleware(volumes_api_bp)

@volumes_api_bp.route('', methods=["GET"])
@jwt_required()
def list_volumes():
    """
    List all volumes

    Optional query parameters:
    - size: true/false (default: false) True to include size information
    - in_use: true/false (default: false) True to include in-use information

    :return:
    """
    query = flask.request.args
    check_size = query.get('size', 'false') == 'true'
    check_in_use = query.get('in_use', 'false') == 'true'

    volumes = g.dkr.list_volumes(check_in_use=check_in_use, check_size=check_size)
    mapped = list(map(lambda x: x.attrs, volumes))
    return jsonify(mapped)
