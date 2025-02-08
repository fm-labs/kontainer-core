import os
import subprocess

from kstack.agent import settings
from kstack.agent.stacks import ContainerStack


class DockerComposeStack(ContainerStack):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.attrs = {}
        self.project_dir = os.path.join(settings.AGENT_DATA_DIR, 'stacks', self.name)

    def start(self):
        print(f"Starting project {self.name} in {self.project_dir}")

        # Run docker compose up
        try:
            cmd = ["docker", "compose", "up", "-d"]
            p1 = subprocess.run(cmd, cwd=self.project_dir, env=os.environ, capture_output=True)
            print(p1.stdout)
        except Exception as e:
            print(e)
            raise e

    def stop(self):
        print(f"Stopping project {self.name} in {self.project_dir}")

        # Run docker compose stop
        try:
            cmd = ["docker", "compose", "stop"]
            p1 = subprocess.run(cmd, cwd=self.project_dir, env=os.environ, capture_output=True)
            print(p1.stdout)
        except Exception as e:
            print(e)
            raise e

    def remove(self):
        print(f"Removing project {self.name} in {self.project_dir}")

        # Run docker compose stop
        try:
            cmd = ["docker", "compose", "down"]
            p1 = subprocess.run(cmd, cwd=self.project_dir, env=os.environ, capture_output=True)
            print(p1.stdout)
        except Exception as e:
            print(e)
            raise e

    def restart(self):
        print(f"Restarting project {self.name} in {self.project_dir}")

        # Run docker compose restart
        try:
            cmd = ["docker", "compose", "restart"]
            p1 = subprocess.run(cmd, cwd=self.project_dir, env=os.environ, capture_output=True)
            print(p1.stdout)
        except Exception as e:
            print(e)
            raise e

    def serialize(self):
        return {
            "name": self.name,
            "project_dir": self.project_dir,
            "attrs": self.attrs
        }

    # @classmethod
    # def from_docker_compose(cls, project, docker_compose_path):
    #     # Read the file path contents
    #     with open(docker_compose_path, "r") as f:
    #         contents = f.read()
    #
    #     p = cls(project, contents)
    #     return p
    #
    # @classmethod
    # def from_json(cls, data):
    #     return cls(data['name'], data['attrs'])
