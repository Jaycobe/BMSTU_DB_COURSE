import flask_login
from flask import Blueprint, request
from flask_login import login_required, current_user
from models import Requests, Teams, Users, t_p_list, Hackathons, h_t_list
from json_responses import *
from __init__ import db
from sqlalchemy import func

requests = Blueprint('requests', __name__)


def check_request_args(data):
    res = False

    if 'type' in data and isinstance(data['type'], int) and 1 <= data['type'] <= 4:
        type = data['type']

        if int(type) == 1:  # создать команду
            if 'name' in data and data['name'].isalnum():
                res = True
        elif type == 2:  # присоединиться к команде
            if 'target_team_id' in data and isinstance(data['target_team_id'], int):
                res = True
        elif type == 3:  # создать мероприятие
            if 'name' in data and data['name'].isalnum():
                res = True
        else:  # присоединиться к мероприятию
            if ('target_team_id' in data and isinstance(data['target_team_id'], int)
                    and 'target_hackathon_id' in data and isinstance(data['target_team_id'], int)):
                res = True

    return res


@requests.route("/requests", methods=['POST'])
@login_required
def post_request():
    data = request.get_json()
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role

    if not check_request_args(data):
        return get_json_fail("Incorrect arguments"), 422

    comment = ''

    if "comment" in data:
        comment = data['comment']

    # создание команды
    if int(data['type']) == 1:
        if user_role == 2:
            return get_json_fail("Organizers cannot create teams"), 403

        new_request = Requests(type=data['type'],
                               name=data['name'],
                               comment=comment,
                               requester_id=current_user.id,
                               requester_role=user_role,
                               status=1)

        db.session.add(new_request)
        db.session.commit()
    elif int(data['type']) == 2:  # присоединиться к команде
        if user_role in (1, 2):
            return get_json_fail("You cannot join teams"), 403

        team = Teams.query.filter(Teams.id == data['target_team_id']).first()

        if not team:
            return get_json_fail("Team with such id not found"), 422

        new_request = Requests(type=data['type'],
                               comment=comment,
                               requester_id=current_user.id,
                               requester_role=user_role,
                               target_team_id=data['target_team_id'],
                               status=1)

        db.session.add(new_request)
        db.session.commit()

    elif int(data['type'] == 3):  # создать событие
        if user_role not in (1, 2):
            return get_json_fail("You cannot create hackathons"), 403

        user_role = Users.query.filter_by(id=user_id).first().role

        new_request = Requests(type=data['type'],
                               name=data['name'],
                               comment=comment,
                               requester_id=current_user.id,
                               requester_role=user_role,
                               status=1)

        db.session.add(new_request)
        db.session.commit()

    elif int(data['type'] == 4):  # присоединиться к событию
        check_team = Teams.query.filter(Teams.id == data["target_team_id"]).first()

        if not check_team:
            return get_json_fail("Team with such id not found"), 422

        check_hackathon = Hackathons.query.filter(Hackathons.id == data['target_hackathon_id']).first()

        if not check_hackathon:
            return get_json_fail("Hackathon with such id not found"), 422

        teams = Teams.query.filter(Teams.cap_id == user_id).all()
        flag = False
        for team in teams:
            if team.cap_id == user_id and data["target_team_id"] == team.id:
                flag = True

        if not flag:
            return get_json_fail("Only team captains are eligible to send requests to join events"), 403

        new_request = Requests(type=4,
                               target_hackathon_id=data['target_hackathon_id'],
                               target_team_id=data['target_team_id'],
                               status=1,
                               requester_id=user_id,
                               requester_role=user_role,
                               comment=comment)
        db.session.add(new_request)
        db.session.commit()

    return get_json_success("Request created successfully", app_data={"request_id": new_request.id}), 200


@requests.route("/requests/my_requests", methods=['GET'])
@login_required
def get_my_requests():
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role
    requests = Requests.query.filter(Requests.requester_id == user_id).all()

    if user_role == 1:
        admin_requests = Requests.query.filter(Requests.adm_id == user_id).all()
        if admin_requests:
            requests.extend(admin_requests)
    elif user_role == 2:
        pass
    elif user_role == 3:
        teams = Teams.query.filter(Teams.cap_id == user_id).all()
        team_ids = [team.id for team in teams]
        print(team_ids)
        captain_requests = Requests.query.filter(Requests.target_team_id.in_( team_ids)).all()
        print(captain_requests)
        if captain_requests:
            requests.extend(captain_requests)
        print(requests)
    if not requests:
        return get_json_success("You have no active requests")

    for i in range(0, len(requests)):
        requests[i] = requests[i].to_dict()

    return get_json_success(app_data=requests)


