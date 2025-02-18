import sys

sys.path.append("./src")

from kstack.agent.srv import app # ! Importing from 'srv' module not 'app' module !
from kstack.agent import settings

# Make sure all tasks are imported, so that Celery can find them
from kstack.agent.celery import celery
from kstack.agent.admin.tasks import *
from kstack.agent.docker.tasks import *
from kstack.agent.stacks.tasks import *


if __name__ == '__main__':
    #host = os.getenv("AGENT_HOST", "127.0.0.1")
    #port = int(os.getenv("AGENT_PORT", "5000"))

    host = settings.AGENT_HOST
    port = settings.AGENT_PORT

    print(f"Starting webserver on port {port}")
    app.run(debug=True, port=port, host=host)
