import os
import bjoern
from app import app

host = os.environ.get("HOST", "127.0.0.1")
port = os.environ.get("PORT", 5000)

if __name__ == '__main__':
    bjoern.run(app, host, port)
