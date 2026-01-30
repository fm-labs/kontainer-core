
#from kontainer.app import app
from kontainer.srv import app # ! Importing from 'srv' module not 'app' module !

from kontainer.settings import KONTAINER_HOST, KONTAINER_PORT # TODO: Check this [mstvb] Replaced with Specific Imports
from kontainer.settings import KONTAINER_DATA_DIR, DOCKER_HOME # TODO: Check this [mstvb] Replaced with Specific Imports

if __name__ == '__main__':

    host = KONTAINER_HOST
    port = KONTAINER_PORT

    print(f"KONTAINER_DATA_DIR: {KONTAINER_DATA_DIR}") 
    print(f"KONTAINER_DATA_HOME: {DOCKER_HOME}") # TODO: Check This [mstvb] DATA HOME not founded replaced with DOCKER_HOME
    print(f"Starting webserver available at http://{host}:{port}")

    app.run(debug=False, port=port, host=host)
