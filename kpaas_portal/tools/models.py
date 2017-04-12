# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import json
from datetime import datetime
from flask import url_for

from kpaas_portal.extensions import db
from kpaas_portal.utils.database import CRUDMixin


class Task(db.Model, CRUDMixin):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id', ondelete='CASCADE'))
    createtime = db.Column(db.DateTime, default=datetime.utcnow)
    overtime = db.Column(db.DateTime)
    data = db.Column(db.Text)
    status = db.Column(db.String(50))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)

    @property
    def url(self):
        return url_for('tools.mr_view_task', task_id=self.id)

    @property
    def data_to_html(self):
        d = json.loads(self.data)
        item = ''
        for k, v in d.items():
            item += '<li><b>{0}</b> : {1}</li>'.format(k, v)
        html = '<ul>' + item + '</ul>'

        return html

    @property
    def remain_time(self):
        result = 0
        if self.overtime:
            result = self.overtime - self.createtime
        return result

    @property
    def data_to_json(self):
        d = json.loads(self.data)
        if not isinstance(d, dict):
            return {}
        return d


class HiveTable(db.Model, CRUDMixin):
    __tablename__ = 'hivetable'

    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    db_name = db.Column(db.String(200))
    table_name = db.Column(db.String(200))
    table_schema = db.Column(db.Text)
    table_fields = db.Column(db.Text)
    table_location = db.Column(db.String(200))
    table_field_separator = db.Column(db.String(10))
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.id)

    def __init__(self, cluster, user, task_id=None, db_name='default', name=None, schema=None, fields=None, location=None, field_separator=' '):
        self.cluster_id = cluster.id
        self.user_id = user.id
        self.task_id = task_id
        self.db_name = db_name
        self.table_name = name
        self.table_schema = schema
        self.table_fields = fields
        self.table_location = location
        self.table_field_separator = field_separator
