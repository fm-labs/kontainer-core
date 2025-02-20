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


def git(cmd: list, working_dir=None, ssh_private_key=None, **kwargs) -> bytes:
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
    if ssh_private_key:
        if not os.path.exists(ssh_private_key):
            raise ValueError(f"Private key file {ssh_private_key} does not exist")
        ssh_command += f" -i {ssh_private_key}"

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

        proc = subprocess.run(pcmd, cwd=working_dir, env=penv, capture_output=True)
        print("STDOUT", proc.stdout)
        print("STDERR", proc.stderr)

        if proc.returncode != 0:
            raise Exception(f"Command exited with non-zero return code: {proc.stderr}")

        return proc.stdout
    except Exception as e:
        print(e)
        raise e
