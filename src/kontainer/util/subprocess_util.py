import os
import subprocess

import paramiko


def kwargs_to_cmdargs(kwargs) -> list:
    """
    Map kwargs to command line arguments.

    :param kwargs:
    :return:
    """
    args = []
    for k, v in kwargs.items():
        if v is not None and v is not False:
            if len(k) == 1 and type(v) is bool:
                args.append(f"-{k}")
                continue

            args.append(f"--{k.replace('_', '-')}")
            if type(v) is not bool:
                args.append(str(v))
    return args


def load_envfile(env_file: str, penv: dict) -> dict:
    """
    Load environment file into a dictionary

    :param env_file: Path to the environment file
    :param penv: Dictionary to load the environment file into
    :return:
    """
    if penv is None:
        penv = dict()

    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Environment file {env_file} does not exist")

    with open(env_file, 'r') as f:
        for line in f.readlines():
            if line.strip() and not line.startswith('#'):
                k, v = line.split('=', 1)
                penv[k] = v.strip()
    return penv


def run_command(cmd: str | list):
    """
    Invoke Docker Command in Local Shell (Blocking)
    """
    try:
        return subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        return e.output


