import paramiko

from kontainer.util.remote_utils import ssh_connect, exec_ssh_client_command, ssh_connect_sock, exec_ssh_sock_command


def rgit_ssh(ssh_config=None) -> paramiko.SSHClient:

    if ssh_config is None:
        ssh_config = {}

    # hostname = ssh_config.get('hostname')
    # username = ssh_config.get('username')
    # password = ssh_config.get('password')
    # private_key_file = ssh_config.get('private_key_file')
    # private_key_pass = ssh_config.get('private_key_pass')
    # private_key_pass_file = ssh_config.get('private_key_pass_file')
    #
    # if hostname is None or username is None:
    #     raise ValueError("SSH hostname and username are required")

    return ssh_connect(**ssh_config)


def rgit_clone(repo_url: str, dest: str, ssh_config, **kwargs) -> bytes:
    """
    Run a git clone command

    :param repo_url: Repository to clone
    :param ssh_config: SSH configuration
    :param dest: Destination directory on the remote server
    :param kwargs: Additional arguments to pass to git clone
    :return:
    """

    command = f"""
    # check if git command exists
    if ! command -v git &> /dev/null; then
        echo "git command not found"
        exit 1
    fi
    mkdir -p {dest} &&
    cd {dest} &&
    if [ ! -d "{dest}" ]; then
        git clone {repo_url} {dest}
    else
        cd {dest} && git pull
    fi
    """

    # Using a ssh transport here, because we want agent forwarding
    ssh_sock = ssh_connect_sock(**ssh_config)
    try:
        stdout, stderr, rc = exec_ssh_sock_command(ssh_sock, command, agent_forward=True)
        if rc != 0:
            raise ValueError(f"Remote cloning repository exit with non-zero exit code: {rc}")
        return stdout
    finally:
        ssh_sock.close()


def rgit_pull_head(working_dir: str, ssh_config, **kwargs) -> bytes:
    """
    Pull the latest changes from the remote repository

    :param working_dir: Working directory
    :param ssh_config: SSH configuration
    :param kwargs: Additional arguments to pass to git pull
    :return:
    """
    cur_head = rgit(["rev-parse", "--abbrev-ref", "HEAD"], ssh_config, working_dir=working_dir, timeout=10)
    cur_head_str = cur_head.decode("utf-8").strip()
    print(f"Current HEAD: {cur_head_str}")
    if cur_head_str is None or cur_head_str == "":
        raise ValueError("Failed to get current HEAD")

    return rgit(["pull", "origin", cur_head_str], ssh_config, working_dir=working_dir, **kwargs)


def rgit(args: list, ssh_config: dict, **kwargs) -> bytes:
    """
    Run a git command

    :param ssh_config: SSH configuration
    :param args: Arguments to pass to git
    :param kwargs: Additional arguments to pass to git
    :return:
    """
    out = b""
    print("rgit", ssh_config, args, **kwargs)

    return out