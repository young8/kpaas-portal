# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

import Queue

from flask import (Blueprint, render_template, redirect, url_for, flash, request, logging, current_app)
from flask_login import login_required, current_user

from .forms import ClusterCreateForm, ClusterDeployForm, ClusterDeleteForm
from .models import Cluster, Pod, Service, StatefulSet

from kpaas_portal.extensions import cache
from kpaas_portal.utils.ambaritools import AmbariServiceClass
from kpaas_portal.utils.k8stools import celery_node_delete, celery_cluster_create, celery_cluster_deploy
from kpaas_portal.utils.haproxytools import HaproxyServiceClass

from kpaas_portal.api_1_1.models import KubeApiService, AmbariApiService

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
    k = KubeApiService(host=current_app.config['K8S_SERVICE_ADDR'], port=current_app.config['K8S_SERVICE_PORT'])
    for cluster in clusters:
        services = cluster.services.all()
        for service in services:
            res = k.view_service(service.namespace, service.name)
            if res and len(res['spec']['ports']) > 0:
                current_app.logger.debug('nodeport is: {}'.format(res['spec']['ports'][0]['nodePort']))
                cluster.status = 'ready'
                cluster.save()
            else:
                cluster.status = 'error'
                cluster.save()
        statefulsets = cluster.statefulsets.all()
        for ss in statefulsets:
            res = k.view_statefulset(ss.namespace, ss.name)
            if res and int(res['status'].get('replicas',0)) == int(cluster.type):
                current_app.logger.debug('statefulset replicas is: {}'.format(int(res['status'].get('replicas',0))))
                cluster.current_nodes = int(res['status'].get('replicas',0))
                cluster.status = 'ready'
                cluster.save()
            else:
                cluster.status = 'error'
                cluster.save()

        current_app.logger.debug('view cluster id: {0}, service is: {1}, statefulset is: {2}'.format(cluster.id, services, statefulsets))

    return render_template('cluster/index.html', clusters=clusters)


@cluster.route('/create', methods=['GET', 'POST'])
@login_required
def create_cluster():
    """
    创建集群
    """
    if not current_app.config['CEPH_CLOSED'] and not current_user.ceph_keys:
        flash(u'失败！当前用户没有配置 Ceph S3 Key，请配置账户信息。', 'danger')
        return redirect(current_user.url)
    form = ClusterCreateForm()
    if request.method == 'POST':
        # 初始化一个集群信息
        current_app.logger.debug('create cluster: description is {0}, type is {1}, machine is {2}'.format(form.cluster_description.data,
                                                                                                          form.cluster_type.data,
                                                                                                          form.cluster_machine.data))
        # write into db: cluster
        cluster_instance = Cluster(form.cluster_description.data, form.cluster_type.data, form.cluster_machine.data)
        cluster_instance.save(current_user)
        cluster_instance.name = 'cluster{0}'.format(cluster_instance.id)
        cluster_instance.status = 'pending'
        cluster_instance.save(current_user)
        # jobs queue
        q = Queue.Queue()
        # write into db: service
        server_service = Service(current_user.namespace, cluster_instance)
        server_service.status = 'pending'
        server_service.save()
        q.put({'id': int(server_service.id), 'type': 'service', 'data': server_service.get_server_json})
        # write into db: server statefulset
        server_statefulset = StatefulSet(current_user.namespace, cluster_instance, '{}-server'.format(cluster_instance.name), 'ambari-server', replicas=1)
        server_statefulset.status = 'pending'
        server_statefulset.save()
        q.put({'id': server_statefulset.id, 'type': 'statefulset', 'data': server_statefulset.parse('ambari-server')})
        # write into db: agent statefulset
        agent_statefulset = StatefulSet(current_user.namespace, cluster_instance, '{}-agent'.format(cluster_instance.name), 'ambari-agent', replicas=3)
        agent_statefulset.status = 'pending'
        agent_statefulset.save()
        q.put({'id': agent_statefulset.id, 'type': 'statefulset', 'data': agent_statefulset.parse('ambari-agent')})
        while not q.empty():
            job = q.get()
            current_app.logger.debug('job is: {}'.format(job))
            id = job.get('id', 0)
            type = job.get('type')
            data = job.get('data')
            current_app.logger.debug('post data: {}'.format(data))
            k = KubeApiService(host=current_app.config['K8S_SERVICE_ADDR'], port=current_app.config['K8S_SERVICE_PORT'])
            if type == 'service' and id and isinstance(data, dict):
                k.create_service(namespace=current_user.namespace, data=data)
                s = Service.query.get(id)
                s.status = 'created'
                s.save()
            if type == 'statefulset' and id and isinstance(data, dict):
                k.create_statefulset(namespace=current_user.namespace, data=data)
                ss = StatefulSet.query.get(id)
                ss.status = 'created'
                ss.save()
            cluster_instance.status = 'created'
            cluster_instance.save()
        return redirect(url_for('cluster.index'))
    return render_template('cluster/cluster_create.html', form=form)


