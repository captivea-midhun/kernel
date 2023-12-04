
import xmlrpc.client
import getpass
import csv

url = 'http://erp-prd1.kernel.corp'
db = 'kernel_production'

email = input('Email: ')
password = getpass.getpass()

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, email, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

subjects = models.execute_kw(db, uid, password, 'naas.subject', 'search_read', [[]], { 'fields': ['internal_subject_id'] })
subject_id_map = { s['id']: s['internal_subject_id'] for s in subjects }

tasks = models.execute_kw(db, uid, password, 'naas.experiment.task', 'search_read', [[['subject_id', '!=', False], ['task_type', '=', 'data']]], { 'fields': ['name', 'subject_id', 'data_session_id'] })


with open('data.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['subject_id', 'name', 'data_session_id'])
    for t in tasks:
        internal_subject_id = subject_id_map[t['subject_id'][0]]
        writer.writerow([
            internal_subject_id,
            t['name'],
            t['data_session_id']
        ])