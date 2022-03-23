from flask import Blueprint, render_template, abort

from nickel_club.model import ClubMember

bp = Blueprint("public", __name__, template_folder='templates')


@bp.route("/about", methods=("GET",))
def about():
    return render_template("public/about.html")

@bp.route("/member/<int:member_id>", methods=["GET"])
def member(member_id):
    member = ClubMember.query.filter_by(id=member_id).first()
    if member is None:
        abort(400)
    return render_template("public/member.html", member=member)
