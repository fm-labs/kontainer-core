import flask
from flask import jsonify

from ..dkr import docker_client


def networks_api(app: flask.app.Flask):

    @app.route('/networks', methods=["GET"])
    def list_networks():
        networks = docker_client.list_networks()
        mapped = list(map(lambda x: x.attrs, networks))
        return jsonify(mapped)
