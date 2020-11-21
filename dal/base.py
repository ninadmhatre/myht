from functools import lru_cache as cache
from collections import defaultdict


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


# if __name__ == '__main__':
#     s = SQLite()
#     user = "ninad.mhatre@gmail.com"
#
#     def print_user_entries():
#         rows = s.view(user)
#         [print(r) for r in rows]
#         print("---------")
#
#     print('before...')
#     print_user_entries()
#
#     # print('insert-1 entry')
#     s.insert(user, "test1", "house,chair,window,tv".split(","))
#
#     # if result:
#     #     print("{} rows added".format(result))
#
#     print("delete 1 tag")
#     s.delete_category_tags(user, "test1", "tv,house".split(','))
#
#     print_user_entries()
#     print('insert-2 individual entries')
#
#     s.insert(user, "test3", "car,bike,cycle,tricycle".split(","))
#     #
#     # if result:
#     #     print("{} rows added".format(result))
#
#     print_user_entries()
#
#     s.delete_category(user, "test1,test2".split(","))
#
#     print_user_entries()
#
#     print('insert-n ...')
#
#     s.delete_user(user)
#
#     print_user_entries()
