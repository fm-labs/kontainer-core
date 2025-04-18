import os
import shutil
from typing import Union

from . import ContainerStack
from .initializer import stack_from_portainer_template, stack_from_gitrepo, \
    stack_from_compose_url, stack_from_scratch, stack_from_template_repo, stack_from_template
from .dockerstacks import DockerComposeStack, UnmanagedDockerComposeStack
from .sync import sync_stack
from ..settings import KONTAINER_DATA_DIR


# Init stack manager
# scan for directories in DOCKER_PROJECTS_DIR and check if they have a stack.json or a docker-compose.yml file
# if they have a stack.json file, load the stack from the file
# if they have a docker-compose.yml file, create a stack from the file
# if they have both, load the stack from the stack.json file and update it with the docker-compose.yml file
# if they have neither, ignore the directory

stack_manager_cache = {}

def get_stacks_manager(ctx_id):
    """
    Get the stack manager for the given context id
    :param ctx_id: context id
    :return: stack manager
    """
    if ctx_id in stack_manager_cache:
        return stack_manager_cache[ctx_id]

    stack_manager = StacksManager(ctx_id)
    stack_manager_cache[ctx_id] = stack_manager
    return stack_manager


class StacksManager:

    # register the default initializers
    initializers = {
        "scratch": stack_from_scratch,
        "template": stack_from_template,
        "template_repo": stack_from_template_repo,
        #"file": stack_from_compose_file,
        #"archive": stack_from_compose_archive,
        #"dir": stack_from_compose_dir,
        "url": stack_from_compose_url,
        "portainer": stack_from_portainer_template,
        "git": stack_from_gitrepo,
        #"svn": stack_from_svnrepo,
    }

    def __init__(self, ctx_id):
        self.ctx_id = ctx_id
        self.stacks = {}
        self.enumerate()


    def enumerate(self):
        """
        Init stack manager
        scan for directories in DOCKER_PROJECTS_DIR and check if they have a stack.json or a docker-compose.yml file
        if they have a stack.json file, load the stack from the file
        if they have a docker-compose.yml file, create a stack from the file
        if they have both, load the stack from the stack.json file and update it with the docker-compose.yml file
        if they have neither, ignore the directory
        """
        self.stacks = {}

        stacks_dir = os.path.join(KONTAINER_DATA_DIR, 'stacks', self.ctx_id)
        os.makedirs(stacks_dir, exist_ok=True)
        for file in os.listdir(stacks_dir):
            file_path = os.path.join(stacks_dir, file)
            # if os.path.isdir(file_path):
            #     docker_compose = os.path.join(file_path, "docker-compose.yml")
            #     if os.path.exists(docker_compose):
            #         stack = DockerComposeStack(file, ctx_id=self.ctx_id, managed=True)
            #         self.add(stack)
            #         print(f"Added from stack dir: {stack.name}")
            #     else:
            #         print(f"Skipping {file_path}")
            if os.path.isfile(file_path) and file.endswith(".stack.json"):
                stack_name = file.replace(".stack.json", "")
                stack = DockerComposeStack(stack_name, ctx_id=self.ctx_id, managed=True)
                self.add(stack)
                print(f"Added from stack.json: {stack.name}")

    
    def register_initializer(self, initializer_name, initializer):
        self.initializers[initializer_name] = initializer


    def deregister_initializer(self, initializer_name):
        del self.initializers[initializer_name]

    
    def init_stack(self, name, initializer_name=None, **kwargs):
        if self.get(name) is not None:
            raise ValueError(f"Stack {name} already exists")

        initializer = self.initializers.get(initializer_name)
        if initializer is None:
            raise ValueError(f"Initializer not registered: {initializer_name}")

        ctx_id = self.ctx_id
        stack = initializer(ctx_id, name, **kwargs)
        self.add(stack)
        return stack

    # MANAGE STACKS

    def list_all(self):
        return self.stacks.values()


    def add(self, stack) -> None:
        if stack.name in self.stacks:
            # raise ValueError(f"Stack {stack.name} already exists")
            return
        self.stacks[stack.name] = stack


    
    def get(self, name) -> Union[ContainerStack, None]:
        if name not in self.stacks:
            return None

        stack = self.stacks[name]
        return stack


    def get_or_unmanaged(self, name) -> ContainerStack:
        stack = self.get(name)
        if stack is None:
            stack = UnmanagedDockerComposeStack(name, ctx_id=self.ctx_id)
            self.add(stack) # Add the unmanaged stack to the manager
        return stack

    
    def remove(self, name) -> None:
        if name not in self.stacks:
            raise ValueError(f"Stack {name} not found")
        stack = self.stacks[name]
        del self.stacks[name]
        return stack



    # STACK OPERATIONS

    def start(self, name) -> bytes:
        # if name not in self.stacks:
        #     raise ValueError(f"Stack {name} not found")
        # stack = self.stacks[name]
        stack = self.get_or_unmanaged(name)
        return stack.up()


    
    def restart(self, name) -> bytes:
        stack = self.get_or_unmanaged(name)
        return stack.restart()


    
    def stop(self, name) -> bytes:
        stack = self.get_or_unmanaged(name)
        return stack.stop()


    
    def delete(self, name) -> bytes:
        stack = self.get_or_unmanaged(name)
        return stack.down()


    
    def destroy(self, name, **kwargs) -> bytes:
        #kwargs['timeout'] = DEFAULT_TIMEOUT_SECONDS if 'timeout' not in kwargs else kwargs['timeout']
        out = b""
        stack = self.get_or_unmanaged(name)

        # Try bringing the stack down first
        try:
            out += stack.down()
        except Exception as e:
            out += bytes(f"\n\nError bringing stack down: {e}", 'utf-8')

        # Destroy the stack resources (implementation specific)
        try:
            out += stack.destroy()
        except Exception as e:
            out += bytes(f"\n\nError during stack destroy: {e}", 'utf-8')

        # Remove the stack file and directory from the local filesystem
        full_project_dir = os.path.join(KONTAINER_DATA_DIR, stack.project_dir)
        if stack.managed and os.path.exists(full_project_dir):
            # Remove the project directory recursively with shutil.rmtree
            shutil.rmtree(full_project_dir)
            out += bytes(f"\n\nDeleted project directory {stack.project_dir}", 'utf-8')

        project_file = os.path.join(KONTAINER_DATA_DIR, stack.name + ".stack.json")
        if stack.managed and os.path.exists(project_file):
            os.remove(project_file)
            out += bytes(f"\n\nDeleted project file {project_file}", 'utf-8')

        # Remove the stack from the manager
        if name in self.stacks:
            del self.stacks[name]

        return out

    
    def sync(self, name) -> bytes:
        if self.ctx_id != "local":
            raise ValueError("Sync is only supported for local stacks")

        # Refresh the list of stacks
        # @todo find a better way to refresh the list of stacks before sync
        self.enumerate()

        stack = self.get_or_unmanaged(name)
        if stack is None or stack.managed == False or isinstance(stack, UnmanagedDockerComposeStack):
            raise ValueError(f"Cannot sync unmanaged stack {name}")

        return sync_stack(stack)
