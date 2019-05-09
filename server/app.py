# -*- coding: utf-8 -*-
import connexion
import sys
from flask_cors import CORS

sys.path.append("..")


def create_app() -> connexion.apps.flask_app.FlaskApp:
    app = connexion.App("server", specification_dir=".")
    app.add_api("api.yaml")
    CORS(app.app, origins="*")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
