# -*- coding: utf-8 -*-
"""
    kpaas.servertools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

import socket


def check_server_port(ip, port):
    result = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, port))
        s.close()
        print '%d is open' % port
        result = True
    except Exception as e:
        print '%d is down! (exception: %s)' % (port, e)

    return result
