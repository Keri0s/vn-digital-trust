"""Closed JSON auth contract, CSRF protection and minimized problem responses."""
from functools import wraps
import json
import uuid

from django.conf import settings
from django.core.exceptions import RequestDataTooBig
from django.db import DatabaseError
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables

from . import service
from .policy import normalize_username


def response_headers(request, response):
    request_id = getattr(request,'vdt_request_id',None) or uuid.uuid4()
    request.vdt_request_id = request_id
    response['X-Request-ID'] = str(request_id)
    response['Cache-Control'] = 'no-store'
    response['Pragma'] = 'no-cache'
    return response


def problem(request, code, status, detail, retry_after=None):
    request_id = getattr(request,'vdt_request_id',None) or uuid.uuid4()
    request.vdt_request_id = request_id
    response = JsonResponse({'type':'about:blank','title':detail,'status':status,
        'code':code,'request_id':str(request_id)},status=status,content_type='application/problem+json')
    if retry_after:
        response['Retry-After'] = str(retry_after)
    return response_headers(request,response)


def csrf_failure(request, reason=''):
    return problem(request,'CSRF_FAILED',403,'Không xác minh được yêu cầu. Hãy tải lại trang và thử lại.')


def _closed_object(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


@sensitive_variables()
def _payload(request, fields):
    if request.content_type != 'application/json':
        raise service.AuthError('UNSUPPORTED_MEDIA_TYPE',415,'Yêu cầu phải dùng JSON.')
    try:
        content_length = int(request.META.get('CONTENT_LENGTH') or 0)
        if content_length < 0:
            raise ValueError('negative content length')
    except ValueError:
        raise service.AuthError('INVALID_INPUT',400,'Độ dài yêu cầu không hợp lệ.') from None
    if content_length > 16_384:
        raise service.AuthError('PAYLOAD_TOO_LARGE',413,'Yêu cầu quá lớn.')
    try:
        body = request.body
        if len(body) > 16_384:
            raise service.AuthError('PAYLOAD_TOO_LARGE',413,'Yêu cầu quá lớn.')
        value = json.loads(body.decode('utf-8'),object_pairs_hook=_closed_object,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError('non-finite')))
    except (ValueError,UnicodeError,RecursionError):
        raise service.AuthError('INVALID_JSON',400,'Nội dung JSON không hợp lệ.') from None
    if not isinstance(value,dict) or set(value) != set(fields):
        raise service.AuthError('INVALID_INPUT',422,'Các trường yêu cầu không hợp lệ.')
    for field,(minimum,maximum) in fields.items():
        if not isinstance(value[field],str) or not minimum <= len(value[field]) <= maximum or '\x00' in value[field]:
            raise service.AuthError('INVALID_INPUT',422,'Các trường yêu cầu không hợp lệ.')
    return value


def _boundary(methods):
    def decorate(view):
        @wraps(view)
        @sensitive_post_parameters('password','current_password','new_password')
        @sensitive_variables()
        def wrapped(request,*args,**kwargs):
            if request.method not in methods:
                response = problem(request,'METHOD_NOT_ALLOWED',405,'Phương thức không được hỗ trợ.')
                response['Allow'] = ', '.join(methods)
                return response
            try:
                response = view(request,*args,**kwargs)
            except service.AuthError as error:
                response = problem(request,error.code,error.status,error.detail,error.retry_after)
            except RequestDataTooBig:
                response = problem(request,'PAYLOAD_TOO_LARGE',413,'Yêu cầu quá lớn.')
            except (DatabaseError,ValueError,AttributeError):
                # Rollback failures must not persist an in-memory new session via
                # SessionMiddleware after this response. No exception details leak.
                request.session.modified = False
                response = problem(request,'AUTH_SERVICE_UNAVAILABLE',503,'Dịch vụ đăng nhập chưa sẵn sàng. Hãy thử lại sau.')
            return response_headers(request,response)
        return wrapped
    return decorate


def _session_dto(request, context):
    return {'user_id':str(context.user.pk),'display_name':context.user.display_name,
            'idle_expires_at':service.policy().idle_expiry(context.last_seen_at,context.expires_at).isoformat(),
            'absolute_expires_at':context.expires_at.isoformat(),
            'permissions':list(context.permissions),'csrf_token':get_token(request),
            'authorization_version':context.authorization_version}


def session_response(request, context):
    response = JsonResponse(_session_dto(request, context))
    # Header keeps the frozen, closed Session DTO unchanged.
    response['X-VDT-Password-Change-Required'] = str(context.user.password_change_required).lower()
    return response


def set_session_cookie(request,response):
    age = max(1,int((request.vdt_cookie_expiry-request.vdt_cookie_issued_at).total_seconds()))
    response.set_cookie(settings.SESSION_COOKIE_NAME,request.session.session_key,max_age=age,
                        secure=True,httponly=True,samesite='Lax',path='/')
    return response


def clear_session_cookie(response):
    response.set_cookie(settings.SESSION_COOKIE_NAME,'',max_age=0,
        expires='Thu, 01 Jan 1970 00:00:00 GMT',secure=True,httponly=True,samesite='Lax',path='/')
    return response


@_boundary(('GET',))
@ensure_csrf_cookie
def csrf_view(request):
    return JsonResponse({'csrf_token':get_token(request)})


@_boundary(('GET','POST','DELETE'))
@csrf_protect
@sensitive_variables()
def session_view(request):
    if request.method == 'POST':
        data = _payload(request,{'username':(1,150),'password':(1,1024)})
        try:
            username = normalize_username(data['username'])
        except ValueError:
            raise service.AuthError('INVALID_INPUT',422,'Tên đăng nhập không hợp lệ.') from None
        context = service.login(request,username,data['password'])
        request.vdt_clear_cookie = False
        return set_session_cookie(request,session_response(request,context))
    if request.method == 'DELETE':
        service.logout(request)
        return clear_session_cookie(HttpResponse(status=204))
    # Recheck under guard just before serializing even though middleware checked.
    context = service.current_session(request)
    if context is None:
        request.vdt_clear_cookie = True
        raise service.AuthError('AUTHENTICATION_REQUIRED',401,'Vui lòng đăng nhập lại.')
    return session_response(request,context)


@_boundary(('POST',))
@csrf_protect
@sensitive_variables()
def password_view(request):
    data = _payload(request,{'current_password':(1,1024),'new_password':(12,1024)})
    service.change_password(request,data['current_password'],data['new_password'])
    request.vdt_clear_cookie = False
    return set_session_cookie(request,HttpResponse(status=204))
