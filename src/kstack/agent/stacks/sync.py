import os

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

def _sync_repo(stack: ContainerStack, repo: dict):

    repo_url = repo.get("url", "")
    if repo_url is None or repo_url == "":
        raise ValueError("Repository URL not provided")

    ssh_private_key = repo.get("ssh_private_key", None)

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