import subprocess

from kstack.agent import settings


def dockercli_login(username, password, registry="https://hub.docker.com"):
    """Login to Docker and ensure credentials persist."""
    result = subprocess.run(
        ["docker", "login", "-u", username, "--password-stdin", registry],
        input=password.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        env=dict({"DOCKER_CONFIG": settings.DOCKER_CONFIG}),
    )
    print("Docker registry login successful", registry, username, result.stdout.decode())
    return result.returncode == 0


def dockercli_login_ecr_with_awscli(ecr_url, region="us-east-1", profile=None, access_key=None, secret_key=None):
    """Login to AWS ECR using AWS CLI."""
    try:
        p_aws_env = dict({
            "DOCKER_CONFIG": settings.DOCKER_CONFIG,
        })
        if profile:
            p_aws_env["AWS_PROFILE"] = profile
        else:
            p_aws_env["AWS_ACCESS_KEY_ID"] = access_key
            p_aws_env["AWS_SECRET_ACCESS_KEY"] = secret_key

        p_aws = subprocess.run(
            ["aws", "ecr", "get-login-password", "--region", region],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            env=p_aws_env,
        )

        print("AWS ECR login successful!", p_aws.stdout.decode(), flush=True)
        ecr_password = p_aws.stdout # bytes
        ecr_username = "AWS"

        # Use the obtained password to log in to Docker
        #ecr_url = f"{region}.dkr.ecr.amazonaws.com"
        p_docker = subprocess.run(
            ["docker", "login", "--username", ecr_username, "--password-stdin", ecr_url],
            input=ecr_password,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            env=dict({
                "DOCKER_CONFIG": settings.DOCKER_CONFIG
            }),
        )

        print("Docker login to ECR successful!", p_docker.stdout.decode(), flush=True)
        return ecr_url, ecr_username, ecr_password.decode()

    except subprocess.CalledProcessError as e:
        print("Docker login failed:", e.stderr.decode(), flush=True)
        return False
