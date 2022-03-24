from enum import Enum

import click
from flask import g
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


class ClubMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    nickels = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<ClubMember %r>" % self.name


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return "<AdminUser %r>" % self.username


class NickelRequestType(Enum):
    debit = 1
    credit = 2


class NickelRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(NickelRequestType), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.UnicodeText)


def init_db():
    """Clear existing data and create new tables."""
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def set_admin_password(password):
    hashed = generate_password_hash(password)

    admin = AdminUser.query.first()
    if admin is None:
        # create it
        admin = AdminUser(password=hashed)
        db.session.add(admin)
    else:
        admin.password = hashed
    db.session.commit()


@click.command("set-admin-password")
@click.argument("password")
@with_appcontext
def set_admin_password_command(password):
    set_admin_password(password)
    click.echo(f"Updated admin password")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(set_admin_password_command)
