import flask
from flask import jsonify

from ..dkr import dkr

def volumes_api(app: flask.app.Flask):

    @app.route('/volumes', methods=["GET"])
    def list_volumes():
        volumes = dkr.list_volumes()
        mapped = list(map(lambda x: x.attrs, volumes))
        return jsonify(mapped)
