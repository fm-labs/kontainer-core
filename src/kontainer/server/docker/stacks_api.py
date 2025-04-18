import flask
from flask import jsonify, request, g
from flask_jwt_extended.view_decorators import jwt_required

from kontainer.docker.util import list_projects_from_containers, filter_containers_by_project, \
    filter_containers_by_status_text
from kontainer.server.middleware import docker_service_middleware
from kontainer.stacks.dockerstacks import DockerComposeStack, UnmanagedDockerComposeStack
from kontainer.stacks.stacksmanager import get_stacks_manager
from kontainer.stacks.tasks import stack_start_task, stack_stop_task, stack_destroy_task, stack_restart_task, \
    create_stack_task, \
    stack_delete_task, stack_sync_task

stacks_api_bp = flask.Blueprint('stacks_api', __name__, url_prefix='/api/stacks')
docker_service_middleware(stacks_api_bp)


@stacks_api_bp.route('', methods=["GET"])
@jwt_required()
def list_stacks():
    # time_start = time.time()
    ctx_id = g.dkr_ctx_id
    stacks_manager = get_stacks_manager(ctx_id=ctx_id)
    stacks_manager.enumerate()
    stacks = list(stacks_manager.list_all())
    managed_names = [s.name for s in stacks]
    # print(f"Enumerated stacks in {time.time() - time_start} seconds")

    # get all running containers
    # time_start = time.time()
    containers = g.dkr.list_containers()
    # print(f"Listed containers (1) in {time.time() - time_start} seconds")
    active_stack_names = list_projects_from_containers(containers)
    # print(f"Listed containers (2) in {time.time() - time_start} seconds")

    # time_start = time.time()
    for active_stack_name in active_stack_names:
        if active_stack_name is None:
            continue
        if active_stack_name not in managed_names:
            #stack = DockerComposeStack(active_stack_name, ctx_id=ctx_id, managed=False)
            stack = UnmanagedDockerComposeStack(active_stack_name, ctx_id=ctx_id)
            stacks.append(stack)

    def _map_managed_stack(_stack):
        stack_data = _stack.serialize()
        stack_containers = filter_containers_by_project(containers, _stack.name)
        stack_data['containers'] = list(map(lambda c: c.attrs, stack_containers))
        stack_data['status'] = 'idle' if _stack.name in active_stack_names else 'created'
        if len(filter_containers_by_status_text(stack_containers, "running")) > 0:
            stack_data['status'] = 'running'
        return stack_data

    mapped = list(map(lambda x: _map_managed_stack(x), stacks))
    # print(f"Mapped stacks in {time.time() - time_start} seconds")
    return jsonify(mapped)


@stacks_api_bp.route('/<string:name>/start', methods=["POST"])
@jwt_required()
def start_stack(name):
    ctx_id = g.dkr_ctx_id
    if request.args.get('sync', None) == "1":
        result = stack_start_task(ctx_id, name)
    else:
        ctx_id = g.dkr_ctx_id
        task = stack_start_task.apply_async(args=[ctx_id, name])
        result = {"task_id": task.id, "ref": f"/docker/{name}", "ctx_id": ctx_id}
    return jsonify(result)


@stacks_api_bp.route('/<string:name>/stop', methods=["POST"])
@jwt_required()
def stop_stack(name):
    ctx_id = g.dkr_ctx_id
    # return jsonify(StacksManager.stop(name).serialize())
    if request.args.get('sync', None) == "1":
        result = stack_stop_task(ctx_id, name)
    else:
        task = stack_stop_task.apply_async(args=[ctx_id, name])
        result = {"task_id": task.id, "ref": f"/docker/{name}", "ctx_id": ctx_id}
    return jsonify(result)


@stacks_api_bp.route('/<string:name>/delete', methods=["POST"])
@jwt_required()
def delete_stack(name):
    ctx_id = g.dkr_ctx_id
    # return jsonify(StacksManager.remove(name).serialize())
    if request.args.get('sync', None) == "1":
        result = stack_delete_task(ctx_id, name)
    else:
        task = stack_delete_task.apply_async(args=[ctx_id, name])
        result = {"task_id": task.id, "ref": f"/docker/{name}", "ctx_id": ctx_id}
    return jsonify(result)


@stacks_api_bp.route('/<string:name>/destroy', methods=["POST"])
@jwt_required()
def destroy_stack(name):
    ctx_id = g.dkr_ctx_id
    # return jsonify(StacksManager.remove(name).serialize())
    if request.args.get('sync', None) == "1":
        result = stack_destroy_task(ctx_id, name)
    else:
        task = stack_destroy_task.apply_async(args=[ctx_id, name])
        result = {"task_id": task.id, "ref": f"/docker/{name}", "ctx_id": ctx_id}
    return jsonify(result)


@stacks_api_bp.route('/<string:name>/sync', methods=["POST"])
@jwt_required()
def sync_stack(name):
    ctx_id = g.dkr_ctx_id
    if request.args.get('sync', None) == "1":
        result = stack_sync_task(ctx_id, name)
    else:
        task = stack_sync_task.apply_async(args=[ctx_id, name])
        result = {"task_id": task.id, "ref": f"/docker/{name}", "ctx_id": ctx_id}
    return jsonify(result)


@stacks_api_bp.route('/<string:name>', methods=["GET"])
@jwt_required()
def describe_stack(name):
    # Managed
    # First check if the stack is managed
    ctx_id = g.dkr_ctx_id
    stacks_manager = get_stacks_manager(ctx_id=ctx_id)
    stack = stacks_manager.get_or_unmanaged(name)
    return jsonify(stack.serialize())


@stacks_api_bp.route('/<string:name>/restart', methods=["POST"])
@jwt_required()
def restart_stack(name):
    ctx_id = g.dkr_ctx_id
    # return jsonify(StacksManager.restart(name).serialize())
    if request.args.get('sync', None) == "1":
        result = stack_restart_task(ctx_id, name)
    else:
        task = stack_restart_task.apply_async(args=[ctx_id, name])
        result = {"task_id": task.id, "ref": f"/docker/{name}"}
    return jsonify(result)


@stacks_api_bp.route('/create', methods=["POST"])
@jwt_required()
def create_stack():
    request_json = flask.request.json
    ctx_id = g.dkr_ctx_id

    try:
        stack_name = request_json.get("stack_name", "").strip()
        if stack_name is None or stack_name == "":
            raise ValueError("stack_name is required")
        del request_json["stack_name"]

        stacks_manager = get_stacks_manager(ctx_id=ctx_id)
        if stacks_manager is None:
            raise ValueError("StacksManager not found")
        if stacks_manager.get(stack_name) is not None:
            raise ValueError(f"Stack {stack_name} already exists")

        initializer_name = request_json.get("launcher", "").strip()
        if initializer_name is None or initializer_name == "":
            raise ValueError("launcher is required")
        del request_json["launcher"]

        # stack = StacksManager.create_stack(stack_name, initializer_name, **request_json)
        if request.args.get('sync', None) == "1":
            result = create_stack_task(ctx_id, stack_name, initializer_name, **request_json)
        else:
            task = create_stack_task.apply_async(args=[ctx_id, stack_name, initializer_name], kwargs=request_json)
            result = {"task_id": task.id, "ref": f"/docker/{stack_name}"}
        return jsonify(result)
    except Exception as e:
        # todo log error
        # raise e
        return jsonify({"error": str(e)}), 400

# @stacks_api_bp.route('/<string:name>/upload', methods=["POST"])
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
#     upload_dir = os.path.join(settings.KONTAINER_DATA_DIR, 'stacks', name, 'uploads')
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
