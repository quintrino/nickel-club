from flask import Blueprint
from flask import render_template

bp = Blueprint("public", __name__, url_prefix=None)


@bp.route("/about", methods=("GET",))
def about():
    return render_template("about.html")
