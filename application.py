# Core
import os
from datetime import timedelta

import custom_filter

from libs.Utils import User
from dal import get_dal

# Flask
from flask import Flask, render_template, redirect, request, session, flash, jsonify, url_for
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_seasurf import SeaSurf
# from authlib.integrations.flask_client import OAuth
# from authlib.
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


# from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
# from flask_security import current_user, login_user, logout_user

users = {
    "ninad.mhatre@gmail.com": generate_password_hash("n1"),
    "nmhatre@gmail.com": generate_password_hash("n2")
}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

_static_folder = os.path.join(BASE_DIR, 'static')
instance_dir = os.path.join(BASE_DIR, 'instance')

app = Flask(__name__, instance_path=instance_dir, static_folder=_static_folder, static_url_path='/static')

app.config.from_object('instance.default')
app.config.from_object('instance.{0}'.format(os.environ.get('APP_ENVIRONMENT', 'dev')))
app.config['BASE_DIR'] = BASE_DIR

# oauth = OAuth(app)
auth = HTTPBasicAuth()

dummy_users = {
    "ninad.mhatre@gmail.com": "gmail",
    "nmhatre@outlook.com": "outlook"
}

# fb_bp = make_facebook_blueprint(
#     client_id=app.config['FACEBOOK_OAUTH_CLIENT_ID'],
#     client_secret=app.config['FACEBOOK_OAUTH_CLIENT_SECRET'],
#     scope='id,name,email',
# )

# custom_logger = AppLogger(app.config['LOGGER'])
# app.logger.addHandler(custom_logger.get_log_handler(LoggerTypes.File))

csrf = SeaSurf(app)

# engine = create_engine('sqlite:///blog.db')
# meta = MetaData()

# sql_storage = SQLAStorage(engine, metadata=meta)
# blog_engine = BloggingEngine(app, sql_storage)
login_manager = LoginManager(app)
# meta.create_all(bind=engine)

# page_view_engine = create_engine('sqlite:///stats.db')
# page_view_meta = MetaData()

# page_view_storage = SqliteStorage(page_view_engine, metadata=page_view_meta)
# page_view_meta.create_all(bind=page_view_engine)
# page_view_stats = Informer(page_view_storage)


app.logger.info('Starting Application')

# Login manager settings

login_manager.session_protection = "strong"


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = app.config['SESSION_TIMEOUT']


@login_manager.needs_refresh_handler
def refresh():
    return redirect(url_for('auth.login'))


@login_manager.user_loader
def load_user(user_id):
    """
    This is called for every request to get the user name
    :param user_id:
    :return:
    """
    return User(user_id)


@auth.verify_password
def verify_password(username, password):
    print(f"username={username} | password={password}")

    if dummy_users.get(username, None) == password:
        user = User(user_id=username)
        login_user(user, duration=timedelta(minutes=5))

        return user


# Initialize Other Modules
# Modules which requires instance of 'app' to be created first!
# from model.StaticAssets import bundles, Environment

# asset = Environment(app)
# asset.init_app(app)
# asset.register(bundles)

@app.route('/')
def home():
    """
    Any guesses?
    :return:
    """
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    """
    Flask does not support having error handler in different blueprint!
    :param e: error
    :return: error page with error code
    """
    msg = "404: Page you are looking for does not exist!"
    return render_template('error_code/generic.html', err_msg=msg), 404


@app.errorhandler(401)
def unauthorized_access(e):
    msg = "401: You need to login to access this page, this incident will be reported!!"
    return render_template('error_code/generic.html', err_msg=msg), 401


@app.errorhandler(500)
def internal_server_error(e):
    msg = "500: Something just crashed! I am going to spend my day trying to " \
          "figure out what went wrong, wanna help??"
    return render_template('error_code/generic.html', err_msg=msg), 500


@app.route('/test')
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
        ("warn", "warning-num-5")
    ]

    for c, m in msgs:
        flash(m, c)

    return render_template('dump/dict.html', data=d)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = request.form.get('user')
        key = request.form.get('chaabi')

        if dummy_users.get(user) == key:
            user = User(user_id=user)
            login_user(user, duration=timedelta(minutes=5))

            return redirect('/')
        else:
            flash("login failed!!", "error")

    return render_template('login/login.html')


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        is_clear_cache = request.form.get("clear_cache")
        if is_clear_cache:
            db = get_dal()
            db.get_user_tags.cache_clear()

    return render_template('admin/admin.html')

# @app.route('/authorize')
# def authorize():
#     token = oauth.facebook.authorize_access_token()
#     resp = oauth.facebook.get('account/verify_credentials.json', token)
#     profile = resp.json()
#     breakpoint()
#     # do something with the token and profile
#     return redirect('/')

# Code Separated to Blueprints!
# from controller.file_io import fileio, fileio_init
# from controller.authentication import auth
# from controller.admin import admin
# from controller.apps import apps
from controller.tags import tags


# app.register_blueprint(apps)
# app.register_blueprint(admin)
app.register_blueprint(tags)
# app.register_blueprint(fb_bp, url_prefix='/login')

# login_manager.login_facebook_view = 'facebook.login'
# login_manager.login_view = 'login'


# @app.route("/index", methods=['GET', 'POST'])
# def index():
#     # if not facebook.authorized:
#         return redirect(url_for("facebook.login"))
#     resp = facebook.get("/me")
#     assert resp.ok, resp.text
#     return "You are {name} on Facebook".format(name=resp.json()["name"])


@app.route("/logout")
@login_required
def logout():
    auth.current_user()
    logout_user()
    flash("You have logged out")
    return redirect(url_for("login"))


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


# @fb_bp.connect_via(fb_bp)
# def logged_in(blueprint, token):
#     """
#     create/login local user on successful OAuth login with github
#     :param blueprint:
#     :param token:
#     :return:
#     """
#     breakpoint()
#     if not token:
#         flash("Failed to log in.", category="error")
#         return False
#
#     session = blueprint.session
#
#     resp = session.get("/user")
#
#     if not resp.ok:
#         msg = "Failed to fetch user info."
#         flash(msg, category="error")
#         return False
#
#     login_user(oauth.user)
#     flash("Successfully signed in.")
#
#     return False

if __name__ == '__main__':
    app.run(port=app.config['PORT'])
