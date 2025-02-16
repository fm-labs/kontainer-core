import flask
from flask import jsonify, request

from .. import settings
from kstack.agent.docker.dkr import dkr

container_api_bp = flask.Blueprint('container_api', __name__, url_prefix='/api')


@container_api_bp.route('/containers', methods=["GET"])
def list_containers():
    containers = dkr.list_containers()
    #mapped = list(map(lambda x: x.attrs, containers))

    mapped = list()
    for container in containers:
        mapped.append(container.attrs)

    return jsonify(mapped)


@container_api_bp.route('/containers/<string:key>', methods=["GET"])
def describe_container(key):
    return jsonify(dkr.get_container(key).attrs)


@container_api_bp.route('/containers/start/<string:key>', methods=["POST"])
def start_container(key):
    try:
        container = dkr.start_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/pause/<string:key>', methods=["POST"])
def pause_container(key):
    try:
        container = dkr.pause_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/stop/<string:key>', methods=["POST"])
def stop_container(key):
    try:
        container = dkr.stop_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/remove/<string:key>', methods=["POST"])
def remove_container(key):
    if not settings.AGENT_ENABLE_DELETE:
        return jsonify({"error": "Delete is disabled"}), 500

    try:
        container = dkr.remove_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/restart/<string:key>', methods=["POST"])
def restart_container(key):
    try:
        container = dkr.restart_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/logs/<string:key>', methods=["GET"])
def get_container_logs(key):
    try:
        logs = dkr.get_container_logs(key)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/exec/<string:key>', methods=["POST"])
def exec_container_command(key):
    command = request.json["command"]
    try:
        result = dkr.exec_container_cmd(key, command)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/create', methods=["POST"])
def create_container():
    run_data = request.json
    image = run_data["image"]
    del run_data["image"]
    run_data["detach"] = True

    container = dkr.create_container(image, **run_data)
    return jsonify(container.attrs)

@container_api_bp.route('/containers/run', methods=["POST"])
def run_container():
    run_data = request.json
    image = run_data["image"]
    del run_data["image"]
    run_data["detach"] = True

    container = dkr.run_container(image, **run_data)
    return jsonify(container.attrs)


@container_api_bp.route('/containers/restart', methods=["POST"])
def restart_all_containers():
    return jsonify(dkr.restart_all_containers())

