from flask import (
    Blueprint,
    request,
    render_template,
)
from libs.validate import AddForm, ManageForm, GenerateForm

faq = Blueprint("faq", __name__, url_prefix="/faq")


@faq.route("/privacy")
def privacy():
    return render_template("faq/privacy.html")


@faq.route("/terms")
def terms():
    return render_template("faq/terms.html")


@faq.route("/about")
def about():
    return render_template("faq/about.html")


@faq.route("/contact")
def contact():
    return render_template("faq/contact.html")
