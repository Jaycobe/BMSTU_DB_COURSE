import flask_login
from flask import Blueprint, request
from flask_login import login_required

from models import Teams, Users, Ratings, t_p_list
from json_responses import *
from __init__ import db

teams = Blueprint('teams', __name__)


@teams.route('/teams', methods=['GET'])
def get_teams():
    res = Teams.query.all()

    for i in range(0, len(res)):
        res[i] = res[i].to_dict()

    return get_json_success(app_data=res), 200


@teams.route('/teams/<team_id>', methods=['GET'])
def get_team(team_id):
    res = Teams.query.filter(Teams.id == team_id).first()

    if not res:
        return get_json_fail("Team not found"), 404

    res = res.to_dict()

    return get_json_success(app_data=res), 200


@teams.route('/teams/<team_id>/participants', methods=['GET'])
def get_team_participants(team_id):
    response = t_p_list.query.filter(t_p_list.team_id == team_id).all()

    if not response:
        return get_json_fail("Team with souch id not found"), 404

    user_ids = []

    for item in response:
        user_ids.append(item.part_id)

    # использовать join c рейтингом
    users_and_ratings = db.session.query(Users, Ratings).filter(
        Users.id.in_(user_ids)
    ).filter(
        Ratings.id == Users.id).all()
    print(users_and_ratings)
    res = []
    for i in range(0, len(users_and_ratings)):
        new_dict = users_and_ratings[i][0].to_dict()
        new_dict.update(users_and_ratings[i][1].to_dict())
        res.append(new_dict)

    print(res)
    return get_json_success(app_data=res), 200


@teams.route('/teams', methods=['POST'])
@login_required
def create_team():
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role

    if user_role != 1:
        return get_json_fail("Privilege level too low"), 401

    data = request.get_json()

    if data and all(key in data for key in ('name', 'cap_id')):
        captain = Users.query.filter(Users.id == data['cap_id']).first()

        if not captain:
            return get_json_fail("User with such captain id not found"), 422

        if captain.role in (1, 2):
            return get_json_fail("Organizers and admins cannot become team captains"), 422

        rating = Ratings.query.filter(Ratings.id == captain.id).first().rating

        new_team = Teams(name=data['name'], cap_id=data['cap_id'], n_members=1, rating=rating)
        db.session.add(new_team)
        db.session.commit()

        db.session.refresh(new_team)
        new_t_p_relation = t_p_list(part_id=captain.id, team_id=new_team.id)

        captain.role = 3

        db.session.add(new_t_p_relation)
        db.session.commit()

        return get_json_success('Team created successfully', app_data={"team_id": new_team.id}), 200

    return get_json_fail("Incorrect input"), 422


@teams.route('/teams/places_available', methods=['GET'])
def get_teams_available():
    res = Teams.query.filter(Teams.n_members < 5).all()

    if len(res) == 0:
        return get_json_fail("No teams with available places"), 200

    for i in range(0, len(res)):
        res[i] = res[i].to_dict()

    return get_json_success(app_data=res), 200


@teams.route('/teams/my_teams', methods=['GET'])
@login_required
def get_my_teams():
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role

    if user_role != 3:
        return get_json_fail("You are not a captain"), 403

    res = Teams.query.filter(Teams.cap_id == user_id).all()

    if not res:
        return get_json_fail("You have no teams"), 404

    for i in range(0, len(res)):
        res[i] = res[i].to_dict()

    return get_json_success("Teams successfully retrieved", app_data=res), 200


@teams.route("/teams/<team_id>/set_captain/<member_id>", methods=["PUT"])
@login_required
def set_captain(team_id, member_id):
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role

    team = Teams.query.filter_by(id=team_id).first()
    if user_role not in (1, 3):
        return get_json_fail("Privilege level too low"), 403

    if not team:
        return get_json_fail("Team with such id not found"), 404

    if user_role == 3 and team.captain_id != user_id:
        return get_json_fail("You are not eligible")

    return get_json_success()


@teams.route("/teams/<team_id>/leave", methods=["PUT"])
@login_required
def leave_team(team_id):
    # TODO
    return get_json_success()


@teams.route("/teams/<team_id>/<member_id>", methods=["DELETE"])
@login_required
def delete_team_member(team_id, member_id):
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role

    if user_role not in (1, 3):
        return get_json_fail("Privilege level too low")

    team = Teams.query.filter_by(id=team_id).first()

    if not team:
        return get_json_fail("Team with such id not found"), 404

    member_relation = t_p_list.query.filter_by(part_id=member_id).first()

    if not member_relation:
        return get_json_fail("Team member with such id not found"), 404

    t_p_list.query.filter(t_p_list.part_id == member_id).delete()
    db.session.commit()

    return get_json_success("Team member deleted successfully")

# !!! не нужно !!!
# @teams.route('/teams/<team_id>', methods=['DELETE'])
# @login_required
# def delete_team(team_id):
#     user_id = flask_login.current_user.id
#     user_role = Users.query.filter_by(id=user_id).first().role
#
#     if user_role not in (1, 3):
#         return get_json_fail("Privilege level too low"), 403
#
#     team = Teams.query.filter(Teams.id == team_id).first()
#
#     if not team:
#         return get_json_fail("Team not found"), 404
#
#     if user_role == 3 and team.cap_id != user_id:
#         return get_json_fail("You can only delete your own teams"), 422
#
#     t_p_list.query.filter(t_p_list.team_id == team_id).delete()
#     Teams.query.filter(Teams.id == team_id).delete()
#     db.session.commit()
#
#     return get_json_success("Team successfully deleted"), 200
