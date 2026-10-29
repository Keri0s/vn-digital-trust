"""Atomic auth operations. Guard lock precedes every user/session row lock.

Limiter locks are taken in lexical order before the organization guard. All auth
mutations use this same order. Session reads do not renew idle expiry. Session
permissions are navigation hints for implemented screens. Every domain endpoint
must independently check the current grant and full object scope under its guard.
"""
from dataclasses import dataclass
from datetime import timedelta
from functools import lru_cache
import secrets
import uuid

from django.conf import settings
from django.contrib.auth import HASH_SESSION_KEY, BACKEND_SESSION_KEY, SESSION_KEY
from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare, salted_hmac
from django.views.decorators.debug import sensitive_variables

from vdt.core.models import AppUser
from .policy import AuthPolicy


class AuthError(Exception):
    def __init__(self, code, status, detail, retry_after=None):
        self.code, self.status, self.detail, self.retry_after = code, status, detail, retry_after
        super().__init__(code)


@dataclass(frozen=True)
class AuthContext:
    user: AppUser
    session_id: uuid.UUID
    issued_at: object
    expires_at: object
    last_seen_at: object
    authorization_version: int
    permissions: tuple


def policy():
    return AuthPolicy.from_mapping(settings.VDT_AUTH_POLICY)


def db_now(cursor):
    cursor.execute('SELECT clock_timestamp()')
    return cursor.fetchone()[0]


def token_hash(key):
    return salted_hmac('vdt.auth.session.v1', key, algorithm='sha256').hexdigest()


def _bucket_key(kind, value):
    return salted_hmac('vdt.auth.rate.' + kind, value, algorithm='sha256').hexdigest()


def guard(cursor, organization_id):
    cursor.execute('SELECT vdt.acquire_authorization_guard(%s)', [organization_id])
    return cursor.fetchone()[0]


def bump_guard(cursor, organization_id):
    cursor.execute('UPDATE vdt.authorization_guard SET version=version+1 WHERE organization_id=%s RETURNING version', [organization_id])
    return cursor.fetchone()[0]


def audit(cursor, request, action, outcome, reason, user_id=None, session_id=None, authorization_version=None):
    # Never include credentials, session keys, CSRF tokens, names, or source IPs.
    cursor.execute('''INSERT INTO vdt.audit_event
        (id, actor_id, session_id, action, target_kind, target_id, outcome,
         reason_code, correlation_id, authorization_version, gate_checked_at)
        VALUES (%s,%s,%s,%s,'VDT_AUTH',%s,%s,%s,%s,%s,clock_timestamp())''',
        [uuid.uuid4(), user_id, session_id, action, user_id, outcome, reason,
         request.vdt_request_id, authorization_version])


def _user(cursor, user_id):
    cursor.execute('''SELECT id, organization_id, login_name, display_name, status,
        password_hash, version, last_login, password_change_required
        FROM vdt.app_user WHERE id=%s FOR UPDATE''', [user_id])
    row = cursor.fetchone()
    if row is None:
        return None
    return AppUser(id=row[0], organization_id=row[1], login_name=row[2], display_name=row[3],
                   status=row[4], password=row[5], version=row[6], last_login=row[7],
                   password_change_required=row[8])


def permissions(cursor, user, now):
    if user.password_change_required:
        return ()
    # Session permissions only choose navigation and forms. Selected domain grants
    # remain scoped in the assessment service; this projection is never sufficient
    # to authorize an object. Administrative rights still require full-org scope.
    cursor.execute('''SELECT DISTINCT p.code FROM vdt.role_assignment a
        JOIN vdt.scope s ON s.id=a.scope_id
        JOIN vdt.role_permission rp ON rp.role_id=a.role_id
        JOIN vdt.permission p ON p.id=rp.permission_id
        WHERE a.user_id=%s AND a.revoked_at IS NULL AND a.valid_from<=%s
        AND (a.access_expires_at IS NULL OR a.access_expires_at>%s)
        AND s.organization_id=%s AND (
            (p.code IN ('organization.manage','roles.assign','users.manage')
             AND s.scope_kind='ORGANIZATION'
             AND NOT EXISTS(SELECT 1 FROM vdt.scope_branch b WHERE b.scope_id=s.id)
             AND NOT EXISTS(SELECT 1 FROM vdt.scope_object o WHERE o.scope_id=s.id))
            OR
            (p.code IN ('assessment.run','assessment.review','report.read')
             AND (s.scope_kind='ORGANIZATION'
                  OR EXISTS(SELECT 1 FROM vdt.scope_branch b WHERE b.scope_id=s.id)
                  OR EXISTS(SELECT 1 FROM vdt.scope_object o WHERE o.scope_id=s.id))
             AND (p.code<>'assessment.review' OR
                  (a.access_expires_at IS NOT NULL AND EXISTS(
                      SELECT 1 FROM vdt.assignment_assessment aa
                      JOIN vdt.scope_object o ON o.scope_id=s.id AND o.assessment_id=aa.assessment_id
                      WHERE aa.assignment_id=a.id))))
        ) ORDER BY p.code''',
        [user.pk, now, now, user.organization_id])
    return tuple(row[0] for row in cursor.fetchall())


