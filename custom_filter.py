__author__ = "ninad"

import jinja2
import hashlib
from libs.utils import Utility, obscure as encode, to_byte


def snippet(text, length=200):
    if text is None or not isinstance(text, str):
        return text

    t_snippet = text[:length]

    return t_snippet


def hash_me(text, prefix="ninad-echo"):
    t = prefix + text
    md5 = hashlib.md5()
    md5.update(t.encode())
    return md5.hexdigest()


def toBoolean(text):
    if isinstance(text, int):
        return text == 1
    return text.lower() in ("on", "yes", "true")


def toAscii(text):
    return Utility.unquote_string(text)


def obscure(text):
    return encode(to_byte(text))


jinja2.filters.FILTERS["snippet"] = snippet
jinja2.filters.FILTERS["page_id"] = hash_me
jinja2.filters.FILTERS["toBoolean"] = toBoolean
jinja2.filters.FILTERS["toAscii"] = toAscii
jinja2.filters.FILTERS["obscure"] = obscure


def get_custom_filters():
    return [
        snippet.__name__,
        hash_me.__name__,
        toBoolean.__name__,
        to_byte.__name__,
        toAscii.__name__,
        obscure.__name__,
    ]


# env = Environment()
# env.filters['snippet'] = snippet
