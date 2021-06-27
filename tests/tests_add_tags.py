import unittest

from dal.dbobj import get_dal
from libs.validate import AddForm

TEST_DB_TABLE = "test_hashes"

_dal = get_dal(tbl_name=TEST_DB_TABLE)


DATA = {
    "numbers": ["1", "2", "3"],
    "objects": ["tree", "sun", "mountains"],
    "sports": ["tennis", "cricket", "football", "golf"],
}


class AddFormTests(unittest.TestCase):
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

    def test_empty_form(self):
        form = AddForm(dict())
        form.parse()
        form.validate(self.user_tags)

        self.assertTrue(len(form.get_result) == 0)

    @classmethod
    def _populate_form_data(cls):
        cls.dummy_data_as_received = {}

        for idx, c in enumerate(DATA):
            cls.dummy_data_as_received[f"cat_{idx}"] = c
            cls.dummy_data_as_received[f"tag_{idx}"] = ",".join(DATA[c])

    def test_for_duplicates(self):
        data = {"cat_3": "  numbers ", "tag_3": "3, 4 , 5  "}

        form = AddForm(data)
        form.parse()
        form.validate(self.user_tags)

        self.assertTrue(len(form.new_tags) == 1)
        self.assertTrue(form.has_errors())
        self.assertEqual(len(form.errors), 1)
        self.assertTrue("'numbers' is duplicate" in form.get_errors()[0])

    def test_max_cats(self):
        data = {}

        for i in range(13):
            data[f"cat_{i}"] = str(i)
            data[f"tag_{i}"] = str(i)

        form = AddForm(data)
        form.parse()
        form.validate(self.user_tags)

        self.assertTrue(len(form.new_tags) == 10, f"expected 10 but got {len(form.new_tags)}")
        self.assertFalse(form.has_errors())

    def test_max_tags_per_cat(self):
        data = {}

        data["cat_3"] = "max tags/cat"
        data["tag_3"] = ",".join([str(n) for n in range(1, 33)])

        form = AddForm(data)
        form.parse()
        form.validate(self.user_tags)

        self.assertTrue(len(form.new_tags), 4)
        self.assertTrue(form.has_errors())
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.get_errors()[0].startswith("only 30 tags"))

    def test_tags_checks(self):
        data = {}

        tag_with_trailing_spaces = " spacedtag "
        tag_with_space = "with space"
        tag_with_emoji = "laptop💻"
        tags_with_invalid_chars = "####, !@$?, $%^&"
        tag_with_max_chars = "a" * 51

        data["cat_3"] = "tag_checks"
        data["tag_3"] = (
            f"{tag_with_trailing_spaces},"
            + f"{tag_with_space},"
            + f"{tag_with_emoji},"
            + f"{tags_with_invalid_chars},"
            + f"{tag_with_max_chars}"
        )

        form = AddForm(data)
        form.parse()
        form.validate(self.user_tags)

        self.assertTrue(form.has_errors())
        print(form.errors)
        self.assertEqual(len(form.errors), 5)
        self.assertTrue(len(form.get_result) == 0)

        valid_data = {"cat_3": "valid_tags", "tag_3": ",".join([tag_with_trailing_spaces, tag_with_emoji]) }
        form = AddForm(valid_data)
        form.parse()
        form.validate(self.user_tags)

        results = form.get_result['valid_tags']
        self.assertIn(tag_with_emoji, results)
        self.assertIn(tag_with_trailing_spaces.strip(), results)

    def test_add_new_entry(self):
        tag_with_trailing_spaces = " spacedtag "
        tag_with_space = "not_with_space"
        tag_with_emoji = "laptop💻"
        tag_with_max_chars = "a" * 49
        cat_name = "new_valid_cat"

        data = {
            "cat_3": cat_name,
            "tag_3": ",".join(
                [
                    tag_with_trailing_spaces,
                    tag_with_space,
                    tag_with_emoji,
                    tag_with_max_chars,
                ]
            ),
        }

        form = AddForm(data)
        form.parse()
        form.validate(self.user_tags)

        self.assertFalse(form.has_errors())

        _dal.insert(self.user, form.get_result)
        self.user_tags = _dal.get_user_tags(self.user)

        self.assertIn(tag_with_max_chars, self.user_tags[cat_name])
        self.assertIn(tag_with_emoji, self.user_tags[cat_name])

        _dal.update(self.user, deleted_categories=[cat_name], updated_vals={})
