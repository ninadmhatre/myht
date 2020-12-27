from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:////tmp/sqlite_orm.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Hashes(Base):
    __tablename__ = 'hashes'

    user = Column(String, nullable=False, primary_key=True)
    category = Column(String, nullable=False, primary_key=True)
    tags = Column(String, nullable=False)

    def __repr__(self):
        return f'<Hashes(user={self.user}, category={self.category}, tags={self.tags})'


class Users(Base):
    __tablename__ = 'users'

    email = Column(String, nullable=False, primary_key=True)
    uid = Column(String, nullable=False, primary_key=True)
    token = Column(String, nullable=True)

    def __repr__(self):
        return f'<Users(email={self.email}, uid={self.uid}, token={self.token})'


Base.metadata.create_all(engine)




def fetch_user(user):
    r = session.query(Users).filter_by(email=user).first()
    return r


def add_one_category_multiple_tags(user, cat_tags):
    entries = []

    for cat, tags in cat_tags.items():
        entries.append(
            Hashes(user=user, category=cat, tags=tags)
        )

    session.add_all(entries)
    session.commit()


def add_multiple_categories_mul_tags_per_cat(use, cats, tags):
    pass


def fetch_all_cats(user):
    for e in session.query(Hashes).filter_by(user=user):
        print(e)


def fetch_tags_for_cat(user, cat):
    pass


#Hashes
def insert(user: str, data: dict) -> int:
    rows = []

    for category in data:
        tags = ",".join(data[category])
        rows.append(Users(user, category, tags))

    try:
        session.add_all(rows)
        session.commit()

        # self.get_user_tags.cache_clear()

        added = len(rows)
    except Exception:
        session.rollback()
        added = 0
    return added


def update(user: str, deleted_categories: list, updated_vals: dict):
    try:
        for cat in deleted_categories:
            session.query(Hashes).filter_by(user=user, category=cat).delete()

        for cat in updated_vals:
            _tags = ",".join(updated_vals[cat])
            session.query(Hashes).filter_by(user=user, category=cat).update({'tags': _tags})

        session.commit()
        # self.get_user_tags.cache_clear()
    except Exception:
        session.rollback()


def view(user: str) -> list:
    rows = []
    for e in session.query(Hashes).filter_by(user=user):
        rows.append(e)

    return rows


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


# Users
def get_user_by_email(user_email) -> Users:
    return session.query(Users).filter_by(email=user_email).first()


def get_user_by_uid(uid) -> Users:
    return session.query(Users).filter_by(uid=uid).first()


def add_user(user_: Users):
    is_new_user = session.query(Users).filter_by(email=user_.email).scalar() is None

    if is_new_user:
        try:
            session.add(user_)
            session.commit()
        except Exception:
            session.rollback()
            return
        else:
            return user_


def update_token(user_email, token):
    try:
        session.query(Users).filter_by(email=user_email).update({'token': token})
        session.commit()
    except Exception:
        session.rollback()
        raise


if __name__ == '__main__':
    user = "a@gmail.com"
    uid = '123'
    # add_user(user, uid)
    print(fetch_user(user))

    category_tags = {
        "one": "1,2,3",
        "fruits": "apple,grapes,straberry",
        "colors": "red,blue,purple,pink"
    }

    # add_one_category_multiple_tags(user, category_tags)
    # fetch_all_cats(user)

    print(f'result >> {get_user_by_email(user)}')
    print(f'result >> {get_user_by_uid(123)}')
    update_token(user, '1234')
    print(f'result >> {get_user_by_email(user)}')

    update_token(user, None)
    print(f'result >> {get_user_by_email(user)}')
