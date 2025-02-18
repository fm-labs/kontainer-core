import os
import time

import flask
from flask import jsonify, request

from .. import settings
from ..docker.manager import DockerManager
from ..stacks.docker import DockerComposeStack
from ..stacks.stacksmanager import StacksManager
from ..stacks.tasks import start_stack_task, stop_stack_task, delete_stack_task, restart_stack_task, create_stack_task

stacks_api_bp = flask.Blueprint('stacks_api', __name__, url_prefix='/api')

dkr = DockerManager()

@stacks_api_bp.route('/stacks', methods=["GET"])
def list_stacks():
    #time_start = time.time()
    #StacksManager.enumerate()
    managed_stacks = list(StacksManager.list_all())
    managed_names = [s.name for s in managed_stacks]
    #print(f"Enumerated stacks in {time.time() - time_start} seconds")

    # get all running containers
    #time_start = time.time()
    containers = dkr.list_containers()
    #print(f"Listed containers (1) in {time.time() - time_start} seconds")
    compose_stack_names = list(set([c.attrs.get('Config', {}).get('Labels', {}).get('com.docker.compose.project') for c in containers]))
    #print(f"Listed containers (2) in {time.time() - time_start} seconds")

    #time_start = time.time()
    for compose_stack_name in compose_stack_names:
        if compose_stack_name is None:
            continue
        if compose_stack_name not in managed_names:
            stack = DockerComposeStack(compose_stack_name)
            stack.managed = False
            managed_stacks.append(stack)

    def _map_managed_stack(_stack):
        _stack.running = _stack.name in compose_stack_names
        _stack.managed = _stack.name in managed_names
        return _stack.serialize()

    mapped = list(map(lambda x: _map_managed_stack(x), managed_stacks))
    #print(f"Mapped stacks in {time.time() - time_start} seconds")
    return jsonify(mapped)


@stacks_api_bp.route('/stack/start/<string:name>', methods=["POST"])
def start_stack(name):
    if request.args.get('sync', None) == "1":
        result = start_stack_task(name)
    else:
        task = start_stack_task.apply_async(args=[name])
        result = { "task_id": task.id }
    return jsonify(result)


@stacks_api_bp.route('/stack/stop/<string:name>', methods=["POST"])
def stop_stack(name):
    #return jsonify(StacksManager.stop(name).serialize())
    if request.args.get('sync', None) == "1":
        result = stop_stack_task(name)
    else:
        task = stop_stack_task.apply_async(args=[name])
        result = { "task_id": task.id }
    return jsonify(result)


@stacks_api_bp.route('/stack/remove/<string:name>', methods=["POST"])
def remove_stack(name):
    #return jsonify(StacksManager.remove(name).serialize())
    if request.args.get('sync', None) == "1":
        result = delete_stack_task(name)
    else:
        task = delete_stack_task.apply_async(args=[name])
        result = { "task_id": task.id }
    return jsonify(result)


@stacks_api_bp.route('/stack/<string:name>', methods=["GET"])
def describe_stack(name):
    return jsonify(StacksManager.get(name).serialize())


@stacks_api_bp.route('/stack/restart/<string:name>', methods=["POST"])
def restart_stack(name):
    # return jsonify(StacksManager.restart(name).serialize())
    if request.args.get('sync', None) == "1":
        result = restart_stack_task(name)
    else:
        task = restart_stack_task.apply_async(args=[name])
        result = { "task_id": task.id }
    return jsonify(result)


@stacks_api_bp.route('/stacks/create', methods=["POST"])
def create_stack():
    request_json = flask.request.json

    try:
        stack_name = request_json.get("stack_name")
        if stack_name is None:
            raise ValueError("stack_name is required")
        del request_json["stack_name"]

        initializer_name = request_json.get("launcher")
        if initializer_name is None:
            raise ValueError("launcher is required")
        del request_json["launcher"]

        # stack = StacksManager.create_stack(stack_name, initializer_name, **request_json)
        if request.args.get('sync', None) == "1":
            result = create_stack_task(stack_name, initializer_name, **request_json)
        else:
            task = create_stack_task.apply_async(args=[stack_name, initializer_name], kwargs=request_json)
            result = { "task_id": task.id }
        return jsonify(result)
    except Exception as e:
        # todo log error
        # raise e
        return jsonify({"error": str(e)}), 400


@stacks_api_bp.route('/stack/upload/<string:name>', methods=["POST"])
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
    upload_dir = os.path.join(settings.AGENT_DATA_DIR, 'stacks', name, 'uploads')
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
        # Save the file to the UPLOAD_DIR
        file.save(target_file)
        return f'File uploaded successfully: {filename}'
    else:
        return 'Invalid file type', 400
