import os

import yaml


def prepend_path_prefix(volume, prefix):
    """Prepend a path prefix to the host path in a volume mount."""
    parts = volume.split(":")
    if len(parts) > 1 and not os.path.isabs(parts[0]):  # Only modify relative host paths
        parts[0] = os.path.join(prefix, parts[0])
    return ":".join(parts)


def modify_docker_compose(file_path, output_path, prefix):
    """Read, modify, and save the docker-compose.yml file with updated volume mounts."""
    with open(file_path, "r") as file:
        compose_data = yaml.safe_load(file)

    if "services" in compose_data:
        for service, config in compose_data["services"].items():
            if "volumes" in config:
                config["volumes"] = [prepend_path_prefix(vol, prefix) for vol in config["volumes"]]

    with open(output_path, "w") as file:
        yaml.dump(compose_data, file, default_flow_style=False)

    print(f"Modified docker-compose.yml saved to {output_path}")
