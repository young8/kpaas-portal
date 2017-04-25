# -*- coding: utf-8 -*-
"""
    kpaas.usertools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from kpaas_portal.user.models import User


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

    return user