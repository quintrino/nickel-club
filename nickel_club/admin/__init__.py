import functools
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from sqlalchemy import exc

from nickel_club.model import AdminUser, ClubMember, db, set_admin_password

bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")

def admin_required(view):
    """View decorator that redirects anonymous users to the admin login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            return redirect(url_for("admin.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_admin():
    admin_id = session.get("admin_id")

    if admin_id is None:
        g.admin = None
    else:
        g.admin = AdminUser.query.filter_by(id=admin_id).first()


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        password = request.form["password"]

        error = None
        admin = AdminUser.query.first()

        if admin is None:
            error = "The admin password hasn't been created yet!"
        elif not check_password_hash(admin.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["admin_id"] = admin.id
            return redirect(url_for("admin.index"))

        flash(error)
    return render_template("admin/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("admin.login"))


@bp.route("/index", methods=("GET",))
@admin_required
def index():
    members = ClubMember.query.order_by(ClubMember.id).all()
    return render_template("admin/index.html", members=members)


@bp.route("/members/<int:member_id>", methods=("POST",))
@admin_required
def member(member_id):
    member = ClubMember.query.filter_by(id=member_id).first()
    member.nickels = request.form["nickels"]
    db.session.commit()
    flash(f"Set {member.name}'s nickels to {member.nickels}")
    return redirect(url_for("admin.index"))

@bp.route("/createmember", methods=["POST"])
@admin_required
def create_member():
    member = ClubMember(
        name = request.form["name"],
        nickels = request.form.get("nickels") or 0
    )
    db.session.add(member)
    db.session.commit()
    return redirect(url_for("admin.index"))


@bp.route("/admin-password", methods=("POST",))
@admin_required
def admin_password():
    password = request.form["new-password"]
    confirm_password = request.form["confirm-password"]

    if password == confirm_password:
        set_admin_password(password)
        flash("Admin password set.")
    else:
        flash("The passwords do not match.")

    return redirect(url_for("admin.index"))


bp.add_url_rule("/", endpoint="index")