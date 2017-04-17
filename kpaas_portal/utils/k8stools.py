# -*- coding: utf-8 -*-
"""
    kpaas.k8stools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

import time
import requests
import json
from flask import current_app

from kpaas_portal.extensions import celery
from kpaas_portal.utils.consultools import ConsulServiceClass
from kpaas_portal.utils.ambaritools import AmbariServiceClass
from kpaas_portal.cluster.models import Pod, Service, Cluster
from kpaas_portal.user.models import User
from kpaas_portal.exceptions import KubeApiError

VERSION = 'v1'
HEADERS = {'Content-Type': 'application/json'}


class K8sServiceClass(object):
    def __init__(self, host, port, namespace):
        """
        K8S 操作
        :param str host: 主机
        :param int port: 端口
        :param str namespace: 名称空间
        """
        self.base_url = 'http://{0}:{1}/api/{2}/namespaces/{3}'.format(host, port, VERSION, namespace)
        current_app.logger.debug('kube api base url: {0}'.format(self.base_url))

    def pods(self):
        """
        查询 pod 列表
        :return: list
        """
        try:
            url = '{0}/pods'.format(self.base_url)
            current_app.logger.debug('k8s api url: {}'.format(url))
            res = requests.get(url)
            if res.status_code != requests.codes.OK:
                raise KubeApiError('kube api get pods error. http code: {}'.format(res.status_code))
            items = res.json()['items']
            result = []
            if items:
                result = [{'pod_name': item['metadata'].get('name', ''),
                           'pod_hostname': item['spec']['containers'][0].get('name', ''),
                           'pod_ip': item['status'].get('podIP', ''),
                           'pod_status': item['status'].get('phase', ''),
                           'pod_node': item['spec'].get('nodeName', ''),
                           'pod_node_ip': item['status'].get('hostIP', '')} for item in items]
            return result
        except (requests.Timeout, requests.ConnectionError, KeyError) as e:
            raise KubeApiError('kube api server connect failed ({})'.format(e))

    def pod_create(self, data):
        result = False
        url = '{0}/pods'.format(self.base_url)
        try:
            res = requests.post(url, data=data, headers=HEADERS)
        except Exception as e:
            current_app.logger.error('exception: {}'.format(e))
            return False
        if res.status_code == 201:
            result = True

        return result

    def pod_delete(self, pod_name):
        result = False
        url = '{0}/pods/{1}'.format(self.base_url, pod_name)
        try:
            res = requests.delete(url, headers=HEADERS)
        except Exception as e:
            current_app.logger.error('exception: {}'.format(e))
            return False
        if res.status_code == 200:
            result = True

        return result

    def pod_view(self, pod_name):
        result = {}
        url = '{0}/pods/{1}'.format(self.base_url, pod_name)
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
        except Exception as e:
            current_app.logger.error('exception: {}'.format(e))
            return {}
        if res.status_code == 200:
            result = res.json()

        return result

    def services(self):
        """
        查询 service 列表
        :return: list
        """

        try:
            url = '{0}/services'.format(self.base_url)
            current_app.logger.debug('url: {}'.format(url))
            res = requests.get(url)
            if res.status_code != requests.codes.OK:
                raise KubeApiError('kube api get service error. http code: {}'.format(res.status_code))
            items = res.json()['items']
            result = []
            if items:
                result = [{'service_name': item['metadata']['name'],
                           'service_ip': item['spec']['portalIP'],
                           'service_sport': item['spec']['ports'][0]['port'],
                           'service_dport': item['spec']['ports'][0].get('nodePort', '')} for item in items]
            return result
        except (requests.Timeout, requests.ConnectionError, KeyError) as e:
            raise KubeApiError('kube api server connect failed ({})'.format(e))

    def service_delete(self, service_name):
        result = False
        url = '{0}/services/{1}'.format(self.base_url, service_name)
        try:
            res = requests.delete(url, headers=HEADERS)
        except Exception as e:
            current_app.logger.error('exception: {}'.format(e))
            return False
        if res.status_code == 200:
            result = True

        return result

    def service_view(self, service_name):
        result = {}
        url = '{0}/services/{2}'.format(self.base_url, service_name)
        try:
            r = requests.get(url)
        except Exception as e:
            current_app.logger.error('exception: {}'.format(e))
            return {}
        if r.status_code == 200:
            result = r.json()

        return result

    def service_create(self, data):
        result = False
        url = '{0}/services'.format(self.base_url)
        try:
            res = requests.post(url, data=data, headers=HEADERS)
        except Exception as e:
            current_app.logger.error('exception: {}'.format(e))
            return False
        if res.status_code == 201:
            result = True

        return result


@celery.task(bind=True)
def celery_node_delete(self, k8s_namespace, pod_name, service_name=None):
    node = {
        "Node": pod_name
    }

    consul_instance = ConsulServiceClass(host=current_app.config['CONSUL_SERVICE_ADDR'], port=current_app.config['CONSUL_SERVICE_PORT'])
    consul_instance.node_deregister(json.dumps(node))
    current_app.logger.debug('celery api delete cluster node: consul delete node is {0}'.format(pod_name))

    k8s_instance = K8sServiceClass(host=current_app.config['K8S_SERVICE_ADDR'], port=current_app.config['K8S_SERVICE_PORT'], namespace=k8s_namespace)
    if service_name:
        k8s_instance.service_delete(service_name)
        current_app.logger.debug('celery api delete cluster node: kube delete service is: {0}'.format(service_name))

    current_app.logger.debug('celery api delete cluster node: kube delete node is {0}, begin.'.format(pod_name))
    k8s_instance.pod_delete(pod_name)
    while True:
        if not k8s_instance.pod_view(pod_name):
            break
        self.update_state(state='PROGRESS')
        time.sleep(10)
    current_app.logger.debug('celery api delete cluster node: kube delete node is {0}, end.'.format(pod_name))

    return {'result': True}


@celery.task(bind=True)
def celery_cluster_create(self, k8s_namespace, pod_id, service_id=None):
    # k8s 创建 pod
    k8s_instance = K8sServiceClass(host=current_app.config['K8S_SERVICE_ADDR'],
                                   port=current_app.config['K8S_SERVICE_PORT'], namespace=k8s_namespace)
    pod_instance = Pod.query.filter_by(id=pod_id).first()
    k8s_instance.pod_create(pod_instance.get_pod_json())

    while True:
        info = k8s_instance.pod_view(pod_instance.name)
        if info.get('status') and info['status'].get('phase') == 'Running':
            break
        self.update_state(state='PROGRESS')
        time.sleep(10)

    pod_instance.status = info['status'].get('phase')
    pod_instance.sip = info['status'].get('podIP')
    pod_instance.nhost = info['spec'].get('host')
    pod_instance.nip = info['status'].get('hostIP')
    pod_instance.save()
    print '---> [k8s] create pod_id: {0}, pod_name: {1}.'.format(pod_instance.id, pod_instance.name)

    # 注册 DNS
    consul_instance = ConsulServiceClass(current_app.config['CONSUL_SERVICE_ADDR'], current_app.config['CONSUL_SERVICE_PORT'])
    consul_instance.node_register(pod_instance.to_consul_node_json())
    print '---> [consul] node register pod: {0}, ip: {1}'.format(pod_instance.name, pod_instance.sip)

    # 把 Ambari 注册为 Service 发布出去
    if service_id and pod_instance.type == 'server':
        service_instance = Service.query.filter_by(id=service_id).first()
        service_instance.name = '{0}-8080'.format(pod_instance.name)
        service_instance.selector_pod = pod_instance.name
        service_instance.sport = 8080
        service_instance.save()
        k8s_instance.service_create(service_instance.to_server_json())

        service_info = k8s_instance.service_view(service_instance.name)
        service_instance.nport = int(service_info['spec']['ports'][0].get('nodePort'))
        service_instance.save()

        print '---> [k8s] create service id={0}, name={1}, nport={2}'.format(service_instance.id, service_instance.name,
                                                                             service_instance.nport)

    return {'result': True}


@celery.task(bind=True)
def celery_cluster_deploy(self, cluster_id):
    cluster_instance = Cluster.query.filter_by(id=cluster_id).first()
    print '---> celery task: {0} deploy ({1} agent)'.format(cluster_instance.name, cluster_instance.type)

    ambari_server = cluster_instance.pods.filter_by(type='server').first()
    ambari_service_ip = ambari_server.sip
    ambari_instance = AmbariServiceClass(ambari_service_ip)

    # ----- hdp source ----- #
    ambari_instance.set_hdp()
    print '---> (1) set hdp is OVER!'

    # ----- blueprint ----- #
    # hive mysql
    hive_db = Pod.query.filter_by(cluster_id=cluster_instance.id, type='hivedb').first()
    hive_host = hive_db.name
    # ceph info (s3_access_key, s3_secret_key, s3_endpoint)
    user = User.query.filter_by(id=cluster_instance.owner).first()
    ceph_key = user.ceph_keys
    ceph_key = ceph_key.split(' ')
    ceph_host = '{0}.{1}'.format(current_app.config['CEPH_SERVICE_HOSTNAME'], current_app.config['CEPH_SERVICE_DOMAIN'])
    ceph_info = (ceph_key[1], ceph_key[2], ceph_host)
    # set blueprint
    bp = AmbariServiceClass.set_ambari_blueprint(hive_host, ceph_info)
    # get blueprint by plan
    plan = 'node{0}'.format(cluster_instance.type)
    blueprint_data = bp.get(plan)
    # call ambari server api
    if ambari_instance.set_blueprint(json.dumps(blueprint_data)):
        print '---> (2) set blueprint is OVER!'

    # ----- hostmapping ----- #
    hosts = ambari_instance.get_hosts()
    hostmapping_data = AmbariServiceClass.set_ambari_hostmapping(plan)
    groups = hostmapping_data['host_groups']
    for group in groups:
        group['hosts'][0]['fqdn'] = hosts.pop()
    print '---> (3) set hostmapping is OVER!'

    # call ambari server api
    r = ambari_instance.cluster_deploy(cluster_instance.name, json.dumps(hostmapping_data))
    if r:
        print '---> (4) cluster deploy is Begin!'

    while True:
        print r.get('href')
        status = ambari_instance.cluster_deploy_status(r.get('href'))
        print status
        if status and status.get('status') == 'COMPLETED':
            break
        print status.get('status')
        print status.get('progress')
        self.update_state(state='PROGRESS')
        time.sleep(10)

    return {'result': True}
