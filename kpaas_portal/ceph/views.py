# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

from kpaas_portal.extensions import cache
from kpaas_portal.utils.cephtools import CephClass
from kpaas_portal.ceph.forms import BucketCreateForm
from kpaas_portal.ceph.models import Bucket

ceph = Blueprint("ceph", __name__)


@ceph.route("/buckets")
@login_required
# @cache.cached(timeout=60)
def view_ceph_buckets():
    ceph_keys = (current_user.ceph_keys).split()
    ceph_instance = CephClass(ceph_keys[1], ceph_keys[2])
    buckets = ceph_instance.get_all_buckets()

    return render_template("ceph/index.html", buckets=buckets)


@ceph.route("/<bucket>")
@login_required
# @cache.cached(timeout=60)
def view_ceph_objects(bucket):
    ceph_keys = (current_user.ceph_keys).split()

    ceph_instance = CephClass(ceph_keys[1], ceph_keys[2])
    buckets = ceph_instance.get_all_buckets()
    b = ceph_instance.get_bucket_by_name(bucket)
    if b:
        content = ceph_instance.get_bucket_content(b)
    else:
        content = 'Empty!'
    return render_template('ceph/index.html', buckets=buckets, bucket=bucket, content=content)


@ceph.route('/')
# @cache.cached(timeout=60)
def index():
    _buckets = Bucket.query.filter_by(owner=current_user.id).all()

    return render_template('ceph/index.html', buckets=_buckets)


@ceph.route('/buckets/<bucket_id>')
# @cache.cached(timeout=60)
def view_bucket(bucket_id):
    objects = []
    bucket = Bucket.query.filter_by(id=bucket_id).first()
    if bucket:
        objects = bucket.list_objects()

    return render_template('ceph/bucket.html', bucket=bucket, objects=objects)


@ceph.route('/create', methods=['GET', 'POST'])
def create_bucket():
    form = BucketCreateForm()

    if form.validate_on_submit():
        bucket = Bucket()
        bucket.name = form.name.data
        bucket.owner = current_user.id
        bucket.save()
        bucket.register_dns()

        return redirect(url_for('ceph.view_ceph_buckets'))

    return render_template('ceph/create_bucket.html', form=form)
