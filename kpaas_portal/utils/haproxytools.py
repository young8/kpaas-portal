# -*- coding: utf-8 -*-

"""
    kpaas.haproxytools
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import json
import httplib
import requests
from flask import current_app, logging


class HaproxyServiceClass(object):
    def __init__(self, url=None):
        if url:
            self.url = url
        else:
            self.url = current_app.config['HAPROXY_SERVICE']
        self.headers = {'Content-Type': 'application/json'}

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    def view_port(self, eid):
        if not eid and isinstance(eid, int):
            return False

        url = '{}/port/{}'.format(self.url, eid)
        res = requests.get(url=url)
        if res.status_code == httplib.OK:
            return res.json()
        return False

    def acquire_port(self, cluster_id=None, nport=None):
        url = '{}/port/allocate'.format(self.url)
        logging.getLogger('app').info(url)
        data = {"cid": cluster_id, "port": nport}
        logging.getLogger('app').info(data)
        res = requests.post(url=url, data=json.dumps(data), headers=self.headers)
        logging.getLogger('app').info(res)
        logging.getLogger('app').info(res.status_code)

        if res.status_code == httplib.OK:
            logging.getLogger('app').info(res.json())
            return res.json()
        return False

    def release_port(self, eid):
        if not eid and isinstance(eid, int):
            return False

        url = '{}/port/{}/deallocate'.format(self.url, eid)
        res = requests.delete(url=url)
        if res.status_code == httplib.NO_CONTENT:
            return True
        return False

    def list_ports(self):
        result = {}
        url = '{}/ports'.format(self.url)
        logging.getLogger('app').info(url)
        res = requests.get(url=url, headers=self.headers)
        logging.getLogger('app').info(res)
        logging.getLogger('app').info(res.status_code)
        if res.status_code == 200:
            result = res.json()

        return result
