# Core
import os

import custom_filter

# Flask
from flask import (
    Flask,
    render_template,
    redirect,
    session,
    jsonify,
    url_for,
    abort,
)
from flask_login import (
    LoginManager, login_required, current_user
)
from flask_seasurf import SeaSurf

from controller.authentication import auth
from controller.faq import faq

# User
from controller.tags import tags
from dal.dbobj import get_dal
from libs.flask_log import LogSetup
from libs.utils import is_admin_user
from instance import get_admin_users

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

_static_folder = os.path.join(BASE_DIR, "static")
instance_dir = os.path.join(BASE_DIR, "instance")
DAL = get_dal()


class ReverseProxy(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if os.environ.get('APP_ENVIRONMENT', "prod") == "prod":
            environ['wsgi.url_scheme'] = "https"

        return self.app(environ, start_response)


app = Flask(
    __name__,
    instance_path=instance_dir,
    static_folder=_static_folder,
    static_url_path="/static",
)
app.wsgi_app = ReverseProxy(app.wsgi_app)

app.config.from_object("instance.default")
app.config.from_object("instance.{0}".format(os.environ.get("APP_ENVIRONMENT", "dev")))
app.config["BASE_DIR"] = BASE_DIR

log = LogSetup(app)
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


app.register_blueprint(tags)
app.register_blueprint(faq)
app.register_blueprint(auth)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/site-map")
@login_required
def site_map():
    if not is_admin_user(current_user.email, get_admin_users()):
        abort(403)

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
