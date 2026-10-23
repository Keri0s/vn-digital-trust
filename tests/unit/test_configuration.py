"""Offline validation of design config; no CRM or deployment test results."""

from copy import deepcopy
from io import BytesIO
from pathlib import Path
import unittest
from unittest.mock import patch

from vdt.configuration import (
    CRM_REQUIRED_FIVE, ConfigurationError, canonical_configuration_sha256,
    canonical_https_origin, load_configuration, preflight,
)


TEMPLATE = Path(__file__).resolve().parents[2] / "docs/design/config-template-v0.1.json"


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.config = load_configuration(TEMPLATE)

    def test_real_template_blocks_all_five_crm_values_without_copying_examples(self):
        before = deepcopy(self.config)
        result = preflight(self.config, "crm")
        self.assertEqual(result.status, "BLOCKED")
        unset = {issue.path for issue in result.issues if issue.code == "REQUIRED_UNSET"}
        for field in CRM_REQUIRED_FIVE:
            self.assertIn("crm_authentication_profile.effective_values." + field, unset)
            self.assertIsNone(self.config["crm_authentication_profile"]["effective_values"][field])
        self.assertEqual(before, self.config)
        self.assertEqual(self.config["runtime_test_status"]["TC_01_T01_to_T24"], "NOT_RUN")

    def test_dependency_specific_results_exclude_unrelated_missing_values(self):
        vdt = preflight(self.config, "vdt")
        crm = preflight(self.config, "crm")
        self.assertTrue(vdt.blocked)
        self.assertFalse(any(issue.path.startswith("crm_authentication_profile") for issue in vdt.issues))
        self.assertFalse(any(issue.path.startswith("vdt") for issue in crm.issues))
        self.assertFalse(any("receiver_base_url" in issue.path for issue in crm.issues))
        self.assertTrue(any("receiver_base_url" in issue.path for issue in preflight(self.config, "sc02").issues))

    def test_unknown_keys_and_bool_in_integer_fields_are_rejected(self):
        self.config["vdt"]["authentication"]["session_idle_timout_seconds"] = 900
        self.config["vdt"]["evidence"]["max_file_bytes"] = True
        codes = {(issue.path, issue.code) for issue in preflight(self.config, "vdt").issues}
        self.assertIn(("vdt.authentication.session_idle_timout_seconds", "UNKNOWN_KEY"), codes)
        self.assertIn(("vdt.evidence.max_file_bytes", "VALUE_INVALID"), codes)

    def test_negative_values_overlarge_limits_and_inconsistent_timeouts_block(self):
        self.config["vdt"]["evidence"]["max_file_bytes"] = 30 * 1024 ** 2
        self.config["vdt"]["evidence"]["scan_timeout_seconds"] = -1
        self.config["vdt"]["http"]["proxy_response_timeout_seconds"] = 240
        codes = {(issue.path, issue.code) for issue in preflight(self.config, "vdt").issues}
        self.assertIn(("vdt.evidence.max_file_bytes", "LIMIT_EXCEEDED"), codes)
        self.assertIn(("vdt.evidence.scan_timeout_seconds", "VALUE_INVALID"), codes)
        self.assertIn(("vdt.http.proxy_response_timeout_seconds", "LIMIT_RELATION_INVALID"), codes)

    def test_origin_strictly_rejects_path_userinfo_wildcards_insecure_and_noncanonical(self):
        for value in ("http://crm.example.com", "https://crm.example.com/", "https://user@crm.example.com",
                      "https://*.example.com", "https://127.0.0.1", "https://crm.example.com?a=1",
                      "https://crm.example.com#", "https://CRM.example.com", "https://crm.example.com:443",
                      "https://crm.example.com:0", "https://crm.example.com:99999", "https://crm.example.com\n"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                canonical_https_origin(value)
        self.assertEqual(canonical_https_origin("https://crm.example.com:8443"), "https://crm.example.com:8443")

    def test_rp_id_is_not_a_url_or_ip_and_origins_are_unique(self):
        effective = self.config["crm_authentication_profile"]["effective_values"]
        for rp_id in ("https://crm.example.com", "example.com:443", "*.example.com", "127.0.0.1", "EXAMPLE.COM"):
            effective["rp_id"] = rp_id
            self.assertTrue(any(issue.path.endswith("effective_values.rp_id") and issue.code == "VALUE_INVALID" for issue in preflight(self.config, "crm").issues))
        effective["allowed_origins"] = ["https://crm.example.com", "https://crm.example.com"]
        self.assertTrue(any(issue.path.endswith("allowed_origins") and issue.code == "VALUE_INVALID" for issue in preflight(self.config, "crm").issues))

    def test_pinned_rp_validator_is_required_and_failures_block(self):
        effective = self.config["crm_authentication_profile"]["effective_values"]
        effective["rp_id"] = "example.com"
        effective["allowed_origins"] = ["https://crm.example.com"]
        self.assertTrue(any(issue.code == "RP_VALIDATOR_REQUIRED" for issue in preflight(self.config, "crm").issues))
        calls = []
        def reject(rp_id, origin):
            calls.append((rp_id, origin))
            return False
        self.assertTrue(any(issue.code == "RP_ORIGIN_INVALID" for issue in preflight(self.config, "crm", rp_id_validator=reject).issues))
        self.assertEqual(calls, [("example.com", "https://crm.example.com")])
        def broken(rp_id, origin):
            raise ValueError("validator unavailable")
        self.assertTrue(any(issue.code == "RP_ORIGIN_INVALID" for issue in preflight(self.config, "crm", rp_id_validator=broken).issues))

    def test_policy_flags_cannot_enable_fixture_time_or_unsafe_behavior(self):
        self.config["lab_environment"]["fixture_clock_may_override_runtime"] = True
        self.config["vdt"]["authorization"]["permission_cache_enabled"] = True
        self.config["vdt"]["authentication"]["cookie_secure"] = False
        issues = preflight(self.config).issues
        for field in ("fixture_clock_may_override_runtime", "permission_cache_enabled", "cookie_secure"):
            self.assertTrue(any(issue.path.endswith(field) and issue.code == "POLICY_INVARIANT" for issue in issues))

    def test_parser_rejects_duplicates_nonfinite_and_nonobjects(self):
        for text in ('{"schema_version":"0.1","schema_version":"0.2"}', '{"x":NaN}', '[]'):
            with patch.object(Path, "open", return_value=BytesIO(text.encode())), self.assertRaises(ConfigurationError):
                load_configuration("config.json")

    def test_canonical_hash_omits_itself_and_is_stable(self):
        digest = canonical_configuration_sha256(self.config)
        self.config["crm_authentication_profile"]["canonical_config_sha256"] = digest
        self.assertEqual(canonical_configuration_sha256(self.config), digest)
        self.config["vdt"]["jobs"]["attempt_limit"] += 1
        self.assertNotEqual(canonical_configuration_sha256(self.config), digest)

    def test_missing_or_wrong_structure_never_validates(self):
        for value in ({}, None, [], {"vdt": "bad"}):
            with self.subTest(value=value):
                self.assertEqual(preflight(value).status, "BLOCKED")
