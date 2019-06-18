# -*- coding: utf-8 -*-

import os

import bjoern

from server.app import app

host = os.environ.get("HOST")
port = int(os.environ.get("PORT"))

if __name__ == "__main__":
    bjoern.run(app, host, port, reuse_port=True)
