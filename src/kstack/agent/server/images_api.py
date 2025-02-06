import flask
from flask import jsonify

from ..dkr import docker_client

def images_api(app: flask.app.Flask):

    @app.route('/images', methods=["GET"])
    def list_images():
        images = docker_client.list_images()
        mapped = list(map(lambda x: x.attrs, images))
        return jsonify(mapped)
