from kontainer.celery import celery
from kontainer.stacks.stacksmanager import get_stacks_manager


@celery.task(bind=True)
def create_stack_task(self, ctx_id, stack_name, initializer_name, **kwargs):
    stack = get_stacks_manager(ctx_id).get(stack_name)
    if stack is not None:
        raise ValueError(f"Stack {stack_name} already exists")

    print(f"Creating stack {stack_name}")
    stack = get_stacks_manager(ctx_id).init_stack(stack_name, initializer_name, **kwargs)
    return stack.__dict__


@celery.task(bind=True)
def stack_start_task(self, ctx_id, stack_name):
    print(f"Stack START {stack_name}")
    return get_stacks_manager(ctx_id).start(stack_name)


@celery.task(bind=True)
def stack_stop_task(self, ctx_id, stack_name):
    print(f"Stack STOP {stack_name}")
    return get_stacks_manager(ctx_id).stop(stack_name)


@celery.task(bind=True)
def stack_restart_task(self, ctx_id, stack_name):
    print(f"Stack RESTART {stack_name}")
    return get_stacks_manager(ctx_id).restart(stack_name)


@celery.task(bind=True)
def stack_delete_task(self,ctx_id,  stack_name):
    print(f"Stack DELETE {stack_name}")
    return get_stacks_manager(ctx_id).delete(stack_name)


@celery.task(bind=True)
def stack_destroy_task(self, ctx_id, stack_name):
    print(f"Stack DESTROY {stack_name}")
    return get_stacks_manager(ctx_id).destroy(stack_name)


@celery.task(bind=True)
def stack_sync_task(self, ctx_id, stack_name):
    print(f"Stack SYNC {stack_name}")
    return get_stacks_manager(ctx_id).sync(stack_name)
