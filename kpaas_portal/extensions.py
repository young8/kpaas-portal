# -*- coding: utf-8 -*-

"""
    kpaas-portal.extensions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from celery import Celery
from flask_allows import Allows
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cache import Cache
from flask_cors import CORS
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from kpaas_portal.exceptions import AuthorizationRequired

# Permissions
allows = Allows(throws=AuthorizationRequired)

# Database
db = SQLAlchemy()

# Login
login_manager = LoginManager()

# Caching
cache = Cache()

# CORS
cors = CORS()

# Migrations
migrate = Migrate()

# CSRF
csrf = CSRFProtect()

# Rate Limiting
limiter = Limiter(auto_check=False, key_func=get_remote_address)

# Celery
celery = Celery('app')

# Moment
moment = Moment()
