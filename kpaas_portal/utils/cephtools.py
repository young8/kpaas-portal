# -*- coding: utf-8 -*-
"""
    kpaas.cephtools
    ~~~~~~~~~~~~~~~

    Author: Y.Z.Y

"""

import boto
import boto.s3.connection

from flask import current_app

from kpaas_portal.utils.helpers import format_datatime


class CephClass(object):
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        try:
            self.conn = boto.connect_s3(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                host=current_app.config['CEPH_SERVICE_IP'],
                is_secure=False,
                calling_format=boto.s3.connection.OrdinaryCallingFormat()
            )
        except Exception as e:
            print e

    def get_all_buckets(self):
        result = []
        try:
            buckets = self.conn.get_all_buckets()
        except Exception as e:
            print e
            return result
        for bucket in buckets:
            b = {
                'name': bucket.name,
                'created': format_datatime(bucket.creation_date)
            }
            result.append(b)

        return result

    def get_bucket_by_name(self, name):
        for bucket in self.conn.get_all_buckets():
            if bucket.name == name:
                return bucket

        return None

    def get_object(self, bucket, obj):
        key = bucket.get_key(obj)
        if key:
            url = key.generate_url(3600, query_auth=True, force_http=False)
            return url

        return None

    def get_bucket_content(self, bucket):
        result = []
        if not bucket:
            return result
        for key in bucket.list():
            c = {
                'name': key.name,
                'size': key.size,
                'modified': format_datatime(key.last_modified),
                'url': self.get_object(bucket, key.name)
            }
            result.append(c)

        return result
