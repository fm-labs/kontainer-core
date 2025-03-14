import flask
from flask import jsonify, request
from flask_jwt_extended.view_decorators import jwt_required

from .. import settings
from kstack.agent.docker.dkr import dkr
from kstack.agent.docker.tasks import container_start_task, container_pause_task, container_stop_task, \
    container_delete_task, container_restart_task

container_api_bp = flask.Blueprint('container_api', __name__, url_prefix='/api/containers')


@container_api_bp.route('', methods=["GET"])
@jwt_required()
def list_containers():
    try:
        containers = dkr.list_containers()
        #mapped = list(map(lambda x: x.attrs, containers))

        mapped = list()
        for container in containers:
            mapped.append(container.attrs)

        return jsonify(mapped)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/<string:key>', methods=["GET"])
@jwt_required()
def describe_container(key):
    try:
        return jsonify(dkr.get_container(key).attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/<string:key>/start', methods=["POST"])
@jwt_required()
def start_container(key):
    try:
        if request.args.get('async', None) == "1":
            task = container_start_task.apply_async(args=[key])
            return jsonify({"task_id": task.id, "ref": f"/docker/containers/{key}"})

        container = dkr.start_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/<string:key>/pause', methods=["POST"])
@jwt_required()
def pause_container(key):
    try:
        if request.args.get('async', None) == "1":
            task = container_pause_task.apply_async(args=[key])
            return jsonify({"task_id": task.id, "ref": f"/docker/containers/{key}"})

        container = dkr.pause_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/<string:key>/stop', methods=["POST"])
@jwt_required()
def stop_container(key):
    try:
        if request.args.get('async', None) == "1":
            task = container_stop_task.apply_async(args=[key])
            return jsonify({"task_id": task.id, "ref": f"/docker/containers/{key}"})

        container = dkr.stop_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/<string:key>/remove', methods=["POST"])
@jwt_required()
def remove_container(key):
    if not settings.AGENT_ENABLE_DELETE:
        return jsonify({"error": "Delete is disabled"}), 403

    try:
        if request.args.get('async', None) == "1":
            task = container_delete_task.apply_async(args=[key])
            return jsonify({"task_id": task.id, "ref": f"/docker/containers/{key}"})

        container = dkr.remove_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/<string:key>/restart', methods=["POST"])
@jwt_required()
def restart_container(key):
    try:
        if request.args.get('async', None) == "1":
            task = container_restart_task.apply_async(args=[key])
            return jsonify({"task_id": task.id, "ref": f"/docker/containers/{key}"})

        container = dkr.restart_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/<string:key>/logs', methods=["GET"])
@jwt_required()
def get_container_logs(key):
    try:
        logs = dkr.get_container_logs(key)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/<string:key>/exec', methods=["POST"])
@jwt_required()
def exec_container_command(key):
    command = request.json["command"]
    try:
        result = dkr.exec_container_cmd(key, command)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/create', methods=["POST"])
@jwt_required()
def create_container():
    run_data = request.json
    image = run_data["image"]
    del run_data["image"]
    run_data["detach"] = True

    try:
        container = dkr.create_container(image, **run_data)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/run', methods=["POST"])
@jwt_required()
def run_container():
    run_data = request.json
    image = run_data["image"]
    del run_data["image"]
    run_data["detach"] = True

    try:
        container = dkr.run_container(image, **run_data)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# @container_api_bp.route('/containers/restart', methods=["POST"])
# def restart_all_containers():
#     return jsonify(dkr.restart_all_containers())

