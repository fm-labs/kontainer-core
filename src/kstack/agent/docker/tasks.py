from kstack.agent.celery import celery
from kstack.agent.docker.dkr import dkr

@celery.task(bind=True)
def container_start_task(self, container_id):
    print(f"Container START {container_id}")
    dkr.start_container(container_id)


@celery.task(bind=True)
def container_pause_task(self, container_id):
    print(f"Container PAUSE {container_id}")
    dkr.pause_container(container_id)


@celery.task(bind=True)
def container_stop_task(self, container_id):
    print(f"Container STOP {container_id}")
    dkr.stop_container(container_id)


@celery.task(bind=True)
def container_restart_task(self, container_id):
    print(f"Container RESTART {container_id}")
    dkr.restart_container(container_id)


@celery.task(bind=True)
def container_delete_task(self, container_id):
    print(f"Container DELETE {container_id}")
    dkr.remove_container(container_id)


@celery.task(bind=True)
def image_pull_task(self, container_id):
    print(f"Image PULL {container_id}")
    dkr.pull_image(container_id)
