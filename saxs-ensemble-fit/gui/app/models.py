from flask.ext.login import UserMixin, request
from flask import redirect
from app import db
from flask_admin.contrib.sqla import ModelView


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String, index=True, unique=True)
    eppn = db.Column(db.String, index=True, unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class UserView(ModelView):
    page_size = 30
    can_edit = False
    can_create = False
    column_editable_list = ['confirmed', 'role']

    def is_accessible(self):
        user_details = get_user_details()
        return is_user_confirmed(user_details[0]) and is_user_admin(user_details[0])

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect("/")


def get_user_details():
    result = [request.environ["HTTP_EPPN"], request.environ["HTTP_CN"].decode("unicode_escape"), request.environ["HTTP_MAIL"].decode("unicode_escape")]
    return result


def is_user_registered(eppn):
    user = User.query.filter_by(eppn=eppn).first()
    return user is not None


def is_user_confirmed(eppn):
    user = User.query.filter_by(eppn=eppn).first()
    return user is not None and user.confirmed


def is_user_admin(eppn):
    user = User.query.filter_by(eppn=eppn).first()
    return user is not None and user.role_id == 1

