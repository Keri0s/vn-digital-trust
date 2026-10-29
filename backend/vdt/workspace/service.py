"""Scoped preparation commands. All work is serialized by the organization auth guard.

Inventory relationships are additive in this milestone. Snapshot membership is
typed and pinned; no DELETE grant or in-place rewrite of history is required.
"""
from copy import deepcopy
import hashlib
import uuid
from django.utils.dateparse import parse_datetime
from vdt.access import service as access
from vdt.access.validation import fail, clean_text, assert_version, uuid_text
from vdt.assessment import service as assessment
from vdt.authn import service as auth
from .validation import validator

KINDS = {'systems':('information_system','InformationSystem','system'),
         'assets':('asset','Asset','asset'), 'data-assets':('data_asset','DataAsset','data_asset'),
         'scenarios':('risk_scenario','Scenario','scenario')}
READ = ('assessment.run','assessment.review','risk.impact_review','report.read')
KNOWN = {'systems':('purpose','hosting','exposure','criticality'),
         'assets':('business_value',), 'data-assets':('sensitivity','record_scope')}


def digest(value):
    return hashlib.sha256(access.canonical(value).encode()).hexdigest()


def run(request, operation):
    def guarded(cursor, principal):
        checked = []
        def gate(permissions, scope, assessment_id=None, *, optional=False):
            for permission in permissions:
                for grant in assessment._grants(cursor,principal,permission):
                    selection = access.scope_dto(cursor,grant[1])
                    if not any(selection[k] for k in access.DIMENSIONS):
                        cursor.execute('SELECT scope_kind FROM vdt.scope WHERE id=%s',[grant[1]])
                        if cursor.fetchone()[0] != 'ORGANIZATION':
                            continue
                    if assessment._covers(cursor,grant,scope,assessment_id):
                        if not optional:
                            checked.append((tuple(permissions),deepcopy(scope),assessment_id))
                        return grant
            if optional:
                return None
            fail('PERMISSION_DENIED',403,'Bạn chưa có quyền phù hợp với phạm vi hồ sơ này.')
        result = operation(cursor,principal,gate)
        for permissions,scope,assessment_id in list(checked):
            gate(permissions,scope,assessment_id,optional=False)
        return result
    return assessment._run(request,guarded)


def scoped(data,kind):
    scope = deepcopy(data['scope'])
    if kind in ('systems','assets','data-assets','scenarios'):
        key = {'systems':'system_ids','assets':'asset_ids','data-assets':'data_asset_ids','scenarios':'scenario_ids'}[kind]
        scope[key] = sorted(set(scope[key]) | {data['id']})
    if kind in ('assets','data-assets'):
        scope['system_ids'] = sorted(set(scope['system_ids']) | set(data['system_ids']))
    return scope


def load(cursor,kind,item_id):
    table,schema,_ = KINDS[kind]
    cursor.execute(f'SELECT id,code,version,api_payload,owner_id FROM vdt.{table} WHERE id=%s FOR UPDATE',[item_id])
    row = cursor.fetchone()
    if not row:
        fail('NOT_FOUND',404,'Không tìm thấy hồ sơ.')
    data = access.json_object(row[3])
    if (not validator(schema).is_valid(data) or data['id']!=str(row[0]) or data['code']!=row[1]
            or data['version']!=row[2] or data['owner_id']!=(str(row[4]) if row[4] else None)):
        fail('STORED_DATA_INVALID',503,'Hồ sơ chưa sẵn sàng; cần kiểm tra tính nhất quán.')
    if kind=='scenarios':
        cursor.execute('SELECT status,context_snapshot_id FROM vdt.risk_scenario WHERE id=%s',[item_id])
        state,ctx = cursor.fetchone()
        if state!=data['state'] or str(ctx)!=data['context_snapshot_id']:
            fail('STORED_DATA_INVALID',503,'Kịch bản không khớp dữ liệu lưu trữ.')
    else:
        links = [('asset_ids','system_asset','asset_id','system_id')] if kind=='systems' else [
            ('system_ids','system_asset' if kind=='assets' else 'system_data_asset','system_id','asset_id' if kind=='assets' else 'data_asset_id')]
        for key,table,column,parent in links:
            cursor.execute(f'SELECT {column} FROM vdt.{table} WHERE {parent}=%s',[item_id])
            if {str(r[0]) for r in cursor.fetchall()} != set(data[key]):
                fail('STORED_DATA_INVALID',503,'Liên kết tài sản không khớp hồ sơ.')
    return data


