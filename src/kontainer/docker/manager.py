import json
from sys import api_version

import docker
from docker.models.containers import Container
from docker.models.images import Image
from docker.models.networks import Network
from docker.models.volumes import Volume

from kontainer import settings
from kontainer.docker.helper import get_docker_volume_size
from kontainer.error import ContainerNotFoundError


class DockerManager:
    """
    A Class to manage Docker resources via Python Docker SDK
    """

    def __init__(self, base_url: str = None, use_ssh_client: bool = False):
        """
        Initialize Python Docker Client
        """
        if base_url is None:
            self.client = docker.from_env(use_ssh_client=use_ssh_client)
        else:
            self.client = docker.DockerClient(base_url=base_url, use_ssh_client=use_ssh_client)

    def ping(self) -> bool:
        """
        Ping Docker Engine

        :return: bool
        """
        return self.client.ping()


    def version(self) -> str:
        """
        Get Docker Version Info

        :return: dict
        """
        return self.client.version(api_version=True)


    def info(self) -> dict:
        """
        Get Docker Client Info as dict
        """
        info = self.client.info()
        info_dict = json.loads(json.dumps(info))
        return info_dict


    def registry_login(self, registry, username, password) -> dict:
        """
        Login to Docker Registry

        :param registry: Registry URL
        :param username: Username
        :param password: Password
        :return: dict The response from the login request
        """
        print(f"Logging in to Docker Registry at {registry}. Using docker config at {settings.DOCKER_CONFIG}")
        result = self.client.login(registry=registry,
                                   username=username,
                                   password=password,
                                   dockercfg_path=settings.DOCKER_CONFIG)
        return result



    def start_container(self, key) -> Container:
        """
        Start Container

        :param key: id from Container on Docker
        :return: Container Object
        """
        if not self.container_exists(key):
            raise ContainerNotFoundError(key)

        container = self.client.containers.get(key)

        # Unpause if paused
        if container.status == 'paused':
            container.unpause()
        # Skip if already running
        elif container.status == 'running':
            pass
        else:
            container.start()
        return container

    def pause_container(self, key) -> Container:
        """
        Pause Container

        :param key: id from Container on Docker
        :return: Container Object
        """
        if not self.container_exists(key):
            raise ContainerNotFoundError(key)

        container = self.client.containers.get(key)
        container.pause()
        return container

    def remove_container(self, key) -> Container:
        """
        Remove Container

        :param key: id from Container on Docker
        :return: Container Object
        """
        if not self.container_exists(key):
            raise ContainerNotFoundError(key)

        container = self.client.containers.get(key)
        container.stop()
        container.remove()
        return container


    def stop_container(self, key) -> Container:
        """
        Stop Container

        :param key: id from Container on Docker
        :return: Container Object
        """
        if not self.container_exists(key):
            raise ContainerNotFoundError(key)

        container = self.client.containers.get(key)
        container.stop()
        return container


    def get_container(self, key) -> Container:
        """
        Get Container

        :param key: id from Container on Docker
        :return: Container Object
        """
        if not self.container_exists(key):
            raise ContainerNotFoundError(key)

        container = self.client.containers.get(key)
        return container


    def list_containers(self) -> list[Container]:
        """
        Get All Containers

        :return: list
        """
        all_containers = self.client.containers.list(all=True)
        return all_containers


    def restart_container(self, key) -> Container:
        """
        Restart Container

        :param key: id from Container on Docker
        :return: Container Object
        """
        if not self.container_exists(key):
            raise ContainerNotFoundError(key)

        container = self.client.containers.get(key)
        container.restart()
        return container


    def restart_all_containers(self) -> list[Container]:
        """
        Restart All Containers

        :return: list
        """
        all_containers = self.client.containers.list(filters={'status': 'running'})
        for container in all_containers:
            container.restart()
        return all_containers


    def container_exists(self, key) -> bool:
        """
        Check if Container Exists

        :param key: id from Container on Docker
        :return: bool
        """
        return True if self.client.containers.get(key) else False


    def run_container(self, image_name, **kwargs) -> Container:
        """
        Run Container

        :param image_name: Image Name
        :param kwargs: Additional Arguments
        :return: Container Object
        """
        container = self.client.containers.run(image_name, **kwargs)
        return container


    def create_container(self, image_name, cmd=None, **kwargs) -> Container:
        """
        Create Container

        :param image_name: Image Name
        :param cmd: Command
        :param kwargs: Additional Arguments
        :return: Container Object
        """
        container = self.client.containers.create(image_name, cmd, **kwargs)
        return container


    def get_container_logs(self, key, **kwargs) -> list[str]:
        """
        Get Container Logs

        :param key: id from Container on Docker
        :return: list
        """
        if not self.container_exists(key):
            raise ContainerNotFoundError(key)

        container_kwargs = {
            'stream': False,
            'tail': 500,
            'follow': False,
            'timestamps': True
        }
        container = self.client.containers.get(key)
        logs = list()
        log_bytes = container.logs(**container_kwargs, **kwargs)
        for log in log_bytes.decode().split('\n'):
            logs.append(log)
        return logs


    def exec_container_cmd(self, key, cmd) -> list[str]:
        """
        Execute Command in Container

        :param key: id from Container on Docker
        :param cmd: Command
        :return: list
        """
        if not self.container_exists(key):
            raise ContainerNotFoundError(key)

        container = self.client.containers.get(key)
        (exit_code, output) = container.exec_run(cmd, detach=False, stream=False, workdir="/")

        lines = output.decode().split('\n')
        return lines


    def list_stack_containers(self, stack_name) -> list[Container]:
        """
        Get Containers for Stack

        :param stack_name: Stack Name
        :return: list
        """
        # Get all containers (running + stopped)
        containers = self.client.containers.list(all=True,
                                                 filters={"label": f"com.docker.compose.project={stack_name}"})

        return containers


    def stack_exists(self, stack_name) -> bool:
        """
        Check if Stack Exists

        :param stack_name: Stack Name
        :return: bool
        """

        return len(self.list_stack_containers(stack_name)) > 0


    def get_stack_project_dir(self, stack_name) -> str | None:
        """
        Get Project Directory for Stack

        :param stack_name: Stack Name
        :return: str
        """
        containers = self.list_stack_containers(stack_name)
        if len(containers) == 0:
            return None

        container = containers[0]
        project_dir = container.attrs['Config']['Labels']['com.docker.compose.project.working_dir']
        return project_dir


    def list_images(self) -> list[Image]:
        """
        Get Images

        :return: Dictionary [id, tags, labels]
        """
        all_containers = self.client.images.list(all=True)
        return all_containers


    def pull_image(self, image_name) -> Image:
        """
        Pull Image

        :param image_name: Image Name
        :return: dict
        """
        image = self.client.images.pull(image_name)
        return image


    def get_image(self, key) -> Image:
        """
        Inspect Image

        :param key: id from Image on Docker
        :return: dict
        """
        image = self.client.images.get(key)
        return image


    def remove_image(self, key) -> Image | None:
        """
        Remove Image

        :param key: id from Image on Docker
        :return: dict
        """
        image = self.client.images.get(key)
        if image is None:
            return None

        image.remove()
        return image


    def list_volumes(self, check_in_use=False, check_size=False) -> list[Volume]:
        """
        Get Volumes

        :return: Dictionary [id, tags, labels]
        """
        all_volumes = self.client.volumes.list()

        if check_in_use:
            containers = self.client.containers.list(all=True)
            def _map_in_use(volume):
                related_containers = []
                for c in containers:
                    for m in c.attrs['Mounts']:
                        if m['Type'] == "volume" and m['Name'] is not None and volume.attrs['Name'] == m['Name']:
                            related_containers.append(c.attrs['Name'])
                            break

                volume.attrs['_InUse'] = len(related_containers) > 0
                volume.attrs['_ContainerIds'] = related_containers
                return volume
            all_volumes = list(map(lambda x: _map_in_use(x), all_volumes))

        if check_size:
            def _map_size(volume):
                volume.attrs['_Size'] = get_docker_volume_size(self.client, volume.attrs['Name'])
                return volume
            all_volumes = list(map(lambda x: _map_size(x), all_volumes))

        return all_volumes


    def get_volume(self, key) -> Volume:
        """
        Get Volume

        :param key: id from Volume on Docker
        :return: Volume Object
        """
        volume = self.client.volumes.get(key)
        return volume


    def get_volume_size(self, volume_name):
        """
        Get Volume Size using docker helper

        :param volume_name: Volume Name
        :return: str
        """
        return get_docker_volume_size(self.client, volume_name)


    def remove_volume(self, key) -> Volume | None:
        """
        Remove Volume

        :param key: id from Volume on Docker
        :return: Volume Object
        """
        volume = self.client.volumes.get(key)
        if volume is None:
            return None

        volume.remove()
        return volume


    def list_networks(self) -> list[Network]:
        """
        Get Networks

        :return: list
        """
        all_networks = self.client.networks.list()
        return all_networks


    def get_network(self, key) -> Network:
        """
        Get Network

        :param key: id from Network on Docker
        :return: Network Object
        """
        network = self.client.networks.get(key)
        return network