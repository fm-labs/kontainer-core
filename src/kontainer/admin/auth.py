import os
import hashlib
import binascii

from kontainer import settings

def get_admin_credentials_file():
    """
    Get the path to the admin credentials file.
    The file is located in the KONTAINER_DATA_DIR directory.
    """
    return os.path.join(settings.KONTAINER_DATA_DIR, "admin.credentials")


def init_admin_credentials_file(initial_user="admin", initial_password="admin"):
    admin_credentials_file = get_admin_credentials_file()
    if os.path.exists(get_admin_credentials_file()):
        return

    with open(admin_credentials_file, 'w') as f:
        f.write(f"{initial_user}:{create_password_hash(initial_password)}\n")

    print("Wrote initial admin credentials to file", admin_credentials_file)


def parse_admin_credentials_file():
    admin_credentials_file = get_admin_credentials_file()
    if not os.path.exists(admin_credentials_file):
        raise ValueError("Admin credentials file not found")

    admin_credentials = []
    with open(admin_credentials_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            username, password_hash = line.split(":", maxsplit=1)
            admin_credentials.append((username, password_hash))

    return admin_credentials


def validate_admin_credentials(username, password_plain) -> bool:
    """
    Validate the admin credentials from the admin_credentials file.
    The credentials are stored in the format: username:password
    Each line in the file is a new set of credentials.
    """
    admin_credentials = parse_admin_credentials_file()
    for cred in admin_credentials:
        if username == cred[0] and validate_password_hash(password_plain, cred[1]):
            return True

    return False


def change_admin_credentials(username, password) -> bool:
    """
    Change the admin credentials in the admin_credentials file.
    The credentials are stored in the format: username:password
    Each line in the file is a new set of credentials.

    :param username: The username to change or add.
    :param password: The new plain password for the username.
    """
    admin_credentials = parse_admin_credentials_file()
    new_admin_credentials = []
    for cred in admin_credentials:
        if username == cred[0]:
            new_password_hash = create_password_hash(password)
            new_admin_credentials.append((username, new_password_hash))
        else:
            new_admin_credentials.append(cred)

    with open(get_admin_credentials_file(), 'w') as f:
        for cred in new_admin_credentials:
            f.write(f"{cred[0]}:{cred[1]}\n")

    return True


def create_password_hash(password_plain: str) -> str:
    """
    Create a password hash using PKCS#5 PBKDF2 with SHA-256 and iterations.

    The hash is stored in the format: salt$hash$iterations
    where:
    - salt is the random salt used during hashing (hex-encoded)
    - hash is the derived key (hex-encoded)
    - iterations is the number of iterations used in PBKDF2

    :param password_plain: The plain text password to hash.
    :return: The hashed password in the format described above.
    """
    # Generate a random salt
    salt = os.urandom(16)

    # Use PBKDF2 to hash the password with the salt
    iterations = 100000
    dk = hashlib.pbkdf2_hmac('sha256', password_plain.encode(), salt, iterations)

    # Combine the salt and hash into a single string
    password_hash = binascii.hexlify(salt).decode() + '$' + binascii.hexlify(dk).decode() + f'${iterations}'

    return password_hash


def validate_password_hash(password_plain: str, expected_hash: str) -> bool:
    """
    Validate a password against a stored hash.
    The expected hash is in the format: salt$hash$iterations
    where:
    - salt is the random salt used during hashing (hex-encoded)
    - hash is the derived key (hex-encoded)
    - iterations is the number of iterations used in PBKDF2

    :param password_plain: The plain text password to validate.
    :param expected_hash: The expected hash in the format described above.
    :return: True if the password matches the hash, False otherwise.
    """

    # Split the expected hash into its components
    parts = expected_hash.split('$')
    if len(parts) != 3:
        raise ValueError("Invalid password hash format")
    salt_hex, hash_hex, iterations_str = parts
    salt = binascii.unhexlify(salt_hex)
    expected_dk = binascii.unhexlify(hash_hex)
    iterations = int(iterations_str)
    # Use PBKDF2 to hash the provided password with the same salt and iterations
    dk = hashlib.pbkdf2_hmac('sha256', password_plain.encode(), salt, iterations)
    # Compare the derived key with the expected hash
    return dk == expected_dk


# def validate_admin_credentials_simple(username, password):
#     admin_username = settings.KONTAINER_ADMIN_USERNAME
#     admin_password_file = settings.KONTAINER_ADMIN_PASSWORD_FILE
#     admin_password = None
#
#     if admin_password_file and os.path.exists(admin_password_file):
#         with open(admin_password_file, 'r') as f:
#             admin_password = f.read().strip()
#
#     if not admin_username or not admin_password:
#         raise ValueError("Admin credentials not set")
#
#     if username == admin_username and password == admin_password:
#         return True
#
#     return False


# def change_admin_credentials_simple(username, password):
#     admin_password_file = settings.KONTAINER_ADMIN_PASSWORD_FILE
#     with open(admin_password_file, 'w') as f:
#         f.write(password)
#
#     return True