# -*- coding: utf-8 -*-

"""
    kpaas-portal.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import json
import requests
from flask import current_app

from kpaas_portal.exceptions import KubeApiError, AmbariApiError


class KubeApiService():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.base_url = 'http://{0}:{1}'.format(self.host, self.port)
        current_app.logger.debug('kube api server url is: {}'.format(self.base_url))

    def create_service(self, namespace, data):
        try:
            headers = {'content-type': 'application/json'}
            url = '{0}/api/v1/namespaces/{1}/services'.format(self.base_url, namespace)
            if not isinstance(data, dict):
                return {}
            res = requests.post(url, json=data, headers=headers)
            current_app.logger.debug('create service: {0} , status code: {1}'.format(res.text, res.status_code))
            if res.status_code == 201:
                return {}
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

    def create_statefulset(self, namespace, data):
        try:
            headers = {'content-type': 'application/json'}
            url = '{0}/apis/apps/v1beta1/namespaces/{1}/statefulsets'.format(self.base_url, namespace)
            if not isinstance(data, dict):
                return {}
            res = requests.post(url, json=data, headers=headers)
            current_app.logger.debug('create statefulset: {0} , status code: {1}'.format(res.text, res.status_code))
            if res.status_code == 201:
                return {}
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

    def delete_service(self):
        pass

    def delete_statefulset(self, namespace, name):
        try:
            url = '{0}/apis/apps/v1beta1/namespaces/{1}/statefulsets/{2}?orphanDependents=false'.format(self.base_url, namespace, name)
            res = requests.delete(url)
            if res.status_code == 200:
                current_app.logger.debug('delete statefulset result: {}'.format(res.text))
                return res.json()
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

    def view_service(self, namespace, name):
        try:
            url = '{0}/api/v1/namespaces/{1}/services/{2}'.format(self.base_url, namespace, name)
            res = requests.get(url)
            if res.status_code == 200:
                current_app.logger.debug('view service is: {}'.format(res.text))
                return res.json()
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

    def view_statefulset(self, namespace, name):
        try:
            url = '{0}/apis/apps/v1beta1/namespaces/{1}/statefulsets/{2}'.format(self.base_url, namespace, name)
            res = requests.get(url)
            if res.status_code == 200:
                current_app.logger.debug('statefulset is: {}'.format(res.text))
                return res.json()
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

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

    def delete_service(self, namespace, name):
        try:
            url = '{0}/api/v1/namespaces/{1}/services/{2}'.format(self.base_url, namespace, name)
            res = requests.delete(url)
            if res.status_code == 200:
                current_app.logger.debug('delete service result: {}'.format(res.text))
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

    def view_pod(self, namespace, name):
        try:
            url = '{0}/api/v1/namespaces/{1}/pods/{2}'.format(self.base_url, namespace, name)
            res = requests.get(url)
            if res.status_code == 200:
                current_app.logger.debug('view pod is: {}'.format(res.text))
                return res.json()
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

    def delete_pod(self, namespace, name):
        try:
            url = '{0}/api/v1/namespaces/{1}/pods/{2}'.format(self.base_url, namespace, name)
            res = requests.delete(url)
            if res.status_code == 200:
                current_app.logger.debug('delete pod result: {}'.format(res.text))
                return res.json()
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

    def create_pod(self, namespace, data):
        try:
            headers = {'content-type': 'application/json'}
            url = '{0}/api/v1/namespaces/{1}/pods'.format(self.base_url, namespace)
            res = requests.post(url, json=data, headers=headers)
            if res.status_code == 201:
                current_app.logger.debug('create pod: {0} , status code: {1}'.format(res.text, res.status_code))
                return {}
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}

    def create_namespace(self, namespace):
        try:
            headers = {'content-type': 'application/json'}
            url = '{0}/api/v1/namespaces'.format(self.base_url)
            data = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": namespace
                }
            }
            res = requests.post(url, json=data, headers=headers)
            current_app.logger.debug('create namespace: {0} , status code: {1}'.format(res.text, res.status_code))
            if res.status_code == 201:
                return {}
        except requests.ConnectionError as e:
            raise KubeApiError(description='kube api server connect error: {}'.format(e.message))
            return {}


class AmbariServerParse():
    def __init__(self, name):
        self.name = name

    def parse(self):
        schema = ''


class AmbariApiService():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.base_url = 'http://{0}:{1}'.format(self.host, self.port)
        self.headers = {'X-Requested-By': 'ambari'}
        self.auth = ('admin', 'admin')
        current_app.logger.debug('ambari api server url is: {}'.format(self.base_url))

    def register_nodes(self):
        try:
            url = '{}/api/v1/hosts'.format(self.base_url)
            res = requests.get(url, headers=self.headers, auth=self.auth)
            if res.status_code == 200:
                current_app.logger.debug('nodes: {}'.format(res.text))
                return res.json()
        except requests.ConnectionError as e:
            raise AmbariApiError(description='ambari api server connect error: {}'.format(e.message))
            return {}

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