def branch_scope(cursor,principal,scope, *, inventory=False):
    for key in access.DIMENSIONS:
        scope[key]=sorted(scope[key])
    if scope['organization_id']!=str(principal.user.organization_id) or len(scope['branch_ids'])!=1:
        fail('INVALID_SCOPE',422,'Mốc lab này cần đúng một chi nhánh của tổ chức.')
    if scope['assessment_ids'] or scope['scenario_ids'] or (inventory and any(scope[k] for k in ('system_ids','asset_ids','data_asset_ids'))):
        fail('INVALID_SCOPE',422,'Phạm vi khai báo không phù hợp với loại hồ sơ.')
    access._branches(cursor,principal.user.organization_id,scope['branch_ids'])
    cursor.execute('SELECT id,version FROM vdt.branch WHERE id=%s',[scope['branch_ids'][0]])
    row=cursor.fetchone()
    return {('branch',str(row[0])):row[1]}


def owner(cursor,principal,owner_id,scope,required=False):
    if owner_id is None:
        if required:
            fail('OWNER_REQUIRED',422,'Cần chọn người phụ trách trước khi sử dụng kịch bản.')
        return {},None
    cursor.execute('''SELECT u.id,u.version,u.display_name FROM vdt.app_user u
        WHERE u.id=%s AND u.organization_id=%s AND u.status='ACTIVE'
        AND (u.id=%s OR EXISTS(SELECT 1 FROM vdt.user_branch b WHERE b.user_id=u.id AND b.branch_id=%s))''',
        [owner_id,principal.user.organization_id,principal.user.pk,scope['branch_ids'][0]])
    row=cursor.fetchone()
    if not row:
        fail('INVALID_OWNER',422,'Người phụ trách cần đang hoạt động và thuộc chi nhánh được chọn.')
    return {('user',str(row[0])):row[1]},row[2]


def validate_content(node):
    if isinstance(node,list):
        for item in node: validate_content(item)
    elif isinstance(node,dict):
        if set(('kind','reference','evidence_revision_id','verification_decision_id')) <= node.keys():
            if node['kind']=='EVIDENCE_REVISION':
                fail('PROTOTYPE_NOT_READY',503,'Liên kết bằng chứng đã xác minh sẽ được mở ở mốc bằng chứng.')
            if node['evidence_revision_id'] or node['verification_decision_id']:
                fail('INVALID_SOURCE',422,'Nguồn tài liệu/giả định không được khai mã xác minh bằng chứng.')
            clean_text(node['reference'],1000); clean_text(node['reason'])
        if set(('state','value','reason','sources')) <= node.keys():
            clean_text(node['reason'])
            if node['state']=='KNOWN':
                clean_text(node['value'])
                if not node['sources']:
                    fail('SOURCE_REQUIRED',422,'Thông tin đã biết cần ghi nguồn.')
            elif node['value'] is not None:
                fail('INVALID_INPUT',422,'Thông tin chưa xác định phải để trống giá trị và ghi lý do.')
        for value in node.values(): validate_content(value)


def make_scope(cursor,scope):
    sid=uuid.uuid4()
    cursor.execute('''INSERT INTO vdt.scope(id,organization_id,scope_kind,description,content_hash)
        VALUES(%s,%s,'SELECTED','Workspace record scope',%s)''',[sid,scope['organization_id'],digest(scope)])
    for branch in scope['branch_ids']:
        cursor.execute('INSERT INTO vdt.scope_branch(id,scope_id,branch_id) VALUES(%s,%s,%s)',[uuid.uuid4(),sid,branch])
    for key,(_,column) in access.OBJECTS.items():
        for value in scope[key]:
            cursor.execute(f'INSERT INTO vdt.scope_object(id,scope_id,{column}) VALUES(%s,%s,%s)',[uuid.uuid4(),sid,value])
    return sid


