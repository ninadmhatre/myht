__author__ = 'ninad'
from . default import *


class OAuthInfo:
    def __init__(self, cl_id: str, cl_secret: str, discoverty_url: str):
        self.cl_id = cl_id
        self.cl_secret = cl_secret
        self.discovery_url = discoverty_url


def get_oauth_details(provider: str = "GOOGLE") -> OAuthInfo:
    return OAuthInfo(
        cl_id=GOOGLE_CLIENT_ID,
        cl_secret=GOOGLE_CLIENT_SECRET,
        discoverty_url=GOOGLE_DISCOVERY_URL
    )


def get_sqllite_db_file_path():
    return


def get_admin_users() -> tuple:
    return ADMIN_USERS
