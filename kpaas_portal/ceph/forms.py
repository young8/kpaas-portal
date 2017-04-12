# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class BucketCreateForm(Form):
    """
    注册 Ceph S3 Bucket
    """
    name = StringField(label=u"Bucket 名称", validators=[DataRequired(message=u"请填写 Bucket 名称.")])

    submit = SubmitField(label=u"注册")