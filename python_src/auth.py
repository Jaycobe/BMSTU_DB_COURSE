import flask_login
from flask import Blueprint, request, session
from flask_login import login_user, login_required, logout_user, current_user
from models import Users, Roles, Ratings
from json_responses import *
from __init__ import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login_post():
    auth = request.authorization
    if auth:

        login = auth.get('username')
        password = auth.get('password')

        if not login or not password:
            return get_json_fail("Not all data is provided"), 422

        if not login.isalnum() or not password.isalnum():
            return get_json_fail("Login and password must contain only alphanumerical symbols"), 422

        user = Users.query.filter_by(login=auth.get('username'), password=auth.get('password')).first()

        if user:
            login_user(user)
            return get_json_success("Login success")

    return get_json_fail("Login failed. Incorrect data"), 422


@auth.route('/logout', methods=['POST'])
@login_required
def logout_func():
    logout_user()
    return get_json_success("Logout success")


@auth.route('/signup', methods=['POST'])
def signup_post():
    data = request.get_json()
    auth = request.authorization

    if auth and data and all(key in data for key in ('name', 'role')):

        login = auth.get('username')
        password = auth.get('password')
        name = data['name']
        role = data['role']

        if not login.isalnum() or not name.isalnum() or not password.isalnum():
            return get_json_fail("Login, name and password must contain only letters and numbers"), 422

        if not role.isalpha():
            return get_json_fail("Role has to be a number"), 422

        if role not in ('Participant', 'Organizer'):
            return get_json_fail("Role has to be either \"Participant\" or \"Organizer\""), 422

        if len(login) < 4:
            return get_json_fail("Login must be at least 4 characters long"), 422

        if len(password) < 8:
            return get_json_fail("Password must be at least 8 characters long"), 422

        user = Users.query.filter_by(login=login).first()

        if user:
            return get_json_fail("User with such login already exists"), 422

        if role == 'Participant':
            role = 4
        else:
            role = 2

        new_user = Users(name=name, login=login, password=password, role=role)

        if role == 4:
            new_participant = Ratings(id=new_user.id, rating=0)
            db.session.add(new_participant)

        db.session.add(new_user)
        db.session.commit()

        return get_json_success("User successfully created"), 200

    return get_json_fail("Not all data is specified"), 422
