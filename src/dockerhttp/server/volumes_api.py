from flask import jsonify

from dockerhttp.server.app import app, dk


@app.route('/volumes', methods=["GET"])
def list_volumes():
    volumes = dk.list_volumes()
    mapped = list(map(lambda x: x.attrs, volumes))
    return jsonify(mapped)
