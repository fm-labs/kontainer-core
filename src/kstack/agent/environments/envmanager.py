import json
import os

from kstack.agent import settings


class KstackEnvironment:

    def __init__(self, remote_host, remote_user=None, remote_ssh_key=None, remote_ssh_port=22,
                 description=None):

        self.remote_host = remote_host
        self.remote_user = remote_user
        self.remote_ssh_key = remote_ssh_key
        self.remote_ssh_port = remote_ssh_port
        self.description = description


    def __str__(self):
        return f"{self.remote_host}"


    def __repr__(self):
        return f"{self.remote_host}"


    def to_dict(self):
        return {
            "remote_host": self.remote_host,
            "remote_user": self.remote_user,
            "remote_ssh_key": self.remote_ssh_key,
            "remote_ssh_port": self.remote_ssh_port,
            "description": self.description
        }


class EnvManager:
    envs = list()

    @classmethod
    def enumerate_environments(cls) -> list:
        cls.envs = list()

        # always add local machine
        localenv = KstackEnvironment("localhost")
        cls.envs.append(localenv)

        # lookup other environments using the available env enumerators
        # built-in enumerator: find 'env.json' files in subdirectories of the data/environments directory
        envs_base_dir = f"{settings.AGENT_DATA_DIR}/environments"
        os.makedirs(envs_base_dir, exist_ok=True)

        for env_dir in os.listdir(envs_base_dir):
            if os.path.isdir(f"{envs_base_dir}/{env_dir}"):
                env_file = f"{envs_base_dir}/{env_dir}/env.json"
                if os.path.exists(env_file):
                    # with open(env_file, "r") as f:
                    #     env_data = json.load(f)
                    #     env = KstackEnvironment(env_data["remote_host"])
                    #     cls.envs.append(env)
                    cls.envs.append(KstackEnvironment(env_dir))

        return cls.envs


    @classmethod
    def list_environments(cls) -> list:
        return cls.envs


    @classmethod
    def create(cls, env: KstackEnvironment) -> KstackEnvironment:
        # check if env already exists
        for _env in cls.envs:
            if _env.remote_host == env.remote_host:
                raise Exception(f"Environment with remote_host {env.remote_host} already exists")

        # create the environment directory and save the env.json file
        env_dir = f"{settings.AGENT_DATA_DIR}/environments/{env.remote_host}"
        os.makedirs(env_dir, exist_ok=True)

        env_file = f"{env_dir}/env.json"
        with open(env_file, "w") as f:
            json.dump(env.to_dict(), f, indent=4)

        cls.envs.append(env)
        return env


    @classmethod
    def get(cls, remote_host) -> KstackEnvironment | None:
        for env in cls.envs:
            if env.remote_host == remote_host:
                return env
        return None


    @classmethod
    def remove(cls, remote_host) -> KstackEnvironment | None:
        for env in cls.envs:
            if env.remote_host == remote_host:
                # just rename the env.json file to env.deleted.json
                env_dir = f"{settings.AGENT_DATA_DIR}/environments/{env.remote_host}"
                os.rename(f"{env_dir}/env.json", f"{env_dir}/env.deleted.json")

                cls.envs.remove(env)
                return env
        return None


    @classmethod
    def reset(cls):
        cls.envs = list()


    # @classmethod
    # def get_by_id(cls, id) -> KstackEnvironment:
    #     for env in cls.envs:
    #         if env.id == id:
    #             return env
    #     return None