def history(cursor,principal,sid,kind,data):
    cursor.execute('''INSERT INTO vdt.mutable_entity_history(id,entity_kind,entity_id,entity_version,
        schema_version,effective_at,actor_id,scope_id,state_snapshot,content_hash)
        VALUES(%s,%s,%s,%s,'WORKSPACE-v0.1',clock_timestamp(),%s,%s,%s::jsonb,%s)''',
        [uuid.uuid4(),kind,data['id'],data['version'],principal.user.pk,sid,access.canonical(data),digest(data)])


def write_inventory_row(cursor,kind,data,creating):
    table,_,_=KINDS[kind]
    values={'code':data['code'],'name':data['name'],'owner_id':data['owner_id'],
            'version':data['version'],'api_payload':access.canonical(data)}
    if kind=='systems':
        values.update({k:data[k]['value'] or 'UNKNOWN' for k in KNOWN[kind]})
    elif kind=='assets':
        values.update(asset_type=data['asset_type'],branch_id=data['scope']['branch_ids'][0],status=data['state'])
    else:
        values.update(branch_id=data['scope']['branch_ids'][0],sensitivity=data['sensitivity']['value'],
                      description=data['record_scope']['value'] or 'UNKNOWN')
    if creating:
        values={'id':data['id'],**values}
        cursor.execute(f"INSERT INTO vdt.{table}({','.join(values)}) VALUES({','.join(['%s']*len(values))})",list(values.values()))
    else:
        cursor.execute(f"UPDATE vdt.{table} SET {','.join(k+'=%s' for k in values)} WHERE id=%s",[*values.values(),data['id']])


def inventory_write(request,kind,body,item_id=None,expected=None):
    def work(cursor,principal,gate):
        before=load(cursor,kind,item_id) if item_id else None
        data=dict(before or {},**{k:v for k,v in body.items() if k!='write_context'})
        required=branch_scope(cursor,principal,data['scope'],inventory=True)
        gate(('inventory.manage',),scoped(before,kind) if before else data['scope'])
        gate(('inventory.manage',),data['scope'])
        op,replay=access._ledger(cursor,request,principal,body,expected)
        if replay: return replay
        if before:
            assert_version(before['version'],expected)
            if data['scope']!=before['scope']:
                fail('SCOPE_CHANGE_UNSUPPORTED',422,'Tạo hồ sơ mới khi cần chuyển chi nhánh; lịch sử cũ được giữ nguyên.')
        clean_text(data['code'],128); clean_text(data['name']); clean_text(body['write_context']['reason'])
        validate_content(data)
        owner_deps,_=owner(cursor,principal,data['owner_id'],data['scope'])
        required.update(owner_deps)
        if kind=='systems' and data['vendor_ids']:
            fail('PROTOTYPE_NOT_READY',503,'Danh mục nhà cung cấp chưa được triển khai.')
        relation_key='asset_ids' if kind=='systems' else 'system_ids'
        if before and not set(before[relation_key])<=set(data[relation_key]):
            fail('RELATION_REMOVAL_UNSUPPORTED',422,'Mốc này giữ các liên kết đã lưu; có thể bổ sung liên kết hoặc ngừng sử dụng hồ sơ.')
        related_kind='assets' if kind=='systems' else 'systems'
        related=[]
        for related_id in sorted(set(data[relation_key]) | set((before or {}).get(relation_key,[]))):
            row=load(cursor,related_kind,related_id)
            gate(('inventory.manage',),scoped(row,related_kind))
            if row['state']!='ACTIVE' or row['scope']['branch_ids']!=data['scope']['branch_ids']:
                fail('INVALID_RELATION',422,'Hệ thống và tài sản phải đang sử dụng trong cùng chi nhánh.')
            required[(KINDS[related_kind][2],row['id'])]=row['version']; related.append(row)
        access._dependencies(cursor,principal.user.organization_id,body,required)
        data.update(id=item_id or str(uuid.uuid4()),version=before['version']+1 if before else 1,
                    updated_at=access.iso(auth.db_now(cursor)),updated_by=str(principal.user.pk))
        write_inventory_row(cursor,kind,data,not before)
        # Mirror only newly added relationships. Existing links cannot be removed.
        for other in related:
            if other['id'] in (before or {}).get(relation_key,[]): continue
            if kind in ('systems','assets'):
                system_id,asset_id=(data['id'],other['id']) if kind=='systems' else (other['id'],data['id'])
                cursor.execute('INSERT INTO vdt.system_asset(id,system_id,asset_id,relationship) VALUES(%s,%s,%s,%s)',[uuid.uuid4(),system_id,asset_id,'Declared in inventory'])
                reverse_key='system_ids' if kind=='systems' else 'asset_ids'
                other[reverse_key]=sorted(set(other[reverse_key])|{data['id']})
            else:
                cursor.execute('INSERT INTO vdt.system_data_asset(id,system_id,data_asset_id) VALUES(%s,%s,%s)',[uuid.uuid4(),other['id'],data['id']])
            other.update(version=other['version']+1,updated_at=data['updated_at'],updated_by=data['updated_by'])
            write_inventory_row(cursor,related_kind,other,False)
            other_scope=make_scope(cursor,scoped(other,related_kind))
            history(cursor,principal,other_scope,KINDS[related_kind][2],other)
            access._audit(cursor,request,principal,other_scope,'inventory.link',KINDS[related_kind][2],other['id'],before=other['version']-1,after=other['version'],reason=body['write_context']['reason'])
        sid=make_scope(cursor,scoped(data,kind)); history(cursor,principal,sid,KINDS[kind][2],data)
        gate(('inventory.manage',),scoped(data,kind))
        access._audit(cursor,request,principal,sid,'inventory.update' if before else 'inventory.create',KINDS[kind][2],data['id'],before=before['version'] if before else None,after=data['version'],reason=body['write_context']['reason'])
        reply=access.Reply(data,200 if before else 201,f'"{data["version"]}"',f'/api/v1/{kind}/{data["id"]}' if not before else None)
        access._complete(cursor,op,reply)
        return reply
    return run(request,work)


