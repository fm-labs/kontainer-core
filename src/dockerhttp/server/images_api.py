from flask import jsonify

from dockerhttp.server.app import app, dk


@app.route('/images', methods=["GET"])
def list_images():
    images = dk.list_images()
    mapped = list(map(lambda x: x.attrs, images))
    return jsonify(mapped)
