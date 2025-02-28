import flask.app
from flask import jsonify
from flask_jwt_extended.view_decorators import jwt_required

system_api_bp = flask.Blueprint('system_api', __name__, url_prefix='/api/system')


@system_api_bp.route('/info', methods=["GET"])
@jwt_required()
def system_info():
    # data = get_system_report()
    data = {
        # "memory": get_memory_usage(),
        # "system": get_system_summary(),
        # "settings": settings,
    }
    return jsonify(data)
