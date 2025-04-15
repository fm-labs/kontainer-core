import os
import json

from kontainer import settings
from kontainer.docker.dkr import get_docker_manager_cached
from kontainer.settings import DEFAULT_CONTAINER_REGISTRIES
from kontainer.util.aws_util import aws_ecr_login
from kontainer.util.docker_utils import dockercli_login_ecr_with_awscli

CONFIG_DIR = os.path.join(settings.KONTAINER_DATA_DIR, 'config')
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
            "username": f"*****" if "username" in registry and len(registry['username']) > 0 else "",
            "password": f"*****" if "password" in registry and len(registry['password']) > 0 else "",
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


def request_container_registry_login(ctx_id: str, registry_name: str) -> bool:
    """
    Request a login to a container registry.

    :param ctx_id: Context ID for the Docker manager
    :param registry_name: Name of the container registry
    :return: Response from the container registry
    """
    print("Requesting login for {}".format(registry_name))
    registry = find_container_registry(registry_name)
    if registry is None:
        raise Exception(f"Container registry '{registry_name}' not found")

    host = registry.get("host", "")
    url_schema = "http" if registry.get("insecure", "false") == "true" else "https"
    url = f"{url_schema}://{host}"
    username = registry.get("username", "")
    password = registry.get("password", "")

    # AWS ECR login
    if host.endswith(".amazonaws.com"):
        # Fallback to AWS credentials if no username and password are set
        if username == "" and password == "":
            username = settings.AWS_ACCESS_KEY_ID
            password = settings.AWS_SECRET_ACCESS_KEY

        print(f"Logging in to AWS ECR {host} with {username}", flush=True)
        # # Request AWS ECR auth token
        # ecr_login_result = aws_ecr_loginregion=settings.AWS_REGION,
        #         #                                  profile=settings.AWS_PROFILE,
        #         #                                  access_key=username,
        #         #                                  secret_key=password
        # if not ecr_login_result:
        #     raise Exception("Failed to login to AWS ECR")
        #
        # # Use the obtained password to log in to Docker
        # url, username, password = ecr_login_result
        ecr_login_result = dockercli_login_ecr_with_awscli(ecr_url=host, # {account}.dkr.ecr.{region}.amazonaws.com
                                        region=settings.AWS_REGION,
                                        profile=settings.AWS_PROFILE,
                                        access_key=username,
                                        secret_key=password)
        if not ecr_login_result:
            raise Exception("Failed to login to AWS ECR")

        #url, username, password = ecr_login_result
        return True

    # @todo GitHub login
    # @todo Docker Hub login
    # @todo Quay.io login

    # Generic Docker registry login
    print(f"Logging in to Docker at {url} with {username}", flush=True)
    dkr = get_docker_manager_cached(ctx_id)
    if dkr.registry_login(url, username, password):
        return True

    return False