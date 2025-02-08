from kstack.agent.stacks.docker import DockerComposeStack


def stack_from_compose_file(stack, **kwargs):
    path = kwargs.get("path")
    if path is None:
        raise ValueError("Path not provided")

    # Read the file path contents
    contents = None
    #with open(docker_compose_path, "r") as f:
    #    contents = f.read()

    p = DockerComposeStack(stack)
    return p


def stack_from_compose_url(stack, **kwargs):
    url = kwargs.get("url")
    if url is None:
        raise ValueError("URL not provided")

    # todo download the file from the url and build the stack
    contents = None
    #with urllib.request.urlopen(url) as f:
    #    contents = f.read().decode('utf-8')
    #p = DockerComposeStack(stack)
    #return p
    pass


def stack_from_gitrepo(stack, **kwargs):
    url = kwargs.get("url")
    if url is None:
        raise ValueError("URL not provided")

    # todo checkout the repo and build the stack from the docker-compose file
    pass


def stack_from_portainer_template(stack, **kwargs):
    url = kwargs.get("url")
    template = kwargs.get("template")
    if url is None:
        raise ValueError("Templates URL not provided")
    if template is None:
        raise ValueError("Template name not provided")

    # todo download the portainer templates url, extract the template, and build the stack
    pass