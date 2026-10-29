"""In-process HTTP foundation checks; these do not verify a real TLS proxy."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vdt.settings')
os.environ.setdefault('VDT_SECRET_KEY', 'unit-test-only-unused-as-deployment-secret-0123456789')
os.environ.setdefault('PGUSER', 'unit-test-no-connection')
os.environ.setdefault('PGPASSWORD', 'unit-test-no-connection')
import django
django.setup()
from django.test import Client, SimpleTestCase, override_settings
from test_auth_policy import CONFIG


@override_settings(VDT_AUTH_POLICY=CONFIG,
                   VDT_AUTH_PROXY_SECRET='unit-test-trusted-proxy-secret-0000000000',
                   VDT_AUTH_ALLOWED_ORIGINS=['https://localhost:8443'])
class WebFoundationTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True, HTTP_HOST='localhost:8443',
                             HTTP_X_VDT_PROXY_SECRET='unit-test-trusted-proxy-secret-0000000000',
                             HTTP_X_VDT_CLIENT_IP='127.0.0.1')

    def test_plain_http_redirects_to_https(self):
        response = self.client.get('/health/live/')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://localhost:8443/health/live/')

    def test_live_is_not_readiness_or_database_health(self):
        self.assertEqual(self.client.get('/health/live/', secure=True).json(), {'status': 'ok'})

    def test_page_offers_login_and_marks_remaining_domain_work_pending(self):
        response = self.client.get('/', secure=True)
        self.assertContains(response, 'Đăng nhập')
        self.assertContains(response, 'các phần nhập bằng chứng và tính toán rủi ro đang được xây dựng.')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_csrf_cookie_is_secure(self):
        response = self.client.get('/api/v1/auth/csrf', secure=True)
        self.assertTrue(response.cookies['csrftoken']['secure'])
        self.assertTrue(response.json()['csrf_token'])

    def test_anonymous_domain_request_requires_authentication(self):
        response = self.client.get('/api/v1/assessments', secure=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['code'], 'AUTHENTICATION_REQUIRED')

    def test_unsafe_auth_request_requires_csrf_and_same_origin(self):
        path = '/api/v1/auth/session'
        self.assertEqual(self.client.post(path, secure=True).status_code, 403)
        token = self.client.get('/api/v1/auth/csrf', secure=True).json()['csrf_token']
        self.assertEqual(self.client.post(path, secure=True, HTTP_X_CSRFTOKEN=token,
                                         HTTP_ORIGIN='https://untrusted.example').status_code, 403)
        response = self.client.post(path, secure=True, HTTP_X_CSRFTOKEN=token,
                                    HTTP_ORIGIN='https://localhost:8443')
        self.assertEqual(response.status_code, 415)

    def test_unrecognized_host_denied(self):
        self.assertEqual(self.client.get('/', secure=True, HTTP_HOST='untrusted.example').status_code, 400)
