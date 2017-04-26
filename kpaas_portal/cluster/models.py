# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

import json
from datetime import datetime
from flask import url_for, current_app
from jinja2 import Environment, PackageLoader

from kpaas_portal.extensions import db
from kpaas_portal.utils.database import CRUDMixin


class Cluster(db.Model, CRUDMixin):
    """
    Cluster
    """
    __tablename__ = 'cluster'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    type = db.Column(db.Integer, default=0)
    machine = db.Column(db.String(1), default='s')
    status = db.Column(db.String(100))
    cluster_deployment = db.Column(db.SmallInteger, default=0)
    agents_deployment = db.Column(db.SmallInteger, default=0)
    createtime = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship One-to-many
    services = db.relationship('Service', backref='cluster', lazy='dynamic', cascade='all, delete-orphan')
    statefulsets = db.relationship('StatefulSet', backref='cluster', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='cluster', lazy='dynamic', cascade='all, delete-orphan')
    hivetables = db.relationship('HiveTable', backref='cluster', lazy='dynamic', cascade='all, delete-orphan')
    # Foreign Key
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def url(self):
        return url_for('cluster.view_cluster', cluster_id=self.id)

    @property
    def agent_count(self):
        return self.pods.filter_by(cluster_id=self.id, type='agent').count()

    @property
    def task_count(self):
        return self.tasks.filter_by(cluster_id=self.id).count()

    @property
    def open_url(self):
        svr = self.services.filter_by(cluster_id=self.id).first()
        if svr and svr.dport:
            return 'http://{0}:{1}'.format(current_app.config['PUBLIC_IP'], svr.dport)
        return None

    @property
    def fromNow(self):
        return int((datetime.now() - self.createtime).total_seconds() / 60 / 60 / 24)

    @property
    def createtime_format(self):
        return self.createtime.strftime("%Y-%m-%d %H:%M:%S")

    # Methods
    def __init__(self, cluster_description='', cluster_type=3, cluster_machine='s'):
        self.description = cluster_description
        self.type = cluster_type
        self.machine = cluster_machine

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.id)

    def save(self, user=None):
        # update / edit the cluster
        if self.id:
            db.session.add(self)
            db.session.commit()
            return self

        # Adding a new cluster
        if user:
            self.owner = user.id
            self.createtime = datetime.utcnow()
            db.session.add(self)
            db.session.commit()

            user.cluster_count += 1
            db.session.add(user)
            db.session.commit()

    @classmethod
    def get_all(cls, user):
        if user.is_authenticated:
            clusters = cls.query.filter_by(cls.owner == user.id).all()
        return clusters

    def get_agent_count(self):
        return self.pods.filter_by(type='agent').count()

    def server_ip_port(self):
        svr = self.services.filter_by(cluster_id=self.id, type='server').first()
        res = {
            'server_ip': svr.dip,
            'server_port': svr.dport
        }
        return res

    def cluster_summary(self):
        _service = self.services.filter_by(type='server').first()
        summary = {
            'cluster_id': self.id,
            'cluster_name': self.name,
            'cluster_description': self.description,
            'cluster_type': self.type,
            'cluster_machine': self.machine,
            'cluster_deployment': self.cluster_deployment,
            'agent_count': self.get_agent_count(),
            'service_ip': _service.sip,
            'service_port': _service.sport
        }
        return summary


