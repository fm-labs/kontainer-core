import json
import os
from typing import Union

from . import ContainerStack
from .builder import stack_from_compose_file, stack_from_portainer_template, stack_from_gitrepo, stack_from_compose_url
from .docker import DockerComposeStack
from ..settings import AGENT_DATA_DIR


# Init project manager
# scan for directories in DOCKER_PROJECTS_DIR and check if they have a project.json or a docker-compose.yml file
# if they have a project.json file, load the project from the file
# if they have a docker-compose.yml file, create a project from the file
# if they have both, load the project from the project.json file and update it with the docker-compose.yml file
# if they have neither, ignore the directory

class StacksManager:
    projects = {}

    # register the default builders
    builders = {
        "file": stack_from_compose_file,
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
        Init project manager
        scan for directories in DOCKER_PROJECTS_DIR and check if they have a project.json or a docker-compose.yml file
        if they have a project.json file, load the project from the file
        if they have a docker-compose.yml file, create a project from the file
        if they have both, load the project from the project.json file and update it with the docker-compose.yml file
        if they have neither, ignore the directory
        """
        cls.projects = {}
        stacks_dir = os.path.join(AGENT_DATA_DIR, 'stacks')
        os.makedirs(stacks_dir, exist_ok=True)
        for dir_name in os.listdir(stacks_dir):
            project_dir = os.path.join(stacks_dir, dir_name)
            if os.path.isdir(project_dir):
                docker_compose = os.path.join(project_dir, "docker-compose.yml")
                if os.path.exists(docker_compose):
                    p = DockerComposeStack(dir_name)
                    cls.add(p)
                    pass
                else:
                    print(f"Skipping {project_dir}")

    @classmethod
    def register_builder(cls, builder_name, builder):
        cls.builders[builder_name] = builder

    @classmethod
    def deregister_builder(cls, builder_name):
        del cls.builders[builder_name]

    @classmethod
    def create_stack(cls, name, **kwargs):
        builder = cls.builders.get(kwargs.get("builder"))
        if builder is None:
            raise ValueError(f"Builder {kwargs.get('builder')} not found")

        stack = builder(name, **kwargs)
        cls.add(stack)
        return stack

    @classmethod
    def list_all(cls):
        return cls.projects.values()

    @classmethod
    def add(cls, project) -> None:
        if project.name in cls.projects:
            raise ValueError(f"Project {project.name} already exists")
        cls.projects[project.name] = project

    @classmethod
    def start(cls, name) -> ContainerStack:
        project = cls.projects[name]
        if project is None:
            raise ValueError(f"Project {name} not found")
        project.start()
        return project

    @classmethod
    def stop(cls, name) -> ContainerStack:
        project = cls.projects[name]
        if project is None:
            raise ValueError(f"Project {name} not found")
        project.stop()
        return project

    @classmethod
    def remove(cls, name) -> ContainerStack:
        project = cls.projects[name]
        if project is None:
            raise ValueError(f"Project {name} not found")
        project.remove()
        #del cls.projects[name]
        return project

    @classmethod
    def get(cls, name) -> Union[ContainerStack, None]:
        project = cls.projects[name]
        #if project is None:
        #    raise ValueError(f"Project {name} not found")
        return project

    @classmethod
    def restart(cls, name) -> ContainerStack:
        project = cls.projects[name]
        if project is None:
            raise ValueError(f"Project {name} not found")
        project.restart()
        return project

    # @classmethod
    # def restart_all(cls):
    #     for project in cls.projects.values():
    #         project.restart()
    #     return cls.projects.values()

