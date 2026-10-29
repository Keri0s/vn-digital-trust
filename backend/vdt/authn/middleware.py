"""Validate every presented VDT session against current database state."""
import uuid

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.db import DatabaseError
from django.utils.crypto import constant_time_compare

from . import service
from .policy import literal_ip,validate_origins
from .views import clear_session_cookie,problem,response_headers


class SecureSessionMiddleware(SessionMiddleware):
    """Keep cookie deletion flags identical after Django's response middleware."""
    def process_response(self,request,response):
        response = super().process_response(request,response)
        cookie = response.cookies.get(settings.SESSION_COOKIE_NAME)
        if cookie is not None:
            cookie['secure'] = True
            cookie['httponly'] = True
            cookie['samesite'] = 'Lax'
            cookie['path'] = '/'
            cookie['domain'] = ''
        return response


class AuthSessionMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response
        # Missing/ambiguous policy is a startup failure, never permissive fallback.
        self.policy = service.policy()
        self.secret = settings.VDT_AUTH_PROXY_SECRET
        if not isinstance(self.secret,str) or len(self.secret) < 32:
            raise ValueError('VDT_AUTH_PROXY_SECRET must be explicitly configured.')
        self.origins = validate_origins(settings.VDT_AUTH_ALLOWED_ORIGINS)

    def __call__(self,request):
        request.vdt_request_id = uuid.uuid4()
        request.vdt_context = None
        request.vdt_clear_cookie = False
        is_api = request.path.startswith('/api/')
        auth_path = request.path.startswith('/api/v1/auth/')
        # Only this direct reverse proxy can attest a source address. It MUST
        # overwrite both headers, and no app port may be published to the host.
        if is_api:
            provided = request.META.get('HTTP_X_VDT_PROXY_SECRET','')
            if (not constant_time_compare(provided,self.secret) or not request.is_secure()
                    or 'https://' + request.get_host() not in self.origins):
                return problem(request,'TRUSTED_PROXY_REQUIRED',403,'Yêu cầu phải đi qua cổng HTTPS của VDT.')
            try:
                request.vdt_source_ip = literal_ip(request.META.get('HTTP_X_VDT_CLIENT_IP'))
            except ValueError:
                return problem(request,'TRUSTED_PROXY_REQUIRED',403,'Không xác minh được nguồn yêu cầu.')
            origin = request.META.get('HTTP_ORIGIN')
            fetch_site = request.META.get('HTTP_SEC_FETCH_SITE')
            if (origin is not None and origin not in self.origins) or fetch_site == 'cross-site':
                return problem(request,'ORIGIN_DENIED',403,'Nguồn yêu cầu không được phép.')
        try:
            context = service.current_session(request)
            request.vdt_context = context
            if context:
                request.user = request._cached_user = context.user
            else:
                request.user = request._cached_user = AnonymousUser()
                if request.session.session_key:
                    request.session.flush()
                    request.session.modified = False
                    request.vdt_clear_cookie = True
            # Services still authorize under the same transaction as each read/write.
            if is_api and not auth_path and context is None:
                response = problem(request,'AUTHENTICATION_REQUIRED',401,'Vui lòng đăng nhập lại.')
            elif is_api and not auth_path and context.user.password_change_required:
                response = problem(request,'PASSWORD_CHANGE_REQUIRED',403,'Hãy đổi mật khẩu tạm thời trước khi tiếp tục.')
            else:
                response = self.get_response(request)
        except DatabaseError:
            request.session.modified = False
            response = problem(request,'AUTH_SERVICE_UNAVAILABLE',503,'Dịch vụ đăng nhập chưa sẵn sàng. Hãy thử lại sau.')
        if request.vdt_clear_cookie:
            clear_session_cookie(response)
        if is_api:
            response_headers(request,response)
        return response
