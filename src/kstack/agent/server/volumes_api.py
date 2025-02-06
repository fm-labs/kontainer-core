import flask
from flask import jsonify

from ..dkr import docker_client

def volumes_api(app: flask.app.Flask):

    @app.route('/volumes', methods=["GET"])
    def list_volumes():
        volumes = docker_client.list_volumes()
        mapped = list(map(lambda x: x.attrs, volumes))

        # get query params
        query = flask.request.args
        # check if 'size' query param is present
        if True or 'size' in query and query['size'] == 'true':
            # get volumes with size
            mapped = list(map(lambda x: {
                **x,
                '_Size': docker_client.get_volume_size(x['Name'])
            }, mapped))

        return jsonify(mapped)
