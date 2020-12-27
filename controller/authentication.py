import json
from datetime import timedelta
from functools import lru_cache as cache

import requests
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
    abort
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)
from oauthlib.oauth2 import WebApplicationClient

from dal.dbobj import get_dal
from instance import get_oauth_details, get_admin_users
from libs.dt import User
from libs.utils import is_admin_user

__OAUTH_INFO = get_oauth_details()

auth = Blueprint("auth", __name__, url_prefix="/auth")

client = WebApplicationClient(__OAUTH_INFO.cl_id)

DAL = get_dal()


@cache()
def get_google_provider_cfg():
    discovery_url = __OAUTH_INFO.discovery_url
    return requests.get(discovery_url).json()


@auth.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["email"],
    )
    return redirect(request_uri)


@auth.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(
            current_app.config["GOOGLE_CLIENT_ID"],
            current_app.config["GOOGLE_CLIENT_SECRET"],
        ),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # user_resp={'sub': '100200154771991934741',
    # 'picture': 'https://lh3.googleusercontent.com/a-/AOh14Gj65LOOJBS0hUCpvR_qtPL9rlEPNt6_5-GzUfzLUN4=s96-c',
    # 'email': 'ninad.mhatre@gmail.com',
    # 'email_verified': True}
    user_resp = userinfo_response.json()

    if user_resp.get("email_verified"):
        unique_id = user_resp["sub"]
        users_email = user_resp["email"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(id_=unique_id, email=users_email, access_token=client.access_token)

    if not DAL.is_existing_user(unique_id, is_get_by_email=False):
        user = DAL.add_user(user)

    # Begin user session by logging the user in
    if user:
        login_user(user, duration=timedelta(hours=6))
        DAL.save_token(user)
    else:
        flash(f"failed to create/login {users_email}!!", "error")
    return redirect(url_for("home"))


@auth.route("/logout", methods=["GET"])
@login_required
def logout():
    user_email = current_user.email
    logout_user()

    if not revoke_token(user_email):
        flash(
            "logged out from app but re-login will log you in with same user!!", "error"
        )

    DAL.clear_token(user_email)
    return redirect(url_for("home"))


@auth.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if not is_admin_user(current_user.email, get_admin_users()):
        abort(403)

    if request.method == "POST":
        is_clear_cache = request.form.get("clear_cache")
        if is_clear_cache:
            DAL.get_user_tags.cache_clear()

    info = {
        'user_count': DAL.get_user_count()
    }

    return render_template("admin/admin.html", info=info)


def revoke_token(user_email: str):
    if user_email is None:
        return

    user = DAL.get_user_by_email(user_email)

    revoke = requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": user.access_token},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    status_code = getattr(revoke, "status_code")
    if status_code == 200:
        current_app.logger.info("Credentials successfully revoked.")
        is_successful = True
    else:
        current_app.logger.error(f"failed to revoke token for {user}")
        is_successful = False

    return is_successful
