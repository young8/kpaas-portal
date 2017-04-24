# -*- coding: utf-8 -*-

"""
    kpaas-portal.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import requests

from flask import current_app
from kpaas_portal.exceptions import KubeApiError


class KubeApiService():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.base_url = 'http://{0}:{1}'.format(self.host, self.port)
        current_app.logger.debug('kube api server url is: {}'.format(self.base_url))

    def create_service(self):
        pass

    def create_statefulset(self):
        pass

    def delete_service(self):
        pass

    def delete_statefulset(self):
        pass

    def view_service(self):
        pass

    def view_statefulset(self):
        pass

    def get_services(self, namespace):
        try:
            url = '{0}/api/v1/namespaces/{1}/services'.format(self.base_url, namespace)
            res = requests.get(url)
            if res.status_code == 200:
                current_app.logger.debug('services: {}'.format(res.text))
                return res.json()
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

    def get_statefulsets(self):
        pass

    def get_pods(self, namespace):
        try:
            url = '{0}/api/v1/namespaces/{1}/pods'.format(self.base_url, namespace)
            res = requests.get(url)
            if res.status_code == 200:
                current_app.logger.debug('pods: {}'.format(res.text))
                return res.json()
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

    def get_pod(self):
        pass


class AmbariApiService():
    def __init__(self):
        pass

    def register_nodes(self):
        pass

    def create_cluster(self):
        pass

    def get_nodes(self):
        pass

    def get_service(self):
        pass

    def get_component(self):
        pass


class CephApiService():
    def __init__(self):
        pass


class HdfsApiService():
    def __init__(self):
        pass


class HiveApiService():
    def __init__(self):
        pass


class OozieApiService():
    def __init__(self):
        pass
