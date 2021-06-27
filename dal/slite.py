import logging
from contextlib import ContextDecorator
import sqlite3
import pathlib
from typing import Any

from libs.dt import User
from dal import DB
from instance import get_sqllite_db_file_path

log = logging.getLogger(__name__)


class DbConn(ContextDecorator):
    def __init__(self, conn):
        self.conn = conn
        self.cur = None

    def __enter__(self):
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# CREATE TABLE "hashes" (
# 	"user"	TEXT NOT NULL,
# 	"category"	TEXT NOT NULL,
# 	"tags"	TEXT NOT NULL DEFAULT '-',
# 	PRIMARY KEY("user","category")
# )

# CREATE TABLE "users" (
# 	"email"	TEXT NOT NULL,
# 	"uid"	TEXT NOT NULL,
# 	"token"	TEXT,
# 	PRIMARY KEY("email","uid")
# )


class SQLiteDAL(DB):
    def __init__(self, tbl_name="main.hashes", usr_tbl_name="main.users"):
        super().__init__()
        self.db_file = get_sqllite_db_file_path() or self.__get_db_file()
        self.db_tbl = tbl_name
        self.usr_tbl = usr_tbl_name
        self.init_connection()

    def __get_db_file(self):
        curr_file = pathlib.Path(__file__)
        db_file = curr_file.parents[1].joinpath("db.sqlite")
        return db_file.as_posix()

    def init_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.conn.isolation_level = None
            self.conn.set_trace_callback(print)
        except sqlite3.Error:
            raise

    def run_query(self, conn, query, params) -> (bool, Any):
        is_successful = False
        result = []

        try:
            result = conn.execute(query, params).fetchall()
        except Exception as e:
            log.exception(e)
        else:
            is_successful = True

        return is_successful, result

    def insert(self, user: str, data: dict) -> int:
        rows = []

        for category in data:
            tags = ",".join(data[category])
            rows.append((user, category, tags))

        cur = self.conn.cursor()
        try:
            query = "insert into {}(user, category, tags) values(?, ?, ?)".format(
                self.db_tbl
            )
            cur.executemany(query, rows)
        except Exception:
            self.conn.rollback()
        finally:
            self.conn.commit()
            self.get_user_tags.cache_clear()

        return len(rows)

    def update(self, user: str, deleted_categories: list, updated_vals: dict):
        queries = []

        for cat in deleted_categories:
            query = "delete from {} where user = ? and category = ?".format(self.db_tbl)
            params = (user, cat)
            queries.append((query, params))

        for cat in updated_vals:
            query = "update {} set tags = ? where user = ? and category = ?".format(
                self.db_tbl
            )
            params = (",".join(updated_vals[cat]), user, cat)
            queries.append((query, params))

        cur = self.conn.cursor()
        cur.execute("begin")

        try:
            for query, params in queries:
                cur.execute(query, params)
                print(f"")
        except sqlite3.Error:
            self.conn.rollback()
            raise
        finally:
            self.conn.commit()
            self.get_user_tags.cache_clear()

    def view(self, user: str) -> list:
        cur = self.conn.cursor()

        query = f"select * from {self.db_tbl} where user = ?"
        params = (user,)

        rows = cur.execute(query, params).fetchall()

        return rows

    def delete(self, user: str) -> bool:
        cur = self.conn.cursor()
        query = "delete from {} where user = ?".format(self.db_tbl)
        success = False

        try:
            cur.execute(query, (user,))
        except sqlite3.Error:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()
            self.get_user_tags.cache_clear()
            success = True

        return success

    def delete_user(self, user: str):
        cur = self.conn.cursor()
        query = f"delete from main.{self.db_tbl} where user = ?"

        try:
            cur.execute(query, (user,))
        finally:
            self.conn.commit()
            self.get_user_tags.cache_clear()

    def delete_category(self, user, categories):
        cur = self.conn.cursor()

        rows = []
        for c in categories:
            rows.append([user, c])

        query = f"delete from main.{self.db_tbl} where user = ? and category = ?"

        try:
            cur.executemany(query, rows)
        finally:
            self.conn.commit()
            self.get_user_tags.cache_clear()

    def delete_category_tags(self, user, category, tags):
        cur = self.conn.cursor()
        rows = []

        for t in tags:
            rows.append([user, category, t])

        query = f"delete from main.{self.db_tbl} where user = ? and category = ? and tag = ?"

        try:
            cur.executemany(query, rows)
        finally:
            self.conn.commit()
            self.get_user_tags.cache_clear()

    def get_user_count(self):
        query = f"select count(email) from {self.usr_tbl}"
        cur = self.conn.cursor()

        row = cur.execute(query).fetchall()
        return row[0][0]

    def get_user_by_email(self, user_email) -> User:
        user = None
        if self.is_existing_user(user_email):
            cur = self.conn.cursor()

            query = f"select email, uid, token from {self.usr_tbl} where email = ?"
            params = (user_email,)

            row = cur.execute(query, params).fetchall()
            first_result = row[0]

            user = User(id_=first_result[1], email=first_result[0], access_token=first_result[2])

        return user

    def get_user_by_uid(self, uid) -> User:
        user = None
        if self.is_existing_user(uid, is_get_by_email=False):
            cur = self.conn.cursor()

            query = f"select email, uid, token from main.{self.usr_tbl} where uid = ?"
            params = (uid,)

            row = cur.execute(query, params).fetchall()
            first_result = row[0]

            user = User(id_=first_result[0], email=first_result[0], access_token=first_result[2])
        return user

    def add_user(self, user: User) -> User:
        cur = self.conn.cursor()
        result = False
        try:
            query = "insert into {}(email, uid) values(?, ?)".format(self.usr_tbl)
            params = (user.email, user.id)
            cur.execute(query, params)
        except Exception as e:
            log.exception(e)
            self.conn.rollback()
        else:
            result = True
        finally:
            self.conn.commit()

        return user if result else None

    def save_token(self, user: User) -> bool:
        with DbConn(self.conn) as conn:
            query = f"update {self.usr_tbl} set token = ? where email = ?"
            params = (user.access_token, user.email)
            is_ok, _ = self.run_query(conn, query, params)

            return is_ok

    def clear_token(self, user_email: str) -> bool:
        with DbConn(self.conn) as conn:
            query = f'update {self.usr_tbl} set token = ? where email = ?'
            params = ('', user_email)
            is_ok, _ = self.run_query(conn, query, params)

            return is_ok

    def is_existing_user(self, user_id: str, is_get_by_email=True) -> bool:
        with DbConn(self.conn) as conn:
            where_clause = 'email' if is_get_by_email else 'uid'
            query = f"select count(email) from {self.usr_tbl} where {where_clause} = ?"
            params = (user_id,)
            row = conn.execute(query, params).fetchall()

            return row[0][0] == 1   # first result, first field


if __name__ == '__main__':
    db = SQLiteDAL()
    breakpoint()
    u = User(id_='123', email="ninad")
    print(f'>> Before: {u}')
    u1 = db.add_user(u)
    print(f'>> After : {u1}')