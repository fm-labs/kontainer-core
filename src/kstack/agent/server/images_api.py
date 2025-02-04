import flask
from flask import jsonify

from ..dkr import dkr

def images_api(app: flask.app.Flask):

    @app.route('/images', methods=["GET"])
    def list_images():
        images = dkr.list_images()
        mapped = list(map(lambda x: x.attrs, images))
        return jsonify(mapped)
