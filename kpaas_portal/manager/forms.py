# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class FindBucketForm(Form):
    """
    查询 ceph s3 的 bucket
    """
    ceph_username = StringField(label=u'User ID', validators=[DataRequired(message=u'请填写用户名称.')])
    ceph_access_key = StringField(label=u'Access Key', validators=[DataRequired(message=u'请填写 Access Key.')])
    ceph_secret_key = StringField(label=u'Secret key', validators=[DataRequired(message=u'请填写Secret key.')])
    submit = SubmitField(label=u'查询')

