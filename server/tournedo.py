from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import app

server = HTTPServer(app)
server.bind(5000)
server.start(9)
IOLoop.current().start()
