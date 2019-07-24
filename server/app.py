import os

import connexion  # type: ignore
from flask_cors import CORS as cors  # type: ignore


con = connexion.App("server", specification_dir=".")
con.add_api("api.yaml")
app = con.app
cors(app, origins="*")


if __name__ == "__main__":
    con.run(host=os.environ.get("HOST"), port=os.environ.get("PORT"))
