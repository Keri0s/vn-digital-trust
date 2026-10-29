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
security=login('assessment-security',password)
admin=login('assessment-admin',admin_password)
reviewer=login('assessment-reviewer',password)
risk_owner=login('assessment-risk-owner',password)
check('Security session exposes assessment navigation without admin permissions',
      set(get(security,'/api/v1/auth/session').json()['permissions'])=={'assessment.run','report.read'})
check('Security can open the assessment HTML page',get(security,'/assessments').status_code==200)
check('Risk Owner session exposes read navigation only',
      get(risk_owner,'/api/v1/auth/session').json()['permissions']==['report.read'])
check('Risk Owner can open assessment HTML page',get(risk_owner,'/assessments').status_code==200)
check('Admin session retains only administrative permissions',
      set(get(admin,'/api/v1/auth/session').json()['permissions'])=={'organization.manage','roles.assign','users.manage'})
check('Admin cannot open business assessment page',get(admin,'/assessments').status_code==302)
check('Unassigned Reviewer has no assessment navigation',get(reviewer,'/api/v1/auth/session').json()['permissions']==[])
check('Unassigned Reviewer cannot open assessment page',get(reviewer,'/assessments').status_code==302)
check('Admin cannot create assessment',post(admin,'/api/v1/assessments',{'code':'ADM','name':'Admin','scenario_ids':[],'scope':scope(branch_a),'write_context':context()},uuid4()).status_code==403)
setup=get(security,'/api/v1/assessments/setup')
check('Security sees only authorized branch in setup',setup.status_code==200 and [b['id'] for b in setup.json()['branches']]==[branch_a])
body={'code':'TEST-ASSESSMENT','name':'Synthetic assessment','scenario_ids':[],'scope':scope(branch_b),'write_context':context()}
check('Cannot create in other branch',post(security,'/api/v1/assessments',body,uuid4()).status_code==403)
body['scope']=scope(branch_a)
key=uuid4()
created=post(security,'/api/v1/assessments',body,key)
check('Security creates real scoped assessment',created.status_code==201 and created.json()['scope']==scope(branch_a))
item=created.json()
check('Same request key replays one assessment',post(security,'/api/v1/assessments',body,key).json()['id']==item['id'] and owner.execute('SELECT count(*) FROM vdt.assessment').fetchone()[0]==1)
other_item=dict(item,id=str(uuid4()),code='OUTSIDE-BRANCH',scope=scope(branch_b))
owner.execute('''INSERT INTO vdt.assessment(id,code,owner_id,workflow_state,api_payload)
    VALUES(%s,%s,%s,'OPEN',%s::jsonb)''',(other_item['id'],other_item['code'],security_id,json.dumps(other_item)))
