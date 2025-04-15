from flask import jsonify, Blueprint
from flask_jwt_extended.view_decorators import jwt_required

from .kube.client import get_kube_client

kube_namespaces_api_bp = Blueprint('kube_namespaces_api', __name__, url_prefix='/api/kube')


@kube_namespaces_api_bp.route('/namespaces', methods=["GET"])
@jwt_required()
def list_namespaces():
    """
    List all namespaces

    :return:
    """
    namespaces = get_kube_client().list_namespace()
    mapped = list(map(lambda x: x.to_dict(), namespaces))
    return jsonify(mapped)


