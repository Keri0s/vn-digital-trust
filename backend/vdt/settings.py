"""PostgreSQL-only settings. Secrets supplied by the local operator/runtime."""
import os
import json
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parents[2]
SECRET_KEY=os.environ['VDT_SECRET_KEY']
DEBUG=False
ALLOWED_HOSTS=os.environ.get('VDT_ALLOWED_HOSTS','localhost,127.0.0.1').split(',')
INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','rest_framework','vdt.core']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
MIDDLEWARE.insert(MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware') + 1, 'vdt.authn.middleware.AuthSessionMiddleware')
MIDDLEWARE[MIDDLEWARE.index('django.contrib.sessions.middleware.SessionMiddleware')] = 'vdt.authn.middleware.SecureSessionMiddleware'
ROOT_URLCONF='vdt.urls'
WSGI_APPLICATION='vdt.wsgi.application'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'backend/vdt/templates'],'APP_DIRS':True}]
DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':os.environ.get('PGDATABASE','vdt_step06'),'USER':os.environ['PGUSER'],'PASSWORD':os.environ['PGPASSWORD'],'HOST':os.environ.get('PGHOST','127.0.0.1'),'PORT':os.environ.get('PGPORT','55432'),'CONN_MAX_AGE':0}}
AUTH_USER_MODEL='core.AppUser'
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':12}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
PASSWORD_HASHERS=['django.contrib.auth.hashers.PBKDF2PasswordHasher']
SESSION_ENGINE='django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME='__Host-vdt_session'
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=3600
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS='DENY'
USE_TZ=True
TIME_ZONE='UTC'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticated'],'DEFAULT_RENDERER_CLASSES':['rest_framework.renderers.JSONRenderer']}
DATA_UPLOAD_MAX_MEMORY_SIZE=64*1024
FILE_UPLOAD_MAX_MEMORY_SIZE=0

# Explicit local VDT policy; these settings never configure AUTH-CRM-01.
_auth_policy_path = os.environ.get('VDT_AUTH_POLICY_PATH')
VDT_AUTH_POLICY = json.loads(Path(_auth_policy_path).read_text(encoding='utf-8')) if _auth_policy_path else None
VDT_AUTH_PROXY_SECRET = os.environ.get('VDT_AUTH_PROXY_SECRET', '')
VDT_AUTH_ALLOWED_ORIGINS = os.environ.get('VDT_AUTH_ALLOWED_ORIGINS', 'https://localhost:8443').split(',')
CSRF_FAILURE_VIEW = 'vdt.authn.views.csrf_failure'
VDT_LOCAL_FOUNDATION_ONLY = os.environ.get('VDT_LOCAL_FOUNDATION_ONLY') == 'true'

# Disposable browser QA must not replace the operator's localhost cookies.
if os.environ.get('VDT_AUTH_INTEGRATION_TEST') == 'true' and os.environ.get('PGHOST') == 'testdb':
    SESSION_COOKIE_NAME = '__Host-vdt_test_session'
    CSRF_COOKIE_NAME = 'vdt_test_csrf'
