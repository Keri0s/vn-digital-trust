"""Transactional TUC-01 administration. Lock order: auth guard, domain, ledger.

The current milestone exposes organization administration only. A selected-scope
administrative grant is never interpreted as an organization-wide grant. Domain
role assignments can constrain branches/objects, but do not open domain APIs.
"""
from dataclasses import dataclass
from datetime import timezone
import hashlib
import json
import uuid

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import connection, transaction, IntegrityError
from django.utils.crypto import salted_hmac
from django.views.decorators.debug import sensitive_variables

from vdt.authn import service as auth
from vdt.core.models import AppUser
from .validation import fail, clean_text, username, timestamp, uuid_text, assert_version, schema_validator

DIMENSIONS = ('branch_ids','system_ids','asset_ids','data_asset_ids','scenario_ids','assessment_ids')
OBJECTS = {'system_ids':('information_system','system_id'), 'asset_ids':('asset','asset_id'),
           'data_asset_ids':('data_asset','data_asset_id'), 'scenario_ids':('risk_scenario','scenario_id'),
           'assessment_ids':('assessment','assessment_id')}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',',':'))


def json_object(value):
    """Normalize raw-cursor JSONB across Django/psycopg loader settings."""
    if isinstance(value,str):
        try:
            value=json.loads(value)
        except (ValueError,RecursionError):
            fail('STORED_DATA_INVALID',503,'Dữ liệu lưu trữ chưa sẵn sàng.')
    if not isinstance(value,dict):
        fail('STORED_DATA_INVALID',503,'Dữ liệu lưu trữ chưa sẵn sàng.')
    return value


def iso(value):
    return value.astimezone(timezone.utc).isoformat() if value else None


@dataclass
class Reply:
    data: object = None
    status: int = 200
    etag: str | None = None
    location: str | None = None


def scope_dto(cursor, scope_id):
    cursor.execute('SELECT organization_id FROM vdt.scope WHERE id=%s',[scope_id])
    row = cursor.fetchone()
    if not row:
        fail('NOT_FOUND',404,'Không tìm thấy phạm vi.')
    result = {'organization_id':str(row[0]), **{key:[] for key in DIMENSIONS}}
    cursor.execute('SELECT branch_id FROM vdt.scope_branch WHERE scope_id=%s ORDER BY branch_id',[scope_id])
    result['branch_ids'] = [str(r[0]) for r in cursor.fetchall()]
    for key, (_, column) in OBJECTS.items():
        cursor.execute(f'SELECT {column} FROM vdt.scope_object WHERE scope_id=%s AND {column} IS NOT NULL ORDER BY {column}',[scope_id])
        result[key] = [str(r[0]) for r in cursor.fetchall()]
    return result


def metadata(cursor, kind, entity_id):
    cursor.execute('''SELECT recorded_at,actor_id FROM vdt.mutable_entity_history
        WHERE entity_kind=%s AND entity_id=%s ORDER BY recorded_at DESC,entity_version DESC LIMIT 1''',[kind,entity_id])
    history = cursor.fetchone()
    cursor.execute('''SELECT recorded_at,actor_id FROM vdt.audit_event
        WHERE target_id=%s AND actor_id IS NOT NULL AND outcome='ALLOWED'
        AND (target_kind=%s OR (%s='user' AND target_kind='VDT_AUTH'
             AND action IN ('auth.login','auth.password')))
        ORDER BY recorded_at DESC LIMIT 1''',[entity_id,kind,kind])
    audit = cursor.fetchone()
    choices = [item for item in (history,audit) if item]
    if not choices:
        fail('METADATA_UNAVAILABLE',503,'Lịch sử tài nguyên chưa sẵn sàng.')
    at, actor = max(choices,key=lambda item:item[0])
    return {'updated_at':iso(at),'updated_by':str(actor)}


def user_dto(cursor, user_id, organization_id):
    cursor.execute('SELECT id,login_name,display_name,status,version FROM vdt.app_user WHERE id=%s AND organization_id=%s',[user_id,organization_id])
    row = cursor.fetchone()
    if not row:
        fail('NOT_FOUND',404,'Không tìm thấy tài khoản.')
    cursor.execute('SELECT branch_id FROM vdt.user_branch WHERE user_id=%s ORDER BY branch_id',[user_id])
    return {'id':str(row[0]),'username':row[1],'display_name':row[2],'active':row[3]=='ACTIVE',
            'version':row[4],'branch_ids':[str(item[0]) for item in cursor.fetchall()], **metadata(cursor,'user',row[0])}