class Pod(db.Model, CRUDMixin):
    """
    Pod
    """
    __tablename__ = 'pod'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    namespace = db.Column(db.String(50))
    sip = db.Column(db.String(50))
    sport = db.Column(db.Integer)
    status = db.Column(db.String(50))
    configure = db.Column(db.Text)
    components = db.Column(db.Text)
    nhost = db.Column(db.String(255))
    nip = db.Column(db.String(50))
    type = db.Column(db.String(20))
    createtime = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id', ondelete='CASCADE'))

    def __init__(self, pod_type, cluster, namespace, pod_name=None):
        if pod_name:
            self.name = '{0}-{1}'.format(cluster.name, pod_name)
        else:
            self.name = '{0}-{1}'.format(cluster.name, pod_type)
        self.type = pod_type
        self.cluster = cluster
        self.namespace = namespace

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.id)

    @property
    def is_namenode2(self):
        result = False
        if self.type == 'agent' and self.components:
            if 'NAMENODE' in self.components.split(','):
                result = True
        return result

    @property
    def is_rm2(self):
        result = False
        if self.type == 'agent' and self.components:
            if 'RESOURCEMANAGER' in self.components.split(','):
                result = True
        return result

    @property
    def is_hive(self):
        result = False
        if self.type == 'agent' and self.components:
            if 'HIVE_SERVER' in self.components.split(','):
                result = True
        return result

    @property
    def is_oozie2(self):
        result = False
        if self.type == 'agent' and self.components:
            if 'OOZIE_SERVER' in self.components.split(','):
                result = True
        return result

    def get_ambari_server(self):
        server = Pod.query.filter_by(cluster_id=self.cluster_id, type='server').first()

        return server.name

    def pod_summary(self):
        tags = []
        if self.is_namenode2:
            tags.append('NN')
        if self.is_rm2:
            tags.append('RM')
        if self.is_oozie2:
            tags.append('OOZIE')
        if self.is_hive:
            tags.append('HIVE')

        components_count = 0
        if self.type == 'agent' and self.components != '':
            components_count = len(str(self.components).split(','))

        _pod = {
            'pod_id': self.id,
            'pod_name': self.name,
            'pod_type': self.type,
            'pod_ip': self.sip,
            'pod_node_hostname': self.nhost,
            'pod_node_ip': self.nip,
            'pod_components': components_count,
            'pod_status': self.status,
            'pod_tags': tags
        }

        return _pod

    # pod json
    def to_k8s_server_json(self):
        schema = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'labels': {
                    'name': self.name
                },
                'name': self.name
            },
            'spec': {
                'restartPolicy': 'Never',
                'containers': [
                    {
                        'resources': {
                            'limits': {
                                'cpu': '4',
                                'memory': '8Gi'
                            }
                        },
                        'image': current_app.config['AMBARI_SERVER'],
                        'name': self.name,
                        'ports': [
                            {
                                'containerPort': 8080
                            }
                        ],
                        'securityContext': {
                            'privileged': True
                        }
                    }
                ]
            }
        }
        return json.dumps(schema)

    def to_k8s_agent_json(self):
        schema = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'labels': {
                    'name': self.name
                },
                'name': self.name
            },
            'spec': {
                'restartPolicy': 'Never',
                'containers': [
                    {
                        'args': [
                            'systemd.setenv=AMBARI_SERVER_ADDR={0}'.format(self.get_ambari_server())
                        ],
                        'resources': {
                            'limits': {
                                'cpu': '4',
                                'memory': '8Gi'
                            }
                        },
                        'image': current_app.config['AMBARI_AGENT'],
                        'name': self.name,
                        'securityContext': {
                            'privileged': True
                        }
                    }
                ]
            }
        }

        return json.dumps(schema)

    def to_k8s_oozie_json(self):
        schema = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'labels': {
                    'name': self.name
                },
                'name': self.name
            },
            'spec': {
                'restartPolicy': 'Never',
                'containers': [
                    {
                        'image': current_app.config['TOOL_OOZIE'],
                        'name': self.name,
                        'ports': [
                            {
                                'containerPort': self.sport
                            }
                        ],
                        'securityContext': {
                            'privileged': True
                        }
                    }
                ]
            }
        }
        return json.dumps(schema)

    def to_k8s_hivedb_json(self):
        schema = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'labels': {
                    'name': self.name
                },
                'name': self.name
            },
            'spec': {
                'restartPolicy': 'Never',
                'containers': [
                    {
                        'resources': {
                            'limits': {
                                'cpu': '2',
                                'memory': '4Gi'
                            }
                        },
                        'env': [
                            {
                                'name': 'MYSQL_ROOT_PASSWORD',
                                'value': 'root'
                            },
                            {
                                'name': 'MYSQL_DATABASE',
                                'value': 'hive'
                            }
                        ],
                        'image': current_app.config['TOOL_MYSQL'],
                        'name': self.name,
                        'ports': [
                            {
                                'containerPort': 3306
                            }
                        ],
                        'securityContext': {
                            'privileged': True
                        }
                    }
                ]
            }
        }
        return json.dumps(schema)

    def to_k8s_ooziedb_json(self):
        schema = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'labels': {
                    'name': self.name
                },
                'name': self.name
            },
            'spec': {
                'restartPolicy': 'Never',
                'containers': [
                    {
                        'resources': {
                            'limits': {
                                'cpu': '2',
                                'memory': '4Gi'
                            }
                        },
                        'env': [
                            {
                                'name': 'MYSQL_ROOT_PASSWORD',
                                'value': 'root'
                            },
                            {
                                'name': 'MYSQL_DATABASE',
                                'value': 'oozie'
                            }
                        ],
                        'image': current_app.config['TOOL_MYSQL'],
                        'name': self.name,
                        'ports': [
                            {
                                'containerPort': 3306
                            }
                        ],
                        'securityContext': {
                            'privileged': True
                        }
                    }
                ]
            }
        }
        return json.dumps(schema)

    def get_pod_json(self):
        d = {
            'server': self.to_k8s_server_json(),
            'agent': self.to_k8s_agent_json(),
            'hivedb': self.to_k8s_hivedb_json(),
            'ooziedb': self.to_k8s_ooziedb_json(),
            'oozie': self.to_k8s_oozie_json()
        }

        return d.get(self.type)

    # consul json
    def to_consul_agent_json(self):
        schema = {
            'Node': self.name,
            'Address': self.sip
        }

        return json.dumps(schema)

    def to_consul_node_json(self):
        schema = {
            'Node': self.name,
            'Address': self.sip
        }

        return json.dumps(schema)

    def to_consul_server_json(self):
        schema = {
            'Node': self.name,
            'Address': self.sip,
            'Service': {
                'Service': self.cluster.name,
                'Tags': [self.cluster.name],
                'Port': self.sport
            }
        }

        return json.dumps(schema)

    def to_consul_tools_json(self):
        schema = {
            'Node': self.name,
            'Address': self.sip,
            'Service': {
                'Service': self.name,
                'Tags': [self.cluster.name],
                'Port': self.sport
            }
        }

        return json.dumps(schema)


