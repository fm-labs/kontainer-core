import sys
sys.path.append("./src")

from kontainer.settings import KONTAINER_HOST, KONTAINER_PORT # TODO: Chech this [mstvb] Replaced with Specific Imports
from kontainer.settings import KONTAINER_DEBUG, KONTAINER_DATA_DIR # TODO: Check this [mstvb] Replaced with specific Imports
from kontainer.srv import app # ! Importing from 'srv' module not 'app' module !

# Make sure all tasks are imported, so that Celery can find them
from kontainer.admin.tasks import *
from kontainer.docker.tasks import *
from kontainer.stacks.tasks import *


if __name__ == '__main__':
    #host = os.getenv("KONTAINER_HOST", "127.0.0.1")
    #port = int(os.getenv("KONTAINER_PORT", "5000"))

    host = KONTAINER_HOST
    port = KONTAINER_PORT
    debug = KONTAINER_DEBUG

    print(f"KONTAINER_DATA_DIR: {KONTAINER_DATA_DIR}")
    #print(f"KONTAINER_DATA_HOME: {settings.KONTAINER_DATA_HOME}")
    print(f"Starting webserver on port {port}")

    app.run(debug=debug, port=port, host=host)