def assignment_dto(cursor, assignment_id, organization_id):
    cursor.execute('''SELECT a.id,a.user_id,a.role_id,a.scope_id,a.valid_from,a.access_expires_at,a.revoked_at,a.version
        FROM vdt.role_assignment a JOIN vdt.app_user u ON u.id=a.user_id
        WHERE a.id=%s AND u.organization_id=%s''',[assignment_id,organization_id])
    row = cursor.fetchone()
    if not row:
        fail('NOT_FOUND',404,'Không tìm thấy quyền được cấp.')
    cursor.execute('SELECT assessment_id FROM vdt.assignment_assessment WHERE assignment_id=%s ORDER BY assessment_id',[assignment_id])
    assigned = [str(item[0]) for item in cursor.fetchall()]
    return {'id':str(row[0]),'user_id':str(row[1]),'role_id':str(row[2]),'scope':scope_dto(cursor,row[3]),
            'effective_at':iso(row[4]),'access_expires_at':iso(row[5]),'revoked_at':iso(row[6]),'version':row[7],
            'assigned_assessment_ids':assigned, **metadata(cursor,'role_assignment',row[0])}


def _authorized(cursor, request, permission):
    binding = auth._locate_binding(request,cursor)
    if binding is None:
        fail('AUTHENTICATION_REQUIRED',401,'Vui lòng đăng nhập lại.')
    located,key = binding
    version = auth.guard(cursor,located[2])
    context = auth._context_locked(cursor,request,located,key,version)
    if context is None:
        fail('AUTHENTICATION_REQUIRED',401,'Vui lòng đăng nhập lại.')
    cursor.execute('SELECT password_change_required FROM vdt.app_user WHERE id=%s',[context.user.pk])
    if cursor.fetchone()[0]:
        fail('PASSWORD_CHANGE_REQUIRED',403,'Cần đổi mật khẩu tạm thời trước khi tiếp tục.')
    now = auth.db_now(cursor)
    cursor.execute('''SELECT a.id,a.scope_id,a.access_expires_at FROM vdt.role_assignment a
        JOIN vdt.scope s ON s.id=a.scope_id JOIN vdt.role_permission rp ON rp.role_id=a.role_id
        JOIN vdt.permission p ON p.id=rp.permission_id
        WHERE a.user_id=%s AND p.code=%s AND a.revoked_at IS NULL AND a.valid_from<=%s
        AND (a.access_expires_at IS NULL OR a.access_expires_at>%s)
        AND s.organization_id=%s AND s.scope_kind='ORGANIZATION'
        AND NOT EXISTS(SELECT 1 FROM vdt.scope_branch b WHERE b.scope_id=s.id)
        AND NOT EXISTS(SELECT 1 FROM vdt.scope_object o WHERE o.scope_id=s.id)
        ORDER BY a.id''',[context.user.pk,permission,now,now,context.user.organization_id])
    grants = cursor.fetchall()
    if not grants:
        fail('PERMISSION_DENIED',403,'Tài khoản chưa có quyền quản trị phù hợp.')
    return context,grants


def _audit(cursor, request, context, scope_id, action, kind, target_id, *, before=None, after=None, reason='', outcome='ALLOWED', code='COMMITTED'):
    safe = {'before_version':before,'after_version':after}
    if reason:
        safe['reason'] = reason
    cursor.execute('''INSERT INTO vdt.audit_event(id,actor_id,session_id,action,target_kind,target_id,
        outcome,reason_code,correlation_id,scope_id,authorization_version,gate_checked_at,safe_metadata)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,clock_timestamp(),%s::jsonb)''',
        [uuid.uuid4(),context.user.pk,context.session_id,action,kind,target_id,outcome,code,
         request.vdt_request_id,scope_id,context.authorization_version,canonical(safe)])


def _history(cursor, context, scope_id, kind, entity_id, version, state):
    text = canonical(state)
    cursor.execute('''INSERT INTO vdt.mutable_entity_history(id,entity_kind,entity_id,entity_version,
        schema_version,effective_at,actor_id,scope_id,state_snapshot,content_hash)
        VALUES(%s,%s,%s,%s,'ACCESS-v0.1',clock_timestamp(),%s,%s,%s::jsonb,%s)''',
        [uuid.uuid4(),kind,entity_id,version,context.user.pk,scope_id,text,hashlib.sha256(text.encode()).hexdigest()])


