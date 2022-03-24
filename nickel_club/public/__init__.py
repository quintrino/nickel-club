from flask import Blueprint, render_template, abort, g, request, flash, redirect, url_for

from nickel_club.model import db, ClubMember, NickelRequest, NickelRequestType

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


@bp.route("/member/<int:member_id>/nickel-request", methods=["POST"])
def nickel_request(member_id):
    # todo: might be nicer to add a from string contructor to the Enum class
    match request.form["request_type"]:
        case "credit":
            request_type = NickelRequestType.credit
        case "debit":
            request_type = NickelRequestType.debit
        case _:
            abort(400)

    nickel_request = NickelRequest(
        amount = request.form["amount"],
        reason = request.form["reason"],
        request_type = request_type,
        member_id = member_id
    )
    db.session.add(nickel_request)
    db.session.commit()
    flash("Request submitted")
    return redirect(url_for('public.member', member_id=member_id))


@bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    members = ClubMember.query.order_by(ClubMember.nickels.desc()).all()
    return render_template("public/leaderboard.html", members=members)
