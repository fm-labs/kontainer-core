
import os
import subprocess

from docker.constants import DEFAULT_TIMEOUT_SECONDS

from kstack.agent.docker.dkr import dkr
from kstack.agent.stacks import ContainerStack
from kstack.agent.util.subprocess_util import kwargs_to_cmdargs, load_envfile


class DockerComposeStack(ContainerStack):
    def __init__(self, name, managed=False, meta=None, **kwargs):
        super().__init__(name, managed=managed, meta=meta)

    def _compose(self, cmd, **kwargs) -> bytes:
        """
        Run a docker compose command
        :param cmd: Command to run
        :param kwargs: Additional arguments to pass to docker compose
        :return:
        """
        if self.project_dir is None or not self.exists():
            return b"Stack does not exist"

        working_dir = self.project_dir
        if self.meta:
            base_path = self.meta.get('base_path', "")
            working_dir = os.path.join(self.project_dir, base_path)

        compose_file = 'docker-compose.yml'
        if os.path.exists(os.path.join(working_dir, 'docker-compose.stack.yml')):
            compose_file = 'docker-compose.stack.yml'
        # if os.path.exists('docker-compose.override.yml'):
        #    compose_file = 'docker-compose.override.yml'

        compose_args = dict()
        compose_args['project-name'] = self.name
        compose_args['project-directory'] = working_dir
        compose_args['file'] = compose_file
        compose_args['progress'] = 'plain'
        try:
            pcmd = ((["docker-compose"]
                     + kwargs_to_cmdargs(compose_args))  # compose specific args
                    + [cmd]  # the compose command (up/down/...)
                    + kwargs_to_cmdargs(kwargs))  # additional command args
            print(f"RAW CMD: {pcmd}")
            print(f"CMD: {" ".join(pcmd)}")

            # penv = os.environ.copy()
            penv = dict()
            penv['PATH'] = os.getenv('PATH')
            penv['COMPOSE_PROJECT_DIRECTORY'] = working_dir
            penv['COMPOSE_PROJECT_NAME'] = self.name
            penv['COMPOSE_FILE'] = compose_file
            penv['PWD'] = working_dir
            # penv['DOCKER_HOST'] = 'unix:///var/run/docker.sock'

            # Load .env file into 'penv'
            env_file = os.path.join(working_dir, '.env')
            if os.path.exists(env_file):
                penv = load_envfile(env_file, penv)
            print(f"ENV: {penv}")

            p1 = subprocess.run(pcmd, cwd=working_dir, env=penv, capture_output=True)
            print("STDOUT", p1.stdout)
            print("STDERR", p1.stderr)

            if p1.returncode != 0:
                raise Exception(f"Error running command: {p1.stderr}")

            return p1.stdout
        except Exception as e:
            print(e)
            raise e

    @property
    def status(self) -> dict:
        """
        Get the status of the stack
        """
        status = dict({
            "name": self.name,
            "project_dir": self.project_dir,
            "managed": self.managed,
            "has_docker_compose": os.path.exists(os.path.join(self.project_dir, "docker-compose.yml")),
            "has_stack_file": os.path.exists(self.project_file),
            "has_stack": os.path.exists(self.project_dir)
        })
        return status

    # @property
    # def meta(self):
    #     # read the stack file contents
    #     meta = dict()
    #     if os.path.exists(self.project_file):
    #         with open(self.project_file, "r") as f:
    #             meta = json.load(f)
    #
    #     return meta

    def exists(self) -> bool:
        if self.project_dir is None:
            return False
        return os.path.exists(self.project_dir)

    def up(self, **kwargs) -> bytes:
        """
        Start the stack
        https://docs.docker.com/reference/cli/docker/compose/up/

        Runs docker compose up

        :param kwargs: Additional arguments to pass to docker compose up
        """
        print(f"Starting project {self.name} in {self.project_dir}")

        kwargs['detach'] = True if 'detach' not in kwargs else kwargs['detach']
        kwargs['build'] = True if 'build' not in kwargs else kwargs['build']
        kwargs['force-recreate'] = True if 'force-recreate' not in kwargs else kwargs['force-recreate']
        # kwargs['y'] = True if 'y' not in kwargs else kwargs['y'] # run non-interactively

        return self._compose("up", **kwargs)

    def down(self, **kwargs) -> bytes:
        """
        Remove the stack.

        Runs docker compose down

        :param kwargs: Additional arguments to pass to docker compose down
        """
        print(f"COMPOSE DOWN {self.name} in {self.project_dir}")

        kwargs['timeout'] = DEFAULT_TIMEOUT_SECONDS if 'timeout' not in kwargs else kwargs['timeout']
        return self._compose("down", **kwargs)

    def stop(self, **kwargs) -> bytes:
        """
        Stop the stack.

        Runs docker compose stop

        :param kwargs: Additional arguments to pass to docker compose stop
        """
        print(f"COMPOSE STOP {self.name} in {self.project_dir}")

        kwargs['timeout'] = DEFAULT_TIMEOUT_SECONDS if 'timeout' not in kwargs else kwargs['timeout']
        return self._compose("stop", **kwargs)

    def restart(self, **kwargs) -> bytes:
        print(f"COMPOSE RESTART {self.name} in {self.project_dir}")

        # Run docker compose restart
        kwargs['timeout'] = DEFAULT_TIMEOUT_SECONDS if 'timeout' not in kwargs else kwargs['timeout']
        return self._compose("restart", **kwargs)

    def destroy(self, **kwargs) -> bytes:
        # print(f"COMPOSE DESTROY {self.name} in {self.project_dir}")
        # No docker-specific destroy actions needed.
        # Just remove the project directory and the project file using the stack manager.
        return b"COMPOSE DESTROY: No docker-specific destroy actions executed."

    def ps(self, **kwargs) -> bytes:
        """
        Get the status of the stack

        Runs docker compose ps

        :param kwargs: Additional arguments to pass to docker compose ps
        """
        return self._compose("ps", **kwargs)




