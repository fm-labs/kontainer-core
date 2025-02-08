import flask
from flask import jsonify

from kstack.agent.docker.dkr import dkr


def networks_api(app: flask.app.Flask):

    @app.route('/networks', methods=["GET"])
    def list_networks():
        networks = dkr.list_networks()
        mapped = list(map(lambda x: x.attrs, networks))
        return jsonify(mapped)
