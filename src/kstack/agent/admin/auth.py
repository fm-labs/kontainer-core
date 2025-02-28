import os

from kstack.agent import settings

def init_admin_credentials_file(initial_user="admin", initial_password="admin"):
    admin_credentials_file = os.path.join(settings.AGENT_DATA_DIR, "admin_credentials")
    if os.path.exists(admin_credentials_file):
        return

    with open(admin_credentials_file, 'w') as f:
        f.write(f"{initial_user}:{initial_password}\n")


def parse_admin_credentials_file():
    admin_credentials_file = os.path.join(settings.AGENT_DATA_DIR, "admin_credentials")
    if not os.path.exists(admin_credentials_file):
        raise ValueError("Admin credentials file not found")

    admin_credentials = []
    with open(admin_credentials_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            username, password = line.split(":")
            admin_credentials.append((username, password))

    return admin_credentials


def validate_admin_credentials_from_file(username, password) -> bool:
    """
    Validate the admin credentials from the admin_credentials file.
    The credentials are stored in the format: username:password
    Each line in the file is a new set of credentials.
    """
    admin_credentials = parse_admin_credentials_file()
    for cred in admin_credentials:
        if username == cred[0] and password == cred[1]:
            return True

    return False


def change_admin_credentials_from_file(username, password) -> bool:
    """
    Change the admin credentials in the admin_credentials file.
    The credentials are stored in the format: username:password
    Each line in the file is a new set of credentials.
    """
    admin_credentials = parse_admin_credentials_file()
    new_admin_credentials = []
    for cred in admin_credentials:
        if username == cred[0]:
            new_admin_credentials.append((username, password))
        else:
            new_admin_credentials.append(cred)

    admin_credentials_file = os.path.join(settings.AGENT_DATA_DIR, "admin_credentials")
    with open(admin_credentials_file, 'w') as f:
        for cred in new_admin_credentials:
            f.write(f"{cred[0]}:{cred[1]}\n")

    return True


def validate_admin_credentials_simple(username, password):
    admin_username = settings.AGENT_ADMIN_USERNAME
    admin_password_file = settings.AGENT_ADMIN_PASSWORD_FILE
    admin_password = None

    if admin_password_file and os.path.exists(admin_password_file):
        with open(admin_password_file, 'r') as f:
            admin_password = f.read().strip()

    if not admin_username or not admin_password:
        raise ValueError("Admin credentials not set")

    if username == admin_username and password == admin_password:
        return True

    return False


def change_admin_credentials_simple(username, password):
    admin_password_file = settings.AGENT_ADMIN_PASSWORD_FILE
    with open(admin_password_file, 'w') as f:
        f.write(password)

    return True