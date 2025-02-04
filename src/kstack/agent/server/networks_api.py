from flask import jsonify

from kstack.agent.server.app import app, dk


@app.route('/networks', methods=["GET"])
def list_networks():
    networks = dk.list_networks()
    mapped = list(map(lambda x: x.attrs, networks))
    return jsonify(mapped)
