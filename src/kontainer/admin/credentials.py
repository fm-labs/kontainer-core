import os.path

from kontainer import settings

CONFIG_DIR = os.path.join(settings.KONTAINER_DATA_DIR, 'config')
KEYS_DIR = os.path.join(CONFIG_DIR, 'keys')
KEYS_FILE_SUFFIX = '.key'

def find_private_keys():
    """
    Returns a list of private keys.
    Looks for all files with a .key extension in the keys directory and returns a list of private key names.
    """
    private_keys = []

    os.makedirs(KEYS_DIR, exist_ok=True)
    for entry in os.scandir(KEYS_DIR):
        if entry.is_file() and entry.name.endswith(KEYS_FILE_SUFFIX):
            private_keys.append(entry.name.replace(KEYS_FILE_SUFFIX, ''))

    return private_keys


def private_key_exists(name: str) -> bool | str:
    """
    Checks if a private key exists.

    :param name: Name of the private key
    :return: Path to the private key file if it exists, False otherwise
    """
    key_file = os.path.join(KEYS_DIR, f"{name}{KEYS_FILE_SUFFIX}")
    if os.path.exists(key_file):
        return key_file

    return False


def read_private_key(name: str) -> str:
    """
    Reads the content of a private key.

    :param name: Name of the private key
    :return: Content of the private key
    """
    key_file = os.path.join(KEYS_DIR, f"{name}{KEYS_FILE_SUFFIX}")

    with open(key_file, 'r') as f:
        return f.read()


def write_private_key(name: str, content: str) -> str:
    """
    Writes a private key to a file.

    :param name: Name of the private key
    :param content: Content of the private key
    :return: Path to the new private key file
    """
    os.makedirs(KEYS_DIR, exist_ok=True)
    key_file = os.path.join(KEYS_DIR, f"{name}{KEYS_FILE_SUFFIX}")

    original_umask = os.umask(0o022)

    try:

        # Set umask to restrict permissions (only owner read/write)
        os.umask(0o177)  # This ensures new files get 0600 permissions

        with open(key_file, 'w') as f:
            f.write(content.strip())
            f.write('\n') # ensure a newline at EOF

        # set proper permissions on the key file
        os.chmod(key_file, 0o600)

    finally:
        os.umask(original_umask)

    return key_file


def delete_private_key(name: str):
    """
    Deletes a private key.

    :param name: Name of the private key
    """
    key_file = os.path.join(KEYS_DIR, f"{name}{KEYS_FILE_SUFFIX}")

    if os.path.exists(key_file):
        os.remove(key_file)
    else:
        raise FileNotFoundError(f"Private key {name} does not exist")