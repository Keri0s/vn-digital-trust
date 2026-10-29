"""Disposable assessment and Reviewer delegation integration checks."""
import io
import json
import os
from pathlib import Path
import secrets
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT / 'backend'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
if not all(os.environ.get(k)==v for k,v in {
    'VDT_AUTH_INTEGRATION_TEST':'true','VDT_LOCAL_FOUNDATION_ONLY':'true',
    'PGHOST':'testdb','PGDATABASE':'vdt_step06','PGUSER':'vdt_owner'}.items()):
    raise SystemExit('Disposable testdb only.')

import psycopg
import database
owner = psycopg.connect(**database.parameters(),autocommit=True)
if owner.execute("SELECT to_regclass('vdt.app_user')").fetchone()[0] and owner.execute('SELECT EXISTS(SELECT 1 FROM vdt.app_user)').fetchone()[0]:
    raise SystemExit('Test database contains accounts; recreate disposable testdb.')
database.migrate(database.parameters())
os.environ.setdefault('DJANGO_SETTINGS_MODULE','vdt.settings')
import django
django.setup()
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.db import connection
from django.test import Client
from vdt.core.local_bootstrap import provision_admin
call_command('seed_rbac_catalog',stdout=io.StringIO())
password = secrets.token_urlsafe(36)+'9A!'
admin_password = secrets.token_urlsafe(36)+'9A!'
bootstrap = provision_admin(username='assessment-admin',display_name='Assessment admin',password=admin_password)
org = bootstrap.organization_id
branch_a,branch_b = [str(row[0]) for row in owner.execute('SELECT id FROM vdt.branch ORDER BY code').fetchall()]
security_id,reviewer_id,risk_owner_id = uuid4(),uuid4(),uuid4()
role = owner.execute("SELECT id FROM vdt.role WHERE code='VDT_SECURITY'").fetchone()[0]
scope_id,assignment_id = uuid4(),uuid4()
for identity,name in ((security_id,'assessment-security'),(reviewer_id,'assessment-reviewer'),(risk_owner_id,'assessment-risk-owner')):
    owner.execute('''INSERT INTO vdt.app_user(id,organization_id,login_name,display_name,status,password_hash)
        VALUES(%s,%s,%s,%s,'ACTIVE',%s)''',(identity,org,name,name,make_password(password)))
with owner.transaction():
    owner.execute('''INSERT INTO vdt.scope(id,organization_id,scope_kind,description,content_hash)
        VALUES(%s,%s,'SELECTED','Assessment test security scope',%s)''',(scope_id,org,'a'*64))
    owner.execute('INSERT INTO vdt.scope_branch(id,scope_id,branch_id) VALUES(%s,%s,%s)',(uuid4(),scope_id,branch_a))
    owner.execute('''INSERT INTO vdt.role_assignment(id,user_id,role_id,scope_id,valid_from,granted_by)
        VALUES(%s,%s,%s,%s,clock_timestamp(),%s)''',(assignment_id,security_id,role,scope_id,bootstrap.user_id))
    risk_owner_role = owner.execute("SELECT id FROM vdt.role WHERE code='VDT_RISK_OWNER'").fetchone()[0]
    owner.execute('''INSERT INTO vdt.role_assignment(id,user_id,role_id,scope_id,valid_from,granted_by)
        VALUES(%s,%s,%s,%s,clock_timestamp(),%s)''',(uuid4(),risk_owner_id,risk_owner_role,scope_id,bootstrap.user_id))
connection.close()
connection.settings_dict['USER']='vdt_app'
connection.settings_dict['PASSWORD']=os.environ['VDT_DB_APP_PASSWORD']

def headers():
    return {'HTTP_HOST':'localhost:8443','HTTP_ORIGIN':'https://localhost:8443',
            'HTTP_X_VDT_PROXY_SECRET':settings.VDT_AUTH_PROXY_SECRET,'HTTP_X_VDT_CLIENT_IP':'198.51.100.45'}
def get(client,path):
    return client.get(path,secure=True,**headers())
def post(client,path,body,key=None):
    csrf=get(client,'/api/v1/auth/csrf').json()['csrf_token']
    return client.post(path,data=json.dumps(body),content_type='application/json',secure=True,
        HTTP_X_CSRFTOKEN=csrf,**({'HTTP_IDEMPOTENCY_KEY':str(key)} if key else {}),**headers())
def login(name,secret):
    client=Client(enforce_csrf_checks=True,raise_request_exception=False)
    response=post(client,'/api/v1/auth/session',{'username':name,'password':secret})
    assert response.status_code==200,(name,response.status_code)
    return client
def scope(branch):
    return {'organization_id':str(org),'branch_ids':[branch],'system_ids':[],
            'asset_ids':[],'data_asset_ids':[],'scenario_ids':[],'assessment_ids':[]}
def context(*extra):
    version=owner.execute('SELECT version FROM vdt.organization WHERE id=%s',(org,)).fetchone()[0]
    return {'dependencies':[{'resource_type':'organization','id':str(org),'version':version},*extra],
            'reason':'Synthetic isolated assessment check'}
def check(label,condition):
    if not condition:
        raise AssertionError(label)
    results.append(label)

results=[]