def _locate_binding(request, cursor):
    session_id = request.session.get('vdt_binding_id')
    key = request.session.session_key
    if not session_id or not key:
        return None
    try:
        session_id = uuid.UUID(str(session_id))
    except (ValueError, TypeError):
        return None
    cursor.execute('''SELECT s.id,u.id,u.organization_id FROM vdt.vdt_session s
        JOIN vdt.app_user u ON u.id=s.user_id WHERE s.id=%s''', [session_id])
    located = cursor.fetchone()
    return (located, key) if located else None


def _context_locked(cursor, request, located, key, version):
    session_id, user_id, _ = located
    user = _user(cursor, user_id)
    cursor.execute('''SELECT session_token_hash, issued_at, expires_at, last_seen_at, revoked_at
        FROM vdt.vdt_session WHERE id=%s AND user_id=%s FOR UPDATE''', [session_id, user_id])
    row = cursor.fetchone()
    now = db_now(cursor)
    if row is None or user is None or not constant_time_compare(row[0], token_hash(key)):
        return None
    if not policy().is_live(now=now, last_seen=row[3], absolute_expiry=row[2], revoked_at=row[4], active=user.is_active):
        if row[4] is None:
            cursor.execute('UPDATE vdt.vdt_session SET revoked_at=%s,version=version+1 WHERE id=%s', [now,session_id])
            version = bump_guard(cursor, user.organization_id)
            audit(cursor, request, 'auth.session.invalidate', 'DENIED', 'SESSION_INACTIVE', user.pk, session_id, version)
        return None
    if (request.session.get(SESSION_KEY) != str(user.pk)
            or not constant_time_compare(request.session.get(HASH_SESSION_KEY, ''), user.get_session_auth_hash())):
        cursor.execute('UPDATE vdt.vdt_session SET revoked_at=%s,version=version+1 WHERE id=%s', [now,session_id])
        version = bump_guard(cursor, user.organization_id)
        audit(cursor, request, 'auth.session.invalidate', 'DENIED', 'SESSION_BINDING_INVALID', user.pk, session_id, version)
        return None
    return AuthContext(user, session_id, row[1], row[2], row[3], version, permissions(cursor,user,now))


def current_session(request):
    # Anonymous static/home/CSRF requests need no database connection. A cookie
    # key is only a lookup hint; every presented key is still verified below.
    if not request.session.session_key:
        return None
    with transaction.atomic(), connection.cursor() as cursor:
        binding = _locate_binding(request, cursor)
        if binding is None:
            return None
        located, key = binding
        version = guard(cursor, located[2])
        return _context_locked(cursor, request, located, key, version)


@lru_cache(maxsize=1)
def _dummy_hash():
    return make_password(secrets.token_urlsafe(48))


@sensitive_variables()
def verify_password(password, encoded):
    # Force a full PBKDF2 check for absent, inactive, unusable, malformed, or
    # unsupported credentials. Django also hardens wrong older PBKDF2 hashes.
    dummy = _dummy_hash()
    try:
        usable = identify_hasher(encoded).algorithm == 'pbkdf2_sha256'
    except (ValueError, TypeError):
        usable = False
    checked = encoded if usable else dummy
    try:
        return check_password(password, checked) and usable
    except (ValueError, TypeError, IndexError):
        check_password(password, dummy)
        return False


