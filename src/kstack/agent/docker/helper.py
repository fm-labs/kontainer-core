import os
import subprocess

import paramiko
from docker import DockerClient


def run_docker_local(cmd: str|list):
    """
    Run Docker Command
    """
    try:
        return subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        return e.output


def run_docker_remote(host: str, cmd: str|list):
    """
    Run Docker via SSH Command
    """
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR {host} {cmd}"

    # use paramiko to run ssh command
    paramiko_ssh = paramiko.SSHClient()
    paramiko_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    paramiko_ssh.connect(host)
    stdin, stdout, stderr = paramiko_ssh.exec_command(ssh_cmd)

    #errors = stderr.read()
    return stdout.read()


def get_docker_volume_size(client: DockerClient, volume_name):

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