import flask
from flask import jsonify, request

from ..docker.manager import DockerManager
from ..stacks.docker import DockerComposeStack
from ..stacks.stacksmanager import StacksManager
from ..stacks.tasks import stack_start_task, stack_stop_task, stack_destroy_task, stack_restart_task, create_stack_task, \
    stack_delete_task, stack_sync_task

stacks_api_bp = flask.Blueprint('stacks_api', __name__, url_prefix='/api')

dkr = DockerManager()


@stacks_api_bp.route('/stacks', methods=["GET"])
def list_stacks():
    # time_start = time.time()
    StacksManager.enumerate()
    stacks = list(StacksManager.list_all())
    managed_names = [s.name for s in stacks]
    # print(f"Enumerated stacks in {time.time() - time_start} seconds")

    # get all running containers
    # time_start = time.time()
    containers = dkr.list_containers()
    # print(f"Listed containers (1) in {time.time() - time_start} seconds")
    active_stack_names = list(
        set([c.attrs.get('Config', {}).get('Labels', {}).get('com.docker.compose.project') for c in containers]))

    # print(f"Listed containers (2) in {time.time() - time_start} seconds")

    def _get_containers_for_stack(stack_name):
        return [c.attrs for c in containers if
                c.attrs.get('Config', {}).get('Labels', {}).get('com.docker.compose.project') == stack_name]

    # time_start = time.time()
    for active_stack_name in active_stack_names:
        if active_stack_name is None:
            continue
        if active_stack_name not in managed_names:
            stack = DockerComposeStack(active_stack_name, managed=False)
            stacks.append(stack)

    def _map_managed_stack(_stack):
        stack_data = _stack.serialize()
        stack_data['status'] = 'running' if _stack.name in active_stack_names else '-'
        stack_data['containers'] = _get_containers_for_stack(_stack.name)
        return stack_data

    mapped = list(map(lambda x: _map_managed_stack(x), stacks))
    # print(f"Mapped stacks in {time.time() - time_start} seconds")
    return jsonify(mapped)


@stacks_api_bp.route('/stacks/<string:name>/start', methods=["POST"])
def start_stack(name):
    if request.args.get('sync', None) == "1":
        result = stack_start_task(name)
    else:
        task = stack_start_task.apply_async(args=[name])
        result = {"task_id": task.id, "ref": f"/docker/stacks/{name}"}
    return jsonify(result)


@stacks_api_bp.route('/stacks/<string:name>/stop', methods=["POST"])
def stop_stack(name):
    # return jsonify(StacksManager.stop(name).serialize())
    if request.args.get('sync', None) == "1":
        result = stack_stop_task(name)
    else:
        task = stack_stop_task.apply_async(args=[name])
        result = {"task_id": task.id, "ref": f"/docker/stacks/{name}"}
    return jsonify(result)


@stacks_api_bp.route('/stacks/<string:name>/delete', methods=["POST"])
def delete_stack(name):
    # return jsonify(StacksManager.remove(name).serialize())
    if request.args.get('sync', None) == "1":
        result = stack_delete_task(name)
    else:
        task = stack_delete_task.apply_async(args=[name])
        result = {"task_id": task.id, "ref": f"/docker/stacks/{name}"}
    return jsonify(result)


@stacks_api_bp.route('/stacks/<string:name>/destroy', methods=["POST"])
def destroy_stack(name):
    # return jsonify(StacksManager.remove(name).serialize())
    if request.args.get('sync', None) == "1":
        result = stack_destroy_task(name)
    else:
        task = stack_destroy_task.apply_async(args=[name])
        result = {"task_id": task.id, "ref": f"/docker/stacks/{name}"}
    return jsonify(result)


@stacks_api_bp.route('/stacks/<string:name>/sync', methods=["POST"])
def sync_stack(name):
    if request.args.get('sync', None) == "1":
        result = stack_sync_task(name)
    else:
        task = stack_sync_task.apply_async(args=[name])
        result = {"task_id": task.id, "ref": f"/docker/stacks/{name}"}
    return jsonify(result)


@stacks_api_bp.route('/stacks/<string:name>', methods=["GET"])
def describe_stack(name):
    return jsonify(StacksManager.get(name).serialize())


@stacks_api_bp.route('/stacks/<string:name>/restart', methods=["POST"])
def restart_stack(name):
    # return jsonify(StacksManager.restart(name).serialize())
    if request.args.get('sync', None) == "1":
        result = stack_restart_task(name)
    else:
        task = stack_restart_task.apply_async(args=[name])
        result = {"task_id": task.id, "ref": f"/docker/stacks/{name}"}
    return jsonify(result)


@stacks_api_bp.route('/stacks/create', methods=["POST"])
def create_stack():
    request_json = flask.request.json

    try:
        stack_name = request_json.get("stack_name", "").strip()
        if stack_name is None or stack_name == "":
            raise ValueError("stack_name is required")
        del request_json["stack_name"]

        if StacksManager.get(stack_name) is not None:
            raise ValueError(f"Stack {stack_name} already exists")

        initializer_name = request_json.get("launcher", "").strip()
        if initializer_name is None or initializer_name == "":
            raise ValueError("launcher is required")
        del request_json["launcher"]

        # stack = StacksManager.create_stack(stack_name, initializer_name, **request_json)
        if request.args.get('sync', None) == "1":
            result = create_stack_task(stack_name, initializer_name, **request_json)
        else:
            task = create_stack_task.apply_async(args=[stack_name, initializer_name], kwargs=request_json)
            result = {"task_id": task.id, "ref": f"/docker/stacks/{stack_name}"}
        return jsonify(result)
    except Exception as e:
        # todo log error
        # raise e
        return jsonify({"error": str(e)}), 400

# @stacks_api_bp.route('/stacks/<string:name>/upload', methods=["POST"])
# def upload_stack(name):
#     """
#     Upload a stack yml file or stack archive (zip, tar.gz)
#     """
#     ALLOWED_EXTENSIONS = {'yml', 'tar', 'tar.gz', 'tar.xz'}
#
#     # Helper function to check if the file has an allowed extension
#     def allowed_file(filename):
#         return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
#     stack = StacksManager.get(name)
#     if not stack:
#         return jsonify({"error": f"Project {name} not found"}), 404
#
#     # Save the file to the stack directory
#     upload_dir = os.path.join(settings.AGENT_DATA_DIR, 'stacks', name, 'uploads')
#     os.makedirs(upload_dir, exist_ok=True)
#
#     # Check if a file is part of the request
#     if 'file' not in request.files:
#         return 'No file part', 400
#     file = request.files['file']
#
#     # If no file is selected
#     if file.filename == '':
#         return 'No selected file', 400
#
#     # If the file has a valid extension
#     if file and allowed_file(file.filename):
#         filename = file.filename
#         target_file = os.path.join(upload_dir, filename)
#         # Save the file to the UPLOAD_DIR
#         file.save(target_file)
#         return f'File uploaded successfully: {filename}'
#     else:
#         return 'Invalid file type', 400
