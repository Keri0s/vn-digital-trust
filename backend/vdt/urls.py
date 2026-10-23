from django.urls import path,re_path
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.middleware.csrf import get_token

@require_GET
def live(request): return JsonResponse({'status':'ok'})
@require_GET
def home(request): return render(request,'index.html')
@require_GET
def csrf(request): return JsonResponse({'csrf_token':get_token(request)})
def unavailable(request,remaining=''):
    # No placeholder endpoint accepts or persists business data.
    return JsonResponse({'type':'about:blank','title':'Chức năng đang được triển khai','status':503,'code':'PROTOTYPE_NOT_READY'},status=503)
urlpatterns=[path('',home),path('health/live/',live),path('api/v1/auth/csrf',csrf),re_path(r'^api/v1/(?P<remaining>.*)$',unavailable)]
