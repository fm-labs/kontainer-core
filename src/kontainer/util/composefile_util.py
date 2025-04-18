import os

import yaml

from kontainer.stacks.stackfile import Stackfile


def modify_docker_compose_volumes(file_path, output_path, prefix):
    """Read, modify, and save the docker-compose.yml file with updated volume mounts."""

    def prepend_volume_path_prefix(volume, prefix):
        """Prepend a path prefix to the host path in a volume mount."""
        parts = volume.split(":")
        if len(parts) == 2:
            host_path: str = parts[0]
            container_path: str = parts[1]
            perm = "rw"
        elif len(parts) == 3:
            host_path: str = parts[0]
            container_path: str = parts[1]
            perm = parts[2]
        else:
            #print(f"Invalid volume mount: {volume}")
            #return volume
            raise ValueError(f"Invalid volume mount: {volume}")

        if host_path.startswith("../") or ".." in host_path:
            raise ValueError(f"Relative parent path not allowed: {host_path}")
        elif host_path.startswith("./"):
            # relative host path
            parts[0] = os.path.join(prefix, host_path[2:])
            return ":".join(parts)
        elif host_path.startswith("/"):
            # absolute host path
            # @todo restrict to paths that are not absolute
            pass
        elif "/" in host_path:
            raise ValueError(f"Invalid host path: {host_path}")
        else:
            # docker volume
            pass
        return volume


    with open(file_path, "r") as file:
        compose_data = yaml.safe_load(file)

    if "services" in compose_data:
        for service, config in compose_data["services"].items():
            if "volumes" in config:
                config["volumes"] = [prepend_volume_path_prefix(vol, prefix) for vol in config["volumes"]]

    with open(output_path, "w") as file:
        yaml.dump(compose_data, file, default_flow_style=False)

    print(f"Modified docker-compose.yml saved to {output_path}")
