# -*- coding: utf-8 -*-

"""
    kpaas-broker-service.setup
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from setuptools import setup

setup(
    name='kpaas-portal',
    version='1.0',
    packages=[
        'kpaas_portal',
        'kpaas_portal.tests',
        'kpaas_portal.api_1_0',
        'kpaas_portal.auth',
        'kpaas_portal.ceph',
        'kpaas_portal.cluster',
        'kpaas_portal.configs',
        'kpaas_portal.main',
        'kpaas_portal.manager',
        'kpaas_portal.myapp',
        'kpaas_portal.tools',
        'kpaas_portal.user',
        'kpaas_portal.utils'
    ],
    package_data={
        'kpaas_portal': ['resources/run.sh']
    },
    description='KPaaS Portal',
    install_requires=[
        'flask',
        'flask-allows',
        'flask-sqlalchemy',
        'flask-login',
        'flask-cache',
        'flask-cors',
        'flask-migrate',
        'flask_wtf',
        'flask-moment',
        'flask-limiter',
        'celery',
        'requests',
        'boto',
        'pyhdfs',
        'pyhs2',
        'MySQL-python'
    ]
)