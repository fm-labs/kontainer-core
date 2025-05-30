import os
import subprocess

RDOCKER_BIN = os.environ.get("RDOCKER_BIN", default="rdocker")

def rdocker_tunnel_up(context: str):
    """
    Run the rdocker tunnel up command.
    """

    try:
        env = os.environ.copy()
        env["RDOCKER_CONTEXT"] = context
        #env["RDOCKER_HOST"] = ""
        result = subprocess.run([RDOCKER_BIN, "tunnel", "up"],
                                check=True,
                                env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Print the output
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

    return True


def rdocker_tunnel_down(context: str):
    """
    Run the rdocker tunnel down command.
    """

    try:
        env = os.environ.copy()
        env["RDOCKER_CONTEXT"] = context
        #env["RDOCKER_HOST"] = ""
        result = subprocess.run([RDOCKER_BIN, "tunnel", "down"],
                                check=True,
                                env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Print the output
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

    return True