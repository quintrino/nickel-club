from flask import Blueprint, render_template, abort, g

from nickel_club.model import ClubMember

bp = Blueprint("public", __name__, template_folder='templates')


@bp.route("/about", methods=("GET",))
def about():
    with open("nickel_club/static/about.md") as f:
        about_md = f.read()
    return render_template("public/about.html", about_md=about_md)

@bp.route("/member/<int:member_id>", methods=["GET"])
def member(member_id):
    member = ClubMember.query.get_or_404(member_id)
    return render_template("public/member.html", member=member)

@bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    members = ClubMember.query.order_by(ClubMember.nickels.desc()).all()
    return render_template("public/leaderboard.html", members=members)
