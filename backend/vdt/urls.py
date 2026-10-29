from django.urls import path,re_path
from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from vdt.authn.views import csrf_view, session_view, password_view
from vdt.access import views as access
from vdt.assessment import views as assessment
from vdt.workspace import views as workspace

@require_GET
def live(request): return JsonResponse({'status':'ok'})
@require_GET
def home(request): return render(request,'index.html')
@require_GET
def administration(request):
    context = getattr(request, 'vdt_context', None)
    if (context is None or context.user.password_change_required
            or not {'users.manage','roles.assign','organization.manage'}.intersection(context.permissions)):
        return redirect('/')
    response = render(request, 'admin.html')
    response['Cache-Control'] = 'no-store'
    return response
@require_GET
def assessment_worklist(request):
    context = getattr(request,'vdt_context',None)
    if (context is None or context.user.password_change_required or
            not {'assessment.run','assessment.review','report.read'}.intersection(context.permissions)):
        return redirect('/')
    response = render(request,'assessments.html')
    response['Cache-Control'] = 'no-store'
    return response
@require_GET
def workspace_page(request):
    context=getattr(request,'vdt_context',None)
    if context is None or context.user.password_change_required or 'assessment.run' not in context.permissions:
        return redirect('/')
    response=render(request,'workspace.html')
    response['Cache-Control']='no-store'
    return response
@require_GET
def asset(request, name):
    # Only explicitly named public assets are routed.
    return FileResponse(open(settings.BASE_DIR / 'backend/vdt/static/vdt' / name, 'rb'),
                        content_type='text/css' if name.endswith('.css') else 'text/javascript')
def unavailable(request,remaining=''):
    # No placeholder endpoint accepts or persists business data.
    return JsonResponse({'type':'about:blank','title':'Chức năng đang được triển khai','status':503,'code':'PROTOTYPE_NOT_READY'},status=503)
urlpatterns=[
    path('',home), path('health/live/',live),
    path('admin/users',administration),
    path('assessments',assessment_worklist),
    path('workspace',workspace_page),
    path('static/vdt/workspace.css',asset,{'name':'workspace.css'}),
    path('static/vdt/workspace.js',asset,{'name':'workspace.js'}),
    path('static/vdt/auth.css',asset,{'name':'auth.css'}),
    path('static/vdt/auth.js',asset,{'name':'auth.js'}),
    path('static/vdt/admin.css',asset,{'name':'admin.css'}),
    path('static/vdt/admin.js',asset,{'name':'admin.js'}),
    path('static/vdt/assessments.js',asset,{'name':'assessments.js'}),
    path('static/vdt/assessments.css',asset,{'name':'assessments.css'}),
    path('api/v1/auth/csrf',csrf_view),
    path('api/v1/auth/session',session_view),
    path('api/v1/auth/password',password_view),
    path('api/v1/organization',access.organization_view),
    path('api/v1/branches',access.branches_view),
    path('api/v1/users',access.users_view),
    path('api/v1/users/<uuid:id>',access.user_view),
    path('api/v1/users/<uuid:id>/credential-resets',access.credential_reset_view),
    path('api/v1/roles',access.roles_view),
    path('api/v1/permissions',access.permissions_view),
    path('api/v1/role-assignments',access.assignments_view),
    path('api/v1/role-assignments/<uuid:id>',access.assignment_view),
    path('api/v1/role-assignments/<uuid:id>/revocations',access.revoke_view),
    path('api/v1/audit-events',access.audit_view),
    path('api/v1/assessments',assessment.collection),
    path('api/v1/assessments/<uuid:id>',assessment.item),
    path('api/v1/assessments/display-context',assessment.display_context),
    path('api/v1/assessments/<uuid:id>/display-context',assessment.display_context),
    path('api/v1/assessments/setup',assessment.setup),
    path('api/v1/admin/assessments',assessment.assignment_catalog),
    path('api/v1/workspace/setup',workspace.setup),
    path('api/v1/systems',workspace.inventory,{'kind':'systems'}),
    path('api/v1/systems/<uuid:id>',workspace.inventory,{'kind':'systems'}),
    path('api/v1/assets',workspace.inventory,{'kind':'assets'}),
    path('api/v1/assets/<uuid:id>',workspace.inventory,{'kind':'assets'}),
    path('api/v1/data-assets',workspace.inventory,{'kind':'data-assets'}),
    path('api/v1/data-assets/<uuid:id>',workspace.inventory,{'kind':'data-assets'}),
    path('api/v1/context-snapshots',workspace.context_create),
    path('api/v1/context-snapshots/<uuid:id>',workspace.snapshot,{'kind':'CONTEXT'}),
    path('api/v1/scenarios',workspace.scenarios),
    path('api/v1/scenarios/<uuid:id>',workspace.scenarios),
    path('api/v1/scenarios/<uuid:id>/transitions',workspace.transition),
    path('api/v1/scenario-snapshots/<uuid:id>',workspace.snapshot,{'kind':'SCENARIO'}),
    path('api/v1/assessments/<uuid:id>/scenario-links',workspace.link),
    path('api/v1/assessments/<uuid:id>/dossier',workspace.dossier),
    re_path(r'^api/v1/(?P<remaining>.*)$',unavailable),
]
