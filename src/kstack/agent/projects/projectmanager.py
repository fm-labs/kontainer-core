import json
import os
import subprocess

from .. import settings

from ..settings import AGENT_COMPOSE_DIR


class DockerComposeProject:
    def __init__(self, key, name, data=None):
        self.key = key
        self.name = name
        self.data = data

    def start(self):
        project_dir = os.path.join(settings.AGENT_COMPOSE_DIR, self.key)
        print(f"Starting project {self.key} in {project_dir}")

        # Run docker compose up
        try:
            p1 = subprocess.run(["docker", "compose", "up", "-d"], cwd=project_dir, env=os.environ, capture_output=True)
            print(p1.stdout)
        except Exception as e:
            print(e)
            raise e

    def stop(self):
        project_dir = os.path.join(settings.AGENT_COMPOSE_DIR, self.key)
        print(f"Stopping project {self.key} in {project_dir}")

        # Run docker compose stop
        try:
            p1 = subprocess.run(["docker", "compose", "stop"], cwd=project_dir, env=os.environ, capture_output=True)
            print(p1.stdout)
        except Exception as e:
            print(e)
            raise e

    def remove(self):
        project_dir = os.path.join(settings.AGENT_COMPOSE_DIR, self.key)
        print(f"Removing project {self.key} in {project_dir}")

        # Run docker compose stop
        try:
            p1 = subprocess.run(["docker", "compose", "down"], cwd=project_dir, env=os.environ, capture_output=True)
            print(p1.stdout)
        except Exception as e:
            print(e)
            raise e

    def restart(self):
        project_dir = os.path.join(settings.AGENT_COMPOSE_DIR, self.key)
        print(f"Restarting project {self.key} in {project_dir}")

        # Run docker compose restart
        try:
            p1 = subprocess.run(["docker", "compose", "restart"], cwd=project_dir, env=os.environ, capture_output=True)
            print(p1.stdout)
        except Exception as e:
            print(e)
            raise e

    def serialize(self):
        return {
            "key": self.key,
            "name": self.name,
            "data": self.data
        }

    @classmethod
    def from_docker_compose(cls, project, docker_compose_path):
        # Read the file path contents
        with open(docker_compose_path, "r") as f:
            contents = f.read()

        p = cls(project, project, contents)
        return p

# Init project manager
# scan for directories in DOCKER_PROJECTS_DIR and check if they have a project.json or a docker-compose.yml file
# if they have a project.json file, load the project from the file
# if they have a docker-compose.yml file, create a project from the file
# if they have both, load the project from the project.json file and update it with the docker-compose.yml file
# if they have neither, ignore the directory

class ProjectManager:
    projects = {}

    @classmethod
    def init(cls):
        """
        Init project manager
        scan for directories in DOCKER_PROJECTS_DIR and check if they have a project.json or a docker-compose.yml file
        if they have a project.json file, load the project from the file
        if they have a docker-compose.yml file, create a project from the file
        if they have both, load the project from the project.json file and update it with the docker-compose.yml file
        if they have neither, ignore the directory
        """
        os.makedirs(AGENT_COMPOSE_DIR, exist_ok=True)
        for project in os.listdir(AGENT_COMPOSE_DIR):
            project_dir = os.path.join(AGENT_COMPOSE_DIR, project)
            if os.path.isdir(project_dir):
                project_json = os.path.join(project_dir, "project.json")
                docker_compose = os.path.join(project_dir, "docker-compose.yml")
                if os.path.exists(project_json):
                    with open(project_json, "r") as f:
                        project_data = json.load(f)
                        p = DockerComposeProject(**project_data)
                        cls.add(p)
                elif os.path.exists(docker_compose):
                    p = DockerComposeProject.from_docker_compose(project, docker_compose)
                    cls.add(p)
                    pass
                else:
                    print(f"Skipping {project_dir}")

    @classmethod
    def add(cls, project) -> None:
        cls.projects[project.key] = project

    @classmethod
    def start(cls, key) -> DockerComposeProject:
        project = cls.projects[key]
        project.start()
        return project

    @classmethod
    def stop(cls, key) -> DockerComposeProject:
        project = cls.projects[key]
        project.stop()
        return project

    @classmethod
    def remove(cls, key) -> DockerComposeProject:
        project = cls.projects[key]
        project.remove()
        #del cls.projects[key]
        return project

    @classmethod
    def list_all(cls):
        return cls.projects.values()

    @classmethod
    def describe(cls, key) -> DockerComposeProject:
        return cls.projects[key]

    @classmethod
    def restart(cls, key) -> DockerComposeProject:
        project = cls.projects[key]
        project.restart()
        return project

    @classmethod
    def restart_all(cls):
        for project in cls.projects.values():
            project.restart()
        return cls.projects.values()
