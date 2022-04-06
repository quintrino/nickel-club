from flask import (
    Blueprint,
    current_app,
    render_template,
    abort,
    g,
    request,
    flash,
    redirect,
    url_for,
)
import requests

from nickel_club.model import db, ClubMember, NickelRequest

bp = Blueprint("public", __name__, template_folder="templates")


@bp.route("/about", methods=("GET",))
def about():
    with open("nickel_club/static/about.md") as f:
        about_md = f.read()
    return render_template("public/about.html", about_md=about_md)


@bp.route("/member/<int:member_id>", methods=["GET"])
def member(member_id):
    member = ClubMember.get_not_deleted_or_404(member_id)
    return render_template("public/member.html", member=member)


@bp.route("/member/<int:member_id>/nickel-request", methods=["POST"])
def nickel_request(member_id):
    # ensure the member exists and is not deleted
    member = ClubMember.get_not_deleted_or_404(member_id)

    try:
        amount = int(request.form["amount"])
    except ValueError:
        abort(400)

    match request.form["request_type"]:
        case "debit":
            pass
        case "credit":
            amount *= -1
        case _:
            abort(400)

    nickel_request = NickelRequest(
        amount=amount,
        reason=request.form["reason"],
        member_id=member_id,
    )
    db.session.add(nickel_request)
    db.session.commit()
    flash("Request submitted")

    fire_webhook(nickel_request)
    return redirect(url_for("public.member", member_id=member_id))


def fire_webhook(nickel_request):
    """If the app configuration contains a nickel request webhook url,
    we notify the endpoint of each new nickel request
    """
    url = current_app.config.get("NICKEL_REQUEST_WEBHOOK_URL")
    if url is None:
        current_app.logger.info("No nickel request webhook configured")
        return

    json = {
        "club_member": nickel_request.club_member.name,
        "amount": nickel_request.amount,
        "reason": nickel_request.reason,
    }

    current_app.logger.info(f"Nickel request web hook found:\n\t{url=}")
    current_app.logger.info("\tNotifying endpoint of new nickel request...")
    response = requests.post(url, json=json)
    if response.status_code == 200:
        current_app.logger.info("\tOK")
    else:
        current_app.logger.info(
            f"\tThe webhook endpoint returned {response.status_code}"
        )


@bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    members = ClubMember.not_deleted().order_by(ClubMember.nickels.desc()).all()
    return render_template("public/leaderboard.html", members=members)
