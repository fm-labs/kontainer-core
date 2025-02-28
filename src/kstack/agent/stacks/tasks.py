from kstack.agent.celery import celery
from kstack.agent.stacks.docker import UnmanagedDockerComposeStack
from kstack.agent.stacks.stacksmanager import StacksManager


@celery.task(bind=True)
def create_stack_task(self, stack_name, initializer_name, **kwargs):
    stack = StacksManager.get(stack_name)
    if stack is not None:
        raise ValueError(f"Stack {stack_name} already exists")

    print(f"Creating stack {stack_name}")
    stack = StacksManager.init_stack(stack_name, initializer_name, **kwargs)
    return stack.__dict__


@celery.task(bind=True)
def stack_down_task(self, stack_name):
    print(f"Stack DOWN {stack_name}")
    return StacksManager.start(stack_name)


@celery.task(bind=True)
def stack_start_task(self, stack_name):
    print(f"Stack START {stack_name}")
    return StacksManager.start(stack_name)


@celery.task(bind=True)
def stack_stop_task(self, stack_name):
    print(f"Stack STOP {stack_name}")
    #return StacksManager.stop(stack_name)
    stack = StacksManager.get(stack_name)
    if stack is None:
        stack = UnmanagedDockerComposeStack(stack_name)
    return stack.stop()


@celery.task(bind=True)
def stack_restart_task(self, stack_name):
    print(f"Stack RESTART {stack_name}")
    #return StacksManager.restart(stack_name)
    stack = StacksManager.get(stack_name)
    if stack is None:
        stack = UnmanagedDockerComposeStack(stack_name)
    return stack.restart()


@celery.task(bind=True)
def stack_delete_task(self, stack_name):
    print(f"Stack DELETE {stack_name}")
    #return StacksManager.delete(stack_name)
    stack = StacksManager.get(stack_name)
    if stack is None:
        stack = UnmanagedDockerComposeStack(stack_name)
    return stack.delete()


@celery.task(bind=True)
def stack_destroy_task(self, stack_name):
    print(f"Stack DESTROY {stack_name}")
    return StacksManager.destroy(stack_name)


@celery.task(bind=True)
def stack_sync_task(self, stack_name):
    print(f"Stack SYNC {stack_name}")
    return StacksManager.sync(stack_name)