def _dependencies(cursor, organization_id, body, required):
    cursor.execute('SELECT id,version FROM vdt.organization WHERE id=%s FOR UPDATE',[organization_id])
    org = cursor.fetchone()
    expected = {('organization',str(org[0])):org[1], **required}
    declared = {}
    for dependency in body['write_context']['dependencies']:
        key = (dependency['resource_type'],dependency['id'])
        if key in declared:
            fail('INVALID_INPUT',422,'Phụ thuộc bị trùng.')
        declared[key] = dependency['version']
    if not expected.keys() <= declared.keys():
        fail('DEPENDENCY_REQUIRED',428,'Cần đọc lại đầy đủ dữ liệu liên quan trước khi lưu.')
    for key, version in expected.items():
        if declared[key] != version:
            fail('DEPENDENCY_CHANGED',409,'Dữ liệu liên quan đã thay đổi. Hãy tải lại.')
    # Extra dependencies cannot smuggle unchecked identifiers/versions.
    if declared.keys() != expected.keys():
        fail('INVALID_INPUT',422,'Danh sách phụ thuộc không khớp thao tác.')


def _branches(cursor, organization_id, ids):
    if not ids:
        return
    cursor.execute('SELECT id FROM vdt.branch WHERE organization_id=%s AND active AND id=ANY(%s::uuid[]) ORDER BY id FOR UPDATE',[organization_id,ids])
    if {str(row[0]) for row in cursor.fetchall()} != set(ids):
        fail('INVALID_SCOPE',422,'Chi nhánh không tồn tại hoặc không hoạt động trong tổ chức.')


def _usable_admin_exists(cursor, organization_id):
    now = auth.db_now(cursor)
    cursor.execute('''SELECT EXISTS(SELECT 1 FROM vdt.app_user u
        JOIN vdt.role_assignment a ON a.user_id=u.id JOIN vdt.role r ON r.id=a.role_id
        JOIN vdt.scope s ON s.id=a.scope_id WHERE u.organization_id=%s AND u.status='ACTIVE'
        AND NOT u.password_change_required AND u.password_hash LIKE 'pbkdf2_sha256$%%'
        AND r.code='VDT_ADMIN' AND a.revoked_at IS NULL AND a.valid_from<=%s
        AND (a.access_expires_at IS NULL OR a.access_expires_at>%s)
        AND s.scope_kind='ORGANIZATION' AND s.organization_id=%s
        AND NOT EXISTS(SELECT 1 FROM vdt.scope_branch b WHERE b.scope_id=s.id)
        AND NOT EXISTS(SELECT 1 FROM vdt.scope_object o WHERE o.scope_id=s.id))''',[organization_id,now,now,organization_id])
    if not cursor.fetchone()[0]:
        fail('LAST_ADMIN_REQUIRED',409,'Cần giữ ít nhất một quản trị viên đang hoạt động và đã đổi mật khẩu tạm thời.')


def _request_hash(request, body, expected):
    # Keyed SHA-256 prevents an idempotency row becoming an offline password oracle.
    return salted_hmac('vdt.access.request.v1',canonical({'body':body,'expected_version':expected}),algorithm='sha256').hexdigest()


def _ledger(cursor, request, context, body, expected):
    raw = request.headers.get('Idempotency-Key')
    if raw is None:
        fail('IDEMPOTENCY_KEY_REQUIRED',428,'Thiếu mã nhận diện thao tác.')
    key = uuid_text(raw)
    digest = _request_hash(request,body,expected)
    cursor.execute('''SELECT id,request_hash,state,result_metadata FROM vdt.idempotency_operation
        WHERE organization_id=%s AND principal_id=%s AND method=%s AND canonical_path=%s AND idempotency_key=%s FOR UPDATE''',
        [context.user.organization_id,context.user.pk,request.method,request.path,key])
    row = cursor.fetchone()
    if row:
        if row[1] != digest:
            fail('IDEMPOTENCY_CONFLICT',409,'Mã thao tác đã được dùng với nội dung khác.')
        if row[2] != 'SUCCEEDED':
            fail('OPERATION_IN_PROGRESS',409,'Thao tác đang được xử lý; hãy thử lại với cùng mã.')
        return None, Reply(**json_object(row[3]))
    operation_id = uuid.uuid4()
    cursor.execute('''INSERT INTO vdt.idempotency_operation(id,organization_id,principal_id,method,canonical_path,
        idempotency_key,request_hash,expected_version,state,created_at,updated_at)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'PROCESSING',clock_timestamp(),clock_timestamp())''',
        [operation_id,context.user.organization_id,context.user.pk,request.method,request.path,key,digest,expected])
    return operation_id,None


