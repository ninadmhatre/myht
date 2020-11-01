from tinydb import TinyDB, Query
from .base import DB


class TinyDBDAL(DB):
    def __init__(self):
        super().__init__()

    def config(self):
        self._cfg = {
            'db_file': 'db.json',
        }

    def init_connection(self):
        if self.conn:
            return self.conn

        self.conn = TinyDB(self._cfg['db_file'])

    def insert(self, key: str, category: str, tags: list) -> bool:
        self.conn.insert

    def get(self, user: str):
        pass



