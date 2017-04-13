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
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@10.37.14.17:3306/kpaas'
    SQLALCHEMY_ECHO = True
    # Celery
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
    # K8S
    K8S_SERVICE_ADDR = '127.0.0.1'
    # Consul
    CONSUL_HOST_ADDR = '127.0.0.1'
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
