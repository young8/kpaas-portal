# -*- coding: utf-8 -*-
"""
    kpaas
    ~~~~~~~~~~~~~~~
    
    Author: Y.Z.Y
    
"""

import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, logging
from werkzeug.utils import secure_filename

from flask_login import current_user
from kpaas_portal.extensions import db
from kpaas_portal.extensions import cache
from kpaas_portal.cluster.models import Cluster, Pod
from kpaas_portal.user.models import User
from kpaas_portal.tools.forms import TaskCreateForm, HiveTableCreateForm, HiveTableCreateFromS3Form
from kpaas_portal.tools.models import Task, HiveTable
from kpaas_portal.utils.filetools import allowed_file
from kpaas_portal.utils.hdfstools import copy_from_local
from kpaas_portal.utils.oozietools import celery_oozie_create_job
from kpaas_portal.utils.hivetools import create_hive_table, view_hive_table

import sys
reload(sys)
sys.setdefaultencoding('utf8')

tools = Blueprint('tools', __name__)


# --- mr 操作 --- #
# 显示有任务的集群列表
@tools.route('/mr/clusters')
def mr_list_clusters():
    tasks = db.session.query(Task.cluster_id.label('cluster_id'), db.func.count(Task.cluster_id).label('task_count')).filter_by(owner=current_user.id).order_by('cluster_id').group_by(Task.cluster_id).all()

    return render_template('tools/mr_clusters.html', tasks=tasks)


# 显示一个集群下任务列表
@tools.route('/mr/cluster/<int:cluster_id>')
def mr_view_cluster(cluster_id):
    cluster = Cluster.query.filter_by(id=cluster_id).first_or_404()
    if cluster.cluster_deployment != 1:
        return redirect(cluster.url)

    tasks = Task.query.filter_by(owner=current_user.id, cluster_id=cluster_id).order_by(Task.createtime.desc()).all()

    return render_template('tools/mr_tasks.html', tasks=tasks, cluster_id=cluster_id)


# 新建任务
@tools.route('/mr/cluster/<int:cluster_id>/task/new', methods=["POST", "GET"])
def mr_new_task(cluster_id):
    cluster_instance = Cluster.query.filter_by(id=cluster_id).first_or_404()
    if cluster_instance.cluster_deployment != 1:
        return redirect(cluster_instance.url)

    pods = cluster_instance.pods.filter_by(type='agent').all()
    for pod in pods:
        if pod.is_namenode2:
            nn_host = pod.name
        if pod.is_rm2:
            rm_host = pod.name
        if pod.is_oozie2:
            oozie_host = pod.name

    _cluster = {
        'cluster_id': cluster_instance.id,
        'cluster_name': cluster_instance.name,
        'hadoop_nn': nn_host,
        'hadoop_rm': rm_host,
        'hadoop_oozie': oozie_host
    }

    form = TaskCreateForm()

    if request.method == 'POST':
        _file = request.files['upload_file']

        if _file and allowed_file(_file.filename):
            filename = secure_filename(_file.filename)
            print filename

            # upload file to hdfs
            file_src = os.path.join('/tmp', filename)
            _file.save(file_src)
            file_dest = os.path.join('/tmp', filename)
            nn = '{}:50070'.format(nn_host)

            if copy_from_local(nn, file_src, file_dest):
                flash(u'成功！上传文件 {0}。'.format(file_src), 'success')
            else:
                flash(u'失败！请重新上传。', 'danger')
                return redirect(url_for('task_create'))

            # call: oozie-service
            hdfs_nn_uri = 'hdfs://{0}:8020'.format(nn_host)
            yarn_rm = '{0}:8050'.format(rm_host)
            oozie_uri = 'http://{0}:11000/oozie'.format(oozie_host)
            tool_oozie_service = 'http://{0}:{1}/paas-task-service'.format('oozie.kpaas', 8080)
            #
            task_instance = Task()
            task_instance.cluster_id = cluster_id
            task_instance.owner = current_user.id
            task_instance.save()
            #
            oozie_data = {
                'jobTracker': yarn_rm,
                'ooziePath': oozie_uri,
                'nameNode': hdfs_nn_uri,
                'wordFlowPath': '/paas/workflow.xml',
                'jarPath': hdfs_nn_uri + file_dest,
                'inputDir': request.form['task_job_input'],
                'outputDir': request.form['task_job_output'],
                'mapClass': request.form['task_job_mapClass'],
                'reduceClass': request.form['task_job_reduceClass'],
                'keyClass': request.form['task_job_keyClass'],
                'valueClass': request.form['task_job_valueClass'],
                'mrJobId': str(task_instance.id)
            }
            #
            task_instance.data = json.dumps(oozie_data)
            task_instance.status = 'CREATE'
            task_instance.save()
            #
            celery_oozie_create_job.apply_async(args=[task_instance.id, tool_oozie_service, oozie_uri, oozie_data])

            return redirect(url_for('tools.mr_view_cluster', cluster_id=cluster_id))

    return render_template('tools/mr_new_task.html', cluster_name=cluster_instance.name, cluster=_cluster, form=form)


