# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask import Blueprint, render_template, request, current_app, logging
from flask_login import current_user
from .forms import FindBucketForm

from kpaas_portal.extensions import cache
from kpaas_portal.cluster.models import Service
from kpaas_portal.user.models import User
from kpaas_portal.utils.cephtools import CephClass
from kpaas_portal.utils.consultools import ConsulServiceClass
from kpaas_portal.utils.haproxytools import HaproxyServiceClass

from kpaas_portal.api_1_1.models import KubeApiService

manager = Blueprint('manager', __name__)


@manager.route('/k8s')
# @cache.cached(timeout=60)
def k8s():
    """
    k8s 查询
    """
    pods, services = [], []
    current_app.logger.debug('GET /k8s')
    k8s_instance = KubeApiService(host=current_app.config['K8S_SERVICE_ADDR'], port=current_app.config['K8S_SERVICE_PORT'])
    pod_items = k8s_instance.get_pods('default')
    if pod_items.get('items'):
        for item in pod_items['items']:
            current_app.logger.debug('pod is: name:{0}, status: {1}, ip: {2}, node: {3}'.format(item['metadata']['name'], item['status']['phase'], item['status']['podIP'], item['status']['hostIP']))
            pods.append({'name': item['metadata']['name'], 'status': item['status']['phase'], 'ip': item['status']['podIP'], 'node': item['status']['hostIP']})
    svr_items = k8s_instance.get_services('default')
    if svr_items.get('items'):
        for item in svr_items['items']:
            current_app.logger.debug('service is: name:{0}, type: {1}, port: {2}, nodeport: {3}'.format(item['metadata']['name'], item['spec']['type'], item['spec']['ports'][0].get('targetPort', 0), item['spec']['ports'][0].get('nodePort', 0)))
            services.append({'name': item['metadata']['name'], 'type': item['spec']['type'], 'port': item['spec']['ports'][0].get('targetPort', 0), 'nodeport': item['spec']['ports'][0].get('nodePort', 0)})
    return render_template('manager/k8s.html', services=services, pods=pods)


@manager.route("/consul")
# @cache.cached(timeout=60)
def consul():
    """
    Consul 服务接口
    节点: cluster
    服务: amb-consul
    ceph object: s3.rgw.ceph
    """
    consul_instance = ConsulServiceClass(host=current_app.config['CONSUL_SERVICE_ADDR'], port=current_app.config['CONSUL_SERVICE_PORT'])
    consul_nodes = consul_instance.nodes()
    _nodes = []
    if consul_nodes:
        for node in consul_nodes:
            n = str(node.get('Node'))
            if not n:
                break
            if n.startswith('cluster'):
                _nodes.append(node)

    return render_template("manager/consul.html", nodes=_nodes)


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
    获取 Ceph Buckets 列表
    """
    buckets = []
    form = FindBucketForm()
    if request.method == 'POST':
        current_app.logger.debug('ceph api get buckets: post data="{}"'.format(form.data))
        access_key = form.data.ceph_access_key
        secret_key = form.data.secret_key
        ceph_instance = CephClass(access_key, secret_key)
        buckets = ceph_instance.get_all_buckets()

    return render_template('manager/ceph.html', buckets=buckets, form=form)


@manager.route('/ceph/buckets/<bucket>')
# @cache.cached(timeout=60)
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
