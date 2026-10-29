"""HTTP routes for the bounded user/role administration milestone."""
from functools import wraps

from django.core.exceptions import RequestDataTooBig
from django.db import DatabaseError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables

from vdt.authn.service import AuthError
from vdt.authn.views import problem, response_headers
from . import service
from .validation import payload, expected_version, uuid_text


def boundary(methods):
    def decorate(view):
        @wraps(view)
        @csrf_protect
        @sensitive_post_parameters('temporary_password')
        @sensitive_variables()
        def wrapped(request,*args,**kwargs):
            if request.method not in methods:
                response=problem(request,'METHOD_NOT_ALLOWED',405,'Phương thức không được hỗ trợ.')
                response['Allow']=', '.join(methods)
                return response
            try:
                if 'id' in kwargs:
                    kwargs['id']=uuid_text(str(kwargs['id']))
                reply=view(request,*args,**kwargs)
                response=HttpResponse(status=reply.status) if reply.status==204 else JsonResponse(reply.data,status=reply.status)
                if reply.etag:
                    response['ETag']=reply.etag
                if reply.location:
                    response['Location']=reply.location
                return response_headers(request,response)
            except AuthError as error:
                try:
                    service.audit_denied(request,error.code)
                except DatabaseError:
                    request.session.modified=False
                    return problem(request,'SERVICE_UNAVAILABLE',503,'Không ghi được nhật ký kiểm soát. Hãy thử lại sau.')
                return problem(request,error.code,error.status,error.detail,error.retry_after)
            except RequestDataTooBig:
                return problem(request,'PAYLOAD_TOO_LARGE',413,'Yêu cầu quá lớn.')
            except DatabaseError:
                request.session.modified=False
                return problem(request,'SERVICE_UNAVAILABLE',503,'Dịch vụ quản trị chưa sẵn sàng. Hãy thử lại sau.')
        return wrapped
    return decorate


@boundary(('GET',))
def organization_view(request):
    return service.organization(request)


@boundary(('GET',))
def branches_view(request):
    return service.branches(request)


@boundary(('GET','POST'))
def users_view(request):
    if request.method=='GET':
        return service.users(request)
    return service.write_user(request,payload(request,'UserWrite'))


@boundary(('GET','PATCH'))
def user_view(request,id):
    if request.method=='GET':
        return service.users(request,id)
    return service.write_user(request,payload(request,'UserWritePatch'),id,expected_version(request,True))


@boundary(('POST',))
def credential_reset_view(request,id):
    return service.reset_credential(request,id,payload(request,'CredentialResetInput'),expected_version(request,True))


@boundary(('GET',))
def roles_view(request):
    return service.catalog(request,'roles')


@boundary(('GET',))
def permissions_view(request):
    return service.catalog(request,'permissions')


@boundary(('GET','POST'))
def assignments_view(request):
    if request.method=='GET':
        return service.assignments(request)
    return service.grant(request,payload(request,'RoleAssignmentInput'))


@boundary(('GET',))
def assignment_view(request,id):
    return service.assignments(request,id)


@boundary(('POST',))
def revoke_view(request,id):
    return service.revoke(request,id,payload(request,'RevokeInput'),expected_version(request,True))


@boundary(('GET',))
def audit_view(request):
    return service.audit_events(request)
