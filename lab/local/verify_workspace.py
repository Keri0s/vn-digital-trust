"""Actual PostgreSQL/runtime-role checks for the complete preparation workflow."""
from workspace_fixture import *
from copy import deepcopy
from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch as mock_patch
from django.db import DatabaseError
from vdt.access import service as access_service
from vdt.workspace.validation import validator

security=login('assessment-security',password)
admin=login('assessment-admin',admin_password)
reviewer=login('assessment-reviewer',password)

def owner_migration(target):
    saved={key:connection.settings_dict[key] for key in ('USER','PASSWORD')}
    connection.close()
    connection.settings_dict.update(USER=os.environ['PGUSER'],PASSWORD=os.environ['PGPASSWORD'])
    try:
        call_command('migrate','core',target,stdout=io.StringIO())
    finally:
        connection.close();connection.settings_dict.update(saved)

def send(client,path,body,*,version=None,key=None,method='POST'):
    csrf=get(client,'/api/v1/auth/csrf').json()['csrf_token']
    return client.generic(method,path,data=json.dumps(body),content_type='application/json',secure=True,
        HTTP_X_CSRFTOKEN=csrf,HTTP_IDEMPOTENCY_KEY=str(key or uuid4()),
        **({'HTTP_IF_MATCH':f'"{version}"'} if version is not None else {}),**headers())

def expect(label,response,status,schema=None):
    if response.status_code!=status:
        raise AssertionError((label,response.status_code,response.content.decode()[:700]))
    check(label,True)
    data=response.json()
    if schema: check(label+' matches schema',validator(schema).is_valid(data))
    return data

setup=expect('Security setup',get(security,'/api/v1/workspace/setup'),200)
owner_migration('0003')
check('Empty workspace migration safely rolls back',owner.execute("SELECT NOT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema='vdt' AND table_name='assessment_scenario' AND column_name='scenario_snapshot_id')").fetchone()[0])
owner_migration('0004')
branch=setup['branches'][0]
def deps(*objects,owner_id=security_id,with_branch=True):
    rows=[]
    if with_branch: rows.append({'resource_type':'branch','id':branch_a,'version':branch['version']})
    if owner_id:
        version=owner.execute('SELECT version FROM vdt.app_user WHERE id=%s',(owner_id,)).fetchone()[0]
        rows.append({'resource_type':'user','id':str(owner_id),'version':version})
    for kind,data in objects: rows.append({'resource_type':kind,'id':data['id'],'version':data['version']})
    return context(*rows)

source={'kind':'DOCUMENT','reference':'Synthetic lab inventory','reason':'Isolated test input',
        'evidence_revision_id':None,'verification_decision_id':None}
def known(value): return {'state':'KNOWN','value':value,'reason':'Synthetic test declaration','sources':[source]}
def unknown(): return {'state':'UNKNOWN','value':None,'reason':'Not measured in this synthetic test','sources':[]}
body={'code':'CRM-TEST','name':'CRM thử nghiệm','owner_id':str(security_id),'scope':scope(branch_a),
      'state':'ACTIVE','sources':[source],**{k:known('Test '+k) for k in ('purpose','hosting','exposure','criticality')},
      'asset_ids':[],'vendor_ids':[],'write_context':deps()}
expect('Anonymous cannot list inventory',get(Client(),'/api/v1/systems'),401)
expect('Admin has no inventory write right',send(admin,'/api/v1/systems',body),403)
bad=deepcopy(body);bad['scope']=scope(branch_b)
expect('Security cannot write another branch',send(security,'/api/v1/systems',bad),403)
bad=deepcopy(body);bad['purpose']['sources']=[]
expect('Known statement requires source',send(security,'/api/v1/systems',bad),422)
bad=deepcopy(body);bad['purpose']=unknown();bad['purpose']['value']='Invented'
expect('Unknown cannot carry invented value',send(security,'/api/v1/systems',bad),422)
bad=deepcopy(body);bad['write_context']['dependencies']=[]
expect('Missing inventory dependencies fail closed',send(security,'/api/v1/systems',bad),428)
key=uuid4(); system=expect('Create system',send(security,'/api/v1/systems',body,key=key),201,'InformationSystem')
check('Create replay returns same system',send(security,'/api/v1/systems',body,key=key).json()['id']==system['id'])
asset_body={'code':'SERVER-TEST','name':'Máy chủ CRM','owner_id':str(security_id),'scope':scope(branch_a),
    'state':'ACTIVE','sources':[source],'asset_type':'SERVER','system_ids':[system['id']],
    'business_value':unknown(),'write_context':deps(('system',system))}
