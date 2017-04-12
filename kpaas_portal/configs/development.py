# -*- coding: utf-8 -*-

"""
    kpaas.development.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from kpaas_portal.configs.default import DefaultConfig


class DevelopmentConfig(DefaultConfig):
    # Indicates that it is a dev environment
    DEBUG = True

    # ------------- upgrade ------------- #

    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@10.37.14.17:3306/kpaas'
    SQLALCHEMY_ECHO = True

    CELERY_BROKER_URL = 'redis://10.15.16.9:6379/1'
    CELERY_RESULT_BACKEND = 'redis://10.15.16.9:6379/0'

    K8S_SERVICE_ADDR = '10.37.14.21'

    CONSUL_HOST_ADDR = '10.37.14.21'

    HDP = 'http://10.37.14.18/HDP/centos7/2.x/updates/2.3.4.0'
    HDP_UTILS = 'http://10.37.14.18/HDP-UTILS-1.1.0.20/repos/centos7'

    CEPH_SERVICE_IP = '10.37.14.21'

    OOZIE_SERVICE = 'http://oozie.kpaas:8080/paas-task-service'

    HAPROXY_SERVICE = 'http://10.37.14.17:5000'

    PUBLIC_IP = '111.235.158.169'