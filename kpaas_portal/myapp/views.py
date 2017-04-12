# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from flask import Blueprint, render_template

myapp = Blueprint('myapp', __name__)


@myapp.route('/')
def index():
    return render_template('myapp/index.html')