import flask
from flask import jsonify

from kstack.agent.docker.dkr import dkr

def volumes_api(app: flask.app.Flask):

    @app.route('/volumes', methods=["GET"])
    def list_volumes():
        volumes = dkr.list_volumes()
        mapped = list(map(lambda x: x.attrs, volumes))

        # get query params
        query = flask.request.args
        # check if 'size' query param is present
        if True or 'size' in query and query['size'] == 'true':
            # get volumes with size
            mapped = list(map(lambda x: {
                **x,
                '_Size': dkr.get_volume_size(x['Name'])
            }, mapped))

        return jsonify(mapped)
