import json
import os

from kontainer import settings

contexts_cache = None


def get_docker_contexts_file():
    """
    Get the contexts file
    :return: path to the context file
    """
    context_file = os.environ.get("KONTAINER_CONTEXT_FILE")
    if not context_file:
        context_file = f"{settings.KONTAINER_DATA_DIR}/contexts.json"
    return context_file


def get_docker_contexts():
    """
    Get the list of environments.
    The list of environments is read from the contexts.json file
    or from the environment variables KONTAINER_CONTEXT_<ctx_nr> and KONTAINER_CONTEXT_<ctx_nr>_HOST.
    If no contexts are found, the default context is added.

    :return: list of environments
    """
    global contexts_cache
    if contexts_cache is None:
        # read the contexts.json file
        _contexts = read_docker_contexts_json()

        # if no contexts are found, check the environment variables
        if not _contexts or len(_contexts) == 0:
            _contexts = read_docker_contexts_from_environment_variables()

        # if no contexts are found, add the default context
        if not _contexts or len(_contexts) == 0:
            _contexts = [{"id": "local", "host": "unix://var/run/docker.sock"}]

        contexts_cache = _contexts
    return contexts_cache


def get_dockerhost_for_ctx_id(ctx_id):
    """
    Get the docker host for the given context id.

    :param ctx_id: context id
    :return: docker host
    """

    # todo: remove this
    if ctx_id == "local" or ctx_id == "default":
        return "unix://var/run/docker.sock"
    elif ctx_id == "local-tcp":
        return "tcp://localhost:2375"

    contexts = get_docker_contexts()
    docker_host = None
    for context in contexts:
        if context["id"] == ctx_id:
            docker_host = context.get("host")
            break

    return docker_host


def get_ssh_config_for_ctx_id(ctx_id):
    """
    Get the SSH config for the given context id.

    :param ctx_id: context id
    :return: ssh config
    """
    contexts = get_docker_contexts()
    ssh_config = None
    for context in contexts:
        if context["id"] == ctx_id:
            ssh_config = context.get("ssh_config")
            break

    return ssh_config


def add_docker_context(ctx_id, host, write=False):
    """
    Add a new environment to the list of environments
    :param ctx_id: context id
    :param host: host name
    :param write: if True, write the context to disk
    """
    contexts = get_docker_contexts()
    # check if the context already exists
    for context in contexts:
        if context["id"] == ctx_id:
            raise Exception(f"Context id {ctx_id} already exists")

    contexts.append({"id": ctx_id, "host": host})
    global contexts_cache
    contexts_cache = contexts
    if write:
        write_docker_contexts_json(contexts)


def remove_docker_context(ctx_id, write=False):
    """
    Remove an environment from the list of environments
    :param ctx_id: context id
    :param write: if True, write the context to disk
    """
    contexts = get_docker_contexts()
    contexts = [context for context in contexts if context["id"] != ctx_id]
    global contexts_cache
    contexts_cache = contexts
    if write:
        write_docker_contexts_json(contexts)


def read_docker_contexts_from_environment_variables():
    """
    Check the environment variables:
    - with the format KONTAINER_CONTEXT_<ctx_nr>=CONTEXT_ID
    - with the format KONTAINER_CONTEXT_<ctx_nr>_HOST=DOCKER_HOST

    :return: list of environments
    """
    i = 0
    contexts = []
    while True:
        ctx_id = os.environ.get(f"KONTAINER_CONTEXT_{i}")
        if not ctx_id:
            break

        host = os.environ.get(f"KONTAINER_CONTEXT_{i}_HOST")
        if host is None:
            break

        print(f"Adding context {ctx_id} with host {host}")
        contexts.append({"id": ctx_id, "host": host})
        i += 1
    return contexts


def read_docker_contexts_json():
    """
    Read the contexts.json file and return the list of environments
    :return: list of environments
    """
    contexts = []
    context_file = get_docker_contexts_file()
    if os.path.exists(context_file):
        with open(context_file, "r") as f:
            contexts = json.load(f)
    return contexts


def write_docker_contexts_json(contexts):
    """
    Write the contexts.json file with the list of environments
    :param contexts: list of environments
    """
    context_file = get_docker_contexts_file()
    try:
        with open(context_file, "w") as f:
            json.dump(contexts, f, indent=4)
    except Exception as e:
        raise Exception(f"Error writing contexts to file: {e}")

    return context_file
