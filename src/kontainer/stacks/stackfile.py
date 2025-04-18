import json

from kontainer.util.yaml_util import yaml_to_dict, dict_to_yaml_string


class Stackfile:
    """
    A class that represents a docker compose stack file.

    This class is used to manage the stack file and its metadata.
    It provides methods to load, dump, and validate the stack file.

    Attributes:
        - content (dict): The content of the stack file as a dictionary.
    """

    def __init__(self, content: dict):
        self.content = content


    def __str__(self):
        return self.content


    def process(self):
        """
        Process the stack file content.

        :return: Processed stack file content.
        """
        # Implement processing logic here
        return self.content


    def validate(self) -> bool:
        """
        Validate the stack file content.

        :raises ValueError: If the stack file is invalid.
        """
        # Implement validation logic here
        return True


    def to_json(self) -> str:
        """
        Convert the stack file content to JSON string.

        :return: JSON string representation of the stack file.
        """
        return json.dumps(self.content, indent=2)


    def write_json_file(self, json_file: str) -> None:
        """
        Write the stack file content to a JSON file.

        :param json_file: Path to the JSON file.
        """
        with open(json_file, 'w') as f:
            json.dump(self.content, f, indent=2)


    def to_yaml(self) -> str:
        """
        Convert the stack file content to YAML string.

        :return: YAML string representation of the stack file.
        """
        return dict_to_yaml_string(self.content)


    def write_yaml_file(self, yaml_file: str) -> None:
        """
        Write the stack file content to a YAML file.

        :param yaml_file: Path to the YAML file.
        """
        with open(yaml_file, 'w') as f:
            f.write(self.to_yaml())


    @staticmethod
    def from_json(json_str: str) -> 'Stackfile':
        """
        Create a Stackfile instance from a JSON string.

        :param json_str: JSON string to convert.
        :return: Stackfile instance.
        """
        content = json.loads(json_str)
        stackfile = Stackfile(content)
        return stackfile


    @staticmethod
    def from_json_file(json_file: str) -> 'Stackfile':
        """
        Create a Stackfile instance from a JSON file.

        :param json_file: Path to the JSON file.
        :return: Stackfile instance.
        """
        with open(json_file, 'r') as f:
            content = json.load(f)
        stackfile = Stackfile(content)
        return stackfile


    @staticmethod
    def from_yaml(yaml_str: str) -> 'Stackfile':
        """
        Create a Stackfile instance from a JSON string.

        :param yaml_str: JSON string to convert.
        :return: Stackfile instance.
        """
        content = yaml_to_dict(yaml_str)
        stackfile = Stackfile(content)
        return stackfile


    @staticmethod
    def from_yaml_file(yaml_file: str) -> 'Stackfile':
        """
        Create a Stackfile instance from a YAML file.

        :param yaml_file: Path to the YAML file.
        :return: Stackfile instance.
        """
        with open(yaml_file, 'r') as f:
            content = yaml_to_dict(f.read())
        stackfile = Stackfile(content)
        return stackfile