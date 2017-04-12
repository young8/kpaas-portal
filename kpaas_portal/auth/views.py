# -*- coding: utf-8 -*-
"""
    kpaas-portal.auth
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from datetime import datetime
from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app
from flask_login import current_user, login_user, logout_user

from kpaas_portal.auth.forms import LoginForm, RegisterForm, ForgotPasswordForm
from kpaas_portal.user.models import User
from kpaas_portal.exceptions import AuthenticationError
from kpaas_portal.utils.helpers import redirect_or_next

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    登录
    """
    current_app.logger.info('GET /login')
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        try:
            user = User.authenticate(form.login.data, form.password.data)
            login_user(user, remember=form.remember_me.data)
            return redirect_or_next(url_for('main.index'))
        except AuthenticationError:
            flash(u'账户名或密码错误.', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    注册
    """
    if current_user is not None and current_user.is_authenticated:
        return redirect_or_next(url_for('main.index'))
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data,
                    phone=form.phone.data,
                    corp=form.corp.data,
                    date_joined=datetime.utcnow(),
                    is_admin=False)
        user.save()
        login_user(user)
        flash(u'感谢您的注册！.', "success")
        return redirect_or_next(current_user.url)
    return render_template('auth/register.html', form=form)


@auth.route('/reset-password', methods=['GET', 'POST'])
def forgot_password():
    """
    忘记密码
    """
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            print user.password
            flash(u"密码邮件已经发送，请查收.", "info")
            return redirect(url_for("auth.login"))
        else:
            flash(u"此邮件未注册，请检查.", "danger")
    return render_template('auth/forgot_password.html', form=form)


@auth.route('/logout')
def logout():
    """
    退出
    """
    logout_user()
    flash(u'退出系统成功.', 'success')
    return redirect(url_for('auth.login'))