def snapshot(cursor,kind,item_id):
    cursor.execute('''SELECT api_payload,scope_id,created_at,created_by,content_hash FROM vdt.snapshot_registry
        WHERE id=%s AND snapshot_kind=%s AND api_payload_schema_version='workspace-v0.1' ''',[item_id,kind])
    row=cursor.fetchone()
    if not row: fail('NOT_FOUND',404,'Không tìm thấy phiên bản hồ sơ.')
    data=access.json_object(row[0])
    if kind=='CONTEXT':
        cursor.execute('SELECT facts FROM vdt.context_snapshot WHERE id=%s',[item_id])
        facts=access.json_object(cursor.fetchone()[0])
    else:
        cursor.execute('SELECT target_snapshot FROM vdt.scenario_snapshot WHERE id=%s',[item_id])
        facts=access.json_object(cursor.fetchone()[0])
    content={k:v for k,v in data.items() if k not in ('created_at','content_sha256')}
    if (not validator('ContextSnapshot' if kind=='CONTEXT' else 'ScenarioSnapshot').is_valid(data)
        or data['id']!=str(item_id) or parse_datetime(data['created_at'])!=row[2]
        or data['created_by']!=str(row[3]) or data['scope']!=access.scope_dto(cursor,row[1])
        or data['content_sha256']!=row[4] or digest({'payload':content,'facts':facts})!=row[4]):
        fail('STORED_DATA_INVALID',503,'Phiên bản hồ sơ không vượt qua kiểm tra tính toàn vẹn.')
    return data,facts


def register(cursor,principal,kind,data,facts,sid,lineage=None):
    content={k:v for k,v in data.items() if k not in ('created_at','content_sha256')}
    data['content_sha256']=digest({'payload':content,'facts':facts})
    cursor.execute('''INSERT INTO vdt.snapshot_registry(id,snapshot_kind,scope_id,created_by,created_at,
        content_hash,lineage_id,revision_number,api_payload_schema_version,api_payload)
        VALUES(%s,%s,%s,%s,clock_timestamp(),%s,%s,%s,'workspace-v0.1',%s::jsonb) RETURNING api_payload''',
        [data['id'],kind,sid,principal.user.pk,data['content_sha256'],lineage or data['id'],data['revision_number'],access.canonical(data)])
    return access.json_object(cursor.fetchone()[0])


