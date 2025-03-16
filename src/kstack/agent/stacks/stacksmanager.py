import os
import shutil
from typing import Union

from docker.constants import DEFAULT_TIMEOUT_SECONDS

from . import ContainerStack
from .initializer import stack_from_portainer_template, stack_from_gitrepo, \
    stack_from_compose_url, stack_from_scratch, stack_from_template_repo, stack_from_template
from .docker import DockerComposeStack, UnmanagedDockerComposeStack
from .sync import sync_stack
from ..settings import AGENT_DATA_DIR


# Init stack manager
# scan for directories in DOCKER_PROJECTS_DIR and check if they have a stack.json or a docker-compose.yml file
# if they have a stack.json file, load the stack from the file
# if they have a docker-compose.yml file, create a stack from the file
# if they have both, load the stack from the stack.json file and update it with the docker-compose.yml file
# if they have neither, ignore the directory

class StacksManager:
    stacks = {}

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

    @classmethod
    def enumerate(cls):
        """
        Init stack manager
        scan for directories in DOCKER_PROJECTS_DIR and check if they have a stack.json or a docker-compose.yml file
        if they have a stack.json file, load the stack from the file
        if they have a docker-compose.yml file, create a stack from the file
        if they have both, load the stack from the stack.json file and update it with the docker-compose.yml file
        if they have neither, ignore the directory
        """
        cls.stacks = {}
        stacks_dir = os.path.join(AGENT_DATA_DIR, 'stacks')
        os.makedirs(stacks_dir, exist_ok=True)
        for file in os.listdir(stacks_dir):
            file_path = os.path.join(stacks_dir, file)
            if os.path.isdir(file_path):
                docker_compose = os.path.join(file_path, "docker-compose.yml")
                if os.path.exists(docker_compose):
                    stack = DockerComposeStack(file, managed=True)
                    cls.add(stack)
                    print(f"Added from dir {stack.name}")
                else:
                    print(f"Skipping {file_path}")
            elif os.path.isfile(file_path) and file.endswith(".stack.json"):
                stack_name = file.replace(".stack.json", "")
                stack = DockerComposeStack(stack_name, managed=True)
                cls.add(stack)
                print(f"Added from Json {stack.name}")


    @classmethod
    def register_initializer(cls, initializer_name, initializer):
        cls.initializers[initializer_name] = initializer


    @classmethod
    def deregister_initializer(cls, initializer_name):
        del cls.initializers[initializer_name]


    @classmethod
    def init_stack(cls, name, initializer_name=None, **kwargs):
        if cls.get(name) is not None:
            raise ValueError(f"Stack {name} already exists")

        initializer = cls.initializers.get(initializer_name)
        if initializer is None:
            raise ValueError(f"Initializer not registered: {initializer_name}")

        stack = initializer(name, **kwargs)
        cls.add(stack)
        return stack

    # MANAGE STACKS

    @classmethod
    def list_all(cls):
        return cls.stacks.values()


    @classmethod
    def add(cls, stack) -> None:
        if stack.name in cls.stacks:
            # raise ValueError(f"Stack {stack.name} already exists")
            return
        cls.stacks[stack.name] = stack


    @classmethod
    def get(cls, name) -> Union[ContainerStack, None]:
        if name not in cls.stacks:
            return None

        stack = cls.stacks[name]
        return stack


    @classmethod
    def get_or_unmanaged(cls, name) -> UnmanagedDockerComposeStack | None:
        stack = cls.get(name)
        if stack is None:
            stack = UnmanagedDockerComposeStack(name)
            cls.add(stack) # Add the unmanaged stack to the manager

        return stack

    @classmethod
    def remove(cls, name) -> None:
        if name not in cls.stacks:
            raise ValueError(f"Stack {name} not found")
        stack = cls.stacks[name]
        del cls.stacks[name]
        return stack



    # STACK OPERATIONS

    @classmethod
    def start(cls, name) -> bytes:
        # if name not in cls.stacks:
        #     raise ValueError(f"Stack {name} not found")
        # stack = cls.stacks[name]
        stack = cls.get_or_unmanaged(name)
        return stack.up()


    @classmethod
    def restart(cls, name) -> bytes:
        stack = cls.get_or_unmanaged(name)
        return stack.restart()


    @classmethod
    def stop(cls, name) -> bytes:
        stack = cls.get_or_unmanaged(name)
        return stack.stop()


    @classmethod
    def delete(cls, name) -> bytes:
        stack = cls.get_or_unmanaged(name)
        return stack.down()


    @classmethod
    def destroy(cls, name, **kwargs) -> bytes:
        #kwargs['timeout'] = DEFAULT_TIMEOUT_SECONDS if 'timeout' not in kwargs else kwargs['timeout']
        out = b""
        stack = cls.get_or_unmanaged(name)

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
        if stack.managed and os.path.exists(stack.project_dir):
            # Remove the project directory recursively with shutil.rmtree
            shutil.rmtree(stack.project_dir)
            out += bytes(f"\n\nDeleted project directory {stack.project_dir}", 'utf-8')

        if stack.managed and os.path.exists(stack.project_file):
            os.remove(stack.project_file)
            out += bytes(f"\n\nDeleted project file {stack.project_file}", 'utf-8')

        # Remove the stack from the manager
        if name in cls.stacks:
            del cls.stacks[name]

        return out


    @classmethod
    def sync(cls, name) -> bytes:
        #if name not in cls.stacks:
        #    raise ValueError(f"Stack {name} not found")

        # Refresh the list of stacks
        # @todo find a better way to do this
        StacksManager.enumerate()

        stack = cls.get_or_unmanaged(name)
        if stack is None or isinstance(stack, UnmanagedDockerComposeStack):
            raise ValueError(f"Cannot sync unmanaged stack {name}")

        # stack = cls.stacks[name]
        return sync_stack(stack)
