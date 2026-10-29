"""Disposable PostgreSQL tests for user/role administration. Never run on lab DB.

HTTP requests use vdt_app credentials. Owner access only sets up synthetic data
and injects expiry faults. Public JSON never includes credentials or tracebacks.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import secrets
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
sys.path.insert(0, str(Path(__file__).resolve().parent))


class CheckFailure(Exception):
    pass


def require(ok, label):
    if not ok:
        raise CheckFailure(label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--browser-fixture-output', type=Path)
    args = parser.parse_args()
    expected = {'VDT_AUTH_INTEGRATION_TEST': 'true', 'VDT_LOCAL_FOUNDATION_ONLY': 'true',
                'PGHOST': 'testdb', 'PGDATABASE': 'vdt_step06', 'PGUSER': 'vdt_owner'}
    if any(os.environ.get(k) != v for k, v in expected.items()):
        raise SystemExit('Refused: isolated testdb and explicit local/integration opt-in required.')
    if args.browser_fixture_output and (args.browser_fixture_output.parent != Path('/reports') or args.browser_fixture_output.name != 'access-browser-fixture.json'):
        raise SystemExit('Refused: browser fixture must be /reports/access-browser-fixture.json, never a public report.')
    import psycopg
    import database
    checks, owner = [], None

    def record(name, work):
        try:
            work()
        except CheckFailure as error:
            checks.append({'check': name, 'passed': False, 'detail': str(error)})
        except Exception as error:
            checks.append({'check': name, 'passed': False, 'detail': type(error).__name__})
        else:
            checks.append({'check': name, 'passed': True})

    def result(setup_error=None):
        report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
                  'scope': 'DISPOSABLE_POSTGRESQL_ACCESS_ADMINISTRATION_HTTP',
                  'database_host': 'testdb', 'http_database_role': 'vdt_app',
                  'synthetic_account_only': True, 'actual_browser_TLS': 'NOT_RUN',
                  'CRM_FLOW_TC_VALID_G': 'NOT_RUN', 'checks': checks,
                  'passed': sum(c['passed'] for c in checks), 'failed': sum(not c['passed'] for c in checks)}
        if setup_error:
            report['setup_error'] = setup_error
            report['failed'] += 1
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded, encoding='utf-8')
        print(encoded)
        return bool(report['failed'])

    try:
        params = database.parameters()
        owner = psycopg.connect(**params, autocommit=True)
        existing = owner.execute("SELECT to_regclass('vdt.app_user')").fetchone()[0]
        if existing and owner.execute('SELECT EXISTS(SELECT 1 FROM vdt.app_user)').fetchone()[0]:
            raise CheckFailure('Test database contains accounts; recreate only disposable testdb.')
        database.migrate(params)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vdt.settings')
        import django
        django.setup()
        from django.conf import settings
        from django.core.management import call_command
        from django.contrib.auth.hashers import check_password
        from django.db import connection, connections
        from django.test import Client
        from vdt.core.local_bootstrap import provision_admin
        import yaml
        from jsonschema import Draft202012Validator, FormatChecker
        call_command('seed_rbac_catalog', stdout=io.StringIO())
        secret_values = []

        def password():
            value = secrets.token_urlsafe(36) + '-9X'
            secret_values.append(value)
            return value

        admin_password = password()
        first = provision_admin(username='synthetic-access-admin', display_name='Synthetic access administrator', password=admin_password)
        org_id, admin_id = first.organization_id, first.user_id
        connection.close()
        connection.settings_dict['USER'] = 'vdt_app'
        connection.settings_dict['PASSWORD'] = os.environ['VDT_DB_APP_PASSWORD']
        with connection.cursor() as cursor:
            cursor.execute('SELECT current_user,rolsuper FROM pg_roles WHERE rolname=current_user')
            runtime_identity = cursor.fetchone()
        record('HTTP uses restricted vdt_app database login', lambda: require(runtime_identity == ('vdt_app', False), 'Unexpected runtime identity.'))
        contract = yaml.safe_load((ROOT / 'docs/design/openapi-v0.1.yaml').read_text(encoding='utf-8'))
        secret_values.extend([settings.VDT_AUTH_PROXY_SECRET, settings.SECRET_KEY, os.environ['VDT_DB_APP_PASSWORD'], os.environ['PGPASSWORD']])

        def validate(data, name):
            Draft202012Validator({'$ref': '#/components/schemas/' + name, 'components': contract['components']}, format_checker=FormatChecker()).validate(data)

        def headers():
            return {'HTTP_HOST': 'localhost:8443', 'HTTP_ORIGIN': 'https://localhost:8443',
                    'HTTP_X_VDT_PROXY_SECRET': settings.VDT_AUTH_PROXY_SECRET, 'HTTP_X_VDT_CLIENT_IP': '198.51.100.20'}

        def client():
            return Client(enforce_csrf_checks=True, raise_request_exception=False)

        def get(c, path):
            return c.get(path, secure=True, **headers())

        def csrf(c):
            response = get(c, '/api/v1/auth/csrf')
            require(response.status_code == 200, 'CSRF endpoint failed.')
            token = response.json()['csrf_token']
            secret_values.append(token)
            return token

        def mutate(c, path, payload, *, method='post', key=None, match=None, include_key=True, include_csrf=True, raw=None):
            options = headers()
            if include_csrf:
                options['HTTP_X_CSRFTOKEN'] = csrf(c)
            if include_key:
                options['HTTP_IDEMPOTENCY_KEY'] = str(key or uuid4())
            if match is not None:
                options['HTTP_IF_MATCH'] = match
            return getattr(c, method)(path, data=json.dumps(payload) if raw is None else raw, content_type='application/json', secure=True, **options)

        def expect(response, status, label):
            require(response.status_code == status, label + f' (HTTP {response.status_code}, expected {status}).')
            if status >= 400:
                validate(response.json(), 'Problem')
            return response

        def login(name, secret):
            c = client()
            response = expect(mutate(c, '/api/v1/auth/session', {'username': name, 'password': secret}, include_key=False), 200, 'Synthetic login failed')
            validate(response.json(), 'Session')
            secret_values.extend([c.cookies[settings.SESSION_COOKIE_NAME].value, response.json()['csrf_token']])
            return c, response

        admin, _ = login('synthetic-access-admin', admin_password)
        branches = owner.execute('SELECT id FROM vdt.branch ORDER BY code').fetchall()
        branch_a, branch_b = map(str, (branches[0][0], branches[1][0]))
        roles = dict(owner.execute('SELECT code,id FROM vdt.role').fetchall())

        def dep(kind, identity):
            table = {'organization': 'organization', 'user': 'app_user', 'role_assignment': 'role_assignment'}[kind]
            version = owner.execute(f'SELECT version FROM vdt.{table} WHERE id=%s', (identity,)).fetchone()[0]
            return {'resource_type': kind, 'id': str(identity), 'version': version}

        def context(user_id=None):
            dependencies = [dep('organization', org_id)]
            if user_id:
                dependencies.append(dep('user', user_id))
            return {'dependencies': dependencies, 'reason': 'Synthetic isolated verification'}

        def scope(branch_ids=None, **overrides):
            data = {'organization_id': org_id, 'branch_ids': branch_ids or [], 'system_ids': [], 'asset_ids': [],
                    'data_asset_ids': [], 'scenario_ids': [], 'assessment_ids': []}
            data.update(overrides)
            return data

        counter = 0

        def user_payload(branch_ids=None):
            nonlocal counter
            counter += 1
            return {'username': f'synthetic-person-{counter}', 'display_name': f'Synthetic person {counter}',
                    'active': True, 'branch_ids': branch_ids or [], 'write_context': context()}

        def create_user(branch_ids=None, actor=None):
            response = expect(mutate(actor or admin, '/api/v1/users', user_payload(branch_ids)), 201, 'User creation failed')
            validate(response.json(), 'User')
            require(response['Location'].endswith(response.json()['id']), 'Creation Location mismatch.')
            require(response['ETag'] == '"' + str(response.json()['version']) + '"', 'Version ETag mismatch.')
            return response.json()

        def current(user_id):
            response = expect(get(admin, '/api/v1/users/' + user_id), 200, 'User read failed')
            validate(response.json(), 'User')
            return response.json(), response['ETag']

        def credential(user_id, secret):
            _, etag = current(user_id)
            return mutate(admin, f'/api/v1/users/{user_id}/credential-resets',
                {'temporary_password': secret, 'force_change': True, 'write_context': context()}, match=etag)

        def ready_user(branch_ids=None):
            user = create_user(branch_ids)
            temporary, final_password = password(), password()
            expect(credential(user['id'], temporary), 204, 'Credential initialization failed')
            c, response = login(user['username'], temporary)
            require(response.get('X-VDT-Password-Change-Required') == 'true', 'Forced-change header missing.')
            require(response.json()['permissions'] == [], 'Temporary session exposes permissions.')
            expect(mutate(c, '/api/v1/auth/password', {'current_password': temporary, 'new_password': final_password}, include_key=False), 204, 'Required password change failed')
            return user, c, final_password

        def grant_payload(user_id, role='VDT_ADMIN', selected=None, effective=None, expiry=None, assigned=None):
            return {'user_id': user_id, 'role_id': str(roles[role]), 'scope': selected if selected is not None else scope(),
                    'assigned_assessment_ids': assigned or [],
                    'effective_at': (effective or datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat(),
                    'access_expires_at': expiry.isoformat() if expiry else None, 'write_context': context(user_id)}

        def grant(user_id, actor=None, **kwargs):
            response = expect(mutate(actor or admin, '/api/v1/role-assignments', grant_payload(user_id, **kwargs)), 201, 'Role assignment failed')
            validate(response.json(), 'RoleAssignment')
            return response.json()

        def revoke(assignment):
            response = expect(get(admin, '/api/v1/role-assignments/' + assignment['id']), 200, 'Assignment read failed')
            return mutate(admin, '/api/v1/role-assignments/' + assignment['id'] + '/revocations',
                {'write_context': context(assignment['user_id'])}, match=response['ETag'])

        def guarded(query, values):
            with owner.transaction():
                owner.execute('SELECT vdt.acquire_authorization_guard(%s)', (org_id,))
                owner.execute(query, values)
                owner.execute('UPDATE vdt.authorization_guard SET version=version+1 WHERE organization_id=%s', (org_id,))

        def catalogs():
            for route, schema, count in [('/organization','Organization',None),('/branches','BranchPage',2),('/roles','RolePage',4),('/permissions','PermissionPage',19)]:
                response = expect(get(admin, '/api/v1' + route), 200, 'Catalog read failed')
                validate(response.json(), schema)
                require(response['Cache-Control'] == 'no-store', 'Private catalog cache enabled.')
                if count is not None:
                    require(len(response.json()['items']) == count, 'Catalog count mismatch.')
                if schema == 'RolePage':
                    codes = {role['code']: set(role['permission_codes']) for role in response.json()['items']}
                    for role in ('VDT_SECURITY', 'VDT_REVIEWER'):
                        require({'evidence.verify', 'evidence.read_assigned'} <= codes[role], 'Evidence permission seed differs from architecture.')
                    require('risk.priority_approve' in codes['VDT_RISK_OWNER'], 'Risk approval permission seed differs from architecture.')
        record('Organization, branch and role catalogs conform to frozen DTOs', catalogs)
        record('Anonymous administration requests return 401', lambda: expect(get(client(), '/api/v1/users'), 401, 'Anonymous list exposed'))

        def edit_user():
            user = create_user([branch_a])
            _, etag = current(user['id'])
            response = expect(mutate(admin, '/api/v1/users/' + user['id'], {'display_name':'Changed display','branch_ids':[branch_b],'write_context':context()}, method='patch', match=etag), 200, 'Edit failed')
            validate(response.json(), 'User')
            require(response.json()['version'] == user['version'] + 1 and response.json()['branch_ids'] == [branch_b], 'User aggregate replacement failed.')
        record('User edit replaces branch membership and increments aggregate version', edit_user)

        def strict_inputs():
            payload = user_payload()
            expect(mutate(admin, '/api/v1/users', dict(payload, unexpected=True)), 422, 'Unknown property accepted')
            expect(mutate(admin, '/api/v1/users', payload, raw='{"username":"a","username":"b"}'), 400, 'Duplicate JSON accepted')
            expect(mutate(admin, '/api/v1/users', dict(payload, active='true')), 422, 'String boolean accepted')
            expect(mutate(admin, '/api/v1/users', payload, include_csrf=False), 403, 'Missing CSRF accepted')
        record('Closed JSON validation and CSRF reject malformed writes', strict_inputs)

        def preconditions():
            payload = user_payload()
            expect(mutate(admin, '/api/v1/users', payload, include_key=False), 428, 'Missing idempotency key accepted')
            payload['write_context']['dependencies'] = []
            expect(mutate(admin, '/api/v1/users', payload), 428, 'Missing organization dependency accepted')
            user = create_user()
            expect(mutate(admin, '/api/v1/users/' + user['id'], {'display_name':'Changed','write_context':context()}, method='patch'), 428, 'Missing If-Match accepted')
        record('Idempotency, dependency and If-Match preconditions are required', preconditions)

        def stale_versions():
            payload = user_payload()
            payload['write_context']['dependencies'][0]['version'] += 1
            expect(mutate(admin, '/api/v1/users', payload), 409, 'Changed dependency accepted')
            user = create_user()
            expect(mutate(admin, '/api/v1/users/' + user['id'], {'display_name':'Changed','write_context':context()}, method='patch', match='"999999"'), 412, 'Stale If-Match accepted')
        record('Stale dependencies and aggregate versions cannot overwrite state', stale_versions)

        def idempotency():
            payload, key = user_payload(), str(uuid4())
            initial = expect(mutate(admin, '/api/v1/users', payload, key=key), 201, 'Initial creation failed')
            replay = expect(mutate(admin, '/api/v1/users', payload, key=key), 201, 'Replay failed')
            require(initial.json() == replay.json(), 'Replay representation changed.')
            require(owner.execute('SELECT count(*) FROM vdt.app_user WHERE login_name=%s',(payload['username'],)).fetchone()[0] == 1, 'Replay duplicated user.')
            expect(mutate(admin, '/api/v1/users', dict(payload, display_name='Different body'), key=key), 409, 'Same key accepted different body')
        record('Idempotent creation replays original result and rejects payload conflict', idempotency)

        def pagination():
            response = expect(get(admin, '/api/v1/users?limit=1'), 200, 'Pagination failed')
            validate(response.json(), 'UserPage')
            require(len(response.json()['items']) == 1 and response.json()['next_cursor'], 'Missing cursor.')
            from urllib.parse import quote
            second = expect(get(admin, '/api/v1/users?limit=1&cursor=' + quote(response.json()['next_cursor'],safe='')), 200, 'Next page failed')
            validate(second.json(), 'UserPage')
            require(second.json()['items'][0]['id'] != response.json()['items'][0]['id'], 'Cursor repeated first user.')
        record('User pagination returns closed Page DTO and advances opaque cursor', pagination)

        def temporary_credentials():
            user = create_user()
            temporary, changed = password(), password()
            expect(credential(user['id'], temporary), 204, 'Credential setup failed')
            c, response = login(user['username'], temporary)
            require(response.get('X-VDT-Password-Change-Required') == 'true' and response.json()['permissions'] == [], 'Temporary session unrestricted.')
            denied = expect(get(c, '/api/v1/users'), 403, 'Forced-change restriction bypassed')
            require(denied.json()['code'] == 'PASSWORD_CHANGE_REQUIRED', 'Wrong forced-change response.')
            expect(mutate(c, '/api/v1/auth/password', {'current_password':temporary,'new_password':changed}, include_key=False), 204, 'Password change failed')
            value = owner.execute('SELECT password_hash,password_change_required FROM vdt.app_user WHERE id=%s',(user['id'],)).fetchone()
            require(check_password(changed,value[0]) and not value[1], 'Credential requirement did not clear atomically.')
            expect(get(c, '/api/v1/users'), 403, 'Password change implicitly granted rights')
        record('Temporary passwords force a change without granting implicit rights', temporary_credentials)

        def reset_revokes():
            user, c1, permanent = ready_user()
            c2, _ = login(user['username'], permanent)
            expect(credential(user['id'], password()), 204, 'Reset failed')
            for c in (c1,c2):
                expect(get(c,'/api/v1/auth/session'),401,'Reset retained old session')
            require(owner.execute('SELECT count(*) FROM vdt.vdt_session WHERE user_id=%s AND revoked_at IS NULL',(user['id'],)).fetchone()[0] == 0, 'Active binding survived reset.')
        record('Administrative credential reset revokes every target session', reset_revokes)

        def disable_revokes():
            user, c, _ = ready_user()
            _, etag = current(user['id'])
            expect(mutate(admin, '/api/v1/users/' + user['id'], {'active':False,'write_context':context()}, method='patch', match=etag),200,'Disable failed')
            expect(get(c,'/api/v1/auth/session'),401,'Disabled user retained session')
        record('Disabling a user invalidates their active session', disable_revokes)

        def security_scope():
            user,c,_ = ready_user([branch_a])
            assignment = grant(user['id'],role='VDT_SECURITY',selected=scope([branch_a]),expiry=datetime.now(timezone.utc)+timedelta(hours=2))
            require(assignment['scope']['branch_ids'] == [branch_a], 'Grant lost branch selector.')
            expect(get(c,'/api/v1/users'),403,'Security gained user administration')
            expect(get(c,'/api/v1/role-assignments'),403,'Security gained role administration')
            revoked = expect(revoke(assignment),201,'Scoped grant revoke failed')
            validate(revoked.json(), 'RoleAssignment')
            require(revoked.json()['revoked_at'] is not None, 'Revocation result lacks timestamp.')
        record('Scoped Security grants retain selectors without administration privileges', security_scope)

        def invalid_scopes():
            user = create_user([branch_a])
            expect(mutate(admin,'/api/v1/role-assignments',grant_payload(user['id'],role='VDT_SECURITY')),422,'Empty Security scope became wildcard')
            for selected in (scope([str(uuid4())]),scope([branch_a],organization_id=str(uuid4()))):
                response=mutate(admin,'/api/v1/role-assignments',grant_payload(user['id'],role='VDT_SECURITY',selected=selected))
                require(response.status_code in (403,404,422),'Unknown or foreign scope accepted.')
            expect(mutate(admin,'/api/v1/role-assignments',grant_payload(user['id'],role='VDT_REVIEWER',selected=scope([branch_a]))),422,'Unassigned/unbounded Reviewer accepted')
        record('Empty, nonexistent and foreign scopes fail closed; Reviewer requires assignments', invalid_scopes)

        def scope_intersection():
            user=create_user([branch_a])
            system_id,asset_id=str(uuid4()),str(uuid4())
            selected=scope([branch_a],system_ids=[system_id],asset_ids=[asset_id])
            # Owner setup is confined to this disposable database. Real rows
            # distinguish missing relationships from nonexistent UUID rejection.
            with owner.transaction():
                owner.execute('SELECT vdt.acquire_authorization_guard(%s)',(org_id,))
                owner.execute('''INSERT INTO vdt.information_system(id,code,name,purpose,api_payload)
                    VALUES(%s,%s,'Synthetic scope system','Isolated scope intersection test',%s::jsonb)''',
                    (system_id,'SCOPE-SYSTEM-'+system_id,json.dumps({'scope':scope([branch_a],system_ids=[system_id])})))
                owner.execute('''INSERT INTO vdt.asset(id,code,name,asset_type,branch_id,status,api_payload)
                    VALUES(%s,%s,'Synthetic scope asset','SERVER',%s,'ACTIVE',%s::jsonb)''',
                    (asset_id,'SCOPE-ASSET-'+asset_id,branch_a,json.dumps({'scope':selected})))
                owner.execute('UPDATE vdt.authorization_guard SET version=version+1 WHERE organization_id=%s',(org_id,))
            attempt=grant_payload(user['id'],role='VDT_SECURITY',selected=selected)
            denied=expect(mutate(admin,'/api/v1/role-assignments',attempt),422,'Missing system-to-asset linkage silently widened scope')
            require(denied.json()['code']=='INVALID_SCOPE','Missing linkage did not fail at scope intersection.')
            require(owner.execute('SELECT count(*) FROM vdt.role_assignment WHERE user_id=%s',(user['id'],)).fetchone()[0]==0,'Rejected intersection persisted assignment.')
            guarded('UPDATE vdt.information_system SET api_payload=%s::jsonb,version=version+1 WHERE id=%s',
                    (json.dumps({'scope':selected}),system_id))
            guarded('UPDATE vdt.asset SET api_payload=%s::jsonb,version=version+1 WHERE id=%s',
                    (json.dumps({'scope':{'branch_ids':[branch_a]}}),asset_id))
            malformed=expect(mutate(admin,'/api/v1/role-assignments',attempt),422,'Malformed materialized scope accepted')
            require(malformed.json()['code']=='SCOPE_RESOLUTION_UNAVAILABLE','Malformed scope did not fail closed.')
            require(owner.execute('SELECT count(*) FROM vdt.role_assignment WHERE user_id=%s',(user['id'],)).fetchone()[0]==0,'Malformed scope persisted assignment.')
            guarded('UPDATE vdt.asset SET api_payload=%s::jsonb,version=version+1 WHERE id=%s',
                    (json.dumps({'scope':selected}),asset_id))
            accepted=grant(user['id'],role='VDT_SECURITY',selected=selected)
            require(accepted['scope']==selected,'Proven scope intersection lost explicit selectors.')
        record('Real object scopes require complete proven intersections across every populated dimension',scope_intersection)

        def temporal_validation():
            user = create_user()
            now=datetime.now(timezone.utc)
            payload=grant_payload(user['id'],effective=now,expiry=now)
            expect(mutate(admin,'/api/v1/role-assignments',payload),422,'Equal start and expiry accepted')
            payload['effective_at']='2026-10-25T12:00:00'
            payload['access_expires_at']=None
            expect(mutate(admin,'/api/v1/role-assignments',payload),422,'Naive timestamp accepted')
        record('Grant timestamps require timezones and increasing validity bounds',temporal_validation)

        def bounded_admin_scope():
            user,c,_=ready_user([branch_a])
            expect(mutate(admin,'/api/v1/role-assignments',grant_payload(user['id'],selected=scope([branch_a]))),422,'Selected admin scope silently widened to organization')
            expect(get(c,'/api/v1/users'),403,'Rejected grant left administrative access')
            assignments=owner.execute('SELECT count(*) FROM vdt.role_assignment WHERE user_id=%s',(user['id'],)).fetchone()[0]
            require(assignments==0,'Rejected admin assignment was persisted.')
        record('Unsupported selected admin scope is rejected without widening or persisting rights',bounded_admin_scope)

        def fresh_authorization():
            user,c,_=ready_user()
            assignment=grant(user['id'])
            expect(get(c,'/api/v1/users'),200,'Fresh grant unrecognized')
            payload,key=user_payload(),str(uuid4())
            expect(mutate(c,'/api/v1/users',payload,key=key),201,'Delegated creation failed')
            expect(revoke(assignment),201,'Revoke failed')
            expect(get(c,'/api/v1/users'),403,'Revoked grant retained reads')
            expect(mutate(c,'/api/v1/users',payload,key=key),403,'Replay bypassed current authorization')
        record('Revocation removes access immediately including idempotent replay',fresh_authorization)

        def expired_grant():
            user,c,_=ready_user()
            assignment=grant(user['id'],expiry=datetime.now(timezone.utc)+timedelta(hours=1))
            guarded("UPDATE vdt.role_assignment SET valid_from=clock_timestamp()-interval '2 days',access_expires_at=clock_timestamp()-interval '1 second',version=version+1 WHERE id=%s",(assignment['id'],))
            expect(get(c,'/api/v1/users'),403,'Expired grant retained access')
        record('Expired administrative grants deny existing authenticated sessions',expired_grant)

        def bounded_delegation():
            actor,c,_=ready_user()
            now=datetime.now(timezone.utc)
            authority=grant(actor['id'],expiry=now+timedelta(hours=1))
            target=create_user()
            for expiry in (None,now+timedelta(hours=2)):
                denied=expect(mutate(c,'/api/v1/role-assignments',grant_payload(target['id'],expiry=expiry)),403,'Delegation exceeded administrative authority lifetime')
                require(denied.json()['code']=='DELEGATION_EXPIRES','Unexpected bounded-delegation denial.')
            require(owner.execute('SELECT count(*) FROM vdt.role_assignment WHERE user_id=%s',(target['id'],)).fetchone()[0]==0,'Rejected delegation persisted a grant.')
            assigned=grant(target['id'],actor=c,expiry=now+timedelta(minutes=30))
            require(datetime.fromisoformat(assigned['access_expires_at'])<=now+timedelta(hours=1),'Accepted delegation outlived its authority.')
            expect(revoke(authority),201,'Temporary authority cleanup failed')
        record('Temporary administrators cannot delegate indefinite or overlong access',bounded_delegation)

        def self_protection():
            _,etag=current(admin_id)
            expect(mutate(admin,'/api/v1/users/'+admin_id,{'active':False,'write_context':context()},method='patch',match=etag),409,'Administrator disabled self')
            expect(credential(admin_id,password()),409,'Administrator reset own credentials through management endpoint')
            own=expect(get(admin,'/api/v1/role-assignments/'+first.assignment_id),200,'Bootstrap grant unavailable').json()
            expect(revoke(own),409,'Administrator revoked sole own grant')
            expect(get(admin,'/api/v1/users'),200,'Rejected self-lockout changed access')
        record('Self-disable, self credential reset and loss of last ready admin are rejected atomically',self_protection)

        def concurrent_occ():
            user=create_user()
            _,etag=current(user['id'])
            sessions=[login('synthetic-access-admin',admin_password)[0] for _ in range(2)]
            tokens=[csrf(c) for c in sessions]
            payloads=[{'display_name':f'Concurrent edit {i}','write_context':context()} for i in range(2)]
            def attempt(i):
                worker=connections['default']
                worker.settings_dict['USER']='vdt_app'
                worker.settings_dict['PASSWORD']=os.environ['VDT_DB_APP_PASSWORD']
                try:
                    options=dict(headers(),HTTP_X_CSRFTOKEN=tokens[i],HTTP_IDEMPOTENCY_KEY=str(uuid4()),HTTP_IF_MATCH=etag)
                    return sessions[i].patch('/api/v1/users/'+user['id'],data=json.dumps(payloads[i]),content_type='application/json',secure=True,**options).status_code
                finally:
                    worker.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                statuses=list(pool.map(attempt,range(2)))
            require(sorted(statuses)==[200,412],'Concurrent edits did not produce one commit and one conflict.')
            actual,_=current(user['id'])
            require(actual['version']==user['version']+1,'Concurrent edits incremented version more than once.')
        record('Concurrent edits of one version produce one commit and one 412',concurrent_occ)

        def concurrent_idempotency():
            payload,key=user_payload(),str(uuid4())
            sessions=[login('synthetic-access-admin',admin_password)[0] for _ in range(2)]
            tokens=[csrf(c) for c in sessions]
            def attempt(i):
                worker=connections['default']
                worker.settings_dict['USER']='vdt_app'
                worker.settings_dict['PASSWORD']=os.environ['VDT_DB_APP_PASSWORD']
                try:
                    options=dict(headers(),HTTP_X_CSRFTOKEN=tokens[i],HTTP_IDEMPOTENCY_KEY=key)
                    response=sessions[i].post('/api/v1/users',data=json.dumps(payload),content_type='application/json',secure=True,**options)
                    return response.status_code,response.json().get('id')
                finally:
                    worker.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                responses=list(pool.map(attempt,range(2)))
            require(all(status==201 for status,_ in responses) and responses[0][1]==responses[1][1],'Concurrent same-key requests did not return one original result.')
            require(owner.execute('SELECT count(*) FROM vdt.app_user WHERE login_name=%s',(payload['username'],)).fetchone()[0]==1,'Concurrent idempotent create duplicated user.')
        record('Concurrent requests sharing an idempotency key create exactly one user',concurrent_idempotency)

        def revoke_race():
            actor,c,_=ready_user()
            assignment=grant(actor['id'])
            target=create_user()
            _,target_etag=current(target['id'])
            grant_response=expect(get(admin,'/api/v1/role-assignments/'+assignment['id']),200,'Assignment read failed')
            actor_token,admin_token=csrf(c),csrf(admin)
            edit_body={'display_name':'Concurrent granted edit','write_context':context()}
            revoke_body={'write_context':context(actor['id'])}
            def attempt(operation):
                worker=connections['default']
                worker.settings_dict['USER']='vdt_app'
                worker.settings_dict['PASSWORD']=os.environ['VDT_DB_APP_PASSWORD']
                try:
                    if operation=='edit':
                        options=dict(headers(),HTTP_X_CSRFTOKEN=actor_token,HTTP_IDEMPOTENCY_KEY=str(uuid4()),HTTP_IF_MATCH=target_etag)
                        return c.patch('/api/v1/users/'+target['id'],data=json.dumps(edit_body),content_type='application/json',secure=True,**options).status_code
                    options=dict(headers(),HTTP_X_CSRFTOKEN=admin_token,HTTP_IDEMPOTENCY_KEY=str(uuid4()),HTTP_IF_MATCH=grant_response['ETag'])
                    return admin.post('/api/v1/role-assignments/'+assignment['id']+'/revocations',data=json.dumps(revoke_body),content_type='application/json',secure=True,**options).status_code
                finally:
                    worker.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                edit_status,revoke_status=list(pool.map(attempt,['edit','revoke']))
            require(revoke_status==201 and edit_status in (200,403),'Revoke/write race did not serialize to an authorized outcome.')
            _,target_etag=current(target['id'])
            expect(mutate(c,'/api/v1/users/'+target['id'],{'display_name':'Must be rejected','write_context':context()},method='patch',match=target_etag),403,'Write after completed revocation was accepted')
        record('Grant revocation and concurrent write serialize; later writes are denied',revoke_race)

        def immutable_history():
            try:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE vdt.mutable_entity_history SET schema_version='modified' WHERE id=(SELECT id FROM vdt.mutable_entity_history LIMIT 1)")
            except Exception as error:
                code=getattr(getattr(error,'__cause__',None),'sqlstate',None)
                require(code=='55000','Unexpected history mutation failure.')
            else:
                raise CheckFailure('Runtime changed immutable user history.')
        record('Runtime cannot rewrite immutable entity history',immutable_history)

        def audit_chronology():
            first=expect(get(admin,'/api/v1/audit-events?limit=2'),200,'First audit page failed').json()
            require(first['next_cursor'] is not None,'Audit continuation missing.')
            second=expect(get(admin,'/api/v1/audit-events?limit=2&cursor='+first['next_cursor']),200,'Second audit page failed').json()
            expected=[str(row[0]) for row in owner.execute('''SELECT a.id FROM vdt.audit_event a
                JOIN vdt.app_user u ON u.id=a.actor_id ORDER BY a.recorded_at DESC,a.id DESC LIMIT 4''').fetchall()]
            require([row['id'] for row in first['items']+second['items']]==expected,
                    'Audit pages omit or reorder the newest events.')
        record('Audit pagination shows newest events first without gaps or duplicates',audit_chronology)

        def audit_privacy():
            response=expect(get(admin,'/api/v1/audit-events?limit=200'),200,'Audit list failed')
            validate(response.json(),'AuditEventPage')
            require(any(event['action']=='user.credential_reset' for event in response.json()['items']),'Audit list omitted administrative mutations.')
            secret_values.extend(row[0] for row in owner.execute('SELECT password_hash FROM vdt.app_user').fetchall() if len(row[0])>20)
            rows=owner.execute('SELECT row_to_json(a)::text FROM vdt.audit_event a').fetchall()
            rows+=owner.execute('SELECT state_snapshot::text FROM vdt.mutable_entity_history').fetchall()
            rows+=owner.execute('SELECT result_metadata::text FROM vdt.idempotency_operation').fetchall()
            serialized='\n'.join(row[0] for row in rows)
            require(not any(value and value in serialized for value in secret_values),'Credential/token leaked in audit/history/idempotency metadata.')
            require(owner.execute("SELECT count(*) FROM vdt.mutable_entity_history WHERE entity_kind='user'").fetchone()[0]>3,'User mutations lack history.')
            require(owner.execute("SELECT count(*) FROM vdt.mutable_entity_history WHERE entity_kind='role_assignment'").fetchone()[0]>2,'Role mutations lack history.')
            require(owner.execute('SELECT count(*) FROM vdt.role').fetchone()[0]==4 and owner.execute('SELECT count(*) FROM vdt.permission').fetchone()[0]==19,'Catalog mutated.')
        record('Audit/history/idempotency omit credentials and catalogs remain unchanged',audit_privacy)
        if args.browser_fixture_output and all(c['passed'] for c in checks):
            # Deliberately separate ignored runtime artifact; never publish/report.
            fixture={'synthetic_only':True,'database_host':'testdb','username':'synthetic-access-admin','password':admin_password}
            args.browser_fixture_output.parent.mkdir(parents=True,exist_ok=True)
            args.browser_fixture_output.write_text(json.dumps(fixture),encoding='utf-8')
            args.browser_fixture_output.chmod(0o600)
        connection.close()
        return result()
    except CheckFailure as error:
        return result(str(error))
    except Exception as error:
        return result(type(error).__name__)
    finally:
        if owner is not None:
            owner.close()


if __name__ == '__main__':
    raise SystemExit(main())
