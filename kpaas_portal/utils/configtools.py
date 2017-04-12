# -*- coding: utf-8 -*-
"""
    kpaas.configtools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from flask import current_app
import ConfigParser


def get_ini():
    ini_file = current_app.config["INI_FILE"]
    cf = ConfigParser.ConfigParser()
    cf.read(ini_file)
    s = cf.sections()

    return [(ss, cf.items(ss)) for ss in s]
