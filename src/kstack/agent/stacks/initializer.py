import json
import os
import time

import requests

from kstack.agent import settings
from kstack.agent.stacks.docker import DockerComposeStack
from kstack.agent.util.git_util import git_clone

DATA_DIR = settings.AGENT_DATA_DIR
TEMPLATES_DIR = f"{DATA_DIR}/templates"
STACKS_DIR = f"{DATA_DIR}/stacks"
REPOS_DIR = f"{DATA_DIR}/repos"
KEYS_DIR = f"{DATA_DIR}/keys"


def _init_docker_compose_stack(stack_name: str, meta=None, exists_ok=False, make_dirs=False) -> DockerComposeStack:
    """
    Initialize a stack.
    Write the metadata to the stack directory.
    Optionally create the stack directory.

    :param stack_name: Name of the stack
    :param meta: Metadata for the stack
    :param exists_ok: If True, do not raise an error if the stack directory already exists
    :param make_dirs: If True, create the stack directory
    :return: DockerComposeStack instance
    """
    if meta is None:
        meta = dict()

    # set default meta data
    meta["name"] = stack_name
    meta["type"] = meta.get("type", "docker-compose")
    meta["base_path"] = meta.get("base_path", "")
    meta["repository"] = meta.get("repository", dict())
    meta["_created"] = int(time.time())

    stack = DockerComposeStack(stack_name, meta=meta)

    # check/create the stack directory
    if make_dirs:
        os.makedirs(stack.project_dir, exist_ok=exists_ok)
    elif exists_ok is False and os.path.exists(stack.project_dir):
        raise ValueError(f"Stack directory {stack.project_dir} already exists")

    # write the metadata stack file to the stacks directory
    stack.dump()

    return stack


def stack_from_scratch(stack_name, **kwargs):
    """
    Create a stack from scratch
    """
    content = kwargs.get("compose_content")
    if content is None:
        raise ValueError("No content provided")

    meta = {}
    stack = _init_docker_compose_stack(stack_name, meta=meta)

    # Write the content to the stack directory
    compose_file = os.path.join(stack.project_dir, "docker-compose.yml")
    with open(compose_file, "w") as f:
        f.write(content)

    return stack


def stack_from_template(stack_name, **kwargs):
    content = kwargs.get("template_content")
    if content is None:
        raise ValueError("No content provided")

    template = json.loads(content)
    if template is None:
        raise ValueError("Invalid template")

    # @todo parse and validate the template

    meta = template
    stack = _init_docker_compose_stack(stack_name, meta=meta)
    return stack



def stack_from_compose_url(stack_name, **kwargs):
    url = kwargs.get("compose_url")
    if url is None:
        raise ValueError("URL not provided")

    meta = {
        "compose_url": url
    }
    stack = _init_docker_compose_stack(stack_name, meta=meta)

    # download the file from the url and build the stack
    with requests.get(url) as r:
        content = r.content.decode("utf-8")

    # @todo parse and validate the content

    # Write the content to the stack directory
    compose_file = os.path.join(stack.project_dir, "docker-compose.yml")
    with open(compose_file, "w") as f:
        f.write(content)

    return stack


