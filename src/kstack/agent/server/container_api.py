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


@container_api_bp.route('/container/<string:key>', methods=["GET"])
def describe_container(key):
    return jsonify(dkr.get_container(key).attrs)


@container_api_bp.route('/container/start/<string:key>', methods=["POST"])
def start_container(key):
    return jsonify(dkr.start_container(key).attrs)


@container_api_bp.route('/container/pause/<string:key>', methods=["POST"])
def pause_container(key):
    return jsonify(dkr.pause_container(key).attrs)


@container_api_bp.route('/container/stop/<string:key>', methods=["POST"])
def stop_container(key):
    return jsonify(dkr.stop_container(key).attrs)


@container_api_bp.route('/container/remove/<string:key>', methods=["POST"])
def remove_container(key):
    if settings.AGENT_ENABLE_DELETE:
        return jsonify(dkr.remove_container(key).attrs)

    return jsonify(dkr.remove_container(key).attrs)


@container_api_bp.route('/container/restart/<string:key>', methods=["POST"])
def restart_container(key):
    return jsonify(dkr.restart_container(key).attrs)


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