class Service(db.Model, CRUDMixin):
    """
    Service
    """
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True)
    namespace = db.Column(db.String(50))
    sport = db.Column(db.Integer, default=0)
    nport = db.Column(db.Integer, default=0)
    dport = db.Column(db.Integer, default=0)
    createtime = db.Column(db.DateTime, default=datetime.utcnow)
    # Foreign Key
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id', ondelete='CASCADE'))

    def __init__(self, namespace, cluster):
        self.namespace = namespace
        self.name = '{0}-8080'.format(cluster.name)
        self.sport = 8080
        self.cluster_id = cluster.id
        self.cluster_name = cluster.name
        self.createtime = datetime.utcnow()

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.id)

    @property
    def get_server_json(self):
        env = Environment(loader=PackageLoader('kpaas_portal', 'templates/k8s'))
        template = env.get_template('server_service.tpl')
        content = template.render(namespace=self.namespace, owner=self.namespace, cluster=self.cluster_name, name=self.name)
        current_app.logger.debug('server service json: "{}"'.format(json.loads(content)))
        return json.loads(content)

    def save(self):
        db.session.add(self)
        db.session.commit()


class StatefulSet(db.Model, CRUDMixin):
    """
    StatefulSet
    """
    __tablename__ = 'k8s_statefulset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True)
    namespace = db.Column(db.String(50), default='default')
    replicas = db.Column(db.Integer, default=1)
    createtime = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))
    # Foreign Key
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id', ondelete='CASCADE'))

    def __init__(self, namespace, cluster, name, type, replicas=0):
        self.namespace = namespace
        self.name = name
        if type == 'ambari-agent':
            self.replicas = replicas
        else:
            self.replicas = 1
        self.cluster_id = cluster.id
        self.cluster_name = cluster.name

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.id)

    def parse(self, type):
        ambariserver = ''
        if type == 'ambari-server':
            tpl = 'server_statefulset.tpl'
        else:
            tpl = 'agent_statefulset.tpl'
            ambariserver = '{0}-server-0.node.{1}'.format(self.cluster_name, self.namespace)

        env = Environment(loader=PackageLoader('kpaas_portal', 'templates/k8s'))
        template = env.get_template(tpl)
        content = template.render(namespace=self.namespace, owner=self.namespace, cluster=self.cluster_name, name=self.name, replicas=self.replicas, ambariserver=ambariserver)
        current_app.logger.debug('{0} post data is: "{1}"'.format(type, json.loads(content)))
        return json.loads(content)

    def save(self):
        db.session.add(self)
        db.session.commit()
