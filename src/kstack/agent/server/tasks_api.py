import flask
from flask import jsonify, request
from flask_jwt_extended.view_decorators import jwt_required

from kstack.agent.celery import celery
from kstack.agent.admin.tasks import long_running_task, resolve_task

tasks_api_bp = flask.Blueprint('tasks_api', __name__, url_prefix='/api/tasks')


# @tasks_api_bp.route('/', methods=["GET"])
# def list_tasks():
#     tasks = list()
#     return jsonify(tasks)


@tasks_api_bp.route('', methods=['POST'])
@jwt_required()
def submit_task():
    """Accepts a task submission request and returns a task ID."""
    data = request.get_json()

    task_name = data.get('task_name', None)
    if task_name is None:
        return jsonify({'error': 'task_name is required'}), 400

    del data['task_name']
    task = resolve_task(task_name, data)
    if task is None:
        return jsonify({'error': f'Task {task_name} not found'}), 404

    return jsonify({'task_id': task.id}), 202


@tasks_api_bp.route('/<string:task_id>/status', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """Fetches the status of a submitted task."""

    try:
        task = celery.AsyncResult(task_id)
        if task is None:
            return jsonify({'error': 'Task not found'}), 404

        print(task_id, task.state, task)
        response = dict()
        response['task_id'] = task_id
        response['status'] = task.state
        if task.state == 'PROGRESS':
            response['progress'] = task.info
        elif task.state == 'SUCCESS':
            try:
                result = task.result
                if type(result) == bytes:
                    result = result.decode('utf-8')

                response['result'] = result
            except Exception as e:
                print(e)
                # response['error'] = str(e)
                raise e

        elif task.state == 'FAILURE':
            response['error'] = str(task.info)

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
