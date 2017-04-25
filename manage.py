# -*- coding: utf-8 -*-

"""
    kpaas.manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

from flask import current_app
from flask_script import Manager, Shell, Server, prompt, prompt_pass
from flask_migrate import MigrateCommand, upgrade, migrate
from werkzeug.contrib.fixers import ProxyFix

from kpaas_portal.factory import create_app, db
from kpaas_portal.utils.usertools import create_admin_user

try:
    from kpaas_portal.configs.development import DevelopmentConfig as Config
except ImportError:
    from kpaas_portal.configs.default import DefaultConfig as Config

app = create_app(Config)
app.wsgi_app = ProxyFix(app.wsgi_app)
manager = Manager(app)


# Run local server
manager.add_command("runserver", Server("localhost", port=8000))

# Migration commands
manager.add_command('db', MigrateCommand)


# Add interactive project shell
def make_shell_context():
    return dict(app=current_app, db=db)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def initdb():
    """
    Creates the database.
    """
    migrate()
    upgrade()


@manager.command
def dropdb():
    """
    Deletes the database.
    """
    db.drop_all()


@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
def create_admin(username=None, password=None):
    """
    Creates the admin user.
    """
    if not (username and password):
        username = prompt("Username")
        password = prompt_pass("Password")
    create_admin_user(username=username, password=password)


if __name__ == '__main__':
    manager.run()