def _complete(cursor, operation_id, reply):
    cursor.execute('''UPDATE vdt.idempotency_operation SET state='SUCCEEDED',result_status=%s,
        result_metadata=%s::jsonb,updated_at=clock_timestamp(),version=version+1 WHERE id=%s''',
        [reply.status,canonical(vars(reply)),operation_id])


def execute(request, permission, operation, *, body=None, expected=None):
    """Reauthorize after work while holding the same guard. Failures roll back."""
    try:
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout='5s'")
            cursor.execute("SET LOCAL statement_timeout='20s'")
            context,grants = _authorized(cursor,request,permission)
            scope_id = grants[0][1]
            operation_id = None
            if body is not None:
                clean_text(body['write_context']['reason'])
                operation_id,replay = _ledger(cursor,request,context,body,expected)
                if replay:
                    _authorized(cursor,request,permission)
                    return replay
            reply = operation(cursor,context,scope_id)
            # Any expiry crossed during hashing/queries invalidates the mutation.
            final_context,_ = _authorized(cursor,request,permission)
            if body is not None:
                now = auth.db_now(cursor)
                cursor.execute('UPDATE vdt.vdt_session SET last_seen_at=%s,version=version+1 WHERE id=%s',[now,final_context.session_id])
                _complete(cursor,operation_id,reply)
            return reply
    except IntegrityError:
        fail('STATE_CONFLICT',409,'Dữ liệu đã tồn tại hoặc quan hệ không còn hợp lệ.')


def audit_denied(request, code):
    """Persist only a minimal refusal after the failed domain transaction rolls back.

    Re-read the opaque session binding rather than trusting middleware's earlier
    context. Unauthenticated events have no attributed actor. Never copy the
    request body, path, reason, credentials, or caller-provided target identifier.
    """
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SET LOCAL lock_timeout='5s'")
        cursor.execute("SET LOCAL statement_timeout='20s'")
        context = None
        binding = auth._locate_binding(request,cursor)
        if binding is not None:
            located,key = binding
            version = auth.guard(cursor,located[2])
            context = auth._context_locked(cursor,request,located,key,version)
        cursor.execute('''INSERT INTO vdt.audit_event(id,actor_id,session_id,action,
            target_kind,outcome,reason_code,correlation_id,authorization_version,gate_checked_at)
            VALUES(%s,%s,%s,%s,'VDT_ACCESS','DENIED',%s,%s,%s,clock_timestamp())''',
            [uuid.uuid4(),context.user.pk if context else None,context.session_id if context else None,
             'access.read' if request.method=='GET' else 'access.write',code,
             request.vdt_request_id,context.authorization_version if context else None])


def _page(request, rows, key='id', descending=False):
    if set(request.GET)-{'cursor','limit'} or any(len(request.GET.getlist(k)) != 1 for k in request.GET):
        fail('INVALID_QUERY',400,'Tham số danh sách không hợp lệ.')
    raw_limit = request.GET.get('limit','50')
    if not raw_limit.isdigit() or not 1<=int(raw_limit)<=200:
        fail('INVALID_QUERY',400,'Số bản ghi phải từ 1 đến 200.')
    limit = int(raw_limit)
    last = None
    if request.GET.get('cursor'):
        try:
            value = signing.loads(request.GET['cursor'],salt='vdt.access.cursor.v1')
            if value['principal'] != str(request.user.pk) or value['path'] != request.path:
                raise ValueError()
            last = value['last']
        except (signing.BadSignature,KeyError,ValueError,TypeError):
            fail('INVALID_CURSOR',400,'Mốc phân trang không hợp lệ.')
    value_of = key if callable(key) else lambda row: row[key]
    ordered = [row for row in sorted(rows,key=value_of,reverse=descending)
               if last is None or (value_of(row)<last if descending else value_of(row)>last)]
    selected = ordered[:limit]
    next_cursor = signing.dumps({'principal':str(request.user.pk),'path':request.path,'last':value_of(selected[-1])},salt='vdt.access.cursor.v1') if len(ordered)>limit else None
    return Reply({'items':selected,'next_cursor':next_cursor})


