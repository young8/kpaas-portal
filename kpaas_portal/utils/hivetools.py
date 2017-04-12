# -*- coding: utf-8 -*-

"""
    kpaas.hivetools
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import pyhs2 as hive

from kpaas_portal.extensions import celery


class MyHiveClient:
    def __init__(self, host='localhost', user='hive', password=None, database='default', port=10000, authMechanism="PLAIN"):
        self.conn = hive.connect(host=host,
                                 port=port,
                                 authMechanism=authMechanism,
                                 user=user,
                                 password=password,
                                 database=database)

    def query(self, sql):
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetch()

    def execute(self, sql):
        with self.conn.cursor() as cursor:
            cursor.execute(sql)

    def close(self):
        self.conn.close()


@celery.task(bind=True)
def create_hive_table(self, host, schema):
    client = MyHiveClient(host=host)
    client.execute(schema)
    client.close()


def view_hive_table(host, table_name, table_fields, rows=20):
    client = MyHiveClient(host=host)
    result = client.query('SELECT {0} FROM {1} LIMIT {2}'.format(table_fields, table_name, rows))
    client.close()

    return result
