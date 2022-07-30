import functools
from flask import (
    current_app,
    Blueprint,
    flash,
    g,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flask_sqlalchemy import Pagination
from sqlalchemy import exc

from nickel_club.model import AdminUser, ClubMember, NickelRequest
from nickel_club.model import db, set_admin_password

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
            # TODO redirect to previous destination
            return redirect(url_for("admin.members"))

        flash(error)
    return render_template("admin/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("admin.login"))


@bp.route("/members", methods=("GET",))
@admin_required
def members():
    members = ClubMember.not_deleted().order_by(ClubMember.id).all()
    return render_template("admin/members.html", members=members)


REQUESTS_PER_PAGE = 30


def get_paginated_requests(page=1) -> Pagination:
    nickel_requests = (
        NickelRequest.member_not_deleted()
        .order_by(
            # Proxy for most recent without getting dates involved
            NickelRequest.id.desc()
        )
        .paginate(page=page, per_page=REQUESTS_PER_PAGE)
    )

    return nickel_requests


@bp.route("/requests", methods=("GET",))
@admin_required
def requests():
    page = request.args.get("page", 1, type=int)
    nickel_requests = get_paginated_requests(page)
    return render_template(
        "admin/nickel_requests.html", nickel_requests=nickel_requests
    )


@bp.route("/deletemember/<int:member_id>")
@admin_required
def delete_member(member_id):
    member = ClubMember.get_not_deleted_or_404(member_id)

    member.deleted = True
    db.session.commit()
    flash(f"Removed {member.name} from Nickel Club.")
    return redirect(url_for("admin.members"))


@bp.route("/debitmember/<int:member_id>", methods=("POST",))
@admin_required
def debit_member(member_id):
    member = ClubMember.get_not_deleted_or_404(member_id)
    try:
        to_add = int(request.form["nickels"])
    except ValueError:
        abort(400)
    ''' Todo: I think good OO principles would dictate that objects are
    responsible for maintaining their own consistent state, so crediting and 
    debiting should be method calls on ClubMember, with debit handling setting 
    total_earnings
    '''
    member.nickels += to_add
    member.total_earnings += to_add
    db.session.commit()
    flash(f"Added {to_add} nickels to {member.name}'s account")
    return redirect(url_for("admin.members"))



@bp.route("/creditmember/<int:member_id>", methods=("POST",))
@admin_required
def credit_member(member_id):
    member = ClubMember.get_not_deleted_or_404(member_id)
    try:
        to_subtract = int(request.form["nickels"])
    except ValueError:
        abort(400)
    member.nickels -= to_subtract
    db.session.commit()
    flash(f"Subtracted {to_subtract} nickels from {member.name}'s account")
    return redirect(url_for("admin.members"))


'''
Todo: we should remove this route's ability to set nickels, since we can't 
tell whether they're being debited or credited, meaning we can't keep 
member.total_earnings in a consistent state. Once we've done that, the only 
thing it does is rename, so we should rename it to rename_member
'''
@bp.route("/member/<int:member_id>", methods=("POST",))
@admin_required
def member(member_id):
    """Allow updating both name and nickel balance of members"""

    member = ClubMember.get_not_deleted_or_404(member_id)
    if "nickels" not in request.form and "name" not in request.form:
        abort(400)

    try:
        member.nickels = int(request.form["nickels"])
        flash(f"Set {member.name}'s nickels to {member.nickels}")
    except ValueError:
        abort(400)
    except KeyError:
        # Since we've already checked that at least one of "nickels" and "name" are present,
        # this means the name, and not the nickels were being set
        pass

    try:
        old_name = member.name
        member.name = request.form["name"]
        flash(f"Renamed {old_name} to {member.name}")
    except KeyError:
        # Since we've already checked that at least one of "nickels" and "name" are present,
        # this means the nickels, and not the name were being set
        pass

    db.session.commit()
    return redirect(url_for("admin.members"))


@bp.route("/createmember", methods=["POST"])
@admin_required
def create_member():
    try:
        nickels = int(request.form.get("nickels")) or 0
    except ValueError:
        abort(400)
    name = request.form["name"]
    member = ClubMember(name=name, nickels=nickels)
    db.session.add(member)
    try:
        db.session.commit()
    except exc.IntegrityError as e:
        flash(f"A user named {name} already exists!")
    return redirect(url_for("admin.members"))


@bp.route("/settings")
@admin_required
def settings():
    return render_template("admin/settings.html")


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

    return redirect(url_for("admin.settings"))


bp.add_url_rule("/", endpoint="members")
