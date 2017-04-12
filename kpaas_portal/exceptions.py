# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

from werkzeug.exceptions import HTTPException, Forbidden


class BaseError(HTTPException):
    description = "An internal error has occured"


class AuthorizationRequired(BaseError, Forbidden):
    description = "Authorization is required to access this area."


class AuthenticationError(BaseError):
    description = "Invalid username and password combination."