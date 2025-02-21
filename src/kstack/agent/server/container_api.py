import flask
from flask import jsonify, request

from .. import settings
from kstack.agent.docker.dkr import dkr
from kstack.agent.docker.tasks import container_start_task, container_pause_task, container_stop_task, \
    container_delete_task, container_restart_task

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


@container_api_bp.route('/containers/<string:key>/start', methods=["POST"])
def start_container(key):
    try:
        if request.args.get('async', None) == "1":
            task = container_start_task.apply_async(args=[key])
            return jsonify({"task_id": task.id, "ref": f"/docker/containers/{key}"})

        container = dkr.start_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/<string:key>/pause', methods=["POST"])
def pause_container(key):
    try:
        if request.args.get('async', None) == "1":
            task = container_pause_task.apply_async(args=[key])
            return jsonify({"task_id": task.id, "ref": f"/docker/containers/{key}"})

        container = dkr.pause_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/<string:key>/stop', methods=["POST"])
def stop_container(key):
    try:
        if request.args.get('async', None) == "1":
            task = container_stop_task.apply_async(args=[key])
            return jsonify({"task_id": task.id, "ref": f"/docker/containers/{key}"})

        container = dkr.stop_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/<string:key>/remove', methods=["POST"])
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


@container_api_bp.route('/containers/<string:key>/restart', methods=["POST"])
def restart_container(key):
    try:
        if request.args.get('async', None) == "1":
            task = container_restart_task.apply_async(args=[key])
            return jsonify({"task_id": task.id, "ref": f"/docker/containers/{key}"})

        container = dkr.restart_container(key)
        return jsonify(container.attrs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/<string:key>/logs', methods=["GET"])
def get_container_logs(key):
    try:
        logs = dkr.get_container_logs(key)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@container_api_bp.route('/containers/<string:key>/exec', methods=["POST"])
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


# @container_api_bp.route('/containers/restart', methods=["POST"])
# def restart_all_containers():
#     return jsonify(dkr.restart_all_containers())