def organization(request):
    def read(cursor,context,scope_id):
        cursor.execute('SELECT id,code,name,version FROM vdt.organization WHERE id=%s',[context.user.organization_id])
        row = cursor.fetchone()
        return Reply({'id':str(row[0]),'code':row[1],'name':row[2],'version':row[3],**metadata(cursor,'organization',row[0])},etag=f'"{row[3]}"')
    return execute(request,'organization.manage',read)


def branches(request):
    def read(cursor,context,scope_id):
        cursor.execute('SELECT id,organization_id,code,name,active,version FROM vdt.branch WHERE organization_id=%s',[context.user.organization_id])
        rows = cursor.fetchall()
        items = [{'id':str(r[0]),'organization_id':str(r[1]),'code':r[2],'name':r[3],'active':r[4],'version':r[5],**metadata(cursor,'branch',r[0])} for r in rows]
        return _page(request,items)
    return execute(request,'organization.manage',read)


def users(request, user_id=None):
    def read(cursor,context,scope_id):
        if user_id:
            result = user_dto(cursor,user_id,context.user.organization_id)
            return Reply(result,etag=f'"{result["version"]}"')
        cursor.execute('SELECT id FROM vdt.app_user WHERE organization_id=%s',[context.user.organization_id])
        ids = [r[0] for r in cursor.fetchall()]
        return _page(request,[user_dto(cursor,item,context.user.organization_id) for item in ids])
    return execute(request,'users.manage',read)


def catalog(request, kind):
    def read(cursor,context,scope_id):
        if kind == 'permissions':
            cursor.execute('SELECT code,description FROM vdt.permission')
            return _page(request,[{'code':r[0],'description':r[1],'application':'VDT'} for r in cursor.fetchall()],key='code')
        cursor.execute('SELECT id,code FROM vdt.role')
        roles = cursor.fetchall()
        rows=[]
        for role_id,code in roles:
            cursor.execute('SELECT p.code FROM vdt.role_permission rp JOIN vdt.permission p ON p.id=rp.permission_id WHERE rp.role_id=%s ORDER BY p.code',[role_id])
            rows.append({'id':str(role_id),'code':code,'permission_codes':[r[0] for r in cursor.fetchall()],'application':'VDT'})
        return _page(request,rows)
    return execute(request,'roles.assign',read)


def assignments(request, assignment_id=None):
    def read(cursor,context,scope_id):
        if assignment_id:
            result=assignment_dto(cursor,assignment_id,context.user.organization_id)
            return Reply(result,etag=f'"{result["version"]}"')
        cursor.execute('SELECT a.id FROM vdt.role_assignment a JOIN vdt.app_user u ON u.id=a.user_id WHERE u.organization_id=%s',[context.user.organization_id])
        ids=[r[0] for r in cursor.fetchall()]
        return _page(request,[assignment_dto(cursor,item,context.user.organization_id) for item in ids])
    return execute(request,'roles.assign',read)


def _lock_user(cursor,user_id,organization_id):
    cursor.execute('SELECT id,version,status FROM vdt.app_user WHERE id=%s AND organization_id=%s FOR UPDATE',[user_id,organization_id])
    row=cursor.fetchone()
    if not row:
        fail('NOT_FOUND',404,'Không tìm thấy tài khoản.')
    return row


def _revoke_sessions(cursor,user_id):
    cursor.execute('UPDATE vdt.vdt_session SET revoked_at=clock_timestamp(),version=version+1 WHERE user_id=%s AND revoked_at IS NULL',[user_id])


