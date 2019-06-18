# -*- coding: utf-8 -*-

import os

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from server.app import app

port = os.environ.get("PORT")
server = HTTPServer(WSGIContainer(app))
server.bind(port)
server.start(9)
IOLoop.current().start()
