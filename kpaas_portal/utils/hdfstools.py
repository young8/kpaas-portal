# -*- coding: utf-8 -*-
"""
    kpaas.hdfstools
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import os
from pyhdfs import HdfsClient


def copy_from_local(nn, src, dest, owner='hdfs'):
    is_upload = False

    file_size = os.path.getsize(src)
    client = HdfsClient(hosts=nn, user_name=owner)
    client.copy_from_local(src, dest, overwrite=True)
    hdfs_file_size = client.get_file_status(dest).length

    if file_size == hdfs_file_size:
        is_upload = True

    return is_upload
