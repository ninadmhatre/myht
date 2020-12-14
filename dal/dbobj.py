from dal.slite import SQLiteDAL
from dal import DB


__DAL = None


def get_dal(tbl_name=None) -> DB:
    global __DAL

    if not __DAL:
        if tbl_name:
            __DAL = SQLiteDAL(tbl_name)
        else:
            __DAL = SQLiteDAL()

    return __DAL

