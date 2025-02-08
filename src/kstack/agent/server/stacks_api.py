import os

import flask
from flask import jsonify, request

from ..stacks.docker import DockerComposeStack
from ..stacks.stacksmanager import StacksManager

def stacks_api(app: flask.app.Flask):

    @app.route('/stacks', methods=["GET"])
    def list_stacks():
        stacks = StacksManager.list_all()
        mapped = list(map(lambda x: x.serialize(), stacks))
        return jsonify(mapped)

    @app.route('/stack/start/<string:name>', methods=["POST"])
    def start_stack(name):
        return jsonify(StacksManager.start(name).serialize())


    @app.route('/stack/stop/<string:name>', methods=["POST"])
    def stop_stack(name):
        return jsonify(StacksManager.stop(name).serialize())


    @app.route('/stack/remove/<string:name>', methods=["POST"])
    def remove_stack(name):
        return jsonify(StacksManager.remove(name).serialize())


    @app.route('/stack/<string:name>', methods=["GET"])
    def describe_stack(name):
        return jsonify(StacksManager.get(name).serialize())


    @app.route('/stack/restart/<string:name>', methods=["POST"])
    def restart_stack(name):
        return jsonify(StacksManager.restart(name).serialize())


    @app.route('/stack/upload/<string:name>', methods=["POST"])
    def upload_stack(name):
        """
        Upload a stack yml file or stack archive (zip, tar.gz)
        """
        ALLOWED_EXTENSIONS = {'yml', 'tar', 'tar.gz', 'tar.xz'}

        # Helper function to check if the file has an allowed extension
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


        stack = StacksManager.get(name)
        if not stack:
            return jsonify({"error": f"Project {name} not found"}), 404

        # Save the file to the stack directory
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], name)
        os.makedirs(upload_dir, exist_ok=True)

        # Check if a file is part of the request
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']

        # If no file is selected
        if file.filename == '':
            return 'No selected file', 400

        # If the file has a valid extension
        if file and allowed_file(file.filename):
            filename = file.filename
            target_file = os.path.join(upload_dir, filename)
            # Save the file to the UPLOAD_FOLDER
            file.save(target_file)
            return f'File uploaded successfully: {filename}'
        else:
            return 'Invalid file type', 400


    @app.route('/stacks/create', methods=["POST"])
    def create_stack():
        request_json = flask.request.json

        name = request_json.get("name")
        if not name:
            return jsonify({"error": "name is required"}), 400

        try:
            stack = StacksManager.create_stack(name, **request_json)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        return jsonify(stack.serialize())
