import os
import subprocess

# Fetch the port from environment variable or use 10000 by default
port = int(os.getenv("default_port", "10000"))
app  = "live_chat.asgi:application"  # Path to your ASGI application

if __name__ == "__main__":
    # Create the arguments for Daphne
    args = [
        "daphne",           # The Daphne command itself
        f"--port={port}",   # Daphne expects `--port` flag
        app                 # The ASGI application path
    ]

    print("Running command:", ' '.join(args))  # Optional for debugging

    # Run the Daphne server with subprocess
    subprocess.run(args)
