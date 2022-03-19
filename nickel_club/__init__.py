__version__ = '0.1.0'

import os

from flask import Flask


# def create_app(test_config=None):
def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # TODO: this is local dev only
    app.config['SECRET_KEY'] = "dev"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://james@localhost/testDatabase'
    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile("config.py", silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.update(test_config)

    from nickel_club import model
    model.init_app(app)

    from nickel_club import admin
    app.register_blueprint(admin.bp)

    from nickel_club import about
    app.register_blueprint(about.bp)

    app.add_url_rule("/", endpoint="about.index")

    return app
