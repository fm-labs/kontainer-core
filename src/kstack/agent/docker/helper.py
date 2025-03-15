import os
import subprocess

import docker

from docker import DockerClient


def get_docker_volume_size(client: DockerClient, volume_name: str):
    """
    Get Docker Volume Size.
    Uses the 'du' command to calculate the size of the directory.
    This is a Unix-based solution and may not work on Windows.
    -> Has bad performance for large volumes.


    :param client: DockerClient
    :param volume_name: str
    """

    # Get the volume details
    volume = client.volumes.get(volume_name)

    # Path to the volume's mount point on the host
    mount_point = volume.attrs['Mountpoint']

    # Use the 'du' command to calculate the size of the directory
    # This works on Unix-based systems (Linux/MacOS)
    size_command = f"du -s {mount_point} | cut -f1"

    volume_size = 0
    try:
        # volume_size = subprocess.check_output(size_command, shell=True).decode().strip()
        output = os.popen(size_command).read().strip()
        if output:
            volume_size = int(output)
    except subprocess.CalledProcessError as e:
        print(f"Failed to get_volume_size for volume {volume_name}: {e}")
        volume_size = -1

    return volume_size


def get_containers_using_volume(client: DockerClient, volume_name: str):
    """
    Get Containers Using a Volume.

    :param client: DockerClient
    :param volume_name: str
    :return: list
    """
    containers_using_volume = []

    # Iterate through all running containers
    for container in client.containers.list(all=True):  # 'all=True' includes stopped containers
        container_info = container.attrs
        mounts = container_info.get("Mounts", [])

        # Check if the volume is in the container's mounts
        for mount in mounts:
            if mount.get("Name") == volume_name:
                containers_using_volume.append(container.name)

    return containers_using_volume


def get_volumes_attached_to_container(client: DockerClient, container_name: str):
    """
    List Volumes for a Given Container.

    :param client: DockerClient
    :param container_name: str
    :return: list
    """
    try:
        container = client.containers.get(container_name)
        mounts = container.attrs.get("Mounts", [])
        volumes = [mount["Name"] for mount in mounts if "Name" in mount]

        return volumes
    except docker.errors.NotFound:
        return f"Container '{container_name}' not found."


def map_volumes_to_containers(client: DockerClient):
    """
    Generate a full map of all volumes and which containers are using them.

    Returns: dict
    """
    volume_usage = {}

    # Iterate through all containers
    for container in client.containers.list(all=True):
        container_name = container.name
        mounts = container.attrs.get("Mounts", [])

        for mount in mounts:
            if "Name" in mount:
                volume_name = mount["Name"]
                if volume_name not in volume_usage:
                    volume_usage[volume_name] = []
                volume_usage[volume_name].append(container_name)

    return volume_usage