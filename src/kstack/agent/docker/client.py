# IMPORTS
import docker


# DOCKER CLIENT CLASS
class DockerMgmtClient:
    """
    A Class to manage Docker Containers
    """

    def __init__(self, base_url: str = None):
        if base_url is None:
            self.docker = docker.from_env(use_ssh_client=True)
        else:
            self.docker = docker.DockerClient(base_url=base_url)

    def start_container(self, key):
        """
        Start Container

        :param key: id from Container on Docker
        :return: dict
        """
        if not self.container_exists(key):
            return

        container = self.docker.containers.get(key)
        container.start()
        return container

    def remove_container(self, key):
        """
        Remove Container

        :param key: id from Container on Docker
        :return: dict
        """
        if not self.container_exists(key):
            return

        container = self.docker.containers.get(key)
        container.stop()
        container.remove()

        return container

    def stop_container(self, key):
        """
        Stop Container

        :param key: id from Container on Docker
        :return: dict
        """
        if not self.container_exists(key):
            return

        container = self.docker.containers.get(key)
        container.stop()

        return container

    def list_images(self):
        """
        Get Images

        :return: Dictionary [id, tags, labels]
        """
        all_containers = self.docker.images.list(all=True)
        return all_containers

    def get_container(self, key):
        """
        Get Container

        :param key: id from Container on Docker
        :return: dict
        """
        if not self.container_exists(key):
            return

        container = self.docker.containers.get(key)
        return container

    def list_containers(self):
        """
        Get All Containers

        :return: dict
        """
        all_containers = self.docker.containers.list(all=True)
        return all_containers

    # RESTARTING CONTAINER
    def restart_container(self, key):
        """
        Restart Container

        :param key: id from Container on Docker
        :return: dict
        """
        if not self.container_exists(key):
            return

        container = self.docker.containers.get(key)
        return container

    # RESTARTING ALL CONTAINERS
    def restart_all_containers(self):
        """
        Restart All Containers

        :return: dict
        """
        all_containers = self.docker.containers.list(filters={'status': 'running'})
        for container in all_containers:
            container.restart()
        return all_containers


    def container_exists(self, key):
        return True if self.docker.containers.get(key) else False


    def list_volumes(self):
        """
        Get Volumes

        :return: Dictionary [id, tags, labels]
        """
        all_volumes = self.docker.volumes.list()
        return all_volumes


    def list_networks(self):
        """
        Get Networks

        :return: Dictionary [id, tags, labels]
        """
        all_networks = self.docker.networks.list()
        return all_networks