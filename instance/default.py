__author__ = "ninad"

import logging
from datetime import timedelta
import os

DEBUG = True
LOG_QUERIES = False
SECRET_KEY = "5nwxi8h9H5)GMl0GR_9ObJXQwdoMo}"
PORT = 22000
ADMIN_MAIL = "ninad.mhatre@gmail.com"
SESSION_TIMEOUT = timedelta(minutes=240)
TESTING=True

APP_ENVIRONMENT = "dev"
LOG_DIR = "/var/log/stapp"
LOG_TYPE = "watched"
LOG_LEVEL = "INFO"
APP_LOG_NAME = "app.log"
WWW_LOG_NAME = "www.log"
LOG_MAX_BYTES = 100 * 1024  # * 1024  # 100MB in bytes
LOG_COPIES = 5


ADMIN_USERS = ("ninad.mhatre@gmail.com",)

GOOGLE_CLIENT_ID = (
    "526235291815-0gcbkrkttfoas4hubl9pphc7j55v4519.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = "2QkkTUUUdv-sTwoAtENx89Ko"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


# URL's
FACEBOOK = "https://www.facebook.com/ninad.mhatre"
GOOGLE_PLUS = "https://plus.google.com/+ninadmhatre"
GIT_HUB = "https://github.com/ninadmhatre/"
LINKED_IN = "https://in.linkedin.com/in/ninadmhatre"
PERSONAL_EMAIL = "ninad.mhatre@gmail.com"

# Dashboard
DASHBOARD_MODS = "dashboard_mods"

__RELEASE__ = "b0"
__VERSION__ = "2020.12.03"
