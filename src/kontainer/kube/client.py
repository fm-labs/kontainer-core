from kubernetes import config, client


def get_kube_client() -> client.CoreV1Api:
    """
    Get a Kubernetes API client

    :return: Kubernetes API client
    """

    # Load kubeconfig from default location (~/.kube/config)
    config.load_kube_config()

    # Create a Kubernetes API client
    cube_client = client.CoreV1Api()
    cube_client = client.CoreV1Api(client.ApiClient())
    return cube_client
