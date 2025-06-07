from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'very-bad-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql://postgres:postgres@0.0.0.0:228/postgres'
    app.config['SESSION_TYPE'] = 'filesystem'

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import Users

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from users import users as users_blueprint
    app.register_blueprint(users_blueprint)

    from hackathons import hackathons as hackathons_blueprint
    app.register_blueprint(hackathons_blueprint)

    from requests import requests as requests_blueprint
    app.register_blueprint(requests_blueprint)

    from teams import teams as teams_blueprint
    app.register_blueprint(teams_blueprint)

    return app
