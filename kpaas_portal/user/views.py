# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required

from kpaas_portal.user.forms import EditCephKeysForm

user = Blueprint('user', __name__)


@user.route('/')
@login_required
def index():
    """
    用户信息
    """
    user = {
        'username': current_user.username,
        'password': current_user.password,
        'email': current_user.email,
        'phone': current_user.phone,
        'corp': current_user.corp,
        'lastime': current_user.last_success_time,
        'is_admin': current_user.is_admin
    }

    kubernetes = {
        'namespace': current_user.namespace
    }

    if current_user.ceph_keys:
        values = (current_user.ceph_keys).split()
        keys = ['user_id', 'access_key', 'secret_key']
        ceph = dict(zip(keys, values))
    else:
        ceph = None

    return render_template('user/index.html', user=user, kubernetes=kubernetes, ceph=ceph)


@user.route('/profile/editCephKeys', methods=['GET', 'POST'])
@login_required
def edit_ceph_keys():
    form = EditCephKeysForm()
    if form.validate_on_submit():
        keys = ' '.join(
            [form.data.get('ceph_user_id'), form.data.get('ceph_access_key'), form.data.get('ceph_secret_key')])
        current_user.ceph_keys = keys
        current_user.save()
        flash(u'成功！新的 Ceph S3 Keys 被保存.', 'success')
        return redirect(url_for('user.index'))
    return render_template('user/edit_ceph_keys.html', form=form)


@user.route('/profile/resetCephKeys')
@login_required
def reset_ceph_keys():
    current_user.ceph_keys = None
    current_user.save()
    flash(u'警告！Ceph S3 Keys 被重置.', 'danger')
    return redirect(url_for('user.index'))
