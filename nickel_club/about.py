from flask import Blueprint
from flask import render_template

bp = Blueprint("about", __name__, url_prefix="/about")


@bp.route("/", methods=("GET",))
def index():
    return render_template("about.html")


bp.add_url_rule("/", endpoint="index")
