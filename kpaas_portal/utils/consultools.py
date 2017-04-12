# -*- coding: utf-8 -*-
"""
    kpaas.consultools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

import requests
from flask import current_app


class ConsulServiceClass(object):
    def __init__(self, host=None, port=None):
        """

        :param str host:
        :param int port:
        :param str scheme:
        :return:
        """

        if host:
            self.host = host
        else:
            self.host = current_app.config['CONSUL_HOST_ADDR']

        if port:
            self.port = port
        else:
            self.port = current_app.config['CONSUL_HOST_PORT']

        self.base_url = 'http://{0}:{1}/v1'.format(self.host, self.port)
        self.headers = {'Content-Type': 'application/json'}

    def nodes(self):
        """

        :return: dict
        """
        url = '{0}/catalog/nodes'.format(self.base_url)
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
        return {}

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