class UnmanagedDockerComposeStack(DockerComposeStack):
    def __init__(self, name, meta=None, **kwargs):
        super().__init__(name, managed=False, meta=meta)

        self.name = name
        self.managed = False
        self._meta = meta  # will always be None

        if dkr.stack_exists(name):
            project_dir = dkr.get_stack_project_dir(name)
            self.project_dir = project_dir
            self.project_file = None

        print(f"Unmanaged stack {self.name} initialized with project_dir {self.project_dir}")

    def __str__(self):
        return f"Unmanaged stack: {self.name}"


    def up(self, **kwargs) -> bytes:
        """
        Start the stack.

        If the stack is managed outside the agent, then only already created containers will be started.
        """
        out = b""
        containers: list = dkr.list_stack_containers(self.name)
        for container in containers:
            try:
                out += f"Starting container {container.id}\n".encode("utf-8")
                dkr.start_container(container.id)
            except Exception as e:
                print(f"Error starting container {container.id}: {e}")
                out += f"Error starting container {container.id}: {e}\n".encode("utf-8")
        return out


    def restart(self, **kwargs) -> bytes:
        """
        Restart the stack.

        If the stack is managed outside the agent, then just restart the containers
        """
        out = b""
        containers: list = dkr.list_stack_containers(self.name)
        for container in containers:
            try:
                out += f"Restarting container {container.id}\n".encode("utf-8")
                dkr.restart_container(container.id)
            except Exception as e:
                print(f"Error restarting container {container.id}: {e}")
                out += f"Error restarting container {container.id}: {e}\n".encode("utf-8")
        return out


    def stop(self, **kwargs) -> bytes:
        """
        Stop the stack.

        If the stack is managed outside the agent, then just stop the containers
        """
        out = b""
        containers: list = dkr.list_stack_containers(self.name)
        for container in containers:
            try:
                out += f"Stopping container {container.id}\n".encode("utf-8")
                dkr.stop_container(container.id)
            except Exception as e:
                print(f"Error stopping container {container.id}: {e}")
                out += f"Error stopping container {container.id}: {e}\n".encode("utf-8")
        return out


    def down(self, **kwargs) -> bytes:
        """
        Delete the stack.

        If the stack is managed outside the agent, then just stop the containers.
        Use 'destroy' to remove the unmanaged containers.
        """
        out = self.stop(**kwargs)
        out += "\n".encode("utf-8")
        out += "The unmanaged stack has been brought DOWN. Use DESTROY to permanently remove the unmanaged containers.\n".encode("utf-8")
        return out


    def destroy(self, **kwargs) -> bytes:
        """
        Destroy the stack.

        If the stack is managed outside the agent, then just delete the containers.
        The stack will disappear after all containers are removed.
        """
        out = b""
        containers: list = dkr.list_stack_containers(self.name)
        for container in containers:
            try:
                out += f"Removing container {container.id}\n".encode("utf-8")
                dkr.remove_container(container.id)
            except Exception as e:
                print(f"Error removing container {container.id}: {e}")
                out += f"Error removing container {container.id}: {e}\n".encode("utf-8")
        return out


    def exists(self) -> bool:
        """
        If a project directory has been set, then the stack exists
        """
        return self.project_dir is not None
