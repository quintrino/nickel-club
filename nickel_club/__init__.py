__version__ = "0.1.0"

import os

from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file, if it exists.
# Does not override existing env variables. In this way, we can store dev
# configuration in a .env file that is not committed, while configuring on heroku using regular env variables
load_dotenv()


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            {
                "SECRET_KEY": os.getenv("SECRET_KEY"),
                "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL").replace(
                    "postgres://", "postgresql://", 1
                ),
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            }
        )
    else:
        # load the test config if passed in
        app.config.update(test_config)

    from nickel_club import model
    from nickel_club import admin
    from nickel_club import public

    model.init_app(app)

    app.register_blueprint(admin.bp)
    app.register_blueprint(public.bp)

    app.add_url_rule("/", endpoint="public.about")

    return app
