# -*- coding: utf-8 -*-
"""
    kpaas.filetools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

import hashlib

ALLOWED_EXTENSIONS = set(['jar'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def file_md5sum(filename):
    fd = open(filename, "r")
    fcont = fd.read()
    fd.close()
    fmd5 = hashlib.md5(fcont)

    return fmd5.hexdigest()