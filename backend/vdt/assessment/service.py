"""First assessment worklist slice. The stored scope is authoritative for delegation."""
import uuid
from django.db import connection, transaction, IntegrityError
from vdt.authn import service as auth
from vdt.access import service as access
from vdt.access.validation import clean_text, fail, schema_validator


def _principal(cursor, request):
    binding = auth._locate_binding(request, cursor)
    if binding is None:
        fail('AUTHENTICATION_REQUIRED', 401, 'Vui lòng đăng nhập lại.')
    located, key = binding
    version = auth.guard(cursor, located[2])
    context = auth._context_locked(cursor, request, located, key, version)
    if context is None:
        fail('AUTHENTICATION_REQUIRED', 401, 'Vui lòng đăng nhập lại.')
    if context.user.password_change_required:
        fail('PASSWORD_CHANGE_REQUIRED', 403, 'Cần đổi mật khẩu tạm thời.')
    return context


def _grants(cursor, context, permission):
    now = auth.db_now(cursor)
    cursor.execute('''SELECT a.id,a.scope_id,a.access_expires_at FROM vdt.role_assignment a
        JOIN vdt.role_permission rp ON rp.role_id=a.role_id
        JOIN vdt.permission p ON p.id=rp.permission_id
        JOIN vdt.scope s ON s.id=a.scope_id
        WHERE a.user_id=%s AND p.code=%s AND s.organization_id=%s
        AND a.revoked_at IS NULL AND a.valid_from<=%s
        AND (a.access_expires_at IS NULL OR a.access_expires_at>%s)
        ORDER BY a.id''', [context.user.pk, permission, context.user.organization_id, now, now])
    return cursor.fetchall()


def _covers(cursor, grant, item_scope, item_id=None):
    grant_scope = access.scope_dto(cursor, grant[1])
    if grant_scope['organization_id'] != item_scope['organization_id']:
        return False
    # A populated selector constrains the whole object; no union of grants.
    for dimension in access.DIMENSIONS:
        selected = grant_scope[dimension]
        if not selected:
            continue
        if dimension == 'assessment_ids':
            if item_id is None or item_id not in selected:
                return False
            cursor.execute('SELECT 1 FROM vdt.assignment_assessment WHERE assignment_id=%s AND assessment_id=%s', [grant[0], item_id])
            if cursor.fetchone() is None:
                return False
        elif not item_scope[dimension] or not set(item_scope[dimension]) <= set(selected):
            return False
    return True


def _dto(cursor, assessment_id):
    cursor.execute('SELECT id,code,version,api_payload FROM vdt.assessment WHERE id=%s', [assessment_id])
    row = cursor.fetchone()
    if not row:
        fail('NOT_FOUND', 404, 'Không tìm thấy đợt đánh giá.')
    data = access.json_object(row[3])
    if not schema_validator('Assessment').is_valid(data) or data['id'] != str(row[0]) or data['code'] != row[1] or data['version'] != row[2]:
        fail('STORED_DATA_INVALID', 503, 'Dữ liệu đánh giá chưa sẵn sàng.')
    return data


def _run(request, operation):
    try:
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout='5s'")
            cursor.execute("SET LOCAL statement_timeout='20s'")
            context = _principal(cursor, request)
            reply = operation(cursor, context)
            _principal(cursor, request)
            return reply
    except IntegrityError:
        fail('STATE_CONFLICT', 409, 'Mã đợt đánh giá đã tồn tại hoặc dữ liệu liên quan đã thay đổi.')


def _display_context(cursor, context, data):
    """Labels for one already-authorized assessment, without widening branch access."""
    cursor.execute('''SELECT id,code,name,active FROM vdt.branch
        WHERE organization_id=%s AND id=ANY(%s::uuid[]) ORDER BY name,id''',
        [context.user.organization_id,data['scope']['branch_ids']])
    branches = [{'id':str(row[0]),'code':row[1],'name':row[2],'active':row[3]} for row in cursor.fetchall()]
    if {row['id'] for row in branches} != set(data['scope']['branch_ids']):
        fail('STORED_DATA_INVALID',503,'Chưa xác định được tên chi nhánh của đợt đánh giá.')
    # Recheck after resolving labels. Reviewer labels are restricted to exact
    # assigned assessments, not the global branch directory or user profile.
    allowed = {permission:[g for g in _grants(cursor,context,permission)
                           if _covers(cursor,g,data['scope'],data['id'])]
               for permission in ('assessment.run','assessment.review','report.read')}
    if not any(allowed.values()):
        fail('PERMISSION_DENIED',403,'Quyền xem đợt đánh giá đã hết hiệu lực.')
    review_limits = [g[2] for g in allowed['assessment.review']]
    review_expiry = (access.iso(max(review_limits)) if review_limits and all(review_limits) else None)
    return {'id':data['id'],'branches':branches,
            'access_permissions':[code for code,grants in allowed.items() if grants],
            'review_access_expires_at':review_expiry}


