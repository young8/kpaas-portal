# -*- coding: utf-8 -*-
"""
    kpaas.consultools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

import requests
from flask import current_app

from kpaas_portal.exceptions import ConsulApiError


class ConsulServiceClass(object):
    def __init__(self, host, port):
        """
        consul 服务接口操作
        :param str host: 主机
        :param int port: 端口
        """
        self.host = host
        self.port = port
        self.base_url = 'http://{0}:{1}/v1'.format(self.host, self.port)
        self.headers = {'Content-Type': 'application/json'}
        current_app.logger.debug('consul api base url: {0}'.format(self.base_url))

    def nodes(self):
        """
        获取 node 列表
        """
        try:
            url = '{0}/catalog/nodes'.format(self.base_url)
            current_app.logger.debug('consul api url: {0}'.format(url))
            res = requests.get(url, headers=self.headers)
            if res.status_code != requests.codes.OK:
                raise ConsulApiError('consul api get nodes error. http code: {}'.format(res.status_code))
            return res.json()
        except (requests.Timeout, requests.ConnectionError, KeyError) as e:
            raise ConsulApiError('consul api server connect failed ({})'.format(e))

    def node_view(self, node_name):
        """

        :param str node_name:
        :return: dict
        """
        result = {}
        url = '{0}/catalog/node/{1}'.format(self.base_url, node_name)
        res = requests.get(url, headers=self.headers)
        if res.status_code == 200:
            result = res.json()

        return result

    def node_register(self, data=None):
        """

        :param dict data:
         {
            'Node': node,
            'Address': address
         }
        :return: bool
        """
        result = False
        url = '{0}/catalog/register'.format(self.base_url)
        res = requests.put(url, data=data, headers=self.headers)
        if res.status_code == 200:
            result = True

        return result

    def node_deregister(self, data=None):
        """

        :param dict data:
         {
            'Node': node
         }
        :return: bool
        """
        result = False
        url = '{0}/catalog/deregister'.format(self.base_url)
        res = requests.put(url, data=data, headers=self.headers)
        if res.status_code == 200:
            result = True

        return result
