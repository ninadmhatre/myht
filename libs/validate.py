import logging
from dataclasses import dataclass
from collections import defaultdict
from flask import flash
import re

from libs.Utils import unobscure

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Validator:
    def __init__(self, form):
        self.form = form
        self.errors = set()

    def has_errors(self):
        return len(self.errors) > 0

    def parse(self):
        raise NotImplementedError

    def validate(self, existing_tags: dict = None):
        raise NotImplementedError

    @staticmethod
    def is_blank(val: str) -> bool:
        return val == ""

    @staticmethod
    def _has_valid_num_of_tags(tag_list: list) -> bool:
        return len(tag_list) > Limits.NumOfTagsPerCats

    @property
    def get_result(self):
        raise NotImplementedError

    def log_errors(self):
        for err in self.errors:
            logger.error(err)

    def flash_errors(self, category="errors"):
        for err in self.errors:
            flash(err, category)

    def get_errors(self, as_list=True):
        return list(self.errors)


TAG_RE = re.compile(r"\w+", re.UNICODE)
NOT_ALLOWED_CHARS = ("!", "$", "%", "^", "&", "*", "+", ".", "#")


@dataclass(frozen=True)
class Limits:
    NumOfCategories: int = 10
    NumOfTagsPerCats: int = 30
    MaxLenOfTag: int = 50
    MaxGenTags: int = NumOfCategories * NumOfTagsPerCats


def validate_tag(tag: str, cat: str) -> list:
    err = []

    if " " in tag:
        err.append(f"space found in {cat}.[{tag}]")
    elif len(tag) > Limits.MaxLenOfTag:
        err.append(f"tag [{tag}] longer than 50 chars")
    else:
        result = TAG_RE.match(tag)

        if result is None:
            err.append(f"tag [{tag}] has one of the invalid [{NOT_ALLOWED_CHARS}] chars")
        elif len(result[0]) != len(tag):
            if any([char in tag for char in NOT_ALLOWED_CHARS]):
                err.append(f"tag [{tag}] has invalid chars!")

    return err


class AddForm(Validator):
    def __init__(self, form):
        super().__init__(form)
        self.new_tags = []
        self.tags_to_add = {}

    def parse(self):
        for i in range(10):
            # obscured_i = obscure(str(i))

            cat_key = f"cat_{i}"
            tag_key = f"tag_{i}"

            if cat_key not in self.form:
                continue

            cat = self.form.get(cat_key)
            user_tags = self.form.get(tag_key)

            if cat == "" and user_tags == "":
                continue

            self.new_tags.append(
                (cat.strip(), [t.strip() for t in user_tags.split(",")])
            )

    def validate(self, existing_tags: dict = None):
        # validate following,
        #  - no duplicates
        #  - max cat count - 10
        #  - max tag per count - 30
        #  - no spaces in each tag

        for cat, tags in self.new_tags:
            has_errors = False

            if self.is_blank(cat) or self.is_blank(tags):
                continue

            if cat in existing_tags:
                self.errors.add(f"category '{cat}' is duplicate!")
                continue

            if self._has_valid_num_of_tags(tags):
                self.errors.add(
                    f"only 30 tags per category allowed, {cat} has {len(tags)} tags!"
                )
                has_errors = True

            _tags = [t for t in tags if t != ""]

            for tag in _tags:
                err = validate_tag(tag, cat)
                if err:
                    has_errors = True
                    self.errors.update(err)

            if not has_errors:
                self.tags_to_add[cat] = set(_tags)

    @property
    def get_result(self):
        return self.tags_to_add