def create_context(request,body):
    def work(cursor,principal,gate):
        required=branch_scope(cursor,principal,body['scope'])
        gate(('inventory.manage',),body['scope'])
        op,replay=access._ledger(cursor,request,principal,body,None)
        if replay: return replay
        clean_text(body['write_context']['reason']); validate_content(body)
        if body['vendor_ids'] or body['data_flow_ids']:
            fail('PROTOTYPE_NOT_READY',503,'Nhà cung cấp và luồng dữ liệu chưa được mở trong mốc này.')
        if not body['system_ids'] and not body['asset_ids']:
            fail('TARGET_REQUIRED',422,'Chọn ít nhất một hệ thống hoặc tài sản làm đối tượng đánh giá.')
        facts={'systems':[],'assets':[],'data-assets':[],'sources':body['sources']}
        for kind,key in (('systems','system_ids'),('assets','asset_ids'),('data-assets','data_asset_ids')):
            if sorted(body[key])!=sorted(body['scope'][key]):
                fail('INVALID_SCOPE',422,'Đối tượng bối cảnh phải khớp phạm vi đã khai báo.')
            for item_id in sorted(body[key]):
                data=load(cursor,kind,item_id); gate(('inventory.manage',),scoped(data,kind))
                if data['scope']['branch_ids']!=body['scope']['branch_ids'] or data['state']!='ACTIVE':
                    fail('INVALID_RELATION',422,'Đối tượng cần đang sử dụng trong chi nhánh của bối cảnh.')
                if kind!='systems' and not set(data['system_ids'])<=set(body['system_ids']):
                    fail('DEPENDENCY_REQUIRED',428,'Chọn đủ hệ thống liên quan tới tài sản/dữ liệu.')
                required[(KINDS[kind][2],data['id'])]=data['version']; facts[kind].append(data)
        access._dependencies(cursor,principal.user.organization_id,body,required)
        data={'id':str(uuid.uuid4()),'created_at':access.iso(auth.db_now(cursor)),'created_by':str(principal.user.pk),
              'revision_number':1,'scope':body['scope'],'source_dependencies':body['write_context']['dependencies'],
              'preconditions':body['preconditions'],'environment':body['environment'],'adversary_capability':body['adversary_capability'],
              'validation_issues':[]}
        sid=make_scope(cursor,data['scope']); data=register(cursor,principal,'CONTEXT',data,facts,sid)
        cursor.execute('''INSERT INTO vdt.context_snapshot(id,schema_version,facts,preconditions,input_versions,environment_fingerprint)
            VALUES(%s,'workspace-v0.1',%s::jsonb,%s::jsonb,%s::jsonb,%s)''',
            [data['id'],access.canonical(facts),access.canonical(data['preconditions']),access.canonical({'dependencies':data['source_dependencies']}),digest(data['environment'])])
        access._audit(cursor,request,principal,sid,'context.create','context',data['id'],reason=body['write_context']['reason'])
        reply=access.Reply(data,201,location=f'/api/v1/context-snapshots/{data["id"]}'); access._complete(cursor,op,reply)
        return reply
    return run(request,work)