def _rate_locked(cursor, action, identity, source):
    conf = policy()
    account_key = _bucket_key(action + '.account', identity)
    source_key = _bucket_key(action + '.source', source)
    keys = sorted([account_key, source_key])
    for key in keys:
        cursor.execute('''INSERT INTO vdt.auth_rate_bucket(bucket_key,window_started_at)
            VALUES (%s,clock_timestamp()) ON CONFLICT(bucket_key) DO NOTHING''', [key])
        cursor.execute('SELECT bucket_key FROM vdt.auth_rate_bucket WHERE bucket_key=%s FOR UPDATE', [key])
    now = db_now(cursor)
    retry_after = 0
    for key in keys:
        cursor.execute('SELECT window_started_at,locked_until FROM vdt.auth_rate_bucket WHERE bucket_key=%s', [key])
        started, locked = cursor.fetchone()
        if locked and now < locked:
            retry_after = max(retry_after, int((locked-now).total_seconds()) + 1)
        elif now >= started + timedelta(seconds=conf.attempt_window_seconds):
            cursor.execute('UPDATE vdt.auth_rate_bucket SET failures=0,window_started_at=%s,locked_until=NULL WHERE bucket_key=%s', [now,key])
    return account_key, keys, retry_after


def _rate_failure(cursor, keys):
    conf = policy()
    now = db_now(cursor)
    for key in keys:
        cursor.execute('''UPDATE vdt.auth_rate_bucket SET failures=failures+1,
            locked_until=CASE WHEN failures+1>=%s THEN %s ELSE locked_until END
            WHERE bucket_key=%s''', [conf.max_attempts, now+timedelta(seconds=conf.lockout_seconds), key])


def _revoke_existing(cursor, request, now):
    # Caller holds current user's organization guard (one organization/database).
    key = request.session.session_key
    if key:
        cursor.execute('''UPDATE vdt.vdt_session SET revoked_at=%s,version=version+1
            WHERE session_token_hash=%s AND revoked_at IS NULL''', [now,token_hash(key)])
        request.session.delete(key)


