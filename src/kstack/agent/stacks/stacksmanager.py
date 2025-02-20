import os
from typing import Union

from . import ContainerStack
from .initializer import stack_from_portainer_template, stack_from_gitrepo, \
    stack_from_compose_url, stack_from_scratch, stack_from_template_repo, stack_from_template
from .docker import DockerComposeStack
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
                    stack = DockerComposeStack(file)
                    cls.add(stack)
                    print(f"Added from dir {stack.name}")
                else:
                    print(f"Skipping {file_path}")
            elif os.path.isfile(file_path) and file.endswith(".stack.json"):
                stack_name = file.replace(".stack.json", "")
                stack = DockerComposeStack(stack_name)
                cls.add(stack)
                print(f"Added from Json {stack.name}")

    @classmethod
    def register_initializer(cls, initializer_name, initializer):
        cls.initializers[initializer_name] = initializer

    @classmethod
    def deregister_initializer(cls, initializer_name):
        del cls.initializers[initializer_name]

    @classmethod
    def create_stack(cls, name, initializer_name=None, **kwargs):
        if cls.get(name) is not None:
            raise ValueError(f"Stack {name} already exists")

        initializer = cls.initializers.get(initializer_name)
        if initializer is None:
            raise ValueError(f"Initializer not registered: {initializer_name}")

        stack = initializer(name, **kwargs)
        cls.add(stack)
        return stack

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
    def start(cls, name) -> ContainerStack:
        if name not in cls.stacks:
            raise ValueError(f"Stack {name} not found")
        stack = cls.stacks[name]
        stack.start()
        return stack

    @classmethod
    def stop(cls, name) -> ContainerStack:
        if name not in cls.stacks:
            raise ValueError(f"Stack {name} not found")
        stack = cls.stacks[name]
        stack.stop()
        return stack

    @classmethod
    def remove(cls, name) -> ContainerStack:
        if name not in cls.stacks:
            raise ValueError(f"Stack {name} not found")
        stack = cls.stacks[name]
        #stack.remove()
        del cls.stacks[name]
        return stack

    @classmethod
    def get(cls, name) -> Union[ContainerStack, None]:
        if name not in cls.stacks:
            return None

        stack = cls.stacks[name]
        return stack

    @classmethod
    def restart(cls, name) -> ContainerStack:
        if name not in cls.stacks:
            raise ValueError(f"Stack {name} not found")
        stack = cls.stacks[name]
        stack.restart()
        return stack

    # @classmethod
    # def restart_all(cls):
    #     for stack in cls.stacks.values():
    #         stack.restart()
    #     return cls.stacks.values()

    @classmethod
    def sync(cls, name) -> ContainerStack:

        if name not in cls.stacks:
            raise ValueError(f"Stack {name} not found")
        stack = cls.stacks[name]

        meta = stack.meta
        if meta is None:
            raise ValueError("No metadata found")

        repo = meta.get("repository", None)
        if repo is not None:
            return cls._sync_repo(stack, repo)

        compose_url = meta.get("compose_url", None)
        if compose_url is not None:
            return cls._sync_compose_url(stack, compose_url)

        print("No sync source detected")
        return stack

    @classmethod
    def _sync_repo(cls, stack, repo):
        raise NotImplementedError("Syncing from a repository is not implemented")

    @classmethod
    def _sync_compose_url(cls, stack, compose_url):
        raise NotImplementedError("Syncing from a compose URL is not implemented")