def scenario_write(request,body,item_id=None,expected=None,transition=False):
    def work(cursor,principal,gate):
        before=load(cursor,'scenarios',item_id) if item_id else None
        if before: gate(('risk.propose',),scoped(before,'scenarios'))
        data=dict(before or {},**{k:v for k,v in body.items() if k!='write_context'})
        if not before: data['state']='DRAFT'
        required=branch_scope(cursor,principal,data['scope'])
        gate(('risk.propose',),data['scope'])
        op,replay=access._ledger(cursor,request,principal,body,expected)
        if replay: return replay
        if before:
            assert_version(before['version'],expected)
            if before['state']=='RETIRED' or (transition and before['state']==data['state']):
                fail('STATE_CONFLICT',409,'Chuyển trạng thái này không còn phù hợp.')
            if data['scope']!=before['scope']:
                fail('SCOPE_CHANGE_UNSUPPORTED',422,'Tạo kịch bản mới khi cần thay đổi đối tượng hoặc chi nhánh.')
        clean_text(body['write_context']['reason'])
        for key in ('code','name','event','consequences'): clean_text(data[key],128 if key=='code' else 4000)
        # Sources are kept in the immutable scenario version, not lost by the DTO.
        old_snapshot,old_facts=snapshot(cursor,'SCENARIO',before['current_scenario_snapshot_id']) if before else ({},{})
        sources=body.get('sources',old_snapshot.get('sources',[]))
        attack=body.get('attack_metadata',old_snapshot.get('attack_metadata',[]))
        validate_content([sources,attack])
        ctx,facts=snapshot(cursor,'CONTEXT',data['context_snapshot_id'])
        if data['scope']!=ctx['scope']:
            fail('INVALID_SCOPE',422,'Kịch bản phải dùng đúng phạm vi bối cảnh đã lưu.')
        gate(('risk.propose',),ctx['scope'])
        owner_deps,owner_name=owner(cursor,principal,data['owner_id'],data['scope'],data['state']=='ACTIVE')
        required.update(owner_deps)
        # Validate current target availability and exact head versions before use.
        for kind in ('systems','assets','data-assets'):
            for frozen in facts[kind]:
                live=load(cursor,kind,frozen['id']); gate(('risk.propose',),scoped(live,kind))
                if live['state']!='ACTIVE' or live['scope']!=frozen['scope']:
                    fail('TARGET_UNAVAILABLE',409,'Đối tượng của bối cảnh đã ngừng sử dụng hoặc thay đổi phạm vi.')
                required[(KINDS[kind][2],live['id'])]=live['version']
        access._dependencies(cursor,principal.user.organization_id,body,required)
        sid_value=str(uuid.uuid4()); item=item_id or str(uuid.uuid4()); version=before['version']+1 if before else 1
        snap={'id':sid_value,'created_at':access.iso(auth.db_now(cursor)),'created_by':str(principal.user.pk),
              'scenario_id':item,'revision_number':version,'context_snapshot_id':ctx['id'],
              **{k:data[k] for k in ('code','name','event','consequences','owner_id','scope')},
              'attack_metadata':attack,'sources':sources}
        result={k:data[k] for k in ('code','name','event','consequences','owner_id','scope','state','context_snapshot_id')}
        result.update(id=item,version=version,updated_at=snap['created_at'],updated_by=snap['created_by'],current_scenario_snapshot_id=sid_value,validation_issues=[])
        if before:
            cursor.execute('''UPDATE vdt.risk_scenario SET code=%s,name=%s,event=%s,consequence=%s,owner_id=%s,
                status=%s,context_snapshot_id=%s,version=%s,api_payload=%s::jsonb WHERE id=%s''',
                [data['code'],data['name'],data['event'],data['consequences'],data['owner_id'],data['state'],ctx['id'],version,access.canonical(result),item])
        else:
            cursor.execute('''INSERT INTO vdt.risk_scenario(id,code,name,event,consequence,owner_id,status,context_snapshot_id,api_payload)
                VALUES(%s,%s,%s,%s,%s,%s,'DRAFT',%s,%s::jsonb)''',
                [item,data['code'],data['name'],data['event'],data['consequences'],data['owner_id'],ctx['id'],access.canonical(result)])
            for key,column in (('system_ids','system_id'),('asset_ids','asset_id')):
                for target in data['scope'][key]:
                    cursor.execute(f'INSERT INTO vdt.scenario_target(id,scenario_id,{column}) VALUES(%s,%s,%s)',[uuid.uuid4(),item,target])
        target_facts={'inventory':facts,'owner_name':owner_name,'state':data['state']}
        sid=make_scope(cursor,data['scope']); snap=register(cursor,principal,'SCENARIO',snap,target_facts,sid,item)
        cursor.execute('''INSERT INTO vdt.scenario_snapshot(id,scenario_id,source_version,context_snapshot_id,code,name,event,
            consequences,owner_id,attack_metadata,sources,target_snapshot) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)''',
            [sid_value,item,version,ctx['id'],data['code'],data['name'],data['event'],data['consequences'],data['owner_id'],access.canonical(attack),access.canonical(sources),access.canonical(target_facts)])
        history(cursor,principal,sid,'scenario',result)
        gate(('risk.propose',),scoped(result,'scenarios'))
        access._audit(cursor,request,principal,sid,'scenario.transition' if transition else 'scenario.write','scenario',item,before=before['version'] if before else None,after=version,reason=body['write_context']['reason'])
        reply=access.Reply(result,200 if before else 201,f'"{version}"',None if before else f'/api/v1/scenarios/{item}')
        access._complete(cursor,op,reply); return reply
    return run(request,work)


