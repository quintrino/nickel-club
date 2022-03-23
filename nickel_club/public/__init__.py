from flask import Blueprint, render_template, abort

from nickel_club.model import ClubMember

bp = Blueprint("public", __name__, template_folder='templates')


@bp.route("/about", methods=("GET",))
def about():
    return render_template("public/about.html")

@bp.route("/member/<int:member_id>", methods=["GET"])
def member(member_id):
    member = ClubMember.query.get_or_404(member_id)
    return render_template("public/member.html", member=member)

@bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    members = ClubMember.query.order_by(ClubMember.nickels.desc()).all()
    return render_template("public/leaderboard.html", members=members)
