import os, uvicorn

default_port = os.getenv("default_port", 10000)
app = "live_chat.asgi.application"

if __name__ == "__main__":
    uvicorn.run(app=app, port=default_port, reload=True)
