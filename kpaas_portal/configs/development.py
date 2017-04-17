# -*- coding: utf-8 -*-

"""
    kpaas-portal.development
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from kpaas_portal.configs.default import DefaultConfig


class DevelopmentConfig(DefaultConfig):
    DEBUG = True

    # ------------- upgrade ------------- #
    # DB
    SQLALCHEMY_DATABASE_URI = 'mysql://kpaas:123456@36.111.132.117:10016/kpaas'
    SQLALCHEMY_ECHO = True
    # Celery
    CELERY_BROKER_URL = 'redis://36.111.132.117:10015/1'
    CELERY_RESULT_BACKEND = 'redis://36.111.132.117:10015/0'
    # K8S
    K8S_SERVICE_ADDR = '111.235.158.169'
    K8S_SERVICE_PORT = 10002 + 21
    K8S_APISERVER = 'http://{0}:{1}'.format(K8S_SERVICE_ADDR, K8S_SERVICE_PORT)
    # Consul
    CONSUL_HOST_ADDR = '192.168.1.240'
    # http://{host}/DHP...
    HDP = 'http://127.0.0.1/HDP/centos7/2.x/updates/2.3.4.0'
    HDP_UTILS = 'http://127.0.0.1/HDP-UTILS-1.1.0.20/repos/centos7'
    # Ceph
    CEPH_SERVICE_IP = '127.0.0.1'
    # Oozie
    OOZIE_SERVICE = 'http://127.0.0.1:8080/paas-task-service'
    # Haproxy
    HAPROXY_SERVICE = 'http://127.0.0.1:5000'
    # Public
    PUBLIC_IP = '127.0.0.1'
