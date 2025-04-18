import json
import yaml


def json_to_yaml_string(json_str: str) -> str:
    """
    Convert a JSON string to a YAML string.

    :param json_str: JSON string to convert.
    :return: Converted YAML string.
    """
    data = json.loads(json_str)
    yaml_str = yaml.dump(data, default_flow_style=False)
    return yaml_str


def yaml_to_json_string(yaml_str: str) -> str:
    """
    Convert a YAML string to a JSON string.

    :param yaml_str: YAML string to convert.
    :return: Converted JSON string.
    """
    data = yaml.safe_load(yaml_str)
    json_str = json.dumps(data, indent=2)
    return json_str


def yaml_to_dict(yaml_str: str) -> dict:
    """
    Convert a YAML string to a dictionary.

    :param yaml_str: YAML string to convert.
    :return: Converted dictionary.
    """
    data = yaml.safe_load(yaml_str)
    return data


def dict_to_yaml_string(data: dict) -> str:
    """
    Convert a dictionary to a YAML string.

    :param data: Dictionary to convert.
    :return: Converted YAML string.
    """
    yaml_str = yaml.dump(data, default_flow_style=False)
    return yaml_str


def json_to_yaml_file(json_path: str, yaml_path: str) -> None:
    """
    Convert a JSON file to a YAML file.

    :param json_path: Path to the JSON file.
    :param yaml_path: Path to the output YAML file.
    """
    with open(json_path, 'r') as jf:
        data = json.load(jf)
    with open(yaml_path, 'w') as yf:
        yaml.dump(data, yf, default_flow_style=False)
    print(f"Converted JSON → YAML: {yaml_path}")


def yaml_to_json_file(yaml_path: str, json_path: str) -> None:
    """
    Convert a YAML file to a JSON file.

    :param yaml_path: Path to the YAML file.
    :param json_path: Path to the output JSON file.
    """
    with open(yaml_path, 'r') as yf:
        data = yaml.safe_load(yf)
    with open(json_path, 'w') as jf:
        json.dump(data, jf, indent=2)
    print(f"Converted YAML → JSON: {json_path}")
