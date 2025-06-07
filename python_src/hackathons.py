import flask_login
from flask import Blueprint, request
from flask_login import login_required

from models import Hackathons, Users, Teams, h_t_list
from json_responses import *
from datetime import datetime
from __init__ import db

hackathons = Blueprint('hackathons', __name__)


def check_arg_types(data):
    res = True

    if "comment" in data and not isinstance(data['comment'], str):
        res = False
    if "name" in data and not isinstance(data['name'], str):
        res = False
    if "address" in data and not isinstance(data['address'], str):
        res = False
    if "theme" in data and not isinstance(data['theme'], str):
        res = False

    return res

@hackathons.route('/hackathons/<hack_id>', methods=["GET"])
def get_hackathon(hack_id):
    res = Hackathons.query.filter(Hackathons.id == hack_id).first()

    if res:
        return get_json_success(app_data=res.to_dict()), 200
    else:
        return get_json_fail("Hackathon not found"), 404


@hackathons.route('/hackathons/<hack_id>', methods=["PUT"])
@login_required
def update_hackathon(hack_id):
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role
    hackathon = Hackathons.query.filter(Hackathons.id == hack_id)

    if not hackathon:
        return get_json_fail("Hackathon with such id does not exist"), 404

    if user_role not in (1, 2):
        return get_json_fail("Privilege level too low"), 403

    if user_role == 2 and hackathon.org_id != user_id:
        return get_json_fail("You are not the organiser of that hackathon"), 200

    data = request.get_json()

    if data and all(key in data for key in ('name', 'date', 'address', 'theme')):

        if not check_arg_types(data):
            return get_json_fail("Argument types should be string"), 422

        try:
            hack_date = datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return get_json_fail("Incorrect datetime format. The format has to be yyyy-mm-dd")

        if hack_date < datetime.today():
            return get_json_fail("The hackathons date cannot be in the past."), 422

        hackathon.name = data['name']
        hackathon.date = data['date']
        hackathon.address = data['address']
        hackathon.theme = data['theme']

        db.session.commit()

        return get_json_success(), 200

    return get_json_fail("Incorrect input"), 422


@hackathons.route('/hackathons/future', methods=["GET"])
def get_future_hackathons():
    current_date = datetime.datetime.utcnow().date()

    res = Hackathons.query.filter(Hackathons.date > current_date).all()

    for i in range(0, len(res)):
        res[i] = res[i].to_dict()

    return get_json_success(app_data=res), 200


@hackathons.route('/hackathons/past', methods=["GET"])
def get_past_hackathons():
    current_date = datetime.utcnow().date()

    res = Hackathons.query.filter(Hackathons.date < current_date).all()

    for i in range(0, len(res)):
        res[i] = res[i].to_dict()

    return get_json_success(app_data=res), 200


@hackathons.route('/hackathons', methods=["GET"])
def get_hackathons():
    res = Hackathons.query.all()

    for i in range(0, len(res)):
        res[i] = res[i].to_dict()

    return get_json_success(app_data=res), 200


@hackathons.route('/hackathons/my_hackathons', methods=["GET"])
@login_required
def get_my_hackathons():
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role

    if user_role != 2:
        return get_json_fail("You cannot have hackathons"), 422

    res = Hackathons.query.filter(Hackathons.org_id == user_id).all()

    for i in range(0, len(res)):
        res[i] = res[i].to_dict()

    return get_json_success(app_data=res), 200


@hackathons.route('/hackathons/<hack_id>/teams', methods=["GET"])
def get_hackathon_teams(hack_id):
    res = h_t_list.query.with_entities(h_t_list.team_id).filter(h_t_list.hack_id == hack_id).all()

    if not res:
        return get_json_success("No teams participate in that hackathon"), 200

    team_ids = []
    for i in range(len(res)):
        team_ids.append(res[i][0])

    for i in range(0, len(team_ids)):
        res[i] = Teams.query.filter(Teams.id == team_ids[i]).first().to_dict()

    return get_json_success(app_data=res), 200


@hackathons.route('/hackathons', methods=["POST"])
@login_required
def create_hackathon():
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role

    if user_role != 1:
        return get_json_fail("Privilege level too low"), 403

    data = request.get_json()

    if data and all(key in data for key in ('name', 'date', 'org_id', 'address', 'theme')):
        try:
            hack_date = datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return get_json_fail("Incorrect datetime format. The format has to be yyyy-mm-dd")

        if hack_date < datetime.today():
            return get_json_fail("The hackathons date cannot be in the past."), 422

        new_hackathon = Hackathons(name=data['name'],
                                   date=data['date'],
                                   address=data['address'],
                                   theme=data['theme'],
                                   org_id=data['org_id'])

        db.session.add(new_hackathon)
        db.session.commit()

        return get_json_success("Hackathon created successfully", app_data={"hackathon_id": new_hackathon.id}), 200

    return get_json_fail("Incorrect input. To create hackathon specify its name, date, address and theme"), 422


@hackathons.route("/hackathons/<hack_id>", methods=["DELETE"])
@login_required
def delete_hackathon(hack_id):
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role
    hackathon = Hackathons.query.filter(Hackathons.id == hack_id).first()

    if user_role not in (1, 2):
        return get_json_fail("Privilege level too low"), 403

    if not hackathon:
        return get_json_fail("Hackathon with such id does not exist"), 404

    if user_role == 2 and hackathon.org_id != user_id:
        return get_json_fail("You are not an organiser of that hackathon"), 403

    Hackathons.query.filter(Hackathons.id == hack_id).delete()
    db.session.commit()

    return get_json_success("Hackathon with given id successfully deleted"), 200


def check_award_arg(data, arg):
    if data and arg in data and isinstance(data[arg], int):
        return True

    return False


@hackathons.route("/hackathons/<hack_id>/award", methods=["POST"])
@login_required
def award_teams(hack_id):
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role
    hackathon = Hackathons.query.filter(Hackathons.id == hack_id).first()
    if not hackathon:
        return get_json_fail("Hackathon with such id not found"), 403

    if user_role == 1 or (user_role == 2 and hackathon.org_id == user_id):
        data = request.get_json()
        flag = False

        if check_award_arg(data, 'id_first'):
            flag = True
            hackathon.id_first = data['id_first']

        if check_award_arg(data, 'id_second'):
            flag = True
            hackathon.id_second = data['id_second']

        if check_award_arg(data, 'id_third'):
            flag = True
            hackathon.id_third = data['id_third']

        if not flag:
            return get_json_fail("At least one of the fields id_first, id_second or id_third should be specified"), 422

        db.session.commit()

        return get_json_success("Winners successfully set"), 200

    return get_json_fail("Privilege level too low"), 403
