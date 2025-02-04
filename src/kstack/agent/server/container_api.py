from flask import jsonify

from kstack.agent.server import settings
from kstack.agent.server.app import app, dk


@app.route('/containers', methods=["GET"])
def list_containers():
    containers = dk.list_containers()
    #mapped = list(map(lambda x: x.attrs, containers))

    mapped = list()
    for container in containers:
        mapped.append(container.attrs)

    return jsonify(mapped)


@app.route('/container/<string:key>', methods=["GET"])
def describe_container(key):
    return jsonify(dk.get_container(key).attrs)


@app.route('/containers/restart', methods=["POST"])
def restart_all_containers():
    return jsonify(dk.restart_all_containers())


@app.route('/container/start/<string:key>', methods=["POST"])
def start_container(key):
    return jsonify(dk.start_container(key).attrs)


@app.route('/container/stop/<string:key>', methods=["POST"])
def stop_container(key):
    return jsonify(dk.stop_container(key).attrs)


@app.route('/container/remove/<string:key>', methods=["POST"])
def remove_container(key):
    if settings.DOCKERHTTP_ENABLE_DELETE:
        return jsonify(dk.remove_container(key).attrs)

    return jsonify(dk.remove_container(key).attrs)


@app.route('/container/restart/<string:key>', methods=["POST"])
def restart_container(key):
    return jsonify(dk.restart_container(key).attrs)