def assessment_data(cursor,principal,gate,assessment_id,write=False):
    data=assessment._dto(cursor,assessment_id)
    gate(('assessment.run',) if write else READ,data['scope'],assessment_id)
    if data['scope']['organization_id']!=str(principal.user.organization_id): fail('NOT_FOUND',404,'Không tìm thấy đợt.')
    return data


def link_scenario(request,assessment_id,body,expected):
    def work(cursor,principal,gate):
        current=assessment_data(cursor,principal,gate,assessment_id,True)
        scenario=load(cursor,'scenarios',body['scenario_id'])
        gate(('assessment.run',),scoped(scenario,'scenarios'))
        op,replay=access._ledger(cursor,request,principal,body,expected)
        if replay: return replay
        assert_version(current['version'],expected)
        if current['state']!='OPEN' or scenario['state']!='ACTIVE':
            fail('STATE_CONFLICT',409,'Đợt cần đang mở và kịch bản cần đang sử dụng.')
        if scenario['id'] in current['scenario_ids']:
            fail('ALREADY_LINKED',409,'Kịch bản đã có trong đợt này.')
        if len(current['scenario_ids'])>=200:
            fail('LIMIT_REACHED',422,'Đợt đã đạt giới hạn 200 kịch bản.')
        for key in access.DIMENSIONS:
            if key in ('assessment_ids','scenario_ids'): continue
            if current['scope'][key] and not set(scenario['scope'][key])<=set(current['scope'][key]):
                fail('INVALID_SCOPE',422,'Kịch bản nằm ngoài phạm vi của đợt.')
        clean_text(body['write_context']['reason'])
        required={('scenario',scenario['id']):scenario['version']}
        access._dependencies(cursor,principal.user.organization_id,body,required)
        snapshot(cursor,'SCENARIO',scenario['current_scenario_snapshot_id'])
        cursor.execute('''INSERT INTO vdt.assessment_scenario(id,assessment_id,scenario_id,scenario_snapshot_id)
            VALUES(%s,%s,%s,%s)''',[uuid.uuid4(),assessment_id,scenario['id'],scenario['current_scenario_snapshot_id']])
        updated=dict(current,scenario_ids=sorted(current['scenario_ids']+[scenario['id']]),version=current['version']+1,
                     updated_at=access.iso(auth.db_now(cursor)),updated_by=str(principal.user.pk))
        cursor.execute('UPDATE vdt.assessment SET version=%s,api_payload=%s::jsonb WHERE id=%s',[updated['version'],access.canonical(updated),assessment_id])
        sid=make_scope(cursor,dict(current['scope'],assessment_ids=[assessment_id]))
        history(cursor,principal,sid,'assessment',updated)
        access._audit(cursor,request,principal,sid,'assessment.scenario.add','assessment',assessment_id,before=current['version'],after=updated['version'],reason=body['write_context']['reason'])
        reply=access.Reply(updated,200,f'"{updated["version"]}"'); access._complete(cursor,op,reply); return reply
    return run(request,work)


def dossier(request,assessment_id):
    def work(cursor,principal,gate):
        data=assessment_data(cursor,principal,gate,assessment_id)
        cursor.execute('SELECT scenario_id,scenario_snapshot_id FROM vdt.assessment_scenario WHERE assessment_id=%s ORDER BY scenario_id',[assessment_id])
        links=cursor.fetchall()
        if {str(r[0]) for r in links}!=set(data['scenario_ids']): fail('STORED_DATA_INVALID',503,'Danh sách kịch bản của đợt không nhất quán.')
        rows=[]
        for scenario_id,snapshot_id in links:
            if not snapshot_id: fail('STORED_DATA_INVALID',503,'Liên kết chưa xác định phiên bản kịch bản.')
            scenario,facts=snapshot(cursor,'SCENARIO',str(snapshot_id))
            scope=dict(scoped(dict(scenario,id=str(scenario_id)),'scenarios'),assessment_ids=[assessment_id])
            if not gate(READ,scope,assessment_id,optional=True): continue
            gate(READ,scope,assessment_id)
            ctx,inventory=snapshot(cursor,'CONTEXT',scenario['context_snapshot_id'])
            rows.append({'scenario':scenario,'context':ctx,'inventory':inventory,'owner_name':facts['owner_name'],'state':facts['state']})
        grant=gate(READ,data['scope'],assessment_id)
        access._audit(cursor,request,principal,grant[1],'assessment.dossier.read','assessment',assessment_id)
        return access.Reply({'assessment':data,'items':rows,'restricted':len(rows)!=len(links)})
    return run(request,work)


def collection(request,kind,item_id=None):
    def work(cursor,principal,gate):
        permission='risk.propose' if kind=='scenarios' else 'inventory.manage'
        if item_id:
            data=load(cursor,kind,item_id)
            if not gate((permission,*READ),scoped(data,kind),optional=True):
                fail('NOT_FOUND',404,'Không tìm thấy hồ sơ trong phạm vi được cấp.')
            grant=gate((permission,*READ),scoped(data,kind))
            access._audit(cursor,request,principal,grant[1],'workspace.read',KINDS[kind][2],item_id)
            return access.Reply(data,etag=f'"{data["version"]}"')
        if not assessment._grants(cursor,principal,permission): fail('PERMISSION_DENIED',403,'Không có quyền xem danh mục này.')
        cursor.execute(f'SELECT id FROM vdt.{KINDS[kind][0]} ORDER BY id')
        rows=[]
        for (item,) in cursor.fetchall():
            data=load(cursor,kind,str(item))
            if gate((permission,),scoped(data,kind),optional=True):
                gate((permission,),scoped(data,kind)); rows.append(data)
        return access._page(request,rows)
    return run(request,work)


def snapshot_read(request,kind,item_id):
    def work(cursor,principal,gate):
        data,_=snapshot(cursor,kind,item_id)
        permissions=('inventory.manage',*READ) if kind=='CONTEXT' else ('risk.propose',*READ)
        if not gate(permissions,data['scope'],optional=True): fail('NOT_FOUND',404,'Không tìm thấy phiên bản trong phạm vi được cấp.')
        grant=gate(permissions,data['scope']); access._audit(cursor,request,principal,grant[1],'snapshot.read',kind.lower(),item_id)
        return access.Reply(data)
    return run(request,work)


def setup(request):
    def work(cursor,principal,gate):
        if not assessment._grants(cursor,principal,'inventory.manage') or not assessment._grants(cursor,principal,'risk.propose'):
            fail('PERMISSION_DENIED',403,'Cần quyền chuẩn bị hồ sơ đánh giá.')
        cursor.execute('SELECT id,code,name,version FROM vdt.organization WHERE id=%s',[principal.user.organization_id]); org=cursor.fetchone()
        cursor.execute('SELECT id,code,name,version FROM vdt.branch WHERE organization_id=%s AND active ORDER BY name',[org[0]])
        branches=[]
        for row in cursor.fetchall():
            scope={'organization_id':str(org[0]),**{key:[] for key in access.DIMENSIONS},'branch_ids':[str(row[0])]}
            if not gate(('inventory.manage',),scope,optional=True) or not gate(('risk.propose',),scope,optional=True): continue
            gate(('inventory.manage',),scope); gate(('risk.propose',),scope)
            cursor.execute('''SELECT u.id,u.display_name,u.version FROM vdt.app_user u WHERE u.organization_id=%s
                AND u.status='ACTIVE' AND (u.id=%s OR EXISTS(SELECT 1 FROM vdt.user_branch b WHERE b.user_id=u.id AND b.branch_id=%s)) ORDER BY u.display_name''',[org[0],principal.user.pk,row[0]])
            owners=[{'id':str(u[0]),'name':u[1],'version':u[2]} for u in cursor.fetchall()]
            branches.append({'id':str(row[0]),'code':row[1],'name':row[2],'version':row[3],'owners':owners})
        return access.Reply({'organization':{'id':str(org[0]),'code':org[1],'name':org[2],'version':org[3]},'branches':branches})
    return run(request,work)
