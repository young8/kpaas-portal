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
    user.save()
    user.namespace = 'ns-{0}'.format(user.id)
    user.save()

    return user