asset=expect('Create related asset',send(security,'/api/v1/assets',asset_body),201,'Asset')
system=expect('Read system after related asset',get(security,'/api/v1/systems/'+system['id']),200)
check('Typed links update both directions and system version',system['asset_ids']==[asset['id']] and system['version']==2)
data_body={'code':'CUSTOMERS-TEST','name':'Khách hàng giả lập','owner_id':str(security_id),'scope':scope(branch_a),
    'state':'ACTIVE','sources':[source],'system_ids':[system['id']],'sensitivity':known('Synthetic only'),
    'record_scope':known('Ten fictitious customer records'),'write_context':deps(('system',system))}
data_asset=expect('Create data asset',send(security,'/api/v1/data-assets',data_body),201,'DataAsset')
system=get(security,'/api/v1/systems/'+system['id']).json()
patch={'name':'CRM cập nhật','write_context':deps(('asset',asset))}
expect('Update requires If-Match',send(security,'/api/v1/systems/'+system['id'],patch,method='PATCH'),428)
expect('Stale system update fails',send(security,'/api/v1/systems/'+system['id'],patch,method='PATCH',version=1),412)
updatekey=uuid4(); system=expect('Update system',send(security,'/api/v1/systems/'+system['id'],patch,method='PATCH',version=system['version'],key=updatekey),200)
check('Update replay accepts old If-Match',send(security,'/api/v1/systems/'+system['id'],patch,method='PATCH',version=system['version']-1,key=updatekey).json()==system)
ctx_scope=dict(scope(branch_a),system_ids=[system['id']],asset_ids=[asset['id']],data_asset_ids=[data_asset['id']])
ctx_body={'scope':ctx_scope,'system_ids':[system['id']],'asset_ids':[asset['id']],'data_asset_ids':[data_asset['id']],
          'vendor_ids':[],'data_flow_ids':[],'preconditions':[known('Local isolated network')],
          'environment':known('LOCAL_LAB'),'adversary_capability':unknown(),'sources':[source],
          'write_context':deps(('system',system),('asset',asset),('data_asset',data_asset),owner_id=None)}
ctx=expect('Freeze context',send(security,'/api/v1/context-snapshots',ctx_body),201,'ContextSnapshot')
expect('Read immutable context',get(security,'/api/v1/context-snapshots/'+ctx['id']),200,'ContextSnapshot')
scenario_body={'code':'SC-CRM','name':'Tài khoản CRM bị chiếm quyền','event':'Người ngoài đăng nhập bằng tài khoản nhân viên',
               'consequences':'Đọc hoặc sửa dữ liệu khách hàng','owner_id':str(security_id),'context_snapshot_id':ctx['id'],
               'scope':ctx_scope,'attack_metadata':[],'sources':[source],
               'write_context':deps(('system',system),('asset',asset),('data_asset',data_asset))}
