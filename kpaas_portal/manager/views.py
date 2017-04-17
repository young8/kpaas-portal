# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask import Blueprint, render_template, request, current_app, logging
from flask_login import current_user
from forms import RegisterBucketForm

from kpaas_portal.extensions import cache
from kpaas_portal.cluster.models import Service
from kpaas_portal.user.models import User
from kpaas_portal.utils.cephtools import CephClass
from kpaas_portal.utils.k8stools import K8sServiceClass
from kpaas_portal.utils.consultools import ConsulServiceClass
from kpaas_portal.utils.haproxytools import HaproxyServiceClass

manager = Blueprint('manager', __name__)


@manager.route('/k8s')
# @cache.cached(timeout=60)
def k8s():
    """
    k8s 查询
    """
    k8s_instance = K8sServiceClass(host=current_app.config['K8S_SERVICE_ADDR'], port=current_app.config['K8S_SERVICE_PORT'], namespace='default')
    return render_template('manager/k8s.html', services=k8s_instance.services(), pods=k8s_instance.pods())


@manager.route("/consul")
# @cache.cached(timeout=60)
def consul():
    """
    Consul
    """
    _nodes = []
    _services = []
    _ceph = []

    consul_instance = ConsulServiceClass(host=current_app.config['CONSUL_SERVICE_ADDR'], port=current_app.config['CONSUL_SERVICE_PORT'])
    consul_nodes = consul_instance.nodes()

    for node in consul_nodes:
        n = str(node.get('Node'))
        if not n:
            break
        if n.startswith('cluster'):
            _nodes.append(node)
            continue
        if n.startswith('amb-consul'):
            _services.append(node)
            continue
        if n.endswith('s3.rgw.ceph'):
            _ceph.append(node)
            continue

    return render_template("manager/consul.html",
                           nodes=_nodes,
                           services=_services,
                           ceph=_ceph)


@manager.route('/users')
@cache.cached(timeout=60)
def users():
    """
    用户
    """
    users = User.query.order_by(User.register_time).all()

    return render_template("manager/user.html", users=users)


@manager.route('/haproxy')
# @cache.cached(timeout=60)
def haproxy():
    """
    haproxy 端口映射服务
    """
    proxy = HaproxyServiceClass()
    ports = proxy.list_ports()
    logging.getLogger('app').info('{}'.format(ports))

    return render_template("manager/haproxy.html", ports=ports)


@manager.route('/ceph/buckets', methods=['POST', 'GET'])
def buckets():
    """
    Ceph Buckets
    """
    form = RegisterBucketForm()

    ceph_keys = (current_user.ceph_keys).split()
    ceph_instance = CephClass(ceph_keys[1], ceph_keys[2])
    buckets = ceph_instance.get_all_buckets()

    if request.method == 'POST':
        print form.data

    return render_template('manager/ceph.html', buckets=buckets, form=form)


@manager.route('/ceph/buckets/<bucket>')
@cache.cached(timeout=60)
def view_bucket(bucket):
    """
    Ceph Bucket Objects
    """

    ceph_keys = (current_user.ceph_keys).split()
    ceph_instance = CephClass(ceph_keys[1], ceph_keys[2])
    buckets = ceph_instance.get_all_buckets()
    b = ceph_instance.get_bucket_by_name(bucket)

    if b:
        content = ceph_instance.get_bucket_content(b)
        print ceph_instance.get_object(b, 'output/')
    else:
        content = 'Empty!'

    return render_template('manager/ceph.html', buckets=buckets, bucket=bucket, content=content)
