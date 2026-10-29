"""Pure policy boundaries, separate from PostgreSQL/integration evidence."""
from datetime import datetime, timedelta, timezone
import unittest

from vdt.authn.policy import AuthPolicy, literal_ip, normalize_username, validate_origins


CONFIG = {'profile':'DEVELOPMENT_LOCAL','idle_timeout_seconds':1800,
          'absolute_timeout_seconds':28800,'max_attempts':5,
          'attempt_window_seconds':900,'lockout_seconds':900}


class AuthPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = AuthPolicy.from_mapping(CONFIG)
        self.now = datetime(2026,10,24,tzinfo=timezone.utc)

    def test_exact_explicit_fields_only(self):
        for value in (None,{},dict(CONFIG,extra=1),{k:v for k,v in CONFIG.items() if k!='profile'}):
            with self.subTest(value=value),self.assertRaises(ValueError):
                AuthPolicy.from_mapping(value)

    def test_no_crm_or_approved_profile(self):
        for profile in ('APPROVED','AUTH-CRM-01','PRODUCTION'):
            with self.assertRaises(ValueError):
                AuthPolicy.from_mapping(dict(CONFIG,profile=profile))

    def test_strict_integer_limits(self):
        for field in set(CONFIG)-{'profile'}:
            for value in (True,0,-1,'900',None,1_000_000):
                with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                    AuthPolicy.from_mapping(dict(CONFIG,**{field:value}))

    def test_idle_cannot_exceed_absolute(self):
        with self.assertRaises(ValueError):
            AuthPolicy.from_mapping(dict(CONFIG,idle_timeout_seconds=9000,absolute_timeout_seconds=1000))

    def test_idle_expiry_is_bounded_by_absolute(self):
        absolute = self.now+timedelta(seconds=50)
        self.assertEqual(self.policy.idle_expiry(self.now,absolute),absolute)

    def test_idle_expiry_equality_denies(self):
        deadline = self.now+timedelta(seconds=1800)
        args = dict(last_seen=self.now,absolute_expiry=self.now+timedelta(hours=8),revoked_at=None,active=True)
        self.assertTrue(self.policy.is_live(now=deadline-timedelta(microseconds=1),**args))
        self.assertFalse(self.policy.is_live(now=deadline,**args))

    def test_absolute_expiry_equality_denies(self):
        deadline = self.now+timedelta(seconds=50)
        self.assertFalse(self.policy.is_live(now=deadline,last_seen=self.now,absolute_expiry=deadline,revoked_at=None,active=True))

    def test_revoked_inactive_naive_and_future_activity_deny(self):
        valid = dict(now=self.now,last_seen=self.now,absolute_expiry=self.now+timedelta(hours=8),revoked_at=None,active=True)
        for delta in ({'revoked_at':self.now},{'active':False},{'active':1},
                      {'now':self.now.replace(tzinfo=None)}, {'last_seen':self.now+timedelta(seconds=1)}):
            self.assertFalse(self.policy.is_live(**dict(valid,**delta)))

    def test_source_is_one_literal_ip(self):
        self.assertEqual(literal_ip('127.0.0.1'),'127.0.0.1')
        self.assertEqual(literal_ip('2001:db8::1'),'2001:db8::1')
        for value in (None,'localhost','127.0.0.1, 10.0.0.1','127.0.0.1:8443','[::1]','fe80::1%eth0',''):
            with self.assertRaises(ValueError):
                literal_ip(value)

    def test_https_origins_exact_and_closed(self):
        self.assertEqual(validate_origins(['https://localhost:8443']),frozenset({'https://localhost:8443'}))
        for value in ([],None,['http://localhost:8443'],['https://localhost:8443/'],
                      ['https://user@localhost:8443'],['https://*.example.com'],['https://localhost:8443?q=1']):
            with self.assertRaises(ValueError):
                validate_origins(value)

    def test_username_nfkc_matches_bootstrap_but_case_remains_distinct(self):
        self.assertEqual(normalize_username('  Ａdmin  '),'Admin')
        self.assertNotEqual(normalize_username('Admin'),normalize_username('admin'))
        for value in (' ',None,'a'*151,'a\x00b'):
            with self.assertRaises(ValueError):
                normalize_username(value)


if __name__=='__main__':
    unittest.main()