scenario=expect('Create draft scenario',send(security,'/api/v1/scenarios',scenario_body),201,'Scenario')
assessment_body={'code':'WORKSPACE-ASSESSMENT','name':'Đợt đánh giá kiểm thử','scenario_ids':[],'scope':scope(branch_a),'write_context':context()}
assessment_item=expect('Create assessment for workflow',send(security,'/api/v1/assessments',assessment_body),201)
link={'scenario_id':scenario['id'],'write_context':context({'resource_type':'scenario','id':scenario['id'],'version':scenario['version']})}
expect('Draft cannot be attached',send(security,f'/api/v1/assessments/{assessment_item["id"]}/scenario-links',link,version=1),409)
transition={'state':'ACTIVE','write_context':scenario_body['write_context']}
scenario=expect('Activate valid scenario',send(security,f'/api/v1/scenarios/{scenario["id"]}/transitions',transition,version=1),200,'Scenario')
link['write_context']['dependencies'][-1]['version']=scenario['version'];linkkey=uuid4()
assessment_item=expect('Attach active scenario',send(security,f'/api/v1/assessments/{assessment_item["id"]}/scenario-links',link,version=1,key=linkkey),200)
check('Membership replay is exactly once',send(security,f'/api/v1/assessments/{assessment_item["id"]}/scenario-links',link,version=1,key=linkkey).json()==assessment_item)
expect('Duplicate membership fails without replacing snapshot',send(security,f'/api/v1/assessments/{assessment_item["id"]}/scenario-links',link,version=2),409)
now=datetime.now(timezone.utc)
reviewer_role=owner.execute("SELECT id FROM vdt.role WHERE code='VDT_REVIEWER'").fetchone()[0]
grant={'user_id':str(reviewer_id),'role_id':str(reviewer_role),'scope':dict(scope(branch_a),assessment_ids=[assessment_item['id']]),
       'assigned_assessment_ids':[assessment_item['id']],'effective_at':(now-timedelta(minutes=1)).isoformat(),
       'access_expires_at':(now+timedelta(hours=3)).isoformat(),
       'write_context':context({'resource_type':'user','id':str(reviewer_id),'version':owner.execute('SELECT version FROM vdt.app_user WHERE id=%s',(reviewer_id,)).fetchone()[0]},
                               {'resource_type':'assessment','id':assessment_item['id'],'version':2})}
assignment=expect('Assign consultant to exact assessment',send(admin,'/api/v1/role-assignments',grant),201)
path=f'/api/v1/assessments/{assessment_item["id"]}/dossier'
dossier=expect('Consultant reads linked scenario and frozen inventory',get(reviewer,path),200)
check('Dossier includes scenario and context names',dossier['items'][0]['scenario']['name']==scenario['name'] and dossier['items'][0]['inventory']['systems'][0]['name']=='CRM cập nhật')
expect('Consultant cannot browse global inventory',get(reviewer,'/api/v1/systems'),403)
expect('Consultant cannot browse global scenario catalog',get(reviewer,'/api/v1/scenarios'),403)
expect('Consultant cannot bypass membership through context ID',get(reviewer,'/api/v1/context-snapshots/'+ctx['id']),404)
expect('Consultant cannot edit inventory',send(reviewer,'/api/v1/systems/'+system['id'],patch,method='PATCH',version=system['version']),403)
expect('Consultant cannot attach scenario',send(reviewer,f'/api/v1/assessments/{assessment_item["id"]}/scenario-links',link,version=2),403)
system=expect('Change live inventory after snapshot',send(security,'/api/v1/systems/'+system['id'],dict(patch,name='CRM thay đổi sau khi chụp'),method='PATCH',version=system['version']),200)
scenario_patch={'name':'Tên kịch bản sửa sau khi giao','write_context':deps(('system',system),('asset',asset),('data_asset',data_asset))}
expect('Edit scenario creates another immutable snapshot',send(security,'/api/v1/scenarios/'+scenario['id'],scenario_patch,method='PATCH',version=2),200)
check('Assigned dossier stays on pinned scenario and context',get(reviewer,path).json()==dossier)
stale=deepcopy(ctx_body)
expect('Stale context source dependencies rejected',send(security,'/api/v1/context-snapshots',stale),409)
other_body=dict(assessment_body,code='UNASSIGNED-ASSESSMENT')
other=expect('Create unassigned assessment',send(security,'/api/v1/assessments',other_body),201)
expect('Consultant cannot open another dossier',get(reviewer,f'/api/v1/assessments/{other["id"]}/dossier'),403)
owner.execute('UPDATE vdt.role_assignment SET revoked_at=clock_timestamp(),version=version+1 WHERE id=%s',(assignment['id'],))
expect('Revocation blocks dossier in existing session',get(reviewer,path),403)
check('No runtime DELETE access granted to domain link tables',not owner.execute("SELECT has_table_privilege('vdt_app','vdt.system_asset','DELETE')").fetchone()[0])
check('Scenario membership pins actual snapshot FK',owner.execute('SELECT scenario_snapshot_id IS NOT NULL FROM vdt.assessment_scenario WHERE assessment_id=%s',(assessment_item['id'],)).fetchone()[0])
concurrent_body=deepcopy(body);concurrent_body['code']='RACE-SYSTEM';concurrent_body['write_context']=deps()
race=expect('Create concurrency target',send(security,'/api/v1/systems',concurrent_body),201)
def concurrent_write(args):
    local_client=Client(enforce_csrf_checks=True,raise_request_exception=False)
    local_client.cookies=deepcopy(security.cookies)
    try:
        return send(local_client,'/api/v1/systems/'+race['id'],args[0],version=args[1],key=args[2],method='PATCH').status_code
    finally:
        connection.close()
