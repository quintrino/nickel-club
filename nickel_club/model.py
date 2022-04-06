from enum import Enum

import click
from flask import (
    g,
    abort,
)
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
    deleted = db.Column(
        db.Boolean, nullable=False, default=False, server_default="false"
    )

    requests = db.relationship("NickelRequest", backref="club_member", lazy=False)

    def __repr__(self):
        return "<ClubMember %r>" % self.name

    @staticmethod
    def not_deleted():
        return ClubMember.query.filter_by(deleted=False)

    @staticmethod 
    def get_not_deleted_or_404(member_id):
        member = ClubMember.query.get_or_404(member_id)
        if member.deleted:
            abort(404)

        return member

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return "<AdminUser %r>" % self.id


class NickelRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.UnicodeText)
    member_id = db.Column(db.Integer, db.ForeignKey("club_member.id"), nullable=False)

    @staticmethod
    def member_not_deleted():
        return NickelRequest.query.filter(NickelRequest.club_member.has(deleted=False))

    def explain(self):
        if self.amount > 0:
            return f"{self.club_member.name} asked for {self.amount} nickels."
        else:
            return f"{self.club_member.name} wants to spend {abs(self.amount)} nickels."

    def request_type(self):
        return "debit" if self.amount > 0 else "credit"

    def __str__(self):
        return f"<NickelRequest {self.id}, amount={self.amount}, member_id={self.member_id}>"


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
