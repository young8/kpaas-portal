# -*- coding: utf-8 -*-

"""
    kpaas-portal.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import requests

from kpaas_portal.exceptions import KubeApiError


class KubeApiService():
    def __init__(self, host, port):
        self.baseurl = 'http://{}:{}'.format(host, port)

    def create_service(self):
        pass

    def create_pod(self):
        pass

    def delete_service(self):
        pass

    def delete_pod(self):
        pass

    def view_service(self):
        pass

    def view_pod(self):
        pass

    def get_services(self):
        pass

    def get_pods(self):
        pass
