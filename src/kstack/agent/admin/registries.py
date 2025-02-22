import os
import json

from kstack.agent import settings
from kstack.agent.settings import DEFAULT_CONTAINER_REGISTRIES

CONFIG_DIR = os.path.join(settings.AGENT_DATA_DIR, 'config')
CONTAINER_REGISTRIES_FILE = os.path.join(CONFIG_DIR, 'registries.json')


def list_container_registries(safe=True) -> list:
    """
    List all available container registries.
    If safe is True, return a list of container registries without credentials.

    :param safe: If True, return a list of container registries without credentials
    :return: List of container registries
    """
    registries = read_container_registries()

    def _strip_credentials(registry):
        return {
            "name": registry["name"],
            "host": registry["host"] if "host" in registry else "",
            "label": registry["label"] if "label" in registry else "",
            "username": f"*****" if "username" in registry else "",
            "password": f"*****" if "password" in registry else "",
        }
    if safe:
        return list(map(_strip_credentials, registries))

    return registries


def read_container_registries() -> list:
    """
    Read the container registries from the registries.json file.
    If the file does not exist, return the default container registries.

    :return: List of container registries
    """
    if not os.path.exists(CONTAINER_REGISTRIES_FILE):
        return DEFAULT_CONTAINER_REGISTRIES

    with open(CONTAINER_REGISTRIES_FILE, 'r') as f:
        return json.load(f)


def write_container_registries(registries: list) -> None:
    """
    Write the container registries to the registries.json file.

    :param registries: List of container registries
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONTAINER_REGISTRIES_FILE, 'w') as f:
        json.dump(registries, f, indent=4)


def find_container_registry(registry_name: str, registries=None) -> dict | None:
    """
    Lookup a container registry by name.

    :param registry_name: Name of the container registry
    :param registries: List of container registries
    :return: Container registry
    """
    if registries is None:
        registries = read_container_registries()

    for r in registries:
        if r["name"] == registry_name:
            return r
    return None


def update_container_registry(registry_name: str, data: dict) -> list:
    """
    Update a container registry.
    If the registry does not exist, it will be appended to the existing list.

    :param registry_name: Name of the container registry
    :param data: Data to update the container registry with
    :return: Updated list of container registries
    """
    registries = read_container_registries()

    # Ensure the registry name is set
    data["name"] = registry_name

    exists = False
    for r in registries:
        if r["name"] == registry_name:
            exists = True
            r.update(data)
            break

    if not exists:
        registries.append(data)

    write_container_registries(registries)
    return registries


def delete_container_registry(registry_name: str) -> list:
    """
    Delete a container registry.

    :param registry_name: Name of the container registry
    :return: Updated list of container registries
    """
    registries = read_container_registries()
    new_registries = [r for r in registries if r["name"] != registry_name]
    write_container_registries(new_registries)
    return new_registries
