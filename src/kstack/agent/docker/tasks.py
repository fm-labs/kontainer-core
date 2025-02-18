from kstack.agent.celery import celery
from kstack.agent.docker.dkr import dkr

@celery.task(bind=True)
def start_container(self, key) -> str:
    dkr.start_container(key)
    return key


@celery.task(bind=True)
def pause_container(self, key) -> str:
    dkr.pause_container(key)
    return key


@celery.task(bind=True)
def stop_container(self, key) -> str:
    dkr.stop_container(key)
    return key


@celery.task(bind=True)
def restart_container(self, key) -> str:
    dkr.restart_container(key)
    return key


@celery.task(bind=True)
def pull_image(self, key) -> str:
    dkr.pull_image(key)
    return key