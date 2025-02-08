import os

import flask.app
from flask import jsonify, request
import psutil

from kstack.agent import settings


def get_memory_usage():
    try:
        tot_m, used_m, free_m = map(int, os.popen('/usr/bin/free -t -m').readlines()[-1].split()[1:])
    except Exception as e:
        return -1, -1, -1

    return tot_m, used_m, free_m


def get_disk_usage(path):
    try:
        return psutil.disk_usage(path)
    except Exception as e:
        return None


def get_system_summary():
    return {
        "boot_time": psutil.boot_time(),
        "boot_time_iso": psutil.datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        "users": psutil.users(),
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(),
        "cpu_loadavg": psutil.getloadavg(),
        "cpu_loadavg_perc": [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()],
        "mem_virt": dict(psutil.virtual_memory()._asdict()),
        "mem_swap": dict(psutil.swap_memory()._asdict()),
        "mem_virt_percent": psutil.virtual_memory().percent,
        "mem_avail_percent": psutil.virtual_memory().available * 100 / psutil.virtual_memory().total,
        "disk_usage": {
            "root": get_disk_usage("/"),
        },
        # "disk_partitions": psutil.disk_partitions("/var"),
    }


def system_api(app: flask.app.Flask):

    @app.route('/system/info', methods=["GET"])
    def system_info():
        # data = get_system_report()
        data = {
            "memory": get_memory_usage(),
            #"system": get_system_summary(),
            #"settings": settings,
        }
        return jsonify(data)
