import flask.app
from flask import jsonify

from kstack.agent.util.system_util import get_memory_usage

system_api_bp = flask.Blueprint('system_api', __name__, url_prefix='/api')


@system_api_bp.route('/system/info', methods=["GET"])
def system_info():
    # data = get_system_report()
    data = {
        "memory": get_memory_usage(),
        #"system": get_system_summary(),
        #"settings": settings,
    }
    return jsonify(data)