def stack_from_gitrepo(stack_name, **kwargs):
    repo_url = kwargs.get("repo_url")
    base_path = kwargs.get("base_path", "")
    repo_ref = kwargs.get("repo_ref", "/ref/heads/main")
    # repo_branch = kwargs.get("repo_branch", "main")
    # repo_tag = kwargs.get("repo_tag", None)

    private = kwargs.get("private", False)
    ssh_private_key = kwargs.get("ssh_private_key", None)
    ssh_private_key_id = kwargs.get("ssh_private_key_id", None)

    # Ensure a repo_url is set
    if repo_url is None:
        raise ValueError("URL not provided")

    repo = {
        "type": "git",
        "url": repo_url,
        "ref": repo_ref,
    }

    # Ensure an ssh_private_key is set for private repos
    # If private is set to True, then ssh_private_key must be set
    # The existence of the private key file is NOT checked here
    if private:
        if ssh_private_key is None:
            if ssh_private_key_id is None:
                raise ValueError("Private repository requires an SSH private key")

            ssh_private_key = f"{KEYS_DIR}/{ssh_private_key_id}"

        repo["private"] = True
        repo["ssh_private_key"] = ssh_private_key
    else:
        ssh_private_key = None

    meta = {
        "base_path": base_path,
        "repository": repo
    }
    stack = _init_docker_compose_stack(stack_name, meta=meta, make_dirs=False)

    # Clone the repository
    try:
        target_dir = stack.project_dir
        # git.Repo.clone_from(repo_url, stack.project_dir)
        output = git_clone(repo_url,
                           target_dir,
                           ssh_private_key=ssh_private_key)
        print(output)
        print(f"Stacked cloned to {stack.project_dir}")
    except Exception as e:
        raise ValueError(f"Error cloning repository: {e}")

    return stack


def stack_from_template_repo(stack_name, repo_url=None, template_name=None, parameters=None, **kwargs):
    if repo_url is None:
        raise ValueError("URL not provided")
    if template_name is None:
        raise ValueError("Template name not provided")

    repo_base_dir = f"{REPOS_DIR}/{stack_name}"
    if os.path.exists(repo_base_dir):
        # todo update repo or delete and clone
        raise ValueError(f"Repository directory {repo_base_dir} already exists")

    ssh_private_key = kwargs.get("ssh_private_key", None)
    output = git_clone(repo_url,
                       repo_base_dir,
                       ssh_private_key=ssh_private_key)
    print(output)
    print(f"Repository cloned to {repo_base_dir}")

    template_dir = f"{repo_base_dir}/{template_name}"
    return stack_from_template_dir(stack_name, template_dir, parameters)


def stack_from_template_dir(stack_name, template_dir=None, parameters=None):
    """
    Launch a stack from a template

    To launch a template (from a template dir) as a stack, we need to:
    - Create a directory for the stack
    - Copy the template files into the stack directory


    :param stack_name: Name of the stack
    :param template_dir: Directory containing the template
    :param parameters: Parameters to pass to the template
    """
    # stack_base_dir = f"{stacks_dir}/{stack_name}"
    # if os.path.exists(stack_base_dir):
    #     raise ValueError(f"Stack directory {stack_base_dir} already exists")
    #
    # os.makedirs(stack_base_dir, exist_ok=True)
    # if not os.path.exists(stack_base_dir):
    #     raise ValueError(f"Stack directory {stack_base_dir} could not be created")
    if template_dir is None:
        raise ValueError("Template directory not provided")
    if not os.path.exists(template_dir):
        raise ValueError(f"Template not found at {template_dir}")

    stack = _init_docker_compose_stack(stack_name)
    stack_base_dir = stack.project_dir

    for root, dirs, files in os.walk(template_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, template_dir)
            stack_file_path = os.path.join(stack_base_dir, rel_path)
            os.makedirs(os.path.dirname(stack_file_path), exist_ok=True)
            with open(file_path, 'r') as f:
                content = f.read()
                for key, value in parameters.items():
                    content = content.replace(f"{{{{ {key} }}}}", value)
            with open(stack_file_path, 'w') as f:
                f.write(content)

    return stack


def stack_from_portainer_template(stack, template_url=None, template_name=None, **kwargs):
    if template_url is None:
        raise ValueError("Templates URL not provided")
    if template_name is None:
        raise ValueError("Template name not provided")

    # todo download the portainer templates url, extract the template, and build the stack
    pass


# def stack_from_compose_file(stack_name, **kwargs):
#     path = kwargs.get("path")
#     if path is None:
#         raise ValueError("Path not provided")
#
#     # Read the file path contents
#     contents = None
#     #with open(docker_compose_path, "r") as f:
#     #    contents = f.read()
#
#     p = DockerComposeStack(stack_name)
#     return p
