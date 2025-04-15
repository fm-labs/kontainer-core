from kontainer.admin.registries import request_container_registry_login
from kontainer.celery import celery
from kontainer.docker.dkr import get_docker_manager_cached


@celery.task(bind=True)
def registry_login_task(self, ctx_id, registry_name):
    print(f"Registry LOGIN {registry_name}")
    #dkr.registry_login(registry, username, password)
    request_container_registry_login(ctx_id, registry_name)


@celery.task(bind=True)
def container_start_task(self, ctx_id, container_id):
    print(f"Container START {container_id}")
    dkr = get_docker_manager_cached(ctx_id)
    dkr.start_container(container_id)


@celery.task(bind=True)
def container_pause_task(self, ctx_id, container_id):
    print(f"Container PAUSE {container_id}")
    dkr = get_docker_manager_cached(ctx_id)
    dkr.pause_container(container_id)


@celery.task(bind=True)
def container_stop_task(self, ctx_id, container_id):
    print(f"Container STOP {container_id}")
    dkr = get_docker_manager_cached(ctx_id)
    dkr.stop_container(container_id)


@celery.task(bind=True)
def container_restart_task(self, ctx_id, container_id):
    print(f"Container RESTART {container_id}")
    dkr = get_docker_manager_cached(ctx_id)
    dkr.restart_container(container_id)


@celery.task(bind=True)
def container_delete_task(self, ctx_id, container_id):
    print(f"Container DELETE {container_id}")
    dkr = get_docker_manager_cached(ctx_id)
    dkr.remove_container(container_id)


@celery.task(bind=True)
def image_pull_task(self, ctx_id, container_id):
    print(f"Image PULL {container_id}")
    dkr = get_docker_manager_cached(ctx_id)
    dkr.pull_image(container_id)
