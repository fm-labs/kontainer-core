from flask import jsonify, Blueprint
from flask_jwt_extended.view_decorators import jwt_required

from .kube.client import get_kube_client

kube_pods_api_bp = Blueprint('kube_pods_api', __name__, url_prefix='/api/kube')


@kube_pods_api_bp.route('/pods', methods=["GET"])
@jwt_required()
def list_pods():
    """
    List pods

    :return:
    """
    pods = get_kube_client().list_pod_for_all_namespaces()
    mapped = list(map(lambda x: x.to_dict(), pods))
    return jsonify(mapped)