one={'name':'Parallel first','write_context':deps()};two={'name':'Parallel second','write_context':deps()}
with ThreadPoolExecutor(max_workers=2) as pool:
    statuses=list(pool.map(concurrent_write,[(one,1,uuid4()),(two,1,uuid4())]))
check('Two concurrent edits produce one success and one stale-version refusal',sorted(statuses)==[200,412])
same={'name':'Idempotent concurrent update','write_context':deps()};same_key=uuid4()
with ThreadPoolExecutor(max_workers=2) as pool:
    statuses=list(pool.map(concurrent_write,[(same,2,same_key),(same,2,same_key)]))
check('Concurrent same-key replay commits once',statuses==[200,200] and owner.execute('SELECT version FROM vdt.information_system WHERE id=%s',(race['id'],)).fetchone()[0]==3)
fault=deepcopy(body);fault['code']='AUDIT-ROLLBACK';fault['write_context']=deps()
with mock_patch.object(access_service,'_audit',side_effect=DatabaseError('synthetic audit failure')):
    expect('Audit failure refuses inventory creation',send(security,'/api/v1/systems',fault),503)
check('Audit failure rolls back inventory and history',owner.execute("SELECT count(*) FROM vdt.information_system WHERE code='AUDIT-ROLLBACK'").fetchone()[0]==0)
complete=access_service._complete
def expire_at_commit(cursor,operation,reply):
    complete(cursor,operation,reply)
    cursor.execute('UPDATE vdt.role_assignment SET access_expires_at=clock_timestamp(),version=version+1 WHERE id=%s',[assignment_id])
fault['code']='EXPIRY-ROLLBACK'
with mock_patch.object(access_service,'_complete',side_effect=expire_at_commit):
    expect('Expiry at final gate refuses inventory creation',send(security,'/api/v1/systems',fault),403)
check('Final-gate refusal rolls back creation and idempotency result',owner.execute("SELECT count(*) FROM vdt.information_system WHERE code='EXPIRY-ROLLBACK'").fetchone()[0]==0)
try:
    owner_migration('0003')
except DatabaseError:
    check('Downgrade refuses to discard used snapshots and bindings',True)
else:
    raise AssertionError('Unsafe downgrade accepted')
# Optional browser QA accepts only a salted hash generated in the browser-tool
# memory. No plaintext password is stored in files, command output or reports.
browser_hash=os.environ.get('VDT_BROWSER_PASSWORD_HASH')
if browser_hash:
    from django.contrib.auth.hashers import identify_hasher
    assert identify_hasher(browser_hash).algorithm=='pbkdf2_sha256'
    for user_id in (security_id,reviewer_id):
        owner.execute('UPDATE vdt.app_user SET password_hash=%s,version=version+1 WHERE id=%s',(browser_hash,user_id))
    grant['write_context']=context({'resource_type':'user','id':str(reviewer_id),'version':owner.execute('SELECT version FROM vdt.app_user WHERE id=%s',(reviewer_id,)).fetchone()[0]},
                                  {'resource_type':'assessment','id':assessment_item['id'],'version':2})
    expect('Prepare consultant browser fixture',send(admin,'/api/v1/role-assignments',grant),201)
report={'scope':'DISPOSABLE_POSTGRESQL_WORKSPACE','passed':len(results),'checks':results}
Path('/reports/workspace-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
