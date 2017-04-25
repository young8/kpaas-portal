# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import json
from datetime import datetime
from flask import current_app
from flask_login import current_user

from kpaas_portal.extensions import db
from kpaas_portal.utils.database import CRUDMixin
from kpaas_portal.utils.cephtools import CephClass


class Bucket(db.Model, CRUDMixin):
    """
    Ceph S3 Bucket
    """
    __tablename__ = 'bucket'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.id)

    @property
    def bucket_fullname(self):
        return '{0}.{1}.{2}'.format(self.name, current_app.config['CEPH_SERVICE_HOSTNAME'], current_app.config['CEPH_SERVICE_DOMAIN'])

    @property
    def bucket_shortname(self):
        return '{0}.{1}'.format(self.name, current_app.config['CEPH_SERVICE_HOSTNAME'])

    @property
    def bucket_ip(self):
        return current_app.config['CEPH_SERVICE_IP']

    @property
    def objects_count(self):
        count = 0
        ceph_keys = (current_user.ceph_keys).split()
        ceph_instance = CephClass(ceph_keys[1], ceph_keys[2])
        name = ceph_instance.get_bucket_by_name(self.name)
        ceph_objects = ceph_instance.get_bucket_content(name)
        if ceph_objects:
            count = len(ceph_objects)

        return count

    def list_objects(self):
        ceph_keys = (current_user.ceph_keys).split()
        ceph_instance = CephClass(ceph_keys[1], ceph_keys[2])
        name = ceph_instance.get_bucket_by_name(self.name)
        ceph_objects = ceph_instance.get_bucket_content(name)

        return ceph_objects
