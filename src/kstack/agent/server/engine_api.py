import json
import threading
import time

import flask
from docker.types import CancellableStream
from flask import jsonify, request

from kstack.agent.docker.dkr import dkr


def engine_api(app: flask.app.Flask):
    """
    Engine API
    https://docker-py.readthedocs.io/en/stable/client.html

    :param app: flask.app.Flask
    """

    @app.route('/engine/info', methods=["GET"])
    def engine_info():
        """
        Get Engine Info

        :return: dict
        """
        info = dkr.client.info()
        info_dict = json.loads(json.dumps(info))
        return jsonify(info_dict)

    @app.route('/engine/version', methods=["GET"])
    def engine_version():
        """
        Get Engine Version

        :return: dict
        """
        version = dkr.client.version()
        return jsonify(version)


    @app.route('/engine/ping', methods=["GET"])
    def engine_ping():
        """
        Get Engine Ping

        :return: dict
        """
        ping = dkr.client.ping()
        return jsonify(ping)


    @app.route('/engine/df', methods=["GET"])
    def engine_df():
        """
        Get Engine Disk Usage

        :return: dict
        """
        df = dkr.client.df()
        return jsonify(df)


    @app.route('/engine/events', methods=["GET"])
    def engine_events():
        """
        Get Engine Events.
        https://docker-py.readthedocs.io/en/stable/events.html

        :return: dict
        """
        since = request.args.get("since", None)
        until = request.args.get("until", None)
        container = request.args.get("container", None)

        filters = {}
        if container:
            filters = {"container": container}
        if since is None or since == "":
            since = int(time.time()) - 3600
        if until is None or until == "":
            until = int(time.time())

        events = list()
        def read_events():
            events_stream: CancellableStream = dkr.client.events(decode=True,
                                                                 since=since,
                                                                 until=until,
                                                                 filters={filters})
            for ev in events_stream:
                events.append(ev)

        # read the (auto-decoded) event steam in a separate thread
        # wait for the thread to finish, max 10 sec
        t = threading.Thread(target=read_events)
        t.start()
        t.join(timeout=10)

        return jsonify(events)