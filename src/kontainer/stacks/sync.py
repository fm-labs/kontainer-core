import os

from kontainer import settings
from kontainer.admin.credentials import private_key_exists
from kontainer.settings import get_real_app_data_path
from kontainer.stacks import ContainerStack
from kontainer.stacks.stackfile import Stackfile
from kontainer.util.composefile_util import modify_docker_compose_volumes
from kontainer.util.git_util import git_clone, git_pull_head
from kontainer.util.rgit_util import rgit_clone


def sync_stack(stack: ContainerStack) -> bytes:
    """
    Sync a stack with the repository or compose URL

    :param stack: The stack to sync
    :return: The output of the sync operation
    """
    config = stack.config
    if config is None:
        raise ValueError("No stack config found")

    parsed_compose_file_path = None
    base_path = config.get("base_path", "")
    full_project_path = os.path.join(settings.KONTAINER_DATA_DIR, stack.project_dir, base_path)
    out = b""

    # sync the stack from a git repository, if any
    repo = config.get("repository", None)
    if repo is not None and isinstance(repo, dict):
        out += _sync_stack_git_repo(stack, repo)
    else:
        # raise ValueError("No repository or compose URL provided")
        out += b"Warning: No repository or other sync source provided."

        # make sure the directory exists
        if not os.path.exists(full_project_path):
            os.makedirs(full_project_path, exist_ok=True)
            out += b"Created project directory: " + full_project_path.encode()

    # try to parse inline template first, if any
    if parsed_compose_file_path is None:
        parsed_compose_file_path = _sync_stack_inline_template(stack)

    # try to parse the compose file, if any
    if parsed_compose_file_path is None:
        parsed_compose_file_path = _sync_stack_compose_file(stack)

    if parsed_compose_file_path:
        out += b"Parsed docker-compose file: " + parsed_compose_file_path.encode()
        return out

    #out += b"Warning: No docker-compose or stack file detected."
    #return out
    raise ValueError("No docker-compose or stack file detected.")


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


def _sync_stack_git_repo(stack: ContainerStack, repo: dict):
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


def _sync_stack_inline_template(stack: ContainerStack) -> str | None:
    """
    Sync a stack from an inline template.

    :param stack: The stack to sync
    :return: The path to the compiled docker-compose file or None
    """

    template = stack.config.get("template", None)
    if template is None or not isinstance(template, dict):
        return None

    base_path = stack.config.get("base_path", "")
    output_path = os.path.join(settings.KONTAINER_DATA_DIR, stack.project_dir, base_path, "docker-compose.stack.yml")

    stackfile = Stackfile(content=template)
    stackfile.write_yaml_file(output_path)
    return str(output_path)


def _sync_stack_compose_file(stack: ContainerStack) -> str | None:
    """
    Modify the docker-compose.yml file to use the kontainer prefix for volumes.

    :param stack: The stack to process
    :return: The path to the compiled docker-compose file
    """
    base_path = stack.config.get("base_path", "")
    compose_file = stack.config.get("compose_file", "docker-compose.yml")
    compose_file_path = os.path.join(settings.KONTAINER_DATA_DIR, stack.project_dir, base_path, compose_file)
    if not os.path.exists(compose_file_path):
        # raise FileNotFoundError(f"docker-compose file not found: {compose_file_path}")
        return None

    output_path = os.path.join(settings.KONTAINER_DATA_DIR, stack.project_dir, base_path, "docker-compose.stack.yml")
    #output_path = os.path.join(settings.KONTAINER_DATA_DIR, stack.name + ".stack.yml")
    #@todo volumes_prefix = os.path.join(get_real_app_data_path(), "stacks", stack.name, base_path)
    #@todo modify_docker_compose_volumes(compose_file_path, output_path, volumes_prefix)
    #print(f"Modified docker-compose.yml saved to {output_path}")

    #stackfile = Stackfile.from_yaml_file(compose_file_path)
    #stackfile.modify_docker_compose_volumes(prefix)
    #stackfile.write_yaml_file(output_path)

    return str(output_path)
