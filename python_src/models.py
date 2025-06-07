from __init__ import db
from flask_login import UserMixin


class Roles:
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)


class Types:
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)


class Statuses:
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    name = db.Column(db.Text)
    role = db.Column(db.Integer, db.ForeignKey(Roles.id))

    def to_dict(self):
        res = {}

        for c in self.__table__.columns:
            if c.name != 'password':
                res[c.name] = getattr(self, c.name)

        return res


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    n_members = db.Column(db.Integer)
    rating = db.Column(db.Float)
    cap_id = db.Column(db.Integer, db.ForeignKey(Users.id))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Ratings(db.Model):
    id = db.Column(db.Integer, db.ForeignKey(Users.id), primary_key=True)
    rating = db.Column(db.Integer)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Hackathons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    address = db.Column(db.Text)
    date = db.Column(db.DateTime)
    theme = db.Column(db.Text)
    org_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    id_first = db.Column(db.Integer, db.ForeignKey(Users.id))
    id_second = db.Column(db.Integer, db.ForeignKey(Users.id))
    id_third = db.Column(db.Integer, db.ForeignKey(Users.id))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, db.ForeignKey(Types.id))
    requester_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    requester_role = db.Column(db.Integer, db.ForeignKey(Roles.id))
    target_team_id = db.Column(db.Integer, db.ForeignKey(Teams.id))
    target_hackathon_id = db.Column(db.Integer, db.ForeignKey(Hackathons.id))
    status = db.Column(db.Integer, db.ForeignKey(Statuses.id))
    name = db.Column(db.Text)
    adm_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    comment = db.Column(db.Text)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



class h_t_list(db.Model):
    hack_id = db.Column(db.Integer, db.ForeignKey(Hackathons.id), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey(Teams.id))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class t_p_list(db.Model):
    part_id = db.Column(db.Integer, db.ForeignKey(Users.id), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey(Teams.id))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