class ManageForm(Validator):
    def __init__(self, form, existing_vals: dict):
        super().__init__(form)
        self.existing_tags = existing_vals
        self.deleted_categories = []
        self.new_vals = defaultdict(list)
        self.deleted_vals = defaultdict(list)

    def parse(self):
        for key, val in self.form.items():
            if key == "_csrf_token":
                continue

            if key.startswith("cat_del"):
                _k = key.replace("cat_del_", "")
                self.deleted_categories.append(unobscure(_k))
            elif key.startswith("tag_add"):
                if self.is_blank(val):
                    continue

                cat = key.replace("tag_add_", "")
                cat = unobscure(cat)

                if cat in self.deleted_categories:
                    continue

                new_tags = [t.strip() for t in val.split(",")]
                for tag in new_tags:
                    err = validate_tag(tag, cat)
                    if err:
                        self.errors.update(err)
                    else:
                        self.new_vals[cat].extend(new_tags)
            else:
                if key.startswith("tag_del"):
                    # breakpoint()
                    pass
                cat_tag = key.split("_", 2)[2]
                cat, tag = cat_tag.split(":", 1)

                cat = unobscure(cat)
                tag = unobscure(tag)

                if cat in self.deleted_categories:
                    continue

                if "del" in key:
                    self.deleted_vals[cat].append(tag)
                    continue

                err = validate_tag(val, cat)
                if err:
                    self.errors.update(err)
                else:
                    self.new_vals[cat].append(val.strip())

        for cat in self.deleted_vals:
            add_tags = set(self.new_vals[cat])
            delete_tags = set(self.deleted_vals[cat])

            new_tags = add_tags.difference(delete_tags)

            if new_tags:
                self.new_vals[cat] = list(new_tags)
            else:
                del self.new_vals[cat]

    def validate(self, existing_tags: dict = None):
        # validate following,
        #  - empty tags
        #  - max tag per count - 30
        #  - each tag length

        for cat, tags in self.deleted_vals.items():
            if len(tags) == len(
                self.existing_tags[cat]
            ):  # all tags marked to be deleted
                self.deleted_categories.append(cat)

        for val in self.deleted_categories:
            if self.is_blank(val):
                self.errors.add("one of the category to be deleted is blank!")

        for cat, tags in self.new_vals.items():
            if self.is_blank(cat):
                self.errors.add(f"one of the category is blank!")
                continue

            if self._has_valid_num_of_tags(tags):
                self.errors.add(
                    f"only 30 tags per category allowed, {cat} has {len(tags)} tags!"
                )

            _tags = [t for t in set(tags) if t != ""]

            for tag in _tags:
                self.errors.update(validate_tag(tag, cat))

            self.new_vals[cat] = _tags

    def is_updated(self) -> bool:
        """ check if values were updated and db update is really required """
        if self.deleted_categories:
            return True

        if sorted(self.existing_tags.keys()) != sorted(self.new_vals.keys()):
            return True

        for cat, val in self.new_vals.items():
            if sorted(val) != sorted(self.existing_tags[cat]):
                return True

        return False

    @property
    def get_result(self):
        print(f"{self.deleted_categories=} | {self.new_vals=}")
        return self.deleted_categories, self.new_vals


class GenerateForm(Validator):
    def __init__(self, form, existing_tags):
        super().__init__(form)
        self.existing = existing_tags
        self.selected = []
        self.formatted = None

    def parse(self):
        for key, val in self.form.items():
            if key.startswith("cat_sel"):
                _k = key.replace("cat_sel_", "")
                self.selected.extend(self.existing[_k])
            elif key.startswith("tag_sel"):
                _, tag = key.replace("tag_sel", "").split(":")
                self.selected.append(tag)

    def validate(self, existing_tags: dict = None):
        # validate following,
        #  - selected is not empty!
        #  - max tags <= 300

        selected = set(self.selected)

        if not selected:
            self.errors.add("No tags were selected!!")
        elif len(selected) > Limits.MaxGenTags:
            self.errors.add("This is suspicious, more than 300 tags were selected!!")
        else:
            self.formatted = " ".join([f"#{t}" for t in selected])

    @property
    def get_result(self):
        return self.formatted
