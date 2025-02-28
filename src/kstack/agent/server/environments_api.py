import flask
from flask import jsonify
from flask_jwt_extended.view_decorators import jwt_required

from kstack.agent.environments.envmanager import EnvManager

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

    if refresh:
        EnvManager.enumerate_environments()

    environments = EnvManager.list_environments()
    mapped = list(map(lambda x: x.to_dict(), environments))
    return jsonify(mapped)


@environments_api_bp.route('', methods=["POST"])
@jwt_required()
def create_environment():
    """
    Add an env to the db

    :return:
    """
    request_json = flask.request.json
    try:
        env = EnvManager.create(request_json)
        return jsonify(env.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@environments_api_bp.route('/host/<string:alias>', methods=["GET"])
@jwt_required()
def describe_environment(alias: str):
    """
    Get an env from the db

    :return:
    """
    env = EnvManager.get(alias)
    if env is None:
        return jsonify({"error": "Environment not found"}), 404

    return jsonify(env.to_dict())


@environments_api_bp.route('/host/<string:alias>', methods=["DELETE"])
@jwt_required()
def remove_environment(alias: str):
    """
    Remove an env from the db

    :return:
    """
    env = EnvManager.get(alias)
    if env is None:
        return jsonify({"error": "Environment not found"}), 404

    EnvManager.remove(alias)
    return jsonify(env.to_dict())