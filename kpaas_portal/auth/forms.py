# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, regexp, InputRequired, EqualTo, ValidationError

from kpaas_portal.user.models import User

USERNAME_RE = r'^[\w.+-]+$'
is_username = regexp(USERNAME_RE, message=u'只能是字母数字及横线.')


class LoginForm(Form):
    """
    登录
    """
    login = StringField(u'账户', validators=[DataRequired(message=u'请输入账户名.')])
    password = PasswordField(u'密码', validators=[DataRequired(message=u'请输入密码.')])
    remember_me = BooleanField(u'记住我', default=False)
    submit = SubmitField(u'登录')


class RegisterForm(Form):
    """
    注册
    """
    username = StringField(u'账户', validators=[DataRequired(message=u'请填写用户名.'), is_username])
    email = StringField(u'电子邮件', validators=[DataRequired(message=u'请填写电子邮件.'), Email(message=u'电子邮件格式错误，请检查.')])
    password = PasswordField(u'密码', validators=[InputRequired(), EqualTo('confirm_password', message=u'两次输入的密码不一致，请检查.')])
    confirm_password = PasswordField(u'再输入一次密码')
    phone = StringField(u'手机号码')
    corp = StringField(u'公司名称')
    submit = SubmitField(u'注册')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError(u'此用户名已经存在.')

    def validate_email(self, field):
        email = User.query.filter_by(email=field.data).first()
        if email:
            raise ValidationError(u'此电子邮件已经存在.')


class ForgotPasswordForm(Form):
    email = StringField(u'Email address', validators=[DataRequired(message=u"请输入电子邮件地址."), Email()])
    submit = SubmitField(u"重置密码")
