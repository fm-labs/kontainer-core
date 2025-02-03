import os
import sys

sys.path.append("./src")

from dockerhttp.server.app import app
from dockerhttp.server import settings

if __name__ == '__main__':
    #host = os.getenv("DOCKERHTTP_HOST", "127.0.0.1")
    #port = int(os.getenv("DOCKERHTTP_PORT", "5000"))

    host = settings.DOCKERHTTP_HOST
    port = settings.DOCKERHTTP_PORT

    print(f"Starting webserver on port {port}")
    app.run(debug=True, port=port, host=host)
