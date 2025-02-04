import os
import subprocess

from .. import settings

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


class ProjectManager:
    projects = {}

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
