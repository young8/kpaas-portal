# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask import (Blueprint, render_template, redirect, url_for, flash, request, logging, current_app)
from flask_login import login_required, current_user

from .forms import ClusterCreateForm, ClusterDeployForm, ClusterDeleteForm
from .models import Cluster, Pod, Service

from kpaas_portal.extensions import cache
from kpaas_portal.utils.ambaritools import AmbariServiceClass
from kpaas_portal.utils.k8stools import celery_node_delete, celery_cluster_create, celery_cluster_deploy
from kpaas_portal.utils.haproxytools import HaproxyServiceClass

cluster = Blueprint('cluster', __name__)
mylogger = logging.getLogger('app')


def mp_deploy_node(node_name, node_cluster, node_namespace, node_type='agent'):
    agent_pod = Pod(node_type, node_cluster, node_name)
    agent_pod.save()
    celery_cluster_create.apply_async(args=[node_namespace, agent_pod.id])


@cluster.route('/')
@login_required
def index():
    """
    获取集群的列表
    """
    clusters = Cluster.query.filter_by(owner=current_user.id).order_by(Cluster.id.desc()).all()

    return render_template('cluster/index.html', clusters=clusters)


@cluster.route('/create', methods=['GET', 'POST'])
@login_required
def create_cluster():
    """
    创建一个新集群
    """

    ceph_key = current_user.ceph_keys
    ceph_key = ceph_key.split(' ')
    ceph_host = '{0}.{1}'.format(current_app.config['CEPH_SERVICE_HOSTNAME'], current_app.config['CEPH_SERVICE_DOMAIN'])
    ceph_info = (ceph_key[1], ceph_key[2], ceph_host)
    print ceph_info

    if not current_user.ceph_keys:
        flash(u'失败！当前用户没有配置 Ceph S3 Key，请配置账户信息。', 'danger')
        return redirect(current_user.url)

    form = ClusterCreateForm()

    if request.method == 'POST':
        # 初始化一个集群信息
        cluster_instance = Cluster(form.cluster_description.data, form.cluster_type.data, form.cluster_machine.data)
        cluster_instance.save(current_user)
        cluster_instance.name = 'cluster{0}'.format(cluster_instance.id)
        cluster_instance.save(current_user)

        # 1、创建 ambari server
        server_pod = Pod('server', cluster_instance)
        server_pod.save()

        server_service = Service('server', cluster_instance)
        server_service.save()

        celery_cluster_create.apply_async(args=['default', server_pod.id, server_service.id])

        # 2、创建 hive mysql
        hive_mysql_pod = Pod('hivedb', cluster_instance)
        hive_mysql_pod.save()
        celery_cluster_create.apply_async(args=['default', hive_mysql_pod.id])

        node_number = int(cluster_instance.type)
        for i in range(1, node_number + 1):
            name = 'agent{0}'.format(i)
            mp_deploy_node(name, cluster_instance, 'default')
        return redirect(url_for('cluster.index'))

    return render_template('cluster/cluster_create.html', form=form)


@cluster.route('/<cluster_id>')
def view_cluster(cluster_id):
    """
    查看并管理一个集群
    """
    cluster_instance = Cluster.query.filter_by(id=cluster_id).first_or_404()
    if not cluster_instance.cluster_deployment:
        flash(u'警告！当前节点还没有部署 Hadoop 集群组件，不能进行工具集相关操作，请检查并选择部署操作！', 'warning')

    service = Service.query.filter_by(cluster_id=cluster_id).first_or_404()
    if (not service) or (service.nport is None):
        flash(u'警告！当前 Hadoop 集群没有注册服务成功，这样会影响集群的正常使用，请检查或联系管理员！', 'warning')

    ambari_server = cluster_instance.pods.filter_by(type='server').first()
    ambari_instance = AmbariServiceClass(ambari_server.sip)

    _pods = []
    pods = cluster_instance.pods.order_by(Pod.type.desc()).all()
    for pod in pods:
        if cluster_instance.cluster_deployment and pod.type == 'agent' and pod.components is None:
            components = ambari_instance.host_components(cluster_instance.name, pod.name)
            pod.components = ','.join(components)
            pod.save()
        _pods.append(pod.pod_summary())

    return render_template('cluster/cluster.html', cluster=cluster_instance, pods=_pods)


