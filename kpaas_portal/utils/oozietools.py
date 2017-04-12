# -*- coding: utf-8 -*-
"""
    kpaas.oozietools
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import time
from datetime import datetime
import json
import requests

from kpaas_portal.extensions import celery
from kpaas_portal.tools.models import Task


def oozie_create_job(tools_oozie_service, data):
    result = requests.post(tools_oozie_service + "/oozie_service?action=" + json.dumps(data))
    print result.text

    return result.text


def oozie_get_job_state(tools_oozie_service, cluster_oozie, job_id):
    post_data = {
        "ooziePath": cluster_oozie,
        "jobid": job_id
    }
    result = requests.post(tools_oozie_service + "/get_job_status?action=" + json.dumps(post_data))
    print result.text

    return result.text


@celery.task(bind=True)
def celery_oozie_create_job(self, task_id, oozie_service, cluster_oozie, data):
    print '---> it is oozie create job!'
    job_id = oozie_create_job(oozie_service, data)
    task = Task.query.filter_by(id=task_id).first()
    task.status = oozie_get_job_state(oozie_service, cluster_oozie, job_id)
    task.save()

    while task.status != 'SUCCEEDED':
        self.update_state(state='PROGRESS')
        time.sleep(5)

        task.status = oozie_get_job_state(oozie_service, cluster_oozie, job_id)
        task.overtime = datetime.utcnow()
        task.save()

    return {'result': True}