def write_user(request, body, user_id=None, expected=None):
    def write(cursor,context,scope_id):
        org=context.user.organization_id
        before=None
        if user_id:
            row=_lock_user(cursor,user_id,org)
            assert_version(row[1],expected)
            before=user_dto(cursor,user_id,org)
        _dependencies(cursor,org,body,{})
        merged=dict(before or {}, **{k:v for k,v in body.items() if k!='write_context'})
        merged['username']=username(merged['username'])
        merged['display_name']=clean_text(merged['display_name'],200)
        _branches(cursor,org,merged['branch_ids'])
        if user_id and str(user_id)==str(context.user.pk) and not merged['active']:
            fail('SELF_LOCKOUT',409,'Bạn không thể khóa chính tài khoản đang dùng.')
        target=user_id or uuid.uuid4()
        state='ACTIVE' if merged['active'] else 'DISABLED'
        if before:
            cursor.execute('UPDATE vdt.app_user SET login_name=%s,display_name=%s,status=%s,version=version+1 WHERE id=%s RETURNING version',
                           [merged['username'],merged['display_name'],state,target])
            version=cursor.fetchone()[0]
            cursor.execute('DELETE FROM vdt.user_branch WHERE user_id=%s',[target])
            if not merged['active'] or merged['username']!=before['username'] or set(merged['branch_ids'])!=set(before['branch_ids']):
                if str(target)!=str(context.user.pk):
                    _revoke_sessions(cursor,target)
        else:
            cursor.execute('INSERT INTO vdt.app_user(id,organization_id,login_name,display_name,status) VALUES(%s,%s,%s,%s,%s)',
                           [target,org,merged['username'],merged['display_name'],state])
            version=1
        for branch_id in sorted(merged['branch_ids']):
            cursor.execute('INSERT INTO vdt.user_branch(id,user_id,branch_id) VALUES(%s,%s,%s)',[uuid.uuid4(),target,branch_id])
        _usable_admin_exists(cursor,org)
        auth.bump_guard(cursor,org)
        state_snapshot={'id':str(target),'username':merged['username'],'display_name':merged['display_name'],
                        'active':merged['active'],'branch_ids':sorted(merged['branch_ids']),'version':version}
        _history(cursor,context,scope_id,'user',target,version,state_snapshot)
        _audit(cursor,request,context,scope_id,'user.update' if before else 'user.create','user',target,
               before=before['version'] if before else None,after=version,reason=body['write_context']['reason'])
        result=user_dto(cursor,target,org)
        return Reply(result,200 if before else 201,f'"{version}"',None if before else f'/api/v1/users/{target}')
    return execute(request,'users.manage',write,body=body,expected=expected)


@sensitive_variables()
def reset_credential(request, user_id, body, expected):
    def write(cursor,context,scope_id):
        row=_lock_user(cursor,user_id,context.user.organization_id)
        assert_version(row[1],expected)
        _dependencies(cursor,context.user.organization_id,body,{})
        if str(user_id)==str(context.user.pk):
            fail('SELF_LOCKOUT',409,'Hãy dùng chức năng đổi mật khẩu cá nhân cho tài khoản đang dùng.')
        try:
            validate_password(body['temporary_password'],user=AppUser(id=user_id))
        except ValidationError:
            fail('PASSWORD_POLICY_REJECTED',422,'Mật khẩu tạm thời cần ít nhất 12 ký tự, không phổ biến và không chỉ gồm số.')
        encoded=make_password(body['temporary_password'])
        cursor.execute('UPDATE vdt.app_user SET password_hash=%s,password_change_required=true,version=version+1 WHERE id=%s RETURNING version',[encoded,user_id])
        version=cursor.fetchone()[0]
        _revoke_sessions(cursor,user_id)
        _usable_admin_exists(cursor,context.user.organization_id)
        auth.bump_guard(cursor,context.user.organization_id)
        public_state=user_dto(cursor,user_id,context.user.organization_id)
        public_state.pop('updated_at')
        public_state.pop('updated_by')
        public_state['password_change_required']=True
        _history(cursor,context,scope_id,'user',user_id,version,public_state)
        _audit(cursor,request,context,scope_id,'user.credential_reset','user',user_id,before=row[1],after=version,reason=body['write_context']['reason'])
        return Reply(status=204)
    return execute(request,'users.manage',write,body=body,expected=expected)


