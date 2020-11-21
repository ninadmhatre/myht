from flask import config
from . import base, slite

__DAL = None


def get_dal(tbl_name=None) -> base.DB:
    global __DAL

    if not __DAL:
        __DAL = slite.SQLiteDAL(tbl_name)

    return __DAL
