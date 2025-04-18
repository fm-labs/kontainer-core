import os
import subprocess

from docker.constants import DEFAULT_TIMEOUT_SECONDS

from kontainer import settings
from kontainer.docker.dkr import get_docker_manager_cached
from kontainer.stacks import ContainerStack
from kontainer.util.subprocess_util import kwargs_to_cmdargs, load_envfile


class DockerComposeStack(ContainerStack):
    """
    Docker Compose container stack.

    This class is used to manage the lifecycle of a Docker Compose stack
    """

    def __init__(self, name, ctx_id, managed=False, config=None, **kwargs):
        super().__init__(name=name, ctx_id=ctx_id, managed=managed, config=config)
        self._dkr = get_docker_manager_cached(ctx_id)


    def _compose(self, cmd, **kwargs) -> bytes:
        """
        Run a docker compose command
        :param cmd: Command to run
        :param kwargs: Additional arguments to pass to docker compose
        :return:
        """
        if self.ctx_id == "local":
            return self._compose_local(cmd, **kwargs)
        else:
            return self._compose_remote(cmd, **kwargs)


    def _compose_remote(self, cmd, **kwargs) -> bytes:
        """
        Run a docker compose command on the remote docker host
        :param cmd: Command to run
        :param kwargs: Additional arguments to pass to docker compose
        :return:
        """
        compose_project_name = self.name
        compose_file_name = 'docker-compose.yml'
        remote_working_dir = "~/.kontainer"

        compose_args = dict()
        compose_args['project-name'] = self.name
        compose_args['project-directory'] = remote_working_dir
        compose_args['file'] = compose_file_name
        compose_args['progress'] = 'plain'
        try:
            pcmd = ((["docker-compose"]
                     + kwargs_to_cmdargs(compose_args))  # compose specific args
                    + [cmd]  # the compose command (up/down/...)
                    + kwargs_to_cmdargs(kwargs))  # additional command args
            print(f"RAW CMD: {pcmd}")
            print(f"CMD: {" ".join(pcmd)}")

            # environment variables for docker compose ON THE REMOTE HOST (!)
            renv = dict()
            # renv['PATH'] = os.getenv('PATH')
            # todo renv['DOCKER_HOST'] = 'unix:///var/run/docker.sock' # the docker host on the remote machine
            # todo renv['DOCKER_CONFIG'] = settings.DOCKER_CONFIG # the docker config on the remote machine
            renv['COMPOSE_PROJECT_DIRECTORY'] = remote_working_dir
            renv['COMPOSE_PROJECT_NAME'] = compose_project_name
            renv['COMPOSE_FILE'] = compose_file_name
            renv['PWD'] = remote_working_dir
            # renv['DOCKER_HOST'] = 'unix:///var/run/docker.sock'

            # todo Load .env file into 'renv'
            # env_file = os.path.join(KONTAINER_DATA_DIR, 'stacks', f'{self.name}.stack.env.production')
            # if os.path.exists(env_file):
            #     renv = load_envfile(env_file, renv)
            # print(f"ENV: {renv}")

            # p1 = subprocess.run(pcmd, cwd=working_dir, env=renv, capture_output=True)
            # print("STDOUT", p1.stdout)
            # print("STDERR", p1.stderr)
            #
            # if p1.returncode != 0:
            #     raise Exception(f"Error running command: {p1.stderr}")
            #
            # return p1.stdout
        except Exception as e:
            print(e)
            raise e



    def _compose_local(self, cmd, **kwargs) -> bytes:
        """
        Run a docker compose command locally

        :param cmd: Command to run
        :param kwargs: Additional arguments to pass to docker compose
        :return:
        """

        base_path = ""
        if self.config:
            base_path = self.config.get('base_path', "")

        working_dir = str(os.path.join(settings.KONTAINER_DATA_DIR, self.project_dir, base_path))
        if working_dir is None or not os.path.isdir(working_dir):
            return b"Stack working dir not found " + self.project_dir.encode("utf-8")

        compose_file = 'docker-compose.yml'
        if os.path.exists(os.path.join(working_dir, 'docker-compose.stack.yml')):
            compose_file = 'docker-compose.stack.yml'

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
            #todo penv['DOCKER_HOST'] = 'unix:///var/run/docker.sock'
            penv['DOCKER_CONFIG'] = settings.DOCKER_CONFIG
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


    # @property
    # def status(self) -> dict:
    #     """
    #     Get the status of the stack
    #     """
    #     status = dict({
    #         "name": self.name,
    #         "project_dir": self.project_dir,
    #         "managed": self.managed,
    #         "has_docker_compose": os.path.exists(os.path.join(self.project_dir, "docker-compose.yml")),
    #         "has_stack_file": os.path.exists(self.project_file),
    #         "has_stack": os.path.exists(self.project_dir)
    #     })
    #     return status
    #
    #
    # def exists(self) -> bool:
    #     if self.project_dir is None:
    #         return False
    #     return os.path.exists(self.project_dir)


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
    """
    Unmanaged Docker Compose stack.

    This class is used to manage the lifecycle of a Docker Compose stack
    that is not managed by the agent.
    """
    def __init__(self, name, ctx_id, config=None, **kwargs):
        super().__init__(name, ctx_id, managed=False, config=config)

        self.name = name
        self.managed = False
        self._meta = config  # will always be None

        if self._dkr.stack_exists(name):
            project_dir = self._dkr.get_stack_project_dir(name)
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
        containers: list = self._dkr.list_stack_containers(self.name)
        for container in containers:
            try:
                out += f"Starting container {container.id}\n".encode("utf-8")
                self._dkr.start_container(container.id)
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
        containers: list = self._dkr.list_stack_containers(self.name)
        for container in containers:
            try:
                out += f"Restarting container {container.id}\n".encode("utf-8")
                self._dkr.restart_container(container.id)
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
        containers: list = self._dkr.list_stack_containers(self.name)
        for container in containers:
            try:
                out += f"Stopping container {container.id}\n".encode("utf-8")
                self._dkr.stop_container(container.id)
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
        containers: list = self._dkr.list_stack_containers(self.name)
        for container in containers:
            try:
                out += f"Removing container {container.id}\n".encode("utf-8")
                self._dkr.remove_container(container.id)
            except Exception as e:
                print(f"Error removing container {container.id}: {e}")
                out += f"Error removing container {container.id}: {e}\n".encode("utf-8")
        return out
