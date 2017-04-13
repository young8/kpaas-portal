# -*- coding: utf-8 -*-

"""
    kpaas-portal.default
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import os


class DefaultConfig(object):
    # Path
    _basedir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(
        os.path.dirname(__file__)))))
    # Base
    DEBUG = False
    TESTING = False
    # Log
    APP_LOG = 'kpaas-portal.log'
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key'
    # Protection against form post fraud
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = "reallyhardtoguess"
    # Caching
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 60

    # ------------- upgrade ------------- #
    # Default Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + _basedir + '/' + 'kpaas.sqlite'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    # Celery
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    CELERY_TASK_SERIALIZER = 'json'
    # Kubernetes
    K8S_SERVICE_ADDR = '127.0.0.1'
    K8S_SERVICE_PORT = 8080
    # Consul
    CONSUL_HOST_ADDR = '127.0.0.1'
    CONSUL_HOST_PORT = 8500
    # Docker Images
    AMBARI_SERVER = 'kpaas/c7-server:v1.0'
    AMBARI_AGENT = 'kpaas/c7-agent:v1.1'
    TOOL_MYSQL = 'kpaas/mysql:v1.0'
    TOOL_OOZIE = 'kpaas/tool-oozie:v1.7'
    # Yum Response
    HDP = 'http://127.0.0.1/HDP/centos7/2.x/updates/2.3.4.0'
    HDP_UTILS = 'http://127.0.0.1/HDP-UTILS-1.1.0.20/repos/centos7'
    # Ceph
    CEPH_SERVICE_HOSTNAME = 's3'
    CEPH_SERVICE_DOMAIN = 'node.dc1.consul'
    CEPH_SERVICE_IP = '127.0.0.1'
    CEPH_SERVICE_PORT = 80
    # Oozie Service
    OOZIE_SERVICE = 'http://127.0.0.1:8080/paas-task-service'
    # Haproxy Service
    HAPROXY_SERVICE = 'http://127.0.0.1:5000'
    # Public IP
    PUBLIC_IP = '127.0.0.1'