# 查看任务
@tools.route('/mr/task/<int:task_id>')
def mr_view_task(task_id):
    task = Task.query.filter_by(id=task_id, owner=current_user.id).first()

    return render_template('tools/mr_task.html', task=task)


# 删除任务
@tools.route('/mr/task/<int:task_id>/delete', methods=["POST"])
def mr_delete_task(task_id=None):
    task = Task.query.filter_by(id=task_id).first_or_404()
    logging.getLogger('app').info('{}'.format(task_id))

    task.delete()
    logging.getLogger('app').info('{}'.format(task.cluster_id))

    return redirect(url_for('tools.mr_view_cluster', cluster_id=task.cluster_id))


# --- hive 操作 --- #
# 显示集群列表
@tools.route('/hive/clusters')
def hive_list_clusters():
    hive_tables = db.session.query(HiveTable.cluster_id.distinct().label('cluster_id')).filter_by(user_id=current_user.id).all()

    return render_template('tools/hive_clusters.html', hive_tables=hive_tables)


# 查看集群的default库
@tools.route('/hive/cluster/<int:cluster_id>/db/<db_name>')
def hive_view_cluster(cluster_id, db_name):
    cluster = Cluster.query.filter_by(id=cluster_id).first_or_404()
    if cluster.cluster_deployment != 1:
        return redirect(cluster.url)

    hive_tables = HiveTable.query.filter_by(user_id=current_user.id, cluster_id=cluster_id, db_name=db_name).order_by(HiveTable.table_name, HiveTable.id.desc()).all()

    return render_template('tools/hive_tables.html', hive_tables=hive_tables, cluster_id=cluster_id)


# 新建表
@tools.route('/hive/cluster/<int:cluster_id>/table/new', methods=["POST", "GET"])
def hive_new_table(cluster_id):
    cluster_instance = Cluster.query.filter_by(id=cluster_id).first_or_404()

    task_id = request.args.get('task_id')

    if not task_id:
        flash(u'失败！请选择已完成的 MR 任务，请查看。', 'danger')
        return redirect(url_for('tools.mr_view_cluster', cluster_id=cluster_id))

    if HiveTable.query.filter_by(task_id=task_id).first():
        flash(u'失败！MR 结果已经创建了 Hive 表，请查看。', 'danger')
        return redirect(url_for('tools.mr_view_task', task_id=task_id))

    form = HiveTableCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        task = Task.query.filter_by(id=task_id).first_or_404()
        db_name = 'default'
        table_fields = form.table_fields.data
        if form.table_field_separator.data not in [',', '|', ';', r'\t']:
            table_field_separator = ' '
        else:
            table_field_separator = form.table_field_separator.data
        if not form.table_name.data:
            table_name = 'mr_{}'.format(task_id)
        else:
            table_name = form.table_name.data
        table_location = task.data_to_json.get('outputDir')
        table_schema = r'CREATE EXTERNAL TABLE {0} ({1}) ROW FORMAT DELIMITED FIELDS TERMINATED BY "{2}" LOCATION "{3}"'.format(table_name, table_fields, table_field_separator, table_location)
        table = HiveTable(cluster_instance, current_user, task_id, db_name, table_name, table_schema, table_fields, table_location, table_field_separator)
        table.save()
        hosts = Pod.query.filter_by(cluster_id=cluster_id, type='agent').all()
        for host in hosts:
            if host.is_hive:
                hive_host = host.name
        create_hive_table.apply_async(args=[hive_host, table_schema])

        flash(u'成功！创建 Hive 表: {0}'.format(table_name), 'success')
        return redirect(url_for('tools.hive_view_cluster', cluster_id=cluster_id, db_name='default'))

    return render_template('tools/hive_new_table.html', form=form, cluster_id=cluster_id, task_id=task_id)


