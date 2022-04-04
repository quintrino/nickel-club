from enum import Enum

import click
from flask import g
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

class ClubMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    nickels = db.Column(db.Integer, nullable=False)
    deleted = db.Column(db.Boolean, nullable=False, default=False, server_default='false')

    requests = db.relationship("NickelRequest", backref="club_member", lazy=False)

    def __repr__(self):
        return "<ClubMember %r>" % self.name


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return "<AdminUser %r>" % self.id


class NickelRequestType(Enum):
    debit = 1
    credit = 2


class NickelRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.Enum(NickelRequestType), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.UnicodeText)
    member_id = db.Column(db.Integer, db.ForeignKey("club_member.id"), nullable=False)

    def explain(self):
        match self.request_type:
            case NickelRequestType.debit:
                return f"{self.club_member.name} asked for {self.amount} nickels."
            case NickelRequestType.credit:
                return f"{self.club_member.name} wants to spend {self.amount} nickels."


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
    # register app with flask-sqlalchemy
    db.init_app(app)
    # register app with flask-migrate
    migrate.init_app(app, db)

    # add click commands for database operations
    app.cli.add_command(set_admin_password_command)

