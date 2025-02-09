import os

import git
import requests

from kstack.agent import settings
from kstack.agent.stacks.docker import DockerComposeStack

data_dir = settings.AGENT_DATA_DIR
templates_dir = f"{data_dir}/templates"
stacks_dir = f"{data_dir}/stacks"
repos_dir = f"{data_dir}/repos"


def stack_from_scratch(stack_name, **kwargs):
    content = kwargs.get("compose_content")
    if content is None:
        raise ValueError("No content provided")

    stack = DockerComposeStack(stack_name)

    # Ensure the stack directory exists
    stack_dir = stack.project_dir
    os.makedirs(stack_dir, exist_ok=True)

    # Write the content to the stack directory
    compose_file = os.path.join(stack_dir, "docker-compose.yml")
    with open(compose_file, "w") as f:
        f.write(content)

    return stack


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


def stack_from_compose_url(stack_name, **kwargs):
    url = kwargs.get("compose_url")
    if url is None:
        raise ValueError("URL not provided")

    # download the file from the url and build the stack
    content = None
    with requests.get(url) as r:
        content = r.content

    stack = DockerComposeStack(stack_name)

    # Ensure the stack directory exists
    stack_dir = stack.project_dir
    os.makedirs(stack_dir, exist_ok=True)

    # Write the content to the stack directory
    compose_file = os.path.join(stack_dir, "docker-compose.yml")
    with open(compose_file, "w") as f:
        f.write(content)

    return stack


def stack_from_gitrepo(stack_name, **kwargs):
    url = kwargs.get("repo_url")

    if url is None:
        raise ValueError("URL not provided")

    stack = init_stack_from_git_repo(stack_name, url)
    return stack


def stack_from_template_repo(stack_name, **kwargs):
    url = kwargs.get("template_repo_url")
    template_name = kwargs.get("template_name")

    if url is None:
        raise ValueError("URL not provided")
    if template_name is None:
        raise ValueError("Template name not provided")

    stack = init_stack_from_template_repo(stack_name, url, template_name)
    return stack


def stack_from_portainer_template(stack, **kwargs):
    url = kwargs.get("url")
    template = kwargs.get("template")
    if url is None:
        raise ValueError("Templates URL not provided")
    if template is None:
        raise ValueError("Template name not provided")

    # todo download the portainer templates url, extract the template, and build the stack
    pass



def init_stack_from_git_repo(stack_name, repo_url, parameters=None):
    stack_base_dir = f"{stacks_dir}/{stack_name}"
    if os.path.exists(stack_base_dir):
        raise ValueError(f"Stack directory {stack_base_dir} already exists")

    # using gitpython
    # clone git repo to stack_base_dir

    git.Repo.clone_from(repo_url, stack_base_dir)
    print(f"Stacked cloned to {stack_base_dir}")

    return stack_base_dir


def init_stack_from_template_repo(stack_name, repo_url, template_name="", parameters=None):

    stack_base_dir = f"{stacks_dir}/{stack_name}"
    if os.path.exists(stack_base_dir):
        raise ValueError(f"Stack directory {stack_base_dir} already exists")

    repo_base_dir = f"{repos_dir}/{stack_name}"
    if os.path.exists(repo_base_dir):
        # todo update repo or delete and clone
        raise ValueError(f"Repository directory {repo_base_dir} already exists")

    # using gitpython
    # clone git repo to repo_base_dir

    git.Repo.clone_from(repo_url, repo_base_dir)
    print(f"Repository cloned to {repo_base_dir}")

    template_dir = f"{repo_base_dir}/{template_name}"
    return init_stack_from_template_dir(stack_name, template_dir, parameters)


def init_stack_from_template_dir(stack_name, template_dir, parameters):
    """
    Launch a stack from a template

    To launch a template (from a template dir) as a stack, we need to:
    - Create a directory for the stack
    - Copy the template files into the stack directory


    :param stack_name: Name of the stack
    :param template_dir: Directory containing the template
    :param parameters: Parameters to pass to the template
    """
    stack_base_dir = f"{stacks_dir}/{stack_name}"
    if os.path.exists(stack_base_dir):
        raise ValueError(f"Stack directory {stack_base_dir} already exists")

    os.makedirs(stack_base_dir, exist_ok=True)
    if not os.path.exists(stack_base_dir):
        raise ValueError(f"Stack directory {stack_base_dir} could not be created")

    if not os.path.exists(template_dir):
        raise ValueError(f"Template not found at {template_dir}")

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

    return stack_base_dir