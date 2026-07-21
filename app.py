import os

from flask import Flask

import db as db_module
from routes.public import public_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ganti-dengan-secret-key-anda")

    db_module.init_app(app)

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()


if __name__ == "__main__":
    db_module.init_db()
    app.run(debug=True)
