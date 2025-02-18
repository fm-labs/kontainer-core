import flask
from flask import jsonify, request

from kstack.agent.celery import celery
from kstack.agent.admin.tasks import long_running_task

tasks_api_bp = flask.Blueprint('tasks_api', __name__, url_prefix='/api/tasks')


@tasks_api_bp.route('/', methods=["GET"])
def list_tasks():
    tasks = list()
    return jsonify(tasks)


@tasks_api_bp.route('/submit', methods=['POST'])
def submit_task():
    """Accepts a task submission request and returns a task ID."""
    data = request.get_json()
    duration = data.get('duration', 10)  # Default duration is 10 seconds
    task = long_running_task.apply_async(args=[duration])
    return jsonify({'task_id': task.id}), 202


@tasks_api_bp.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """Fetches the status of a submitted task."""
    task = celery.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {'status': 'PENDING'}
    elif task.state == 'PROGRESS':
        response = {'status': 'IN_PROGRESS', 'progress': task.info}
    elif task.state == 'SUCCESS':
        response = {'status': 'COMPLETED', 'result': task.result}
    else:
        response = {'status': task.state, 'error': str(task.info)}

    return jsonify(response)