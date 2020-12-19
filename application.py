# Core
import os

import custom_filter

from dal.dbobj import get_dal

# Flask
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    session,
    flash,
    jsonify,
    url_for,
)
from flask_login import (
    LoginManager,
    login_required,
)
from flask_seasurf import SeaSurf

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

_static_folder = os.path.join(BASE_DIR, "static")
instance_dir = os.path.join(BASE_DIR, "instance")
DAL = get_dal()

app = Flask(
    __name__,
    instance_path=instance_dir,
    static_folder=_static_folder,
    static_url_path="/static",
)

app.config.from_object("instance.default")
app.config.from_object("instance.{0}".format(os.environ.get("APP_ENVIRONMENT", "dev")))
app.config["BASE_DIR"] = BASE_DIR

csrf = SeaSurf(app)
login_manager = LoginManager(app)

app.logger.info("Starting Application")

# Login manager settings
login_manager.session_protection = "strong"
login_manager.refresh_view = "auth.login"
login_manager.needs_refresh_message = (
    "To protect your account, please re-authenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = app.config["SESSION_TIMEOUT"]


@login_manager.needs_refresh_handler
def refresh():
    return redirect(url_for("auth.login"))


@login_manager.user_loader
def load_user(user_id):
    """
    This is called for every request to get the user name
    :param user_id:
    :return:
    """
    return DAL.get_user_by_email(user_id)

# @auth.verify_password
# def verify_password(username, password):
#     if dummy_users.get(username, None) == password:
#         user = User(user_id=username)
#         login_user(user, duration=timedelta(minutes=5))
#
#         return user


@app.route("/")
def home():
    """
    Any guesses?
    :return:
    """
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    """
    Flask does not support having error handler in different blueprint!
    :param e: error
    :return: error page with error code
    """
    msg = "404: Page you are looking for does not exist!"
    return render_template("error_code/generic.html", err_msg=msg, title="404: Page Not Found"), 404


@app.errorhandler(401)
def re_login(e):
    return redirect(url_for('auth.login'), code=303)
    # msg = "401: You need to login to access this page, this incident will be reported!!"
    # return render_template("error_code/generic.html", err_msg=msg, title="401: Re-login"), 401


@app.errorhandler(403)
def unauthorized_access(e):
    msg = "403: You do not have access to this page"
    return render_template("error_code/generic.html", err_msg=msg, title="403: No Access!!"), 403


@app.errorhandler(500)
def internal_server_error(e):
    msg = (
        "500: Something just crashed! I am going to spend my day trying to "
        "figure out what went wrong, wanna help??"
    )
    return render_template("error_code/generic.html", err_msg=msg, title="500: Please retry"), 500


@app.route("/test")
@login_required
def test():
    d = {}
    for p in dir(request):
        d[p] = getattr(request, p)

    msgs = [
        ("info", "info msg-0"),
        ("error", "error msg-1"),
        ("warn", "warning-2"),
        ("error", "error-num-3"),
        ("info", "info-num-4"),
        ("warn", "warning-num-5"),
    ]

    for c, m in msgs:
        flash(m, c)

    return render_template("dump/dict.html", data=d)


# @app.route("/testlogin", methods=["GET", "POST"])
# def login_basic():
#     if request.method == "POST":
#         user = request.form.get("user")
#         key = request.form.get("chaabi")
#
#         if dummy_users.get(user) == key:
#             user = User(user_id=user)
#             login_user(user, duration=timedelta(minutes=5))
#
#             return redirect("/")
#         else:
#             flash("login failed!!", "error")
#
#     return render_template("login/login.html")


from controller.tags import tags
from controller.faq import faq
from controller.authentication import auth

app.register_blueprint(tags)
app.register_blueprint(faq)
app.register_blueprint(auth)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))

    return jsonify(links)


if __name__ == "__main__":
    app.run(port=app.config["PORT"])
