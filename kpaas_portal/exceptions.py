# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from werkzeug.exceptions import HTTPException, Forbidden


class KpaasError(HTTPException):
    description = "An internal error has occured"


class AuthorizationRequired(KpaasError, Forbidden):
    description = "Authorization is required to access this area."


class AuthenticationError(KpaasError):
    description = "Invalid username and password combination."