@cluster.route('/<cluster_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_cluster(cluster_id):
    """
    删除集群
    """
    cluster_instance = Cluster.query.get(cluster_id)
    form = ClusterDeleteForm()
    if form.validate_on_submit():
        k = KubeApiService(host=current_app.config['K8S_SERVICE_ADDR'], port=current_app.config['K8S_SERVICE_PORT'])
        # delete all services
        services = cluster_instance.services.all()
        for service in services:
            k.delete_service(service.namespace, service.name)
            current_app.logger.debug('delete service is: {0}'.format(service.name))
        # delete all statefulsets
        statefulsets = cluster_instance.statefulsets.all()
        for ss in statefulsets:
            k.delete_statefulset(ss.namespace, ss.name)
            for i in range(0, int(ss.replicas)):
                k.delete_pod(ss.namespace, '{0}-{1}'.format(ss.name, i))
            current_app.logger.debug('delete statefulset is: {0}'.format(ss.name))
        # db delete all cluster records
        cluster_instance.delete()
        flash(u'成功！集群 {0} 被删除。'.format(cluster_instance.name), 'success')
        return redirect(url_for('cluster.index'))
    return render_template('cluster/cluster_delete.html', cluster=cluster_instance, form=form)


@cluster.route('/<cluster_id>/deploy', methods=['GET', 'POST'])
@login_required
def deploy_cluster(cluster_id):
    """
    部署集群
    """
    cluster_instance = Cluster.query.get(cluster_id)
    if cluster_instance.cluster_deployment != 0:
        flash(u'失败！集群 {} 已经部署过了，不能重新部署，请查看。'.format(cluster_instance.name), 'danger')
    if not cluster_instance.status == 'ready':
        flash(
            u'失败！集群 {} 节点资源还没有准备好，请查看。'.format(cluster_instance.name), 'danger')
    sss = []
    k = KubeApiService(host=current_app.config['K8S_SERVICE_ADDR'], port=current_app.config['K8S_SERVICE_PORT'])
    # get server info
    server_name = '{0}-server-0'.format(cluster_instance.name)
    server_fullname = '{0}.node.{1}.svc.cluster.local'.format(server_name, current_user.namespace)
    server_info = k.view_pod(current_user.namespace, server_name)
    sss.append({
        'name': server_fullname,
        'ip': server_info['status'].get('podIP', ''),
        'status': server_info['status'].get('phase', ''),
        'register': False
    })
    current_app.logger.debug(
        'cluster is: {0}, server pod is: {1}, data is: "{2}"'.format(cluster_instance.name, server_name, server_info))
    # get agents info
    ambari_instance = AmbariApiService('42.123.106.18', 10011)
    nodes = ambari_instance.register_nodes()
    ambari_nodes = []
    if nodes['items']:
        ambari_nodes = [n['Hosts']['host_name'] for n in nodes['items']]
    current_app.logger.debug('ambari register nodes is: "{}"'.format(ambari_nodes))
    for i in range(0, int(cluster_instance.current_nodes)):
        agent_name = '{0}-agent-{1}'.format(cluster_instance.name, i)
        agent_fullname = '{0}.node.{1}.svc.cluster.local'.format(agent_name, current_user.namespace)
        is_register = False
        if agent_fullname in ambari_nodes:
            is_register = True
        agent_info = k.view_pod(current_user.namespace, agent_name)
        sss.append({
            'name': agent_fullname,
            'ip': agent_info['status'].get('podIP', ''),
            'status': agent_info['status'].get('phase', ''),
            'register': is_register
        })
        current_app.logger.debug(
            'cluster is: {0}, agent pod is: {1}, data is: "{2}"'.format(cluster_instance.name, agent_name, agent_info))
    form = ClusterDeployForm()
    if form.validate_on_submit():
        cluster_instance.cluster_deployment = 1
        cluster_instance.status = 'deploying'
        cluster_instance.save()
        flash(u'成功！集群 {0} 已经提交部署。'.format(cluster_instance.name), 'success')
        return redirect(url_for('cluster.index'))
    return render_template('cluster/cluster_deploy.html', cluster=cluster_instance, sss=sss, form=form)


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