@cluster.route('/<cluster_id>/delete', methods=['GET', 'POST'])
def delete_cluster(cluster_id):
    """
    删除一个集群
    """
    cluster_instance = Cluster.query.filter_by(id=cluster_id).first()

    form = ClusterDeleteForm()

    if form.validate_on_submit():
        pods = cluster_instance.pods.all()
        for pod in pods:
            if pod.type != 'server':
                celery_node_delete.apply_async(args=['default', pod.name])
            else:
                celery_node_delete.apply_async(args=['default', pod.name, '{0}-8080'.format(pod.name)])
            flash(u'成功！集群 {0} 删除节点 {1}。'.format(cluster_instance.name, pod.name), 'success')

        # 数据库自动删除 cluster 关联 pod 记录
        cluster_instance.delete()

        flash(u'成功！集群 {0} 被删除。'.format(cluster_instance.name), 'success')

        return redirect(url_for('cluster.index'))

    return render_template('cluster/cluster_delete.html', cluster=cluster_instance, form=form)


@cluster.route('/<cluster_id>/deploy', methods=['GET', 'POST'])
def deploy_cluster(cluster_id):
    """
    部署一个集群
    """
    cluster_instance = Cluster.query.filter_by(id=cluster_id).first()

    if cluster_instance.cluster_deployment != 0:
        flash(u'失败！集群 {0} 已经部署过了，不能重新部署，请查看。'.format(cluster_instance.name), 'danger')
        return redirect(cluster_instance.url)

    agent_count = cluster_instance.get_agent_count()
    if agent_count != cluster_instance.type:
        flash(
            u'失败！集群 {0} 中节点数量为 {1} 未达到申请节点数量 {2}，请查看。'.format(cluster_instance.name, agent_count,
                                                              cluster_instance.type), 'danger')
        return redirect(cluster_instance.url)

    ambari_server = cluster_instance.pods.filter_by(type='server').first()
    ambari_instance = AmbariServiceClass(ambari_server.sip)

    pods = cluster_instance.pods.filter_by(type='agent').all()
    for pod in pods:
        pod.configure = ambari_instance.host_info(pod.name).get('host_status')
        pod.save()

    form = ClusterDeployForm()

    if form.validate_on_submit():
        cluster_instance.cluster_deployment = 1
        cluster_instance.save()

        celery_cluster_deploy.apply_async(args=[cluster_instance.id])

        flash(u'成功！集群 {0} 已经提交部署。'.format(cluster_instance.name), 'success')

        return redirect(cluster_instance.url)

    return render_template('cluster/cluster_deploy.html', cluster=cluster_instance, pods=pods, form=form)


@cluster.route('/<int:cluster_id>/open')
def open_cluster(cluster_id):
    """
    Ambari Server 端口映射到外网访问，进行配置
    :param cluster_id:
    :return:
    """

    cluster_instance = Cluster.query.filter_by(id=cluster_id).first_or_404()
    if not cluster_instance.cluster_deployment:
        flash(u'警告！当前节点还没有部署 Hadoop 集群组件，不能进行工具集相关操作，请检查并选择部署操作！', 'warning')
        return redirect(cluster_instance.url)

    service = Service.query.filter_by(cluster_id=cluster_id).first_or_404()
    if (not service) or (service.nport is None):
        flash(u'警告！当前 Hadoop 集群没有注册服务成功，这样会影响集群的正常使用，请检查或联系管理员！', 'warning')
        return redirect(cluster_instance.url)

    if service and service.nport and (service.dport is None):
        proxy = HaproxyServiceClass()
        eid = proxy.acquire_port(cluster_id, service.nport)
        logging.getLogger('app').info('acquire port eid: {}'.format(eid))
        res = proxy.view_port(eid)
        service.eid = eid
        service.dport = res['dport']
        service.dip = current_app.config['PUBLIC_IP']
        service.save()

        flash(u'成功！当前 Hadoop 集群映射了外网端口 {}.', 'success')

    return redirect(url_for('cluster.index'))


@cluster.route('/<int:cluster_id>/close')
def close_cluster(cluster_id):
    """
    关闭 Ambari Server 端口映射到外网访问
    :param cluster_id:
    :return:
    """

    cluster_instance = Cluster.query.filter_by(id=cluster_id).first_or_404()
    if not cluster_instance.cluster_deployment:
        flash(u'警告！当前节点还没有部署 Hadoop 集群组件，不能进行工具集相关操作，请检查并选择部署操作！', 'warning')
        return redirect(cluster_instance.url)

    service = Service.query.filter_by(cluster_id=cluster_id).first_or_404()
    if (not service) or (service.nport is None):
        flash(u'警告！当前 Hadoop 集群没有注册服务成功，这样会影响集群的正常使用，请检查或联系管理员！', 'warning')
        return redirect(cluster_instance.url)

    if service and service.nport and service.dport and service.eid:
        proxy = HaproxyServiceClass()
        eid = proxy.release_port(service.eid)
        logging.getLogger('app').info('release port eid: {}'.format(eid))
        service.eid, service.dport, service.dip = None, None, None
        service.save()

        flash(u'成功！当前 Hadoop 集群关闭了外网映射端口 {}.！', 'success')

    return redirect(url_for('cluster.index'))