"""In-process HTTP foundation checks; these do not verify a real TLS proxy."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vdt.settings')
os.environ.setdefault('VDT_SECRET_KEY', 'unit-test-only-unused-as-deployment-secret-0123456789')
os.environ.setdefault('PGUSER', 'unit-test-no-connection')
os.environ.setdefault('PGPASSWORD', 'unit-test-no-connection')
import django
django.setup()
from django.test import Client, SimpleTestCase


class WebFoundationTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True, HTTP_HOST='localhost')

    def test_plain_http_redirects_to_https(self):
        response = self.client.get('/health/live/')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://localhost/health/live/')

    def test_live_is_not_readiness_or_database_health(self):
        self.assertEqual(self.client.get('/health/live/', secure=True).json(), {'status': 'ok'})

    def test_page_reports_incomplete_prototype(self):
        response = self.client.get('/', secure=True)
        self.assertContains(response, 'Prototype đang được xây dựng')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_csrf_cookie_is_secure(self):
        response = self.client.get('/api/v1/auth/csrf', secure=True)
        self.assertTrue(response.cookies['csrftoken']['secure'])
        self.assertTrue(response.json()['csrf_token'])

    def test_domain_endpoint_never_reports_placeholder_success(self):
        response = self.client.get('/api/v1/assessments', secure=True)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['code'], 'PROTOTYPE_NOT_READY')

    def test_unsafe_domain_request_requires_csrf_and_remains_unavailable(self):
        path = '/api/v1/assessments/x/evidence-revisions'
        self.assertEqual(self.client.post(path, secure=True).status_code, 403)
        token = self.client.get('/api/v1/auth/csrf', secure=True).json()['csrf_token']
        self.assertEqual(self.client.post(path, secure=True, HTTP_X_CSRFTOKEN=token,
                                         HTTP_ORIGIN='https://untrusted.example').status_code, 403)
        response = self.client.post(path, secure=True, HTTP_X_CSRFTOKEN=token,
                                    HTTP_ORIGIN='https://localhost')
        self.assertEqual(response.status_code, 503)

    def test_unrecognized_host_denied(self):
        self.assertEqual(self.client.get('/', secure=True, HTTP_HOST='untrusted.example').status_code, 400)
