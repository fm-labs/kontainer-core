import json
import os.path
from os import scandir

import requests

from kstack.agent import settings

TEMPLATES_DIR = os.path.join(settings.AGENT_DATA_DIR, 'templates')
TEMPLATES_FILE_SUFFIX = '.templates.json'

def find_templates() -> list:
    """
    Find all templates in the templates directory.
    Look for all files with a .json extension in the templates directory and return a list of template names.

    :return: List of template names
    """
    templates = []

    for entry in scandir(TEMPLATES_DIR):
        if entry.is_file() and entry.name.endswith(TEMPLATES_FILE_SUFFIX):
            templates.append(entry.name.replace(TEMPLATES_FILE_SUFFIX, ''))

    return templates


def write_template(name: str, content: str) -> str:
    """
    Create a new template.

    Write the content to a new file in the templates directory

    :param name: Name of the template
    :param content: Content of the template
    :return: Path to the new template file
    """
    template_file = os.path.join(TEMPLATES_DIR, f"{name}{TEMPLATES_FILE_SUFFIX}")
    #if os.path.exists(template_file):
    #    raise FileExistsError(f"Template {name} already exists")

    with open(template_file, 'w') as f:
        f.write(content)

    return template_file


def download_template(name: str, url: str) -> str:
    """
    Create a new template from a URL
    Download the content from the url and create a new template

    :param name: Name of the template
    :param url: URL to download the content from
    :return: Path to the new template file
    """
    try:
        content = requests.get(url).content
        if not content or len(content) == 0:
            raise Exception(f"Failed to download content from {url}")
    except Exception as e:
        raise e
    return write_template(name, content)


def read_template(name: str) -> str:
    """
    Load the raw contents of a template

    :param name: Name of the template
    :return: Template content as a string
    """
    template_file = os.path.join(TEMPLATES_DIR, f"{name}{TEMPLATES_FILE_SUFFIX}")
    if not os.path.exists(template_file):
        raise FileNotFoundError(f"Template {name} not found")

    with open(template_file, 'r') as f:
        return f.read()


def load_template(name: str) -> dict:
    """
    Load the contents of a template as dictionary

    :param name: Name of the template
    :return: Template content as a dictionary
    """
    template_file = os.path.join(TEMPLATES_DIR, f"{name}{TEMPLATES_FILE_SUFFIX}")
    if not os.path.exists(template_file):
        raise FileNotFoundError(f"Template {name} not found")

    with open(template_file, 'r') as f:
        return json.load(f)