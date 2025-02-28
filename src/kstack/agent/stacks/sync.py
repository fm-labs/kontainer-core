import os

from kstack.agent.admin.credentials import private_key_exists
from kstack.agent.stacks import ContainerStack
from kstack.agent.util.git_util import git_clone, git_update, git_pull_head


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

    private_key_file = repo.get("private_key_file", '')
    private_key_id = repo.get("private_key_id", '')

    if private_key_file is None or private_key_file == '':
        if private_key_id is None or private_key_id == '':
            raise ValueError("Private repository requires an SSH private key")

        # triple check the key exists
        _key_file = private_key_exists(private_key_id)
        if (_key_file is None
                or _key_file is False
                or _key_file == ''
                or not os.path.exists(_key_file)):
            raise ValueError(f"SSH private key {private_key_id} not found")
        private_key_file = _key_file

    return private_key_file


def _sync_repo(stack: ContainerStack, repo: dict):
    repo_url = repo.get("url", "")
    repo_branch = repo.get("branch", "main")
    if repo_url is None or repo_url == "":
        raise ValueError("Repository URL not provided")

    private_key_file = _get_ssh_key_for_repo(repo)

    project_dir = stack.project_dir
    project_git_dir = os.path.join(project_dir, ".git")
    if os.path.exists(project_dir) and os.path.exists(project_git_dir):
        # Pull the latest changes
        try:
            output = git_pull_head(project_dir,
                                force=True,
                                # reset=True,
                                private_key_file=private_key_file,
                                timeout=120)
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
                               private_key_file=private_key_file,
                               single_branch=True,
                               branch=repo_branch,
                               timeout=120)
            print(output)
            print(f"Cloned git repo to {stack.project_dir}")
        except Exception as e:
            raise ValueError(f"Error cloning repository: {e}")

    return output


def _sync_compose_url(stack: ContainerStack, compose_url: str):
    raise NotImplementedError("Syncing from a compose URL is not implemented")
