from flask import Blueprint
from flask import render_template

bp = Blueprint("public", __name__, template_folder='templates')


@bp.route("/about", methods=("GET",))
def about():
    return render_template("public/about.html")
