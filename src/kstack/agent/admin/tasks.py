import time

from kstack.agent.celery import celery


@celery.task(bind=True)
def long_running_task(self, duration):
    """A simple task that simulates a long-running process."""
    for i in range(duration):
        time.sleep(1)  # Simulate work
        self.update_state(state='PROGRESS', meta={'current': i + 1, 'total': duration})
    return {'status': 'Task completed!', 'duration': duration}

