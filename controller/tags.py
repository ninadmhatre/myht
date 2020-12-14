from functools import lru_cache as cache

from flask import (
    Blueprint,
    current_app,
    request,
    jsonify,
    render_template,
    flash,
    redirect,
    url_for,
)
from flask_login import login_required, current_user

from dal.dbobj import get_dal
from collections import defaultdict
from sqlite3 import IntegrityError

from libs.Utils import unobscure
from libs.validate import AddForm, ManageForm, GenerateForm

tags = Blueprint("tags", __name__, url_prefix="/tags")

# user = "ninad.mhatre@gmail.com"
DAL = get_dal()

# data = {
#     user: {
#         "natute": ['sun', 'moon', 'river'],
#         "manmade": ['dam', 'boat', 'ship', 'bridge'],
#         'vehicles': ['car', 'bike', 'cycle']
#     }
# }


def parse_tags(string: str) -> (dict, list):
    parsed = {}
    errors = []

    for entry in string.splitlines():
        entry = entry.strip()
        category, _tags = entry.split(":")

        if category in parsed:
            errors.append("Duplicate category: {}".format(category))
        else:
            parsed[category] = [t.strip() for t in _tags.split(",")]

    return parsed, errors


def remove_existing(user_tags, user) -> dict:
    existing_tags = DAL.get_user_tags(user)

    result = {}

    for category in user_tags:
        if category in existing_tags:
            existing_tags = set(existing_tags[category])
            new_tags = set(user_tags[category])
            result[category] = list(new_tags.difference(existing_tags))
        else:
            result[category] = user_tags[category]

    return result


@tags.route("/add", methods=["GET", "POST"])
@login_required
def add_tags():
    if request.method == "POST":
        form = AddForm(request.form)
        form.parse()
        form.validate(DAL.get_user_tags(current_user.id))

        if form.has_errors():
            form.flash_errors(category="error")
            # TODO:
            #  on errors, populate all others
        else:
            tags_to_add = form.get_result
            DAL.insert(current_user.id, tags_to_add)

    result = DAL.get_user_tags(current_user.id)
    additional = 10 - len(result)

    return render_template("tags/add.html", existing=result, additional=additional)


@tags.route("/manage", methods=["GET", "POST"])
@login_required
def manage_tags():
    if request.method == "POST":
        # deleted_cat, new_vals, deleted_vals = [], defaultdict(list), defaultdict(list)
        existing_tags = DAL.get_user_tags(current_user.id)

        form = ManageForm(request.form, existing_tags)
        form.parse()
        form.validate()

        if form.is_updated():
            if form.has_errors():
                form.flash_errors()
            else:
                deleted_categories, new_vals = form.get_result
                DAL.update(current_user.id, deleted_categories, new_vals)

    result = DAL.get_user_tags(current_user.id)
    return render_template("tags/manage.html", tags=result)


@tags.route("/generate", methods=["GET", "POST"])
@login_required
def generate_tags():
    if request.method == "POST":
        existing_tags = DAL.get_user_tags(current_user.id)

        form = GenerateForm(request.form, existing_tags)
        form.parse()
        form.validate()

        if form.has_errors():
            form.flash_errors()
            return render_template("tags/generate.html", tags=existing_tags)
        return render_template("tags/generate.html", generated=form.get_result)
    else:
        result = DAL.get_user_tags(current_user.id)
        return render_template("tags/generate.html", tags=result)
