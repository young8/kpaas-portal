# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    """
    首页
    """
    return render_template('index.html')
