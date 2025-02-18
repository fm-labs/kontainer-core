from kstack.agent.celery import celery
from kstack.agent.stacks.stacksmanager import StacksManager


@celery.task(bind=True)
def create_stack_task(self, stack_name, initializer_name, **kwargs):
    stack = StacksManager.get(stack_name)
    if stack is not None:
        raise ValueError(f"Stack {stack_name} already exists")

    print(f"Creating stack {stack_name}")
    return StacksManager.create_stack(stack_name, initializer_name, **kwargs)


@celery.task(bind=True)
def start_stack_task(self, stack_name):
    stack = StacksManager.get(stack_name)
    if stack is None:
        raise ValueError(f"Stack {stack_name} not found")

    print(f"Starting stack {stack_name}")
    return stack.start()


@celery.task(bind=True)
def stop_stack_task(self, stack_name):
    stack = StacksManager.get(stack_name)
    if stack is None:
        raise ValueError(f"Stack {stack_name} not found")

    print(f"Stopping stack {stack_name}")
    return stack.stop()


@celery.task(bind=True)
def restart_stack_task(self, stack_name):
    stack = StacksManager.get(stack_name)
    if stack is None:
        raise ValueError(f"Stack {stack_name} not found")

    print(f"Restarting stack {stack_name}")
    return stack.restart()



@celery.task(bind=True)
def delete_stack_task(self, stack_name):
    stack = StacksManager.get(stack_name)
    if stack is None:
        raise ValueError(f"Stack {stack_name} not found")

    print(f"Delete stack {stack_name}")
    pass
    #return stack.delete()