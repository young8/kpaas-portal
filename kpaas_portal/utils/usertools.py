# -*- coding: utf-8 -*-
"""
    kpaas.usertools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask import current_app

from kpaas_portal.user.models import User
from kpaas_portal.api_1_1.models import KubeApiService


def create_admin_user(username, password):
    user = User()
    user.username = username
    user.password = password
    user.activated = True
    user.is_admin = True
    if isinstance(username, str):
        t = username.split(' ')
        user.namespace = ''.join(t)
    else:
        user.namespace = 'default'
    user.save()
    k = KubeApiService(host=current_app.config['K8S_SERVICE_ADDR'], port=current_app.config['K8S_SERVICE_PORT'])
    k.create_namespace(user.namespace)

    data = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": "node",
            "namespace": user.namespace
        },
        "spec": {
            "ports": [
                {
                    "port": 1
                }
            ],
            "clusterIP": "None",
            "selector": {
                "owner": user.namespace
            }
        }
    }
    k.create_service(user.namespace, data)

    return user