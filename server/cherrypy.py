import os
from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher
from app import app

dispatcher = PathInfoDispatcher({'/': app})
host = os.environ.get("HOST", "127.0.0.1")
port = os.environ.get("PORT", 5000)
server = WSGIServer((host, port), dispatcher, numthreads=0, max=9, request_queue_size=-1)

if __name__ == '__main__':
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
