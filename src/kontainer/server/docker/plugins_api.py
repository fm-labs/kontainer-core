from flask import jsonify, request, Blueprint, g
from flask_jwt_extended.view_decorators import jwt_required

from kontainer.server.middleware import docker_service_middleware
from kontainer.util.docker_plugins_util import DockerPluginChecker

plugins_api_bp = Blueprint('plugins_api', __name__, url_prefix='/api/docker/plugins')
docker_service_middleware(plugins_api_bp)


@plugins_api_bp.route('/', methods=["GET"])
@jwt_required()
def list_plugins():
    """
    List all installed Docker plugins.

    :return: JSON list of plugin names
    """
    docker_host = g.dkr_host
    checker = DockerPluginChecker(docker_host=docker_host)
    checker.run_all_checks()
    plugins = checker.results
    return jsonify(plugins)