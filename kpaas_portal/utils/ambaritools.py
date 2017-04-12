# -*- coding: utf-8 -*-
"""
    kpaas.ambaritools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

import json
import requests

from flask import current_app

requests.adapters.DEFAULT_RETRIES = 5


class AmbariServiceClass(object):
    def __init__(self, ip, port=8080, user='admin', passwd='admin'):
        self.base_url = 'http://{0}:{1}/api/v1'.format(ip, port)
        self.auth = (user, passwd)
        self.headers = {'X-Requested-By': 'ambari'}

    def check_service(self):
        url = '{0}/hosts'.format(self.base_url)
        result = False
        try:
            info = requests.get(url, auth=self.auth, headers=self.headers, timeout=10)
            if info.status_code == 200 and 'items' in info.json():
                result = True
        except requests.ConnectionError as e:
            print e
            result = False

        return result

    def set_hdp(self):
        # hdp 的内部地址
        hdp_schema = {
            'Repositories': {
                'base_url': current_app.config["HDP"],
                'verify_base_url': True
            }
        }
        hdp_url = '{0}/stacks/HDP/versions/2.3/operating_systems/redhat7/repositories/HDP-2.3'.format(self.base_url)
        r1 = requests.put(hdp_url, data=json.dumps(hdp_schema), auth=self.auth, headers=self.headers)
        # hdp-utils 的内部地址
        hdp_utils_schema = {
            'Repositories': {
                'base_url': current_app.config["HDP_UTILS"],
                'verify_base_url': True
            }
        }
        hdp_utils_url = '{0}/stacks/HDP/versions/2.3/operating_systems/redhat7/repositories/HDP-UTILS-1.1.0.20'.format(
            self.base_url)
        r2 = requests.put(hdp_utils_url, data=json.dumps(hdp_utils_schema), auth=self.auth, headers=self.headers)
        print r1, r2

        return r1, r2

    def set_blueprint(self, data):
        url = '{0}/blueprints/multi-node-hdfs'.format(self.base_url)
        print url
        res = requests.post(url=url, data=data, auth=self.auth, headers=self.headers)
        print res.content
        print res.status_code
        result = False
        if res.status_code == 201:
            result = True

        return result

    @staticmethod
    def set_ambari_blueprint(hive_host, ceph_info):
        hive_connection_url = "jdbc:mysql://{}:3306/hive?createDatabaseIfNotExist=true".format(hive_host)
        s3_access_key, s3_secret_key, s3_endpoint = ceph_info

        ambari_blueprint = \
            {
                "node3": {
                    "configurations": [
                        {
                            "hive-env": {
                                "properties_attributes": {

                                },
                                "properties": {
                                    "hive_user": "hive",
                                    "hive_ambari_database": "MySQL",
                                    "hive_database": "Existing MySQL Database",
                                    "hive_database_type": "mysql",
                                    "hive_database_name": "hive"
                                }
                            }
                        },
                        {
                            "hive-site": {
                                "properties_attributes": {

                                },
                                "properties": {
                                    "javax.jdo.option.ConnectionURL": hive_connection_url,
                                    "javax.jdo.option.ConnectionDriverName": "com.mysql.jdbc.Driver",
                                    "javax.jdo.option.ConnectionUserName": "root",
                                    "javax.jdo.option.ConnectionPassword": "root",
                                    "fs.s3a.access.key": s3_access_key,
                                    "fs.s3a.secret.key": s3_secret_key,
                                    "fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
                                    "fs.s3a.connection.ssl.enabled": "false",
                                    "fs.s3a.endpoint": s3_endpoint
                                }
                            }
                        },
                        {
                            "hdfs-site": {
                                "properties_attributes": {

                                },
                                "properties": {
                                    "fs.s3a.access.key": s3_access_key,
                                    "fs.s3a.secret.key": s3_secret_key,
                                    "fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
                                    "fs.s3a.connection.ssl.enabled": "false",
                                    "fs.s3a.endpoint": s3_endpoint
                                }
                            }
                        },
                        {
                            "oozie-site": {
                                "properties_attributes": {

                                },
                                "properties": {
                                    "fs.s3a.access.key": s3_access_key,
                                    "fs.s3a.secret.key": s3_secret_key,
                                    "fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
                                    "fs.s3a.connection.ssl.enabled": "false",
                                    "fs.s3a.endpoint": s3_endpoint
                                }
                            }
                        }
                    ],
                    "host_groups": [
                        {
                            "name": "host_group_1",
                            "configurations": [

                            ],
                            "components": [
                                {
                                    "name": "ZOOKEEPER_SERVER"
                                },
                                {
                                    "name": "ZOOKEEPER_CLIENT"
                                },
                                {
                                    "name": "PIG"
                                },
                                {
                                    "name": "OOZIE_CLIENT"
                                },
                                {
                                    "name": "NAMENODE"
                                },
                                {
                                    "name": "HCAT"
                                },
                                {
                                    "name": "METRICS_MONITOR"
                                },
                                {
                                    "name": "TEZ_CLIENT"
                                },
                                {
                                    "name": "HDFS_CLIENT"
                                },
                                {
                                    "name": "HIVE_CLIENT"
                                },
                                {
                                    "name": "NODEMANAGER"
                                },
                                {
                                    "name": "YARN_CLIENT"
                                },
                                {
                                    "name": "MAPREDUCE2_CLIENT"
                                },
                                {
                                    "name": "DATANODE"
                                }
                            ],
                            "cardinality": "1"
                        },
                        {
                            "name": "host_group_2",
                            "configurations": [

                            ],
                            "components": [
                                {
                                    "name": "ZOOKEEPER_SERVER"
                                },
                                {
                                    "name": "ZOOKEEPER_CLIENT"
                                },
                                {
                                    "name": "PIG"
                                },
                                {
                                    "name": "HISTORYSERVER"
                                },
                                {
                                    "name": "OOZIE_CLIENT"
                                },
                                {
                                    "name": "HIVE_SERVER"
                                },
                                {
                                    "name": "OOZIE_SERVER"
                                },
                                {
                                    "name": "HCAT"
                                },
                                {
                                    "name": "METRICS_MONITOR"
                                },
                                {
                                    "name": "SECONDARY_NAMENODE"
                                },
                                {
                                    "name": "TEZ_CLIENT"
                                },
                                {
                                    "name": "HIVE_METASTORE"
                                },
                                {
                                    "name": "APP_TIMELINE_SERVER"
                                },
                                {
                                    "name": "NODEMANAGER"
                                },
                                {
                                    "name": "HIVE_CLIENT"
                                },
                                {
                                    "name": "HDFS_CLIENT"
                                },
                                {
                                    "name": "YARN_CLIENT"
                                },
                                {
                                    "name": "MAPREDUCE2_CLIENT"
                                },
                                {
                                    "name": "DATANODE"
                                },
                                {
                                    "name": "RESOURCEMANAGER"
                                },
                                {
                                    "name": "WEBHCAT_SERVER"
                                }
                            ],
                            "cardinality": "1"
                        },
                        {
                            "name": "host_group_3",
                            "configurations": [

                            ],
                            "components": [
                                {
                                    "name": "ZOOKEEPER_SERVER"
                                },
                                {
                                    "name": "NODEMANAGER"
                                },
                                {
                                    "name": "METRICS_COLLECTOR"
                                },
                                {
                                    "name": "METRICS_MONITOR"
                                },
                                {
                                    "name": "DATANODE"
                                }
                            ],
                            "cardinality": "1"
                        }
                    ],
                    "Blueprints": {
                        "blueprint_name": "multi-node-hdfs",
                        "stack_name": "HDP",
                        "stack_version": "2.3"
                    }
                }
            }

        return ambari_blueprint

    @staticmethod
    def set_ambari_hostmapping(plan):
        plans = {
            'node3': {"blueprint": "multi-node-hdfs", "default_password": "admin",
                      "host_groups": [{"name": "host_group_1", "hosts": [{"fqdn": "localhost"}]},
                                      {"name": "host_group_2", "hosts": [{"fqdn": "localhost"}]},
                                      {"name": "host_group_3", "hosts": [{"fqdn": "localhost"}]}]}
        }
        return plans.get(plan)

    def get_hosts(self):
        result = []
        url = '{0}/hosts'.format(self.base_url)
        res = requests.get(url, auth=self.auth, headers=self.headers)
        if res.status_code == 200:
            hosts = res.json()
            result = [host['Hosts']['host_name'] for host in hosts['items']]

        return result

    def cluster_deploy(self, cluster_name, data):
        url = '{0}/clusters/{1}'.format(self.base_url, cluster_name)
        res = requests.post(url=url, data=data, auth=self.auth, headers=self.headers)
        result = None
        if res.status_code == 202:
            result = res.json()

        return result

    def cluster_deploy_status(self, url):
        result = {}
        print url
        res = requests.get(url=url, auth=self.auth, headers=self.headers)
        if res.status_code == 200:
            j = res.json()
            print j
            result = {
                'status': j['Requests'].get('request_status'),
                'progress': j['Requests'].get('progress_percent')
            }

        return result

    def host_components(self, cluster_name, host_name):
        result = []
        url = '{0}/clusters/{1}/hosts/{2}/host_components'.format(self.base_url, cluster_name, host_name)
        res = requests.get(url, auth=self.auth, headers=self.headers)
        if res.status_code == 200 and res.text:
            hosts = res.json()
            result = [item['HostRoles']['component_name'] for item in hosts.get('items')]

        return result

    def host_info(self, hostname):
        result = {}
        url = '{0}/hosts/{1}'.format(self.base_url, hostname)
        try:
            info = requests.get(url, auth=self.auth, headers=self.headers, timeout=10)
            if info.status_code == 200:
                res = info.json().get('Hosts')
                if res:
                    result = {
                        'host': hostname,
                        'ip': res.get('ip'),
                        'cpu_count': res.get('cpu_count'),
                        'total_mem': res.get('total_mem'),
                        'host_status': res.get('host_state')
                    }
        except Exception as ex:
            print ex

        return result

    def host_delete(self, hostname):
        url = '{0}/hosts/{1}'.format(self.base_url, hostname)
        print url
        res = requests.delete(url, auth=self.auth, headers=self.headers)
        print res.status_code

        return res
