import boto3
import base64

def aws_ecr_login(region="us-east-1", profile=None, access_key=None, secret_key=None):
    """
    Authenticate Docker to AWS ECR using AWS CLI.

    :param region: AWS region where the ECR is hosted (e.g., "us-east-1")
    :param profile: AWS CLI profile name (optional)
    :param access_key: AWS access key ID (optional)
    :param secret_key: AWS secret access key (optional)
    :return: True if login is successful, False otherwise
    """

    # Initialize AWS session (optionally with a profile)
    session_args = {"region_name": region}
    if profile:
        session_args["profile_name"] = profile
    else:
        session_args["aws_access_key_id"] = access_key
        session_args["aws_secret_access_key"] = secret_key

    session = boto3.Session(**session_args)
    ecr_client = session.client("ecr")

    try:
        # Get the Docker authentication token from AWS ECR
        response = ecr_client.get_authorization_token()
        print("ECR authorization token obtained successfully", response)

        auth_token = response["authorizationData"][0]["authorizationToken"]
        ecr_url = response["authorizationData"][0]["proxyEndpoint"]

        print(f"ECR URL: {ecr_url}")
        print(f"ECR authorization token: {auth_token}")

        # Decode the base64 encoded auth token
        decoded = base64.b64decode(auth_token).decode("utf-8")
        print(f"ECR decoded token: {decoded}")
        username, password = decoded.split(":")

        return ecr_url, username, password

    except Exception as e:
        print(f"Failed to get ECR authorization token: {e}")
        return False