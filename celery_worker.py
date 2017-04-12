# -*- coding: utf-8 -*-
"""
    kpaas.celery_worker
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from kpaas_portal.configs.development import DevelopmentConfig as Config
from kpaas_portal.factory import create_app
from kpaas_portal.extensions import celery

app = create_app(Config)
