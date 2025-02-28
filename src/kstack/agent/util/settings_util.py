import os


def get_or_create_jwt_secret(secret_file_path: str):
    if os.path.exists(secret_file_path):
        with open(secret_file_path, 'rb') as f:
            jwt_secret = f.read()

    else:
        jwt_secret = os.urandom(32)
        with open(secret_file_path, 'wb') as f:
            f.write(jwt_secret)

        print("Wrote new JWT secret to file", secret_file_path)

    return jwt_secret