
from flask import jsonify

from dockerhttp.projects.projectmanager import ProjectManager
from dockerhttp.server.app import app


@app.route('/projects', methods=["GET"])
def list_projects():
    projects = ProjectManager.list_all()
    mapped = list(map(lambda x: x.serialize(), projects))
    return jsonify(mapped)

@app.route('/project/start/<string:key>', methods=["POST"])
def start_project(key):
    return jsonify(ProjectManager.start(key).serialize())


@app.route('/project/stop/<string:key>', methods=["POST"])
def stop_project(key):
    return jsonify(ProjectManager.stop(key).serialize())


@app.route('/project/remove/<string:key>', methods=["POST"])
def remove_project(key):
    return jsonify(ProjectManager.remove(key).serialize())


@app.route('/project/<string:key>', methods=["GET"])
def describe_project(key):
    return jsonify(ProjectManager.describe(key).serialize())


@app.route('/project/restart/<string:key>', methods=["POST"])
def restart_project(key):
    return jsonify(ProjectManager.restart(key).serialize())


@app.route('/projects/restart', methods=["POST"])
def restart_all_projects():
    return jsonify(ProjectManager.restart_all())
