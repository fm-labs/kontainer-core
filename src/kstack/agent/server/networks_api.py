from flask import jsonify, Blueprint

from kstack.agent.docker.dkr import dkr

networks_api_bp = Blueprint('networks_api', __name__, url_prefix='/api/networks')

@networks_api_bp.route('', methods=["GET"])
def list_networks():
    networks = dkr.list_networks()
    mapped = list(map(lambda x: x.attrs, networks))
    return jsonify(mapped)