@requests.route("/requests", methods=['GET'])
@login_required
def get_all_requests():
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role

    if user_role != 1:
        return get_json_fail("Privilege level too low"), 403

    res = Requests.query.filter().all()

    for i in range(0, len(res)):
        res[i] = res[i].to_dict()

    return get_json_success("Requests retrieved successfully", app_data=res), 200


@requests.route("/requests/open", methods=['GET'])
@login_required
def get_open_requests():
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role

    if user_role != 1:
        return get_json_fail("Privilege level too low"), 403

    res = Requests.query.filter(Requests.status == 1).all()

    for i in range(0, len(res)):
        res[i] = res[i].to_dict()

    return get_json_success("Requests retrieved successfully", app_data=res), 200


@requests.route("/requests/<id>", methods=['GET'])
def get_request(req_id):
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role
    req = Requests.query.filter(Requests.id == req_id).first()

    if not req:
        return get_json_fail("Request with such id doesn't exist"), 404

    if req.requester_id == user_id or user_role == 1:
        return get_json_success(app_data=req.to_dict()), 200

    return get_json_fail("Privilege level too low"), 403


@requests.route("/requests/accept/<request_id>", methods=["PUT"])
@login_required
def accept_request(request_id):
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role
    req = Requests.query.filter(Requests.id == request_id).first()

    if user_role != 1:
        return get_json_fail("Privilege level too low"), 403

    if not req:
        return get_json_fail("Request not found"), 404

    if req.status != 1:
        return get_json_fail("Request is already accepted"), 422

    req.status = 2
    req.adm_id = user_id
    db.session.commit()

    return get_json_success("Request accepted"), 200


@requests.route("/requests/approve/<request_id>", methods=["PUT"])
@login_required
def approve_request(request_id):
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role
    req = Requests.query.filter(Requests.id == request_id).first()

    if user_role == 4:
        return get_json_fail("Privilege level too low"), 403

    if not req:
        return get_json_fail("Request not found"), 404

    if req.type in (1, 3):
        if user_role == 1:
            req.status = 3
            db.session.commit()
        else:
            return get_json_fail("You cannot approve that request"), 403
    elif req.type == 2:
        if user_role == 3:
            team = Teams.query.filter(Teams.cap_id == user_id, Teams.id == req.target_team_id).first()

            if not team:
                return get_json_fail("Cannot accept member to that team"), 422

            if team.n_members == 5:
                return get_json_fail("Team is full"), 422

            check_relation = t_p_list.query.filter(t_p_list.team_id == team.id,
                                                   t_p_list.part_id == req.requester_id).first()

            if check_relation:
                return get_json_fail("That member is already in team"), 422

            new_t_p_relation = t_p_list(part_id=req.requester_id, team_id=team.id)
            db.session.add(new_t_p_relation)
            db.session.commit()
            db.session.query(func.public.update_team_data(team.id)).all()
            db.session.commit()
    elif req.type == 4:
        hackathon = Hackathons.query.filter(Hackathons.id == req.target_hackathon_id).first()

        if not hackathon:
            return get_json_fail("The specified hackathon does not exist"), 422

        if user_role != 2 or hackathon.org_id != user_id:
            return get_json_fail("You are not eligible to approve requests to join that event"), 403

        check_relation = h_t_list.query.filter(h_t_list.team_id == req.target_team_id,
                                               h_t_list.hack_id == req.target_hackathon_id).first()

        if check_relation:
            return get_json_fail("That team already participates in the hackathon"), 422

        new_h_t_relation = h_t_list(team_id=req.target_team_id, hack_id=req.target_hackathon_id)
        print(new_h_t_relation)
        db.session.add(new_h_t_relation)
        db.session.commit()

    return get_json_success("Request approved"), 200


@requests.route("/requests/decline/<request_id>", methods=["PUT"])
@login_required
def decline_request(request_id):
    user_id = flask_login.current_user.id
    user_role = Users.query.filter_by(id=user_id).first().role
    req = Requests.query.filter(Requests.id == request_id)

    if user_role == 4:
        return get_json_fail("Privilege level too low"), 403

    if not req:
        return get_json_fail("Request not found"), 404

    req.status = 4
    db.session.commit()

    return get_json_success("Request denied"), 200
