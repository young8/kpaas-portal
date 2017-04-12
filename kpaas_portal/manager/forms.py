# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class RegisterBucketForm(Form):
    """
    注册 ceph s3 bucket
    """
    bucket_name = StringField(label=u'Bucket 名称',
                              validators=[DataRequired(message=u'请填写 Bucket 名称.')])
    submit = SubmitField(label=u'注册一个 Bucket')

