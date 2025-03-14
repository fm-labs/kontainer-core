
#from kstack.agent.app import app
from kstack.agent.srv import app # ! Importing from 'srv' module not 'app' module !
from kstack.agent import settings


if __name__ == '__main__':

    host = settings.AGENT_HOST
    port = settings.AGENT_PORT

    print(f"Starting webserver available at http://{host}:{port}")
    app.run(debug=False, port=port, host=host)