def assessments(request, assessment_id=None, *, display_context=False):
    def read(cursor, context):
        def current_grants():
            return [g for code in ('assessment.run','assessment.review','report.read') for g in _grants(cursor,context,code)]
        grants = current_grants()
        if not grants:
            fail('PERMISSION_DENIED', 403, 'Tài khoản chưa có quyền xem đợt đánh giá.')
        if assessment_id:
            data = _dto(cursor, assessment_id)
            if not any(_covers(cursor, g, data['scope'], assessment_id) for g in grants):
                fail('NOT_FOUND', 404, 'Không tìm thấy đợt đánh giá trong phạm vi được cấp.')
            final = next((g for g in current_grants() if _covers(cursor,g,data['scope'],assessment_id)),None)
            if final is None:
                fail('PERMISSION_DENIED',403,'Quyền xem đợt đánh giá đã hết hiệu lực.')
            access._audit(cursor,request,context,final[1],'assessment.read','assessment',assessment_id)
            if display_context:
                return access.Reply(_display_context(cursor,context,data))
            return access.Reply(data, etag=f'"{data["version"]}"')
        cursor.execute('SELECT id FROM vdt.assessment ORDER BY id')
        rows = []
        for (item_id,) in cursor.fetchall():
            data = _dto(cursor, item_id)
            if any(_covers(cursor, g, data['scope'], str(item_id)) for g in grants):
                rows.append(data)
        final_grants = current_grants()
        if not final_grants:
            fail('PERMISSION_DENIED',403,'Quyền xem đợt đánh giá đã hết hiệu lực.')
        rows = [data for data in rows if any(_covers(cursor,g,data['scope'],data['id']) for g in final_grants)]
        access._audit(cursor,request,context,final_grants[0][1],'assessment.list','assessment',None)
        if display_context:
            rows = [_display_context(cursor,context,data) for data in rows]
        return access._page(request, rows)
    return _run(request, read)


def create(request, body):
    def write(cursor, context):
        org = str(context.user.organization_id)
        scope = body['scope']
        if scope['organization_id'] != org or not scope['branch_ids'] or any(scope[key] for key in access.DIMENSIONS if key != 'branch_ids'):
            fail('INVALID_SCOPE', 422, 'Đợt đánh giá ban đầu cần chi nhánh cụ thể, chưa gắn đối tượng khác.')
        access._branches(cursor, org, scope['branch_ids'])
        if body['scenario_ids']:
            fail('DEPENDENCY_REQUIRED', 428, 'Cần tạo và xác thực kịch bản trước khi gắn vào đợt đánh giá.')
        access._dependencies(cursor, org, body, {})
        clean_text(body['code'],128); clean_text(body['name']); clean_text(body['write_context']['reason'])
        grants = _grants(cursor, context, 'assessment.run')
        grant = next((g for g in grants if _covers(cursor, g, scope)), None)
        if grant is None:
            fail('PERMISSION_DENIED', 403, 'Chưa được cấp quyền đánh giá cho chi nhánh này.')
        operation_id, replay = access._ledger(cursor, request, context, body, None)
        if replay:
            return replay
        item_id = uuid.uuid4()
        data = {'id':str(item_id),'version':1,'updated_at':access.iso(auth.db_now(cursor)),
                'updated_by':str(context.user.pk),'code':body['code'],'name':body['name'],
                'scenario_ids':[],'scope':scope,'state':'OPEN'}
        cursor.execute('''INSERT INTO vdt.assessment(id,code,owner_id,workflow_state,api_payload)
            VALUES(%s,%s,%s,'OPEN',%s::jsonb)''',[item_id,body['code'],context.user.pk,access.canonical(data)])
        access._history(cursor,context,grant[1],'assessment',item_id,1,data)
        access._audit(cursor,request,context,grant[1],'assessment.create','assessment',item_id,
                      after=1,reason=body['write_context']['reason'])
        # Check the same grant again before committing; a revoked/expired grant cannot commit.
        if not any(g[0] == grant[0] and _covers(cursor,g,scope) for g in _grants(cursor,context,'assessment.run')):
            fail('PERMISSION_DENIED',403,'Quyền đánh giá đã hết hiệu lực.')
        reply = access.Reply(data,201,'"1"',f'/api/v1/assessments/{item_id}')
        access._complete(cursor,operation_id,reply)
        return reply
    return _run(request,write)


def assignment_catalog(request):
    """Administrative selector list; detailed assessment content stays protected."""
    def read(cursor, context, _scope):
        cursor.execute('SELECT id FROM vdt.assessment ORDER BY id')
        items = []
        for (item_id,) in cursor.fetchall():
            data = _dto(cursor,item_id)
            if data['scope']['organization_id'] == str(context.user.organization_id):
                items.append({k:data[k] for k in ('id','code','name','version','scope','state')})
        return access._page(request,items)
    return access.execute(request,'roles.assign',read)


def setup(request):
    """Minimal assessment-run form data, limited to eligible branches."""
    def read(cursor,context):
        grants = _grants(cursor,context,'assessment.run')
        if not grants:
            fail('PERMISSION_DENIED',403,'Chưa có quyền tạo đợt đánh giá.')
        allowed = set()
        for grant in grants:
            scope = access.scope_dto(cursor,grant[1])
            allowed.update(scope['branch_ids'])
        cursor.execute('SELECT id,code,name,version FROM vdt.organization WHERE id=%s',[context.user.organization_id])
        org = cursor.fetchone()
        cursor.execute('SELECT id,name FROM vdt.branch WHERE organization_id=%s AND active ORDER BY name',[org[0]])
        branches = [{'id':str(row[0]),'name':row[1]} for row in cursor.fetchall() if str(row[0]) in allowed]
        if not _grants(cursor,context,'assessment.run'):
            fail('PERMISSION_DENIED',403,'Quyền tạo đợt đánh giá đã hết hiệu lực.')
        return access.Reply({'organization':{'id':str(org[0]),'version':org[3]},'branches':branches})
    return _run(request,read)
