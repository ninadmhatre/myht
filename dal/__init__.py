from typing import Union
from functools import lru_cache as cache
from collections import defaultdict

from libs.dt import User

__DAL = None


class DB:
    def __init__(self):
        self._cfg = None
        self.conn = None

    def config(self):
        raise NotImplementedError

    def init_connection(self):
        raise NotImplementedError

    def insert(self, user: str, data: dict) -> bool:
        raise NotImplementedError

    def update(self, user: str, deleted_categories: list, updated_vals: dict) -> bool:
        raise NotImplementedError

    def delete(self, user: str) -> bool:
        raise NotImplementedError

    def view(self, user: str):
        raise NotImplementedError

    @cache()
    def get_user_tags(self, user: str) -> dict:
        data = self.view(user)
        result = defaultdict(list)

        for _, category, user_tags in data:
            result[category] = user_tags.split(",")

        return result

    def get_user(self, user_email: Union[None, str], user_id: Union[None, str]):
        assert (user_email or user_id), "must specify user_email or id to fetch user!"

        if user_email:
            return self.get_user_by_email(user_email)
        else:
            return self.get_user_by_uid(user_id)

    def get_user_by_email(self, user_email):
        raise NotImplementedError

    def get_user_count(self):
        raise NotADirectoryError

    def get_user_by_uid(self, user_id):
        raise NotImplementedError

    def add_user(self, user: User):
        raise NotImplementedError

    def is_existing_user(self, user_id, is_get_by_email: bool = True) -> bool:
        raise NotImplementedError

    def save_token(self, user: User) -> bool:
        raise NotImplementedError

    def clear_token(self, user: User) -> bool:
        raise NotImplementedError
