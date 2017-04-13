# -*- coding: utf-8 -*-

"""
    kpaas-portal.factory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import logging
from flask import Flask, g, render_template
from flask_login import current_user

from kpaas_portal.extensions import db, moment, login_manager, cors, celery, migrate, cache, limiter, allows, csrf
from kpaas_portal.user.models import User, Guest


def create_app(config=None):
    """
    工厂函数
    """
    app = Flask(__name__)
    app.config.from_object(config)
    # 配置celery
    configure_celery_app(app, celery)
    # 蓝本
    configure_blueprints(app)
    # 扩展插件
    configure_extensions(app)
    # Add the before request handler
    app.before_request(create_before_request(app))
    # logging
    configure_logging(app)
    return app


def create_before_request(app):
    """
    配置上下文
    """
    def before_request():
        g.db = db
        g.config = app.config
        g.is_admin = current_user.is_admin

    return before_request


def configure_celery_app(app, celery):
    """
    配置 celery
    """
    from celery import platforms
    platforms.C_FORCE_ROOT = True

    app.config.update({
        'BROKER_URL': app.config['CELERY_BROKER_URL'],
        'RESULT_BACKEND': app.config['CELERY_RESULT_BACKEND']
    })
    celery.conf.update(app.config)
    task_base = celery.Task

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)

    celery.Task = ContextTask


def configure_blueprints(app):
    """
    配置蓝图
    """
    # 主页面
    from kpaas_portal.main.views import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='')
    # 注册 登录 退出
    from kpaas_portal.auth.views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_perfix='/auth')
    # Hadoop 集群
    from kpaas_portal.cluster.views import cluster as cluster_blueprint
    app.register_blueprint(cluster_blueprint, url_prefix='/cluster')
    # Ceph 存储
    from kpaas_portal.ceph.views import ceph as ceph_blueprint
    app.register_blueprint(ceph_blueprint, url_prefix='/ceph')
    # 工具集
    from kpaas_portal.tools.views import tools as tools_blueprint
    app.register_blueprint(tools_blueprint, url_prefix='/tools')
    # 应用
    from kpaas_portal.myapp.views import myapp as myapp_blueprint
    app.register_blueprint(myapp_blueprint, url_prefix='/myapp')
    # 用户
    from kpaas_portal.user.views import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')
    # 系统管理
    from kpaas_portal.manager.views import manager as manager_blueprint
    app.register_blueprint(manager_blueprint, url_prefix='/manager')
    # REST API
    from kpaas_portal.api_1_0.service import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')


def configure_extensions(app):
    """
    配置扩展
    """
    # Flask-WTF CSRF
    csrf.init_app(app)
    # Flask-Moment
    moment.init_app(app)
    # Flask-SQLAlchem
    db.init_app(app)
    # Flask-Migrate
    migrate.init_app(app, db)
    # Flask-Cache
    cache.init_app(app)
    # Flask-Limiter
    limiter.init_app(app)
    # Flask-cors
    cors.init_app(app)
    # Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.needs_refresh_message_category = 'info'
    login_manager.anonymous_user = Guest

    @login_manager.user_loader
    def load_user(user_id):
        """Loads the user. Required by the `login` extension."""

        user_instance = User.query.filter_by(id=user_id).first()
        if user_instance:
            return user_instance
        else:
            return None

    login_manager.init_app(app)

    # Flask-Allows
    allows.init_app(app)
    allows.identity_loader(lambda: current_user)


def configure_errorhandlers(app):
    """
    配置错误处理
    """
    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/forbidden_page.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/page_not_found.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/server_error.html"), 500


def configure_logging(app):
    """
    配置日志
    """
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    info_file_handler = logging.handlers.RotatingFileHandler(
        app.config['APP_LOG'],
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    info_file_handler.setLevel(logging.DEBUG)
    info_file_handler.setFormatter(formatter)
    app.logger.addHandler(info_file_handler)
