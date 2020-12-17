__author__ = "ninad"

from functools import wraps
from typing import Union
import os
import simplejson as json
import hashlib
from urllib import parse
from flask_login import UserMixin
from base64 import b64encode, b64decode
import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d


# class User(UserMixin):
#     """
#     User Mixin; with get name being changed!
#     """

#     def __init__(self, user_id):
#         self.id = user_id

#     def get_id(self):
#         return self.id


def to_byte(s: str) -> bytes:
    return s.encode("utf-8")


def to_str(b: bytes) -> str:
    return b.decode("utf-8")


def obscure(data: Union[str, bytes]) -> str:
    if isinstance(data, str):
        data = to_byte(data)
    return to_str(b64e(zlib.compress(data, 9)))


def unobscure(obscured: bytes) -> str:
    if obscured in ("", None):
        return ""
    return to_str(zlib.decompress(b64d(obscured)))


# def requires_roles(*roles):
#     def wrapper(f):
#         @wraps(f)
#         def wrapped(*args, **kwargs):
#             if get_current_user_role() not in roles:
#                 return "You've got no permission to access this page.", 403
#             return f(*args, **kwargs)
#         return wrapped
#     return wrapper



class Utility(object):
    @staticmethod
    def write_to_file(filename, content, as_json=False, safe=False):
        if safe:
            return Utility.safe_write_to_file(filename, content, as_json)

        with open(filename, "w") as f:
            if as_json:
                f.write(json.dumps(content, indent=4))
            else:
                f.write(content)

    @staticmethod
    def read_from_file(filename, as_json=False, safe=False):
        if safe:
            return Utility.safe_read_from_file(filename, as_json)

        if os.path.isfile(filename):
            with open(filename, "r") as f:
                content = f.read()  # Read full file
                if as_json:
                    data = json.loads(content, encoding="utf-8")
                    return data, None
                return content, None

    @staticmethod
    def safe_read_from_file(filename, as_json=False):
        try:
            with open(filename, "r+") as f:
                content = f.read()  # Read full file
                if as_json:
                    data = json.loads(content, encoding="utf-8")
                    return data, None
                return content, None
        except IOError as e:
            return False, e
        except ValueError as e:
            return False, e

    @staticmethod
    def safe_write_to_file(filename, content, as_json=False):
        try:
            with open(filename, "w+") as f:
                if as_json:
                    f.write(json.dumps(content, indent=4))
                else:
                    f.write(content)
        except IOError as e:
            return False, e
        except ValueError as e:
            return False, e
        else:
            return True, None

    @staticmethod
    def get_ip(request):
        if "HTTP_X_REAL_IP" in request.environ:
            return request.environ["HTTP_X_REAL_IP"]
        elif "HTTP_X_FORWARDED_FOR" in request.environ:
            ips = request.environ["HTTP_X_FORWARDED_FOR"]
            return ips.split(",")[0]
        else:
            return request.remote_addr

    @staticmethod
    def get_md5_hash(string):
        if string and isinstance(string, str):
            return hashlib.md5(string.encode("utf-8")).hexdigest()

    @staticmethod
    def get_md5_hash_of_title(string):
        if string:
            _title = parse.quote(string)
            return hashlib.md5(_title.encode("utf-8")).hexdigest()
        return None

    @staticmethod
    def quote_string(string):
        if string:
            return parse.quote(string)

    @staticmethod
    def unquote_string(string):
        if string:
            return parse.unquote(string, encoding="utf-8")

    @staticmethod
    def base64encode(val: str) -> str:
        return b64encode(to_byte(val)).decode("utf-8")

    @staticmethod
    def decode_dict(vals: dict) -> dict:
        result = {}
        for e_key, e_val in vals.items():
            e_key = unobscure(e_key)
            e_val = [unobscure(v) for v in e_val]
            result[e_key] = e_val

        return result
