from contextlib import ContextDecorator
import sqlite3
from .base import DB


class DbConn(ContextDecorator):
    def __init__(self, conn):
        self.conn = conn
        self.cur = None

    def __enter__(self):
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class SQLiteDAL(DB):
    def __init__(self, tbl_name="main.hashes"):
        super().__init__()
        self.db_file = r'/home/ninadmhatre/Documents/Projects/Python/hashed/db.sqlite' # FIXME: get from config
        self.db_tbl = tbl_name or "main.hashes"
        self.init_connection()

    def init_connection(self):
        try:
            self.conn = sqlite3.connect(
                self.db_file,
                check_same_thread=False)
            self.conn.isolation_level = None
            self.conn.set_trace_callback(print)
        except sqlite3.Error as e:
            raise

    def insert(self, user: str, data: dict) -> int:
        rows = []

        for category in data:
            tags = ",".join(data[category])
            rows.append((user, category, tags))

        cur = self.conn.cursor()
        try:
            query = "insert into {}(user, category, tags) values(?, ?, ?)".format(self.db_tbl)
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
            query = "update {} set tags = ? where user = ? and category = ?".format(self.db_tbl)
            params = (",".join(updated_vals[cat]), user, cat)
            queries.append((query, params))

        cur = self.conn.cursor()
        cur.execute("begin")

        try:
            for query, params in queries:
                cur.execute(query, params)
                print(f'')
        except sqlite3.Error:
            self.conn.rollback()
            raise
        finally:
            self.conn.commit()
            self.get_user_tags.cache_clear()

    def view(self, user: str) -> list:
        cur = self.conn.cursor()

        query = "select * from {} where user = ?".format(self.db_tbl)
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
        query = "delete from main.{} where user = '%s'".format(self.db_tbl)

        try:
            cur.execute(query % user)
        finally:
            self.conn.commit()
            self.get_user_tags.cache_clear()

    def delete_category(self, user, categories):
        cur = self.conn.cursor()

        rows = []
        for c in categories:
            rows.append([user, c])

        query = "delete from main.{} where user = ? and category = ?".format(self.db_tbl)

        try:
            cur.executemany(query, rows)
        finally:
            self.conn.commit()
            self.get_user_tags.cache_clear()

    def delete_category_tags(self, user, category, tags):
        cur = self.conn.cursor()
        rows = []

        for t in tags:
            rows.append(
                [user, category, t]
            )

        query = "delete from main.{} where user = ? and category = ? and tag = ?".format(self.db_tbl)

        try:
            cur.executemany(query, rows)
        finally:
            self.conn.commit()
            self.get_user_tags.cache_clear()