def _validate_scope(cursor,context,body,role_code):
    scope=body['scope']
    org=str(context.user.organization_id)
    if scope['organization_id']!=org:
        fail('INVALID_SCOPE',422,'Phạm vi phải thuộc tổ chức hiện tại.')
    populated=any(scope[key] for key in DIMENSIONS)
    if role_code=='VDT_ADMIN' and populated:
        fail('ADMIN_SCOPE_UNSUPPORTED',422,'Quản trị viên trong phiên bản này dùng phạm vi tổ chức.')
    if role_code!='VDT_ADMIN' and not populated:
        fail('SCOPE_REQUIRED',422,'Vai trò nghiệp vụ cần phạm vi được chọn rõ ràng.')
    _branches(cursor,org,scope['branch_ids'])
    dependencies={}
    for key,(table,_) in OBJECTS.items():
        for entity_id in sorted(scope[key]):
            cursor.execute(f'SELECT version,api_payload FROM vdt.{table} WHERE id=%s FOR UPDATE',[entity_id])
            row=cursor.fetchone()
            if not row:
                fail('INVALID_SCOPE',422,'Đối tượng trong phạm vi không tồn tại.')
            # A future inventory adapter must have materialized authoritative
            # object scope before it may be used for administration delegation.
            actual=json_object(row[1]).get('scope')
            if not schema_validator('Scope').is_valid(actual) or actual['organization_id']!=org:
                fail('SCOPE_RESOLUTION_UNAVAILABLE',422,'Đối tượng chưa có phạm vi đã xác thực để cấp quyền.')
            for dimension in DIMENSIONS:
                # The object's own identifier is authoritative for its own
                # dimension. Every other requested dimension needs explicit,
                # nonempty membership from the materialized inventory scope.
                # An absent/empty selector must never silently mean wildcard.
                if dimension!=key and scope[dimension] and (
                        not actual[dimension] or not set(actual[dimension])<=set(scope[dimension])):
                    fail('INVALID_SCOPE',422,'Các chiều phạm vi không giao nhau hợp lệ.')
            if key in ('scenario_ids','assessment_ids'):
                dependencies[('scenario' if key=='scenario_ids' else 'assessment',entity_id)]=row[0]
    assigned=set(body['assigned_assessment_ids'])
    if role_code=='VDT_REVIEWER':
        if not assigned or assigned!=set(scope['assessment_ids']) or body['access_expires_at'] is None:
            fail('REVIEWER_ASSIGNMENT_REQUIRED',422,'Reviewer cần đợt đánh giá cụ thể và thời hạn truy cập.')
    elif assigned:
        fail('INVALID_INPUT',422,'Chỉ vai trò Reviewer có danh sách đánh giá được giao.')
    return scope,dependencies


def grant(request,body):
    def write(cursor,context,parent_scope):
        org=context.user.organization_id
        user=_lock_user(cursor,body['user_id'],org)
        cursor.execute('SELECT code FROM vdt.role WHERE id=%s',[body['role_id']])
        role=cursor.fetchone()
        if not role:
            fail('INVALID_INPUT',422,'Vai trò không tồn tại.')
        scope,dependencies=_validate_scope(cursor,context,body,role[0])
        dependencies[('user',body['user_id'])]=user[1]
        _dependencies(cursor,org,body,dependencies)
        effective=timestamp(body['effective_at'])
        expiry=timestamp(body['access_expires_at']) if body['access_expires_at'] else None
        now=auth.db_now(cursor)
        if expiry and (expiry<=effective or expiry<=now):
            fail('INVALID_INPUT',422,'Hạn truy cập phải sau thời điểm hiệu lực và thời điểm hiện tại.')
        # One authority grant must cover the full lifetime; do not union grants.
        _,authorities=_authorized(cursor,request,'roles.assign')
        if not any(limit is None or (expiry is not None and expiry<=limit) for _,_,limit in authorities):
            fail('DELEGATION_EXPIRES',403,'Không thể cấp quyền dài hơn thời hạn quản trị hiện tại.')
        scope_id,assignment_id=uuid.uuid4(),uuid.uuid4()
        scope_kind='SELECTED' if any(scope[k] for k in DIMENSIONS) else 'ORGANIZATION'
        description='Explicit access administration scope'
        digest=hashlib.sha256(canonical({'scope_kind':scope_kind,'description':description,'selectors':scope}).encode()).hexdigest()
        cursor.execute('INSERT INTO vdt.scope(id,organization_id,scope_kind,description,content_hash) VALUES(%s,%s,%s,%s,%s)',[scope_id,org,scope_kind,description,digest])
        for branch_id in sorted(scope['branch_ids']):
            cursor.execute('INSERT INTO vdt.scope_branch(id,scope_id,branch_id) VALUES(%s,%s,%s)',[uuid.uuid4(),scope_id,branch_id])
        for dimension,(_,column) in OBJECTS.items():
            for entity_id in sorted(scope[dimension]):
                cursor.execute(f'INSERT INTO vdt.scope_object(id,scope_id,{column}) VALUES(%s,%s,%s)',[uuid.uuid4(),scope_id,entity_id])
        cursor.execute('''INSERT INTO vdt.role_assignment(id,user_id,role_id,scope_id,valid_from,access_expires_at,granted_by)
            VALUES(%s,%s,%s,%s,%s,%s,%s)''',[assignment_id,user[0],body['role_id'],scope_id,effective,expiry,context.user.pk])
        for assessment_id in sorted(body['assigned_assessment_ids']):
            cursor.execute('INSERT INTO vdt.assignment_assessment(id,assignment_id,assessment_id) VALUES(%s,%s,%s)',[uuid.uuid4(),assignment_id,assessment_id])
        auth.bump_guard(cursor,org)
        _history(cursor,context,parent_scope,'role_assignment',assignment_id,1,{'id':str(assignment_id),**{k:v for k,v in body.items() if k!='write_context'},'version':1,'revoked_at':None})
        _audit(cursor,request,context,parent_scope,'role_assignment.grant','role_assignment',assignment_id,after=1,reason=body['write_context']['reason'])
        return Reply(assignment_dto(cursor,assignment_id,org),201,'"1"',f'/api/v1/role-assignments/{assignment_id}')
    return execute(request,'roles.assign',write,body=body)


