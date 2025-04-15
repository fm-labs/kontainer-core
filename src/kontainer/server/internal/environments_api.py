import flask
from flask import jsonify
from flask_jwt_extended.view_decorators import jwt_required

from kontainer.docker.context import get_docker_envs, add_docker_env, remove_docker_env
from kontainer.docker.manager import DockerManager
from kontainer.environments.envmanager import EnvManager

environments_api_bp = flask.Blueprint('environments_api', __name__, url_prefix='/api/environments')

EnvManager.enumerate_environments()

@environments_api_bp.route('', methods=["GET"])
@jwt_required()
def list_environments():
    """
    List all environments

    :return:
    """
    query = flask.request.args
    refresh = query.get('refresh', None) == 'true'
    # host_type = query.get('type', None)

    # if refresh:
    #     EnvManager.enumerate_environments()
    #
    # environments = EnvManager.list_environments()
    # mapped = list(map(lambda x: x.to_dict(), environments))
    # return jsonify(mapped)
    return jsonify(get_docker_envs())


@environments_api_bp.route('', methods=["POST"])
@jwt_required()
def create_environment():
    """
    Add an env to the db

    :return:
    """
    request_json = flask.request.json
    try:
        #env = EnvManager.create(request_json)
        #return jsonify(env.to_dict())
        env = add_docker_env(**request_json)
        return jsonify(env), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@environments_api_bp.route('/<string:name>', methods=["GET"])
@jwt_required()
def describe_environment(name: str):
    """
    Get an env from the db

    :return:
    """
    #env = EnvManager.get(name)
    envs = get_docker_envs()
    env = None
    for e in envs:
        if e["id"] == name:
            env = e
            break

    if env is None:
        return jsonify({"error": "Environment not found"}), 404

    return jsonify(env)

@environments_api_bp.route('/<string:name>/connect', methods=["POST"])
@jwt_required()
def connect_environment(name: str):
    """
    Connect to a remote env

    :return:
    """
    #env = EnvManager.get(name)
    envs = get_docker_envs()
    env = None
    for e in envs:
        if e["id"] == name:
            env = e
            break

    if env is None:
        return jsonify({"error": "Environment not found"}), 404

    try:
        docker_host = env["host"]
        dkr = DockerManager(docker_host)
        info = dkr.info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@environments_api_bp.route('/<string:name>', methods=["DELETE"])
@jwt_required()
def remove_environment(name: str):
    """
    Remove an env from the db

    :return:
    """
    # env = EnvManager.get(alias)
    # if env is None:
    #     return jsonify({"error": "Environment not found"}), 404
    #
    # EnvManager.remove(alias)
    # return jsonify(env.to_dict())
    remove_docker_env(name)
    return jsonify({"message": "Environment removed"}), 200