def _issue(cursor, request, user, now, *, absolute_expiry=None):
    expires = absolute_expiry or now + timedelta(seconds=policy().absolute_timeout_seconds)
    _revoke_existing(cursor, request, now)
    session_id = uuid.uuid4()
    store = SessionStore()
    store[SESSION_KEY] = str(user.pk)
    store[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
    store[HASH_SESSION_KEY] = user.get_session_auth_hash()
    store['vdt_binding_id'] = str(session_id)
    store.set_expiry(expires)
    store.save()
    cursor.execute('''INSERT INTO vdt.vdt_session
        (id,user_id,session_token_hash,issued_at,expires_at,last_seen_at)
        VALUES (%s,%s,%s,%s,%s,%s)''', [session_id,user.pk,token_hash(store.session_key),now,expires,now])
    # We save explicitly in the auth transaction, not after the response in
    # SessionMiddleware. The view sets the Secure cookie after the commit.
    store.modified = False
    request.session = store
    request.vdt_cookie_expiry = expires
    request.vdt_cookie_issued_at = now
    request.user = request._cached_user = user
    rotate_token(request)
    version = bump_guard(cursor,user.organization_id)
    return AuthContext(user,session_id,now,expires,now,version,permissions(cursor,user,now))


@sensitive_variables()
def login(request, username, password):
    error = None
    result = None
    with transaction.atomic(), connection.cursor() as cursor:
        account_key, keys, retry = _rate_locked(cursor,'login',username,request.vdt_source_ip)
        if retry:
            audit(cursor,request,'auth.login','DENIED','RATE_LIMITED')
            error = AuthError('RATE_LIMITED',429,'Tạm khóa thử đăng nhập. Hãy thử lại sau.',retry)
        else:
            cursor.execute('SELECT id,organization_id FROM vdt.app_user WHERE login_name=%s',[username])
            identity = cursor.fetchone()
            user = None
            version = None
            if identity:
                version = guard(cursor,identity[1])
                user = _user(cursor,identity[0])
            # Inactive identities follow the same current-cost dummy path as
            # unknown users, even when an old stored hash has a lower work factor.
            valid = verify_password(password,user.password if user and user.is_active else '!')
            if not user or not valid or not user.is_active:
                _rate_failure(cursor,keys)
                audit(cursor,request,'auth.login','DENIED','INVALID_CREDENTIALS',user.pk if user else None,authorization_version=version)
                error = AuthError('INVALID_CREDENTIALS',401,'Tên đăng nhập hoặc mật khẩu không hợp lệ.')
            else:
                now = db_now(cursor)
                cursor.execute('UPDATE vdt.app_user SET last_login=%s,version=version+1 WHERE id=%s',[now,user.pk])
                cursor.execute('UPDATE vdt.auth_rate_bucket SET failures=0,locked_until=NULL,window_started_at=%s WHERE bucket_key=%s',[now,account_key])
                result = _issue(cursor,request,user,now)
                audit(cursor,request,'auth.login','ALLOWED','AUTHENTICATED',user.pk,result.session_id,result.authorization_version)
    if error:
        raise error
    return result


def logout(request):
    with transaction.atomic(), connection.cursor() as cursor:
        binding = _locate_binding(request,cursor)
        if binding:
            located,key = binding
            guard(cursor,located[2])
            user = _user(cursor,located[1])
            cursor.execute('SELECT session_token_hash,revoked_at FROM vdt.vdt_session WHERE id=%s FOR UPDATE',[located[0]])
            row = cursor.fetchone()
            if user and row and row[1] is None and constant_time_compare(row[0],token_hash(key)):
                now = db_now(cursor)
                cursor.execute('UPDATE vdt.vdt_session SET revoked_at=%s,version=version+1 WHERE id=%s',[now,located[0]])
                version = bump_guard(cursor,user.organization_id)
                audit(cursor,request,'auth.logout','ALLOWED','SESSION_REVOKED',user.pk,located[0],version)
        request.session.flush()
        request.session.modified = False
        rotate_token(request)


@sensitive_variables()
def change_password(request, current_password, new_password):
    error = None
    result = None
    with transaction.atomic(), connection.cursor() as cursor:
        # Reading opaque binding identity is not authorization; recheck under
        # guard and row lock after acquiring the rate buckets in global order.
        binding = _locate_binding(request,cursor)
        if not binding:
            raise AuthError('AUTHENTICATION_REQUIRED',401,'Vui lòng đăng nhập lại.')
        located,key = binding
        account_key,keys,retry = _rate_locked(cursor,'password',str(located[1]),request.vdt_source_ip)
        version = guard(cursor,located[2])
        context = _context_locked(cursor,request,located,key,version)
        if context is None:
            error = AuthError('AUTHENTICATION_REQUIRED',401,'Vui lòng đăng nhập lại.')
        elif retry:
            audit(cursor,request,'auth.password','DENIED','RATE_LIMITED',context.user.pk,context.session_id,context.authorization_version)
            error = AuthError('RATE_LIMITED',429,'Tạm khóa thử đổi mật khẩu. Hãy thử lại sau.',retry)
        elif not verify_password(current_password,context.user.password):
            _rate_failure(cursor,keys)
            audit(cursor,request,'auth.password','DENIED','INVALID_CREDENTIALS',context.user.pk,context.session_id,context.authorization_version)
            error = AuthError('INVALID_CREDENTIALS',401,'Không xác nhận được mật khẩu hiện tại.')
        else:
            user = context.user
            try:
                if constant_time_compare(current_password,new_password):
                    raise ValidationError('Choose a different password.')
                validate_password(new_password,user=user)
            except ValidationError:
                error = AuthError('PASSWORD_POLICY_REJECTED',422,'Mật khẩu mới cần ít nhất 12 ký tự, không phổ biến, không chỉ gồm số và khác mật khẩu hiện tại.')
                audit(cursor,request,'auth.password','DENIED','PASSWORD_POLICY_REJECTED',user.pk,context.session_id,context.authorization_version)
            else:
                encoded = make_password(new_password)
                now = db_now(cursor)
                # Hashing may cross expiry; do not revive a session at commit.
                if not policy().is_live(now=now,last_seen=context.last_seen_at,absolute_expiry=context.expires_at,revoked_at=None,active=user.is_active):
                    error = AuthError('AUTHENTICATION_REQUIRED',401,'Vui lòng đăng nhập lại.')
                else:
                    cursor.execute('UPDATE vdt.app_user SET password_hash=%s,password_change_required=false,version=version+1 WHERE id=%s',[encoded,user.pk])
                    user.password = encoded
                    user.password_change_required = False
                    cursor.execute('UPDATE vdt.vdt_session SET revoked_at=%s,version=version+1 WHERE user_id=%s AND revoked_at IS NULL',[now,user.pk])
                    cursor.execute('UPDATE vdt.auth_rate_bucket SET failures=0,locked_until=NULL,window_started_at=%s WHERE bucket_key=%s',[now,account_key])
                    # Rotation preserves the original absolute deadline.
                    result = _issue(cursor,request,user,now,absolute_expiry=context.expires_at)
                    audit(cursor,request,'auth.password','ALLOWED','PASSWORD_CHANGED_OTHER_SESSIONS_REVOKED',user.pk,result.session_id,result.authorization_version)
    if error:
        raise error
    return result
