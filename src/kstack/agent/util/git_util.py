import os
import subprocess

from kstack.agent.util.subprocess_util import kwargs_to_cmdargs

# https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables
# https://stackoverflow.com/questions/4565700/how-to-specify-the-private-ssh-key-to-use-when-executing-shell-command-on-git
#
# Use the GIT_SSH_COMMAND environment variable to specify the private key file
#
# $ git config core.sshCommand 'ssh -i private_key_file -o IdentitiesOnly=yes'
# # or
# $ git -c core.sshCommand="ssh -i private_key_file -o IdentitiesOnly=yes" clone host:repo.git
# # or
# $ set "GIT_SSH_COMMAND=ssh -i private_key_file -o IdentitiesOnly=yes"

def git_clone(repo: str, dest: str, **kwargs) -> bytes:
    """
    Run a git clone command

    :param repo: Repository to clone
    :param dest: Destination directory
    :param kwargs: Additional arguments to pass to git clone
    :return:
    """
    return git(["clone", repo, dest], **kwargs)


def git_pull_head(working_dir=None, **kwargs) -> bytes:
    """
    Pull the latest changes from the remote repository

    :param working_dir: Working directory
    :param kwargs: Additional arguments to pass to git pull
    :return:
    """
    cur_head = git(["rev-parse", "--abbrev-ref", "HEAD"], working_dir=working_dir, timeout=10)
    cur_head_str = cur_head.decode("utf-8").strip()
    print(f"Current HEAD: {cur_head_str}")
    if cur_head_str is None or cur_head_str == "":
        raise ValueError("Failed to get current HEAD")

    return git(["pull", "origin", cur_head_str], working_dir=working_dir, **kwargs)


def git_update(working_dir=None, force=False, reset=False, **kwargs) -> bytes:
    """
    Update a git repository.

    Runs a git pull command.
    Forces a pull from the remote repository, overwriting any local changes.

    How Jenkins does it:
      > git rev-parse --resolve-git-dir /var/jenkins_home/workspace/example/.git # timeout=10
     Fetching changes from the remote Git repository
      > git config remote.origin.url git@git-server:example.git # timeout=10
     Fetching upstream changes from git@git-server:example.git
      > git --version # timeout=10
      > git --version # 'git version 2.39.2'
     using GIT_SSH to set credentials Buildserver SSH keys
     Verifying host key using known hosts file, will automatically accept unseen keys
      > git fetch --tags --force --progress -- git@git-server:example.git +refs/heads/*:refs/remotes/origin/* # timeout=10
     Seen branch in repository origin/dev
     Seen branch in repository origin/main
     Seen 2 remote branches
      > git show-ref --tags -d # timeout=10
     Checking out Revision 92888d3003585ce11bf317ed04baa30044d2ccbd (origin/main, refs/tags/2.3.1-alpha.3)
      > git config core.sparsecheckout # timeout=10
      > git checkout -f 92888d3003585ce11bf317ed04baa30044d2ccbd # timeout=10
     Commit message: "Initial commit"
      > git rev-list --no-walk 22752c774c5cfdd3f6f5456c310de22e892cc067 # timeout=10

    :param working_dir: Working directory
    :param kwargs: Additional arguments to pass to git pull
    :return:
    """
    if reset:
        git(["reset", "--hard"], working_dir=working_dir)

    if force:
        kwargs["force"] = True
    return git(["pull"], working_dir=working_dir, **kwargs)


def git(cmd: list, working_dir=None, private_key_file=None, timeout=None, **kwargs) -> bytes:
    """
    Run a docker git command

    :param cmd: Command to run
    :param kwargs: Additional arguments to pass to git command
    :return:
    """
    if working_dir is None:
        working_dir = os.getcwd()

    # ssh command
    ssh_command = f"ssh -o IdentitiesOnly=yes"
    if private_key_file:
        if not os.path.exists(private_key_file):
            raise ValueError(f"Private key file {private_key_file} does not exist")
        ssh_command += f" -i {private_key_file}"

    # git specific args
    git_args = {}
    git_cmd_args = kwargs_to_cmdargs(git_args)

    # command specific args
    cmd_args = kwargs_to_cmdargs(kwargs)
    try:
        pcmd = ["git"] + git_cmd_args + cmd + cmd_args
        print(f"RAW CMD: {pcmd}")
        print(f"CMD: {" ".join(pcmd)}")
        print(f"PWD: {working_dir}")

        # penv = os.environ.copy()
        penv = dict()
        penv['PATH'] = os.getenv('PATH')
        penv['PWD'] = working_dir

        penv['GIT_TERMINAL_PROMPT'] = '0' # disable prompting for credentials (git 2.3+)
        penv['GIT_SSH_COMMAND'] = ssh_command

        # # Load .env file into 'penv'
        # env_file = '.env'
        # if os.path.exists(env_file):
        #     with open(env_file, 'r') as f:
        #         for line in f.readlines():
        #             if line.strip() and not line.startswith('#'):
        #                 k, v = line.split('=', 1)
        #                 penv[k] = v.strip()

        print(f"Environment: {penv}")

        proc = subprocess.run(pcmd,
                              cwd=working_dir,
                              env=penv,
                              capture_output=True,
                              timeout=timeout)
        print("STDOUT", proc.stdout)
        print("STDERR", proc.stderr)

        if proc.returncode != 0:
            raise Exception(f"Command exited with non-zero return code: {proc.stderr}")

        return proc.stdout
    except Exception as e:
        print(e)
        raise e
