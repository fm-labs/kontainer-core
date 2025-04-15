import sys

sys.path.append("./src")

from kontainer.srv import app # ! Importing from 'srv' module not 'app' module !
from kontainer import settings

# Make sure all tasks are imported, so that Celery can find them
from kontainer.celery import celery
from kontainer.admin.tasks import *
from kontainer.docker.tasks import *
from kontainer.stacks.tasks import *


if __name__ == '__main__':
    #host = os.getenv("KONTAINER_HOST", "127.0.0.1")
    #port = int(os.getenv("KONTAINER_PORT", "5000"))

    host = settings.KONTAINER_HOST
    port = settings.KONTAINER_PORT
    debug = settings.KONTAINER_DEBUG

    print(f"KONTAINER_DATA_DIR: {settings.KONTAINER_DATA_DIR}")
    print(f"KONTAINER_DATA_HOME: {settings.KONTAINER_DATA_HOME}")
    print(f"Starting webserver on port {port}")

    app.run(debug=debug, port=port, host=host)
