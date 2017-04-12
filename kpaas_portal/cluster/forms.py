# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Required


class ClusterCreateForm(Form):
    """
    创建集群
    """
    cluster_description = StringField(label=u"集群描述", validators=[DataRequired(message=u"请填写集群描述。")])
    cluster_type = SelectField(label=u"节点数量",
                               choices=[(3, u"3 节点"),
                                        (8, u"8 节点"),
                                        (16, u"16 节点"),
                                        (20, u"20 节点")],
                               default=3, validators=[Required(u"请选择节点数量。")])
    cluster_machine = SelectField(label=u"节点配置",
                                  choices=[("s", u"Small (8C CPU, 16G MEM)"),
                                           ("m", u"Normal (12C CPU, 32G MEM)"),
                                           ("l", u"Large (16C CPU, 32G MEM)")],
                                  default="s", validators=[Required(u"请选择节点配置。")])
    submit = SubmitField(label=u"创建集群")


class ClusterDeployForm(Form):
    """
    部署集群
    """
    submit = SubmitField(label=u"开始部署")


class ClusterPublishForm(Form):
    """
    发布集群
    """
    submit = SubmitField(label=u"确认发布")


class ClusterDeleteForm(Form):
    """
    删除集群
    """
    submit = SubmitField(label=u"彻底删除集群")

