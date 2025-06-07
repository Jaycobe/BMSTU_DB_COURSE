import flask_login

from models import Users
from __init__ import db
from flask import Blueprint, request
from flask_login import login_required
from json_responses import *

users = Blueprint("users_blueprint", __name__)


@users.route("/participants", methods=["GET"])
@login_required
def show_participants():
    result = Users.query.filter(Users.role == 4 or Users.role == 3).all()

    for i in range(0, len(result)):
        result[i] = result[i].to_dict()

    return get_json_success("Successfully retrieved users", app_data=result), 200


@users.route("/organizers", methods=["GET"])
@login_required
def show_organizers():
    result = Users.query.filter(Users.role == 2).all()

    for i in range(0, len(result)):
        result[i] = result[i].to_dict()

    return get_json_success("Successfully retrieved users", app_data=result), 200


@users.route("/organizers/<org_id>", methods=["GET"])
@login_required
def show_organizer(org_id):
    result = Users.query.filter(Users.role == 2, Users.id == org_id).first()

    if not result:
        return get_json_fail("Organizer not found"), 404

    return get_json_success("Successfully retrieved user", app_data=result.to_dict()), 200


@users.route("/participants/<user_id>", methods=["GET"])
@login_required
def show_participant(user_id):
    result = Users.query.filter(Users.id == user_id, Users.role == 4 or Users.role == 3).first()

    if not result:
        return get_json_fail("Participant not found"), 404

    return get_json_success("Successfully retrieved user", app_data=result.to_dict()), 200
