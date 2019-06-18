# -*- coding: utf-8 -*-

import connexion
import os

from flask_cors import CORS as cors

con = connexion.App("server", specification_dir=".")
app = con.app
con.add_api("api.yaml")
cors(app, origins="*")

if __name__ == "__main__":
    con.run(
        host=os.environ.get("HOST", "127.0.0.1"), port=os.environ.get("PORT", "5000")
    )
