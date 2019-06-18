# -*- coding: utf-8 -*-

import os

from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher

from server.app import app

dispatcher = PathInfoDispatcher({"/": app})
host = os.environ.get("HOST")
port = int(os.environ.get("PORT"))
server = WSGIServer(
    (host, port), dispatcher, numthreads=0, max=9, request_queue_size=-1
)

if __name__ == "__main__":
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
