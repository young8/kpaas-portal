# -*- coding: utf-8 -*-

"""
    kpaas.service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from flask import Blueprint, jsonify, current_app

from kpaas_portal.utils.k8stools import K8sServiceClass

api = Blueprint('api', __name__)


@api.route('/k8s/namespaces/<namespace>/pods')
def pods(namespace):
    k8s_instance = K8sServiceClass(namespace=namespace)
    pods = k8s_instance.pods()

    return jsonify({'result': pods})
