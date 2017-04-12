# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from flask_wtf import Form
from wtforms import StringField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired


class TaskCreateForm(Form):
    """
    创建 MR 任务
    """
    upload_file = FileField(label=u"上传 Jar 文件")

    task_job_input = StringField(label=u"输入路径", validators=[DataRequired(message=u'请填写输入路径')])
    task_job_output = StringField(label=u"输出路径", validators=[DataRequired(message=u'请填写输出路径')])
    task_job_mapClass = StringField(label=u"Map Class 参数", validators=[DataRequired(message=u'请填写输入 Map Class 参数')])
    task_job_reduceClass = StringField(label=u"Reduce Class 参数",
                                       validators=[DataRequired(message=u'请填写输入 Reduce Class 参数')])
    task_job_keyClass = StringField(label=u"Key Class 参数", validators=[DataRequired(message=u'请填写输入 Key Class 参数')])
    task_job_valueClass = StringField(label=u"Value Class 参数",
                                      validators=[DataRequired(message=u'请填写输入 Value Class 参数')])

    submit = SubmitField(label=u'创建 MR 任务')


class HiveTableCreateForm(Form):
    """
    创建 Hive 表
    """
    table_name = StringField(label=u'输入表名，注意不能重名，默认为 mr_ 加 任务id，如：mr_1')
    table_fields = StringField(label=u'输入表结构，如: word STRING, count INT', validators=[DataRequired(message=u'请填写表结构')])
    table_field_separator = StringField(label=u'输入分割符，如: 竖线或逗号等，默认为空格分隔')

    submit = SubmitField(label=u'创建 Hive 表')


class HiveTableCreateFromS3Form(Form):
    """
    S3 创建 Hive 表
    """

    cluster_id = SelectField(label=u"可用集群", choices=[], validators=[DataRequired(u"请选一个集群")], coerce=int)
    table_name = StringField(label=u'输入表名，注意不能重名，默认为 mr_ 加 任务id，如：mr_1')
    table_fields = StringField(label=u'输入表结构，如: word STRING, count INT', validators=[DataRequired(message=u'请填写表结构')])
    table_field_separator = StringField(label=u'输入分割符，如: 竖线或逗号等，默认为空格分隔')

    submit = SubmitField(label=u'创建 Hive 表')