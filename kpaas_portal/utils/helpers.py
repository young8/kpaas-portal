# -*- coding: utf-8 -*-
"""
    kpaas.helpers
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from datetime import datetime
from flask import request, redirect


def redirect_or_next(endpoint, **kwargs):
    return redirect(
        request.args.get('next') or endpoint, **kwargs
    )


def format_datatime(dt):
    sdt = dt.encode('utf-8')

    return datetime.strptime(sdt, '%Y-%m-%dT%H:%M:%S.000Z')