def revoke(request,assignment_id,body,expected):
    def write(cursor,context,parent_scope):
        current=assignment_dto(cursor,assignment_id,context.user.organization_id)
        cursor.execute('SELECT version FROM vdt.role_assignment WHERE id=%s FOR UPDATE',[assignment_id])
        assert_version(cursor.fetchone()[0],expected)
        user=_lock_user(cursor,current['user_id'],context.user.organization_id)
        _dependencies(cursor,context.user.organization_id,body,{('user',current['user_id']):user[1]})
        if current['revoked_at']:
            fail('ALREADY_REVOKED',409,'Quyền này đã được thu hồi.')
        cursor.execute('UPDATE vdt.role_assignment SET revoked_at=clock_timestamp(),version=version+1 WHERE id=%s RETURNING version',[assignment_id])
        version=cursor.fetchone()[0]
        _usable_admin_exists(cursor,context.user.organization_id)
        auth.bump_guard(cursor,context.user.organization_id)
        public_state=assignment_dto(cursor,assignment_id,context.user.organization_id)
        public_state.pop('updated_at')
        public_state.pop('updated_by')
        _history(cursor,context,parent_scope,'role_assignment',assignment_id,version,public_state)
        _audit(cursor,request,context,parent_scope,'role_assignment.revoke','role_assignment',assignment_id,before=current['version'],after=version,reason=body['write_context']['reason'])
        return Reply(assignment_dto(cursor,assignment_id,context.user.organization_id),201,f'"{version}"',f'/api/v1/role-assignments/{assignment_id}')
    return execute(request,'roles.assign',write,body=body,expected=expected)


def audit_events(request):
    def read(cursor,context,scope_id):
        cursor.execute('''SELECT a.id,a.recorded_at,a.actor_id,a.action,a.target_kind,a.target_id,a.outcome,a.reason_code,a.correlation_id,a.safe_metadata
            FROM vdt.audit_event a JOIN vdt.app_user u ON u.id=a.actor_id WHERE u.organization_id=%s''',[context.user.organization_id])
        rows=[{'id':str(r[0]),'created_at':iso(r[1]),'created_by':str(r[2]),'action':r[3],
               'target_type':r[4],'target_id':str(r[5]) if r[5] else None,'outcome':r[6],
               'reason_code':r[7],'request_id':str(r[8]),'before_version':json_object(r[9]).get('before_version'),
               'after_version':json_object(r[9]).get('after_version')} for r in cursor.fetchall()]
        return _page(request,rows,key=lambda row:row['created_at']+'|'+row['id'],descending=True)
    return execute(request,'organization.manage',read)
