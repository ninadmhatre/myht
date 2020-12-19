__author__ = 'ninad'

import logging
from datetime import timedelta
import os

DEBUG = True
LOG_QUERIES = False
SECRET_KEY = '5nwxi8h9H5)GMl0GR_9ObJXQwdoMo}'
PORT = 22000
ADMIN_MAIL = 'ninad.mhatre@gmail.com'
LOGGER = {
    'FILE': dict(FILE='logs/log.log',
                 LEVEL=logging.DEBUG,
                 NAME='web_logger',
                 HANDLER='File',
                 FORMAT='%(asctime)s %(levelname)s %(filename)s %(module)s [at %(lineno)d line] %(message)s',
                 EXTRAS=dict(when='D', interval=1, backupCount=7))
}

ASSETS_DEBUG = False

SESSION_TIMEOUT = timedelta(minutes=240)

GOOGLE_CLIENT_ID = "526235291815-0gcbkrkttfoas4hubl9pphc7j55v4519.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "2QkkTUUUdv-sTwoAtENx89Ko"
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")


# URL's

FACEBOOK = 'https://www.facebook.com/ninad.mhatre'
GOOGLE_PLUS = 'https://plus.google.com/+ninadmhatre'
GIT_HUB = 'https://github.com/ninadmhatre/'
LINKED_IN = 'https://in.linkedin.com/in/ninadmhatre'
PERSONAL_EMAIL = 'ninad.mhatre@gmail.com'

# Dashboard
DASHBOARD_MODS = 'dashboard_mods'

__RELEASE__ = 'b0'
__VERSION__ = '2020.12.03'
