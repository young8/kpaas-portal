# -*- coding: utf-8 -*-
"""
    kpaas-portal.auth
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from datetime import datetime
from flask import url_for
from flask_login import UserMixin, AnonymousUserMixin

from kpaas_portal.extensions import db
from kpaas_portal.exceptions import AuthenticationError


class Guest(AnonymousUserMixin):
    """
    组
    """
    is_admin = False
    pass


class User(db.Model, UserMixin):
    """
    账户
    """
    __tablename__ = "user"
    __searchable__ = ["username", "email"]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    _password = db.Column('password', db.String(120))
    register_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    corp = db.Column(db.String(100))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_failed_time = db.Column(db.DateTime)
    last_success_time = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    activated = db.Column(db.Boolean, default=False)
    namespace = db.Column(db.String(50), default='default')
    cluster_count = db.Column(db.Integer, default=0)
    ceph_keys = db.Column(db.String(255))

    buckets = db.relationship('Bucket', backref='user', lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')
    clusters = db.relationship('Cluster', backref='user', lazy='dynamic')

    @property
    def url(self):
        return url_for('user.index', username=self.username)

    @property
    def days_registered(self):
        days_registered = (datetime.utcnow() - self.register_time).days
        if not days_registered:
            return 1
        return days_registered

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.username)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if not password:
            return
        self._password = password

    password = db.synonym('_password', descriptor=property(_get_password, _set_password))

    def check_password(self, password):
        if self.password is None:
            return False
        # !!!
        if not self.password == password:
            return False
        return True

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(db.or_(User.username == login,
                                       User.email == login)).first()
        if user:
            if user.check_password(password):
                user.login_attempts = 0
                user.save()
                return user
            user.login_attempts += 1
            user.last_failed_login = datetime.utcnow()
            user.save()

        raise AuthenticationError

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
