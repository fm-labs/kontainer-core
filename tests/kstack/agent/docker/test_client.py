from unittest import TestCase

import requests

from kstack.agent.docker.client import DockerMgmtClient


class TestDockerMgmtClient(TestCase):
    def test_start_container(self):
        self.fail()

    def test_stop_container(self):
        self.fail()

    def test_list_images(self):
        self.fail()

    def test_list_containers(self):

        test_client = DockerMgmtClient()
        result = test_client.list_containers()
        self.assertIsNotNone(result)

        # assert that container named "sonja-testcontainer" is in the list
        for container in result:
            print("id=", container.id)
            print("name=", container.name)
            print("attrs=", container.attrs)

        self.assertIn("silly_kowalevski", [container.name for container in result])


    def test_integration_list_containers(self):
        # make a request to the server to /containers
        result = requests.get("http://localhost:5000/containers")
        self.assertEqual(result.status_code, 200)

        # assert that the response is a list of containers
        #print(result.json())
        self.assertIsNotNone(result)

        # assert that container named "sonja-testcontainer" is in the list
        containers = result.json()
        #print(containers)
        self.assertIn("/silly_kowalevski", [container.Name for container in containers])

        pass