branch_label=owner.execute('SELECT code,name FROM vdt.branch WHERE id=%s',(branch_a,)).fetchone()
security_labels=get(security,'/api/v1/assessments/display-context')
check('Security labels include only readable assessment',security_labels.status_code==200 and [x['id'] for x in security_labels.json()['items']]==[item['id']])
check('Branch labels come from stored name and code',security_labels.json()['items'][0]['branches']==[{'id':branch_a,'code':branch_label[0],'name':branch_label[1],'active':True}])
owner_labels=get(risk_owner,'/api/v1/assessments/display-context')
check('Read-only Risk Owner receives branch names without assessment.run',owner_labels.status_code==200 and owner_labels.json()['items'][0]['branches'][0]['name']==branch_label[1])
check('Outside assessment cannot disclose branch display context',get(security,'/api/v1/assessments/'+other_item['id']+'/display-context').status_code==404)
check('Admin cannot read business branch display context',get(admin,'/api/v1/assessments/display-context').status_code==403)
check('Anonymous cannot read branch display context',get(Client(),'/api/v1/assessments/display-context').status_code==401)
check('Unassigned Reviewer cannot read display context',get(reviewer,'/api/v1/assessments/'+item['id']+'/display-context').status_code==403)
check('Admin cannot read assessment detail',get(admin,'/api/v1/assessments/'+item['id']).status_code==403)
check('Unassigned reviewer cannot read',get(reviewer,'/api/v1/assessments/'+item['id']).status_code==403)
catalog=get(admin,'/api/v1/admin/assessments')
check('Admin sees assignment selector only',catalog.status_code==200 and catalog.json()['items'][0]['id']==item['id'] and 'updated_by' not in catalog.json()['items'][0])
user_version=owner.execute('SELECT version FROM vdt.app_user WHERE id=%s',(reviewer_id,)).fetchone()[0]
reviewer_role=owner.execute("SELECT id FROM vdt.role WHERE code='VDT_REVIEWER'").fetchone()[0]
from datetime import datetime,timedelta,timezone
now=datetime.now(timezone.utc)
grant={'user_id':str(reviewer_id),'role_id':str(reviewer_role),'scope':dict(scope(branch_a),assessment_ids=[item['id']]),
    'assigned_assessment_ids':[item['id']],'effective_at':(now-timedelta(minutes=1)).isoformat(),
    'access_expires_at':(now+timedelta(hours=2)).isoformat(),
    'write_context':context({'resource_type':'user','id':str(reviewer_id),'version':user_version},
                            {'resource_type':'assessment','id':item['id'],'version':1})}
granted=post(admin,'/api/v1/role-assignments',grant,uuid4())
check('Admin grants exact Reviewer assignment',granted.status_code==201)
check('Reviewer reads assigned assessment',get(reviewer,'/api/v1/assessments/'+item['id']).status_code==200)
check('Reviewer session gains navigation after assignment without relogin',
      get(reviewer,'/api/v1/auth/session').json()['permissions']==['assessment.review'])
check('Assigned Reviewer can open assessment HTML page',get(reviewer,'/assessments').status_code==200)
review_display=get(reviewer,'/api/v1/assessments/'+item['id']+'/display-context')
check('Assigned Reviewer gets real branch name',review_display.status_code==200 and review_display.json()['branches'][0]['name']==branch_label[1])
check('Detail reports only current Reviewer permission and expiry',review_display.json()['access_permissions']==['assessment.review'] and review_display.json()['review_access_expires_at']==grant['access_expires_at'])
check('Reviewer branch catalog contains only assigned assessment',
      [row['id'] for row in get(reviewer,'/api/v1/assessments/display-context').json()['items']]==[item['id']])
check('Reviewer cannot look up another assessment branch',get(reviewer,'/api/v1/assessments/'+other_item['id']+'/display-context').status_code==404)
check('Reviewer cannot create assessment',post(reviewer,'/api/v1/assessments',body,uuid4()).status_code==403)
owner.execute('UPDATE vdt.role_assignment SET revoked_at=clock_timestamp(),version=version+1 WHERE id=%s',(granted.json()['id'],))
check('Revocation removes Reviewer navigation from existing session',
      get(reviewer,'/api/v1/auth/session').json()['permissions']==[])
check('Revocation closes assessment HTML page',get(reviewer,'/assessments').status_code==302)
check('Revocation closes assessment API',get(reviewer,'/api/v1/assessments/'+item['id']).status_code==403)
check('Revocation closes detail display context',get(reviewer,'/api/v1/assessments/'+item['id']+'/display-context').status_code==403)
owner.execute('UPDATE vdt.role_assignment SET access_expires_at=clock_timestamp(),version=version+1 WHERE id=%s',(assignment_id,))
check('Expiry removes Security navigation from existing session',get(security,'/api/v1/auth/session').json()['permissions']==[])
check('Expiry closes assessment HTML page',get(security,'/assessments').status_code==302)
check('Expiry closes branch display context',get(security,'/api/v1/assessments/display-context').status_code==403)
report={'scope':'DISPOSABLE_POSTGRESQL_ASSESSMENT','passed':len(results),'checks':results}
Path('/reports/assessment-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
