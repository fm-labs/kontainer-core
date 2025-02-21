import time

from kstack.agent.celery import celery


def resolve_task(task_name: str, data: dict):
    """
    Resolve a task name to a Celery task function.

    Currently only a small hard-coded list of tasks is supported.

    :param task_name: The name of the task to resolve.
    """
    if task_name == 'long_running_task':
        duration = data.get('duration', '10')
        return long_running_task.apply_async(args=[duration])
    elif task_name == 'echo_task':
        message = data.get('message', None)
        return echo_task.apply_async(args=[message])


@celery.task(bind=True)
def long_running_task(self, duration):
    """A simple task that simulates a long-running process."""
    for i in range(duration):
        time.sleep(1)  # Simulate work
        self.update_state(state='PROGRESS', meta={'current': i + 1, 'total': duration})
    return {'status': 'Task completed!', 'duration': duration}


@celery.task(bind=True)
def echo_task(self, message=None):
    if message is None:
        message = "Hello, World!"
    return {'message': message}
