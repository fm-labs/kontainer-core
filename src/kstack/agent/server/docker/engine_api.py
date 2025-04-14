import json
import threading
import time

from docker.types import CancellableStream
from flask import jsonify, request, Blueprint, g
from flask_jwt_extended.view_decorators import jwt_required

from kstack.agent.server.middleware import docker_service_middleware

engine_api_bp = Blueprint('engine_api', __name__, url_prefix='/api/docker/engine')
docker_service_middleware(engine_api_bp)


@engine_api_bp.route('/info', methods=["GET"])
@jwt_required()
def engine_info():
    """
    Get Engine Info

    :return: dict
    """
    info = g.dkr.client.info()
    info_dict = json.loads(json.dumps(info))
    return jsonify(info_dict)


@engine_api_bp.route('/version', methods=["GET"])
#@jwt_required()
def engine_version():
    """
    Get Engine Version

    :return: dict
    """
    version = g.dkr.client.version()
    return jsonify(version)


@engine_api_bp.route('/ping', methods=["GET"])
#@jwt_required()
def engine_ping():
    """
    Get Engine Ping

    :return: dict
    """
    ping = g.dkr.client.ping()
    return jsonify(ping)


@engine_api_bp.route('/df', methods=["GET"])
@jwt_required()
def engine_df():
    """
    Get Resource Usage Summary

    :return: dict
    """
    df = g.dkr.client.df()
    return jsonify(df)


@engine_api_bp.route('/events', methods=["GET"])
@jwt_required()
def engine_events():
    """
    Get Engine Events.
    https://docker-py.readthedocs.io/en/stable/events.html

    :return: dict
    """
    p_since = request.args.get("since", None)
    p_until = request.args.get("until", None)
    p_container = request.args.get("container", None)

    since = int(p_since) if p_since else None
    until = int(p_until) if p_until else None
    container = str(p_container) if p_container else None

    filters = {}
    if container:
        filters = {"container": container}
    if since is None or since == "":
        since = int(time.time()) - 3600
    if until is None or until == "":
        until = int(time.time())

    # now = int(time.time())
    # print("now:   ", now)
    # print("since: ", since, now - since)
    # print("until: ", until, now - until)

    events = list()

    def read_events():
        events_stream: CancellableStream = g.dkr.client.events(decode=True,
                                                             since=since,
                                                             until=until,
                                                             filters=filters)
        for ev in events_stream:
            events.append(ev)

    # read the (auto-decoded) event steam in a separate thread
    # wait for the thread to finish, max 10 sec
    t = threading.Thread(target=read_events)
    t.start()
    t.join(timeout=10)

    return jsonify(events)
