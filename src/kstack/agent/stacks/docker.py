import os
import subprocess

from kstack.agent import settings
from kstack.agent.stacks import ContainerStack


class DockerComposeStack(ContainerStack):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        #self.attrs = {}
        self.project_dir = os.path.join(settings.AGENT_DATA_DIR, 'stacks', self.name)
        self.managed = True


    @staticmethod
    def _map_kwargs(kwargs):
        """
        Map kwargs to docker compose arguments
        :param kwargs:
        :return:
        """
        args = []
        for k, v in kwargs.items():
            if v is not None and v is not False:
                if len(k) == 1 and type(v) is bool:
                    args.append(f"-{k}")
                    continue

                args.append(f"--{k.replace('_', '-')}")
                if type(v) is not bool:
                    args.append(str(v))
        return args


    def _compose(self, cmd, **kwargs) -> bytes:
        """
        Run a docker compose command
        :param cmd: Command to run
        :param kwargs: Additional arguments to pass to docker compose
        :return:
        """
        compose_args = {}
        #compose_args['project-directory'] = self.project_dir
        compose_args['project-name'] = self.name
        #compose_args['file'] = 'docker-compose.yml'
        #compose_args['progress'] = 'auto'

        try:
            pcmd = ((["docker", "compose"]
                    + self._map_kwargs(compose_args)) # compose specific args
                    + [cmd] # the compose command (up/down/...)
                    + self._map_kwargs(kwargs)) # additional command args
            print(f"Running command: {pcmd}")
            print(f"CMD: {" ".join(pcmd)}")

            #penv = os.environ.copy()
            penv = dict()
            penv['PATH'] = os.getenv('PATH')
            penv['COMPOSE_PROJECT_NAME'] = self.name
            penv['COMPOSE_FILE'] = 'docker-compose.yml'
            penv['COMPOSE_PROJECT_DIRECTORY'] = self.project_dir
            penv['PWD'] = self.project_dir
            #penv['DOCKER_HOST'] = 'unix:///var/run/docker.sock'

            # Load .env file into 'penv'
            env_file = os.path.join(self.project_dir, '.env')
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f.readlines():
                        if line.strip() and not line.startswith('#'):
                            k, v = line.split('=', 1)
                            penv[k] = v.strip()

            print(f"Environment: {penv}")

            p1 = subprocess.run(pcmd, cwd=self.project_dir, env=penv, capture_output=True)
            print("STDOUT", p1.stdout)
            print("STDERR", p1.stderr)

            if p1.returncode != 0:
                raise Exception(f"Error running command: {p1.stderr}")

            return p1.stdout
        except Exception as e:
            print(e)
            raise e


    def start(self, **kwargs):
        """
        Start the stack
        https://docs.docker.com/reference/cli/docker/compose/up/

        :param kwargs: Additional arguments to pass to docker compose up
        """
        print(f"Starting project {self.name} in {self.project_dir}")

        kwargs['detach'] = True if 'detach' not in kwargs else kwargs['detach']
        kwargs['build'] = True if 'build' not in kwargs else kwargs['build']
        kwargs['force-recreate'] = True if 'force-recreate' not in kwargs else kwargs['force-recreate']
        #kwargs['y'] = True if 'y' not in kwargs else kwargs['y'] # run non-interactively

        return self._compose("up", **kwargs)


    def stop(self, **kwargs):
        """
        Stop the stack.

        Runs docker compose stop

        :param kwargs: Additional arguments to pass to docker compose stop
        """
        print(f"Stopping project {self.name} in {self.project_dir}")

        kwargs['timeout'] = 30 if 'timeout' not in kwargs else kwargs['timeout']
        return self._compose("stop", **kwargs)


    def remove(self, **kwargs):
        """
        Remove the stack.

        Runs docker compose down

        :param kwargs: Additional arguments to pass to docker compose down
        """
        print(f"Removing project {self.name} in {self.project_dir}")

        kwargs['timeout'] = 30 if 'timeout' not in kwargs else kwargs['timeout']
        return self._compose("down", **kwargs)


    def restart(self, **kwargs):
        print(f"Restarting project {self.name} in {self.project_dir}")

        # Run docker compose restart
        kwargs['timeout'] = 30 if 'timeout' not in kwargs else kwargs['timeout']
        return self._compose("restart", **kwargs)


    def serialize(self):
        return {
            "name": self.name,
            "project_dir": self.project_dir,
            #"attrs": self.attrs,
            "managed": self.managed
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
