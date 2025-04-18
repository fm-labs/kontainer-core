import socket

import paramiko
from paramiko.client import SSHClient


def ssh_connect(hostname, username, password=None,
                private_key_file=None, private_key_pass=None, private_key_pass_file=None) -> SSHClient:
    """
    Connect to a remote server using SSH.

    :param hostname: The hostname or IP address of the remote server.
    :param username: The username to use for the SSH connection.
    :param password: The password for the SSH connection (optional). Not recommended to use.
    :param private_key_file: The path to the private key file (optional).
    :param private_key_pass: The passphrase for the private key (optional). Not recommended to use.
    :param private_key_pass_file: The path to the file containing the passphrase for the private key (optional).
    :return: An SSH client object connected to the remote server.
    """
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    key_filename = None
    key_passphrase = None
    if private_key_file:
        key_filename = private_key_file
        key_passphrase = None
        if private_key_pass_file:
            with open(private_key_pass_file, 'r') as f:
                key_passphrase = f.read().strip()
        else:
            key_passphrase = private_key_pass

    ssh.connect(hostname,
                username=username, password=password,
                key_filename=key_filename, passphrase=key_passphrase)
    return ssh


def ssh_connect_sock(hostname, username, password=None,
                     private_key_file=None, private_key_pass=None,
                     private_key_pass_file=None) -> paramiko.transport.Transport:
    """
    Connect to a remote server using SSH and return a Transport object.

    :param hostname: The hostname or IP address of the remote server.
    :param username: The username to use for the SSH connection.
    :param password: The password for the SSH connection (optional). Not recommended to use.
    :param private_key_file: The path to the private key file (optional).
    :param private_key_pass: The passphrase for the private key (optional). Not recommended to use.
    :param private_key_pass_file: The path to the file containing the passphrase for the private key (optional).
    :return: An SSH client object connected to the remote server.
    """
    print(f"Connecting to {hostname}...")
    sock = paramiko.Transport((hostname, 22))

    pkey = None
    if private_key_file:
        if private_key_pass_file:
            with open(private_key_pass_file, 'r') as f:
                key_passphrase = f.read().strip()
        else:
            key_passphrase = private_key_pass

        pkey = paramiko.RSAKey.from_private_key_file(private_key_file, password=key_passphrase)

    sock.connect(username=username, password=password, pkey=pkey, hostkey=None)
    return sock


def exec_ssh_client_command(ssh: SSHClient, command, environment=None, timeout=None, fail_on_error=False, verbose=False) -> tuple[bytes,bytes,int] | None:
    """
    Execute a command on the remote server using SSH.

    :param ssh: The SSH client object.
    :param command: The command to execute on the remote server.
    :param environment: A dictionary of environment variables to set for the command.
    :param timeout: The timeout for the command execution.
    :param fail_on_error: If True, raise an exception if the command fails (has stderr output).
    :param verbose: If True, print the command before executing it.
    :return: The output of the command. Tuple of (stdout, stderr, exit_code).
    """
    try:
        print(f"Executing command on remote: {command}")

        if environment is None:
            environment = dict()

        environment["KONTAINER_REMOTE_ENV"] = "1"
        environment["KONTAINER_REMOTE_UTILS_VERSION"] = "0.1.0"
        environment["KONTAINER_REMOTE_HOME"] = "~/.kontainer"
        # environment["KONTAINER_REMOTE_GIT_BIN"] = "/usr/bin/git"
        # environment["KONTAINER_REMOTE_DOCKER_BIN"] = "/usr/bin/docker"

        if verbose:
            command = f"""
            set -x
            {command}
            """

        if fail_on_error:
            command = f"""
            set -e
            {command}
            """

        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout, environment=environment)

        # Wait for command to finish and get the exit status
        exit_code = stdout.channel.recv_exit_status()

        stdout_bytes = stdout.read()
        stderr_bytes = stderr.read()
        print(stdout_bytes.decode())

        if exit_code != 0 and fail_on_error:
            raise Exception(f"Command failed with non-zero exit code: {exit_code}")

        return stdout_bytes, stderr_bytes, exit_code

    except socket.timeout as e:
        print(f"❌ Command timed out after {timeout} seconds.")
        raise e

    except Exception as e:
        print(f"❌ Command failed: {e}")
        raise e

    finally:
        # ssh.close()
        pass


def exec_ssh_sock_command(sock: paramiko.transport.Transport, command, environment=None, timeout=None,
                          agent_forward=False, fail_on_error=False, verbose=False) -> tuple[bytes,bytes,int] | None:
    """
    Execute a command on the remote server using SSH Transport.
    This is a lower-level interface than exec_ssh_client_command.
    This is useful for executing commands on a remote server using an existing SSH Transport object.
    Additionally, it allows for agent forwarding.

    :param sock: The SSH Transport object.
    :param command: The command to execute on the remote server.
    :param environment: A dictionary of environment variables to set for the command.
    :param timeout: The timeout for the command execution.
    :param agent_forward: If True, enable agent forwarding on the channel.
    :param fail_on_error: If True, raise an exception if the command fails (has stderr output).
    :param verbose: If True, print the command before executing it.
    :return: The output of the command. Tuple of (stdout, stderr, exit_code).
    """

    # Create a new session channel
    session = sock.open_session()
    try:
        # 🔑 Enable agent forwarding on this channel
        if agent_forward:
            paramiko.agent.AgentRequestHandler(session)

        print(f"Executing command on remote: {command}")

        if environment is None:
            environment = dict()
        environment["KONTAINER_REMOTE_ENV"] = "1"
        environment["KONTAINER_REMOTE_UTILS_VERSION"] = "0.1.0"
        environment["KONTAINER_REMOTE_HOME"] = "~/.kontainer"
        # environment["KONTAINER_REMOTE_GIT_BIN"] = "/usr/bin/git"
        # environment["KONTAINER_REMOTE_DOCKER_BIN"] = "/usr/bin/docker"

        if verbose:
            command = f"""
            set -x
            {command}
            """

        if fail_on_error:
            command = f"""
            set -e
            {command}
            """

        session.exec_command(command)

        # Wait for command to finish with a timeout
        if session.recv_ready() or session.recv_stderr_ready():
            # Already ready — no need to wait
            pass
        elif timeout is not None and timeout > 0:
            session.settimeout(timeout)

        # Wait until command finishes
        exit_code = session.recv_exit_status() # Blocks

        stdout = session.makefile('rb')
        stderr = session.makefile_stderr('rb')

        stdout_bytes = stdout.read()
        stderr_bytes = stderr.read()
        print(stdout_bytes.decode())
        print(f"Error: {stderr_bytes.decode()}")

        if exit_code != 0 and fail_on_error:
            raise Exception(f"Command failed with non-zero exit code: {exit_code}")

        return stdout_bytes, stderr_bytes, exit_code

    except socket.timeout as e:
        print(f"❌ Command timed out after {timeout} seconds.")
        raise e
    except Exception as e:
        print(f"❌ Command failed: {e}")
        raise e

    finally:
        session.close()


def exec_remote_command(hostname: str, username:str, cmd: str | list):
    """
    Invoke Docker Command via SSH on a Remote Host (Blocking)
    """
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR {username}@{hostname} {cmd}"

    # use paramiko to run ssh command
    paramiko_ssh = paramiko.SSHClient()
    paramiko_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    paramiko_ssh.connect(hostname)
    stdin, stdout, stderr = paramiko_ssh.exec_command(ssh_cmd)

    #errors = stderr.read()
    return stdout.read()
