import unittest
from copy import copy

from dal import get_dal
from libs.Utils import obscure
from libs.validate import ManageForm

TEST_DB_TABLE = "test_hashes"

_dal = get_dal(tbl_name=TEST_DB_TABLE)


DATA = {
    "numbers": ["1", "2", "3"],
    "objects": ["tree", "sun", "mountains"],
    "sports": ["tennis", "cricket", "football", "golf"],
}

# 1. 1 blank category received
# 2. 1 blank tag received
# 3. tag deleted and added
# 4. blank new tag, space in tag, special chars in tag, tag length, number of new tags
# 5. tag edited to have special chars, max length, more than 1 specified


class ManageFormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = "dummy@myht.com"
        cls._populate_form_data()

        _dal.insert(cls.user, DATA)

    @classmethod
    def tearDownClass(cls):
        print(f"deleting {cls.user} entries from db")
        _dal.delete(cls.user)

    def setUp(self):
        self.user_tags = _dal.get_user_tags(self.user)

    @classmethod
    def _populate_form_data(cls):
        cls.dummy_data_as_received = {}

        for idx, c in enumerate(DATA):
            cls.dummy_data_as_received[f"cat_{idx}"] = c
            cls.dummy_data_as_received[f"tag_{idx}"] = ",".join(DATA[c])

    def test_blank_category(self):
        data = {"cat_del_": "on"}

        form = ManageForm(data, self.user_tags)
        form.parse()
        form.validate()

        self.assertTrue(form.has_errors())
        self.assertTrue(len(form.errors) == 1)

        self.assertIn("be deleted is blank!", form.errors.pop())

    def test_blank_tag(self):
        data = {f'tag_add_{obscure(b"numbers")}': "3 , , 4,#,!,&*&*"}

        form = ManageForm(data, self.user_tags)
        form.parse()
        form.validate()

        self.assertTrue(form.has_errors())
        self.assertTrue(len(form.errors), 4)

    def test_edited_tag(self):
        data = {
            f'tag_upd_{obscure(b"numbers")}:{obscure(b"1")}': "11",
            f'tag_upd_{obscure(b"numbers")}:{obscure(b"2")}': "a b",
            f'tag_upd_{obscure(b"numbers")}:{obscure(b"3")}': "123#!@$",
            f'tag_upd_{obscure(b"numbers")}:{obscure(b"4")}': "1" * 51,
        }

        form = ManageForm(data, self.user_tags)
        form.parse()
        form.validate()

        self.assertTrue(form.has_errors())
        print(f"{form.errors=}")
        self.assertTrue(len(form.errors) == 3)

    def test_deleted_tag_is_re_added(self):
        data = {
            f'tag_del_{obscure(b"numbers")}:{obscure(b"abcd")}': "on",
            f'tag_add_{obscure(b"numbers")}': "xyz, llll, abcd",
        }

        form = ManageForm(data, self.user_tags)
        form.parse()
        form.validate()

        _, new_vals = form.get_result

        self.assertNotIn("abcd", new_vals)

    def test_check_all_tags_deleted_for_cat(self):
        data = {
            f'tag_del_{obscure(b"objects")}:{obscure(b"tree")}': True,
            f'tag_del_{obscure(b"objects")}:{obscure(b"sun")}': True,
            f'tag_del_{obscure(b"objects")}:{obscure(b"mountain")}': True,
        }

        form = ManageForm(data, self.user_tags)
        form.parse()
        form.validate()

        deleted_categories, _ = form.get_result

        self.assertIn("objects", deleted_categories)
        self.assertTrue(len(deleted_categories) == 1)
