from flask import jsonify, Blueprint
from flask_jwt_extended.view_decorators import jwt_required

from kstack.agent.docker.dkr import dkr

images_api_bp = Blueprint('images_api', __name__, url_prefix='/api/images')

@images_api_bp.route('', methods=["GET"])
@jwt_required()
def list_images():
    images = dkr.list_images()
    mapped = list(map(lambda x: x.attrs, images))
    return jsonify(mapped)
