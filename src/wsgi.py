
#from kontainer.app import app
from kontainer.srv import app # ! Importing from 'srv' module not 'app' module !
from kontainer import settings


if __name__ == '__main__':

    host = settings.KONTAINER_HOST
    port = settings.KONTAINER_PORT

    print(f"KONTAINER_DATA_DIR: {settings.KONTAINER_DATA_DIR}")
    print(f"KONTAINER_DATA_HOME: {settings.KONTAINER_DATA_HOME}")
    print(f"Starting webserver available at http://{host}:{port}")

    app.run(debug=False, port=port, host=host)
