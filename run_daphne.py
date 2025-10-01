import os
import subprocess
from django.core.asgi import get_asgi_application

# Fetch the port from environment variable or use 10000 by default
port = int(os.getenv("default_port", "10000"))
app  = "live_chat.asgi:application"  # Path to your ASGI application


def main():
    args = [
        "daphne",
        f"--port={port}",
        app
    ]
    subprocess.run(args)

if __name__ == '__main__':
    # print(get_asgi_application())
    main()
