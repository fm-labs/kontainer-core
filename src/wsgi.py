
from kstack.agent.app import app
from kstack.agent import settings

if __name__ == '__main__':
    #host = os.getenv("AGENT_HOST", "127.0.0.1")
    #port = int(os.getenv("AGENT_PORT", "5000"))

    host = settings.AGENT_HOST
    port = settings.AGENT_PORT

    print(f"Starting webserver on port {port}")
    app.run(debug=True, port=port, host=host)
