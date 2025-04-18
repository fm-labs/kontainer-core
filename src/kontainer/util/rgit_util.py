
def rgit_clone(repo: str, dest: str, ssh_config, **kwargs) -> bytes:
    """
    Run a git clone command

    :param repo: Repository to clone
    :param ssh_config: SSH configuration
    :param dest: Destination directory
    :param kwargs: Additional arguments to pass to git clone
    :return:
    """
    return rgit(["clone", repo, dest], ssh_config, **kwargs)


def rgit_pull_head(working_dir: str, ssh_config, **kwargs) -> bytes:
    """
    Pull the latest changes from the remote repository

    :param working_dir: Working directory
    :param ssh_config: SSH configuration
    :param kwargs: Additional arguments to pass to git pull
    :return:
    """
    cur_head = rgit(["rev-parse", "--abbrev-ref", "HEAD"], ssh_config, working_dir=working_dir, timeout=10)
    cur_head_str = cur_head.decode("utf-8").strip()
    print(f"Current HEAD: {cur_head_str}")
    if cur_head_str is None or cur_head_str == "":
        raise ValueError("Failed to get current HEAD")

    return rgit(["pull", "origin", cur_head_str], ssh_config, working_dir=working_dir, **kwargs)


def rgit(args: list, ssh_config: dict, **kwargs) -> bytes:
    """
    Run a git command

    :param ssh_config: SSH configuration
    :param args: Arguments to pass to git
    :param kwargs: Additional arguments to pass to git
    :return:
    """
    out = b""
    print("rgit", ssh_config, args, **kwargs)
    if True:
        raise NotImplementedError("rgit not implemented")
    return out