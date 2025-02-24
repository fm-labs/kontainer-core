import os

from kstack.agent.admin.credentials import private_key_exists
from kstack.agent.stacks import ContainerStack
from kstack.agent.util.git_util import git_clone, git_update


def sync_stack(stack: ContainerStack) -> bytes:
    meta = stack.meta
    if meta is None:
        raise ValueError("No metadata found")

    repo = meta.get("repository", None)
    if repo is not None:
        out = _sync_repo(stack, repo)
        return out

    compose_url = meta.get("compose_url", None)
    if compose_url is not None:
        out = _sync_compose_url(stack, compose_url)
        return out

    return b""

def _get_ssh_key_for_repo(repo: dict):
    is_private = repo.get("private", False)
    if not is_private:
        return None

    ssh_private_key = repo.get("ssh_private_key", '')
    ssh_private_key_id = repo.get("ssh_private_key_id", '')

    if ssh_private_key is None or ssh_private_key == '':
        if ssh_private_key_id is None or ssh_private_key_id == '':
            raise ValueError("Private repository requires an SSH private key")

        # triple check the key exists
        _key_file = private_key_exists(ssh_private_key_id)
        if (_key_file is None
                or _key_file is False
                or _key_file == ''
                or not os.path.exists(_key_file)):
            raise ValueError(f"SSH private key {ssh_private_key_id} not found")
        ssh_private_key = _key_file

    return ssh_private_key

def _sync_repo(stack: ContainerStack, repo: dict):

    repo_url = repo.get("url", "")
    if repo_url is None or repo_url == "":
        raise ValueError("Repository URL not provided")

    ssh_private_key = _get_ssh_key_for_repo(repo)

    project_dir = stack.project_dir
    if os.path.exists(project_dir):
        # Pull the latest changes
        try:
            output = git_update(project_dir,
                                force=True,
                                # reset=True,
                                ssh_private_key=ssh_private_key)
            print(output)
            print(f"Updated git repo at {stack.project_dir}")
        except Exception as e:
            raise ValueError(f"Error updating repository: {e}")

    else:
        # Clone the repository
        try:
            # git.Repo.clone_from(repo_url, stack.project_dir)
            output = git_clone(repo_url,
                               project_dir,
                               ssh_private_key=ssh_private_key)
            print(output)
            print(f"Cloned git repo to {stack.project_dir}")
        except Exception as e:
            raise ValueError(f"Error cloning repository: {e}")

    return output


def _sync_compose_url(stack: ContainerStack, compose_url: str):
    raise NotImplementedError("Syncing from a compose URL is not implemented")