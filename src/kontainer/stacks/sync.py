import os

from kontainer import settings
from kontainer.admin.credentials import private_key_exists
from kontainer.settings import get_real_app_data_path
from kontainer.stacks import ContainerStack
from kontainer.util.composefile_util import modify_docker_compose_volumes
from kontainer.util.git_util import git_clone, git_pull_head
from kontainer.util.rgit_util import rgit_clone, rgit_pull_head


def sync_stack(stack: ContainerStack) -> bytes:
    """
    Sync a stack with the repository or compose URL

    :param stack: The stack to sync
    :return: The output of the sync operation
    """
    meta = stack.config
    if meta is None:
        raise ValueError("No metadata found")

    repo = meta.get("repository", None)

    out = b""
    if repo is not None:
        out = _sync_repo(stack, repo)
    else:
        raise ValueError("No repository or compose URL provided")

    _process_compose_file(stack)

    return out


def _lookup_ssh_key_for_repo(repo: dict):
    """
    Get the SSH private key for a repository

    :param repo: The repository metadata
    """
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
    """
    Sync a stack from a git repository

    :param stack: The stack to sync
    :param repo: The repository metadata
    :return: The output of the git command
    """
    repo_url = repo.get("url", "")
    repo_branch = repo.get("branch", "main")
    if repo_url is None or repo_url == "":
        raise ValueError("Repository URL not provided")

    private_key_file = _lookup_ssh_key_for_repo(repo)
    full_project_dir = str(os.path.join(settings.KONTAINER_DATA_DIR, stack.project_dir))
    ssh_config = {
        "private_key_file": private_key_file,
    }

    output = b""
    if stack.ctx_id == "local" and os.path.exists(full_project_dir):
        # Pull the latest changes
        try:
            pull_output = git_pull_head(full_project_dir,
                                        force=True,
                                        # reset=True,
                                        private_key_file=private_key_file,
                                        timeout=120)

            print(pull_output)
            print(f"Updated git repo at {stack.project_dir}")
            output += pull_output
        except Exception as e:
            raise ValueError(f"Error updating repository: {e}")

    elif stack.ctx_id == "local" and not os.path.exists(full_project_dir):

        # Clone the repository
        try:
            # git.Repo.clone_from(repo_url, stack.project_dir)
            clone_output = git_clone(repo_url,
                                     dest=full_project_dir,
                                     private_key_file=private_key_file,
                                     single_branch=True,
                                     branch=repo_branch,
                                     timeout=120)


            print(clone_output)
            print(f"Cloned git repo to {stack.project_dir}")
            output += clone_output
        except Exception as e:
            raise ValueError(f"Error cloning repository: {e}")

    elif stack.ctx_id != "local":

        # pull_output = rgit_pull_head(stack.project_dir,
        #                              ssh_config,
        #                              force=True,
        #                              # reset=True,
        #                              timeout=120)

        try:
            clone_output = rgit_clone(repo_url,
                                      dest=stack.project_dir,
                                      ssh_config=ssh_config,
                                      single_branch=True,
                                      branch=repo_branch,
                                      timeout=120)
            print(clone_output)
            print(f"Cloned git repo to {stack.project_dir}")
            output += clone_output
        except Exception as e:
            raise ValueError(f"Error remote cloning repository: {e}")

    return output


def _process_compose_file(stack: ContainerStack) -> str | None:
    """
    Modify the docker-compose.yml file to use the kontainer prefix

    :param stack: The stack to process
    :return: The path to the modified docker-compose file
    """
    base_path = stack.config.get("base_path", "")
    compose_file_path = os.path.join(stack.project_dir, base_path, "docker-compose.yml")
    if not os.path.exists(compose_file_path):
        return None

    output_path = os.path.join(stack.project_dir, base_path, "docker-compose.stack.yml")
    prefix = os.path.join(get_real_app_data_path(), "stacks", stack.name, base_path)
    modify_docker_compose_volumes(compose_file_path, output_path, prefix)
    print(f"Modified docker-compose.yml saved to {output_path}")
    return output_path
