# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class EditCephKeysForm(Form):
    """
    Edit Ceph S3 Keys
    """
    ceph_user_id = StringField(label=u"Ceph S3 的 User ID", validators=[DataRequired(message=u"请填写 Ceph S3 User ID.")])
    ceph_access_key = StringField(label=u"Ceph S3 的 Access Key",
                                  validators=[DataRequired(message=u"请填写 Ceph S3 Access Key.")])
    ceph_secret_key = StringField(label=u"Ceph S3 的 Secret key",
                                  validators=[DataRequired(message=u"请填写 Ceph S3 Secret key.")])

    submit = SubmitField(label=u"保存")