# 查看表
@tools.route('/hive/table/<int:table_id>')
@cache.cached(timeout=300)
def hive_view_table(table_id):
    _column_num = 10

    hivetable = HiveTable.query.filter_by(id=table_id).first()
    table_fields = map(lambda x: x.split()[0], hivetable.table_fields.split(','))

    cluster_id = hivetable.cluster_id
    hosts = Pod.query.filter_by(cluster_id=cluster_id, type='agent').all()
    for host in hosts:
        if host.is_hive:
            hive_host = host.name

    table_fields = table_fields[:_column_num]
    table_fields_num = range(len(table_fields))
    fields = ','.join(table_fields)
    table_body = view_hive_table(hive_host, hivetable.table_name, fields)
    table_body.insert(0, table_fields)

    return render_template('tools/hive_table.html', hivetable=hivetable, table_body=table_body, table_fields_num=table_fields_num)


# 删除表
@tools.route('/hive/table/<int:table_id>/delete', methods=["POST"])
def hive_delete_table(table_id):
    print table_id

    return render_template('tools/hive_clusters.html')


# s3 导入表
@tools.route('/hive/table/s3load', methods=["POST", "GET"])
def hive_s3load_table():
    input_file = request.args['input_file']
    bucket_id = request.args['bucket_id']

    form = HiveTableCreateFromS3Form()
    form.cluster_id.choices = [(a.id, a.description) for a in Cluster.query.filter_by(owner=current_user.id, cluster_deployment=1).order_by(Cluster.createtime.desc()).all()]

    if request.method == 'POST' and form.validate_on_submit():
        db_name = 'default'

        cluster_instance = Cluster.query.filter_by(id=int(form.cluster_id.data)).first_or_404()

        table_fields = form.table_fields.data
        if form.table_field_separator.data not in [',', '|', ';', r'\t', '^']:
            table_field_separator = ' '
        else:
            table_field_separator = form.table_field_separator.data

        table_name = form.table_name.data
        table_location = input_file
        table_schema = r'CREATE EXTERNAL TABLE {0} ({1}) ROW FORMAT DELIMITED FIELDS TERMINATED BY "{2}" LOCATION "{3}"'.format(table_name, table_fields, table_field_separator, table_location)
        table = HiveTable(cluster_instance, current_user, None, db_name, table_name, table_schema, table_fields, table_location, table_field_separator)
        table.save()
        hosts = Pod.query.filter_by(cluster_id=cluster_instance.id, type='agent').all()
        for host in hosts:
            if host.is_hive:
                hive_host = host.name
        create_hive_table.apply_async(args=[hive_host, table_schema])

        flash(u'成功！创建 Hive 表: {0}'.format(table_name), 'success')
        return redirect(url_for('tools.hive_view_cluster', cluster_id=cluster_instance.id, db_name='default'))

    return render_template('tools/hive_s3load_table.html', form=form, input_file=input_file, bucket_id=bucket_id)
