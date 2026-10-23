"""Strict, offline checks for the versioned Step 05 configuration contract.

Parsing or CONFIG_VALID proves only local configuration checks. It never means
CRM is implemented, a deployment/lab is ready, or a control has passed. No values
are copied from illustrative examples and no clock or secret is resolved here.
The CRM adapter must provide its pinned public-suffix-aware RP/origin validator;
without it CRM preflight stays BLOCKED. This module makes no network calls.
"""

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from ipaddress import ip_address
import json
from pathlib import Path
import re
from typing import Callable, Mapping
from urllib.parse import urlsplit


MAX_CONFIG_BYTES = 1_048_576
CRM_REQUIRED_FIVE = (
    "challenge_ttl_seconds", "max_attempt_limit", "session_idle_timeout_seconds",
    "rp_id", "allowed_origins",
)


@dataclass(frozen=True)
class Issue:
    path: str
    code: str
    message: str


@dataclass(frozen=True)
class PreflightResult:
    status: str
    issues: tuple[Issue, ...]
    target: str

    @property
    def valid(self) -> bool:
        return self.status == "CONFIG_VALID"

    @property
    def blocked(self) -> bool:
        return not self.valid

    def as_dict(self) -> dict:
        return {"status": self.status, "target": self.target,
                "issues": [vars(issue) for issue in self.issues]}


class ConfigurationError(ValueError):
    """A JSON document cannot be parsed safely as configuration."""


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ConfigurationError("duplicate configuration key")
        value[key] = item
    return value


def load_configuration(path: str | Path) -> dict:
    """Read a bounded UTF-8 JSON document without merging any defaults."""
    with Path(path).open("rb") as source:
        raw = source.read(MAX_CONFIG_BYTES + 1)
    if len(raw) > MAX_CONFIG_BYTES:
        raise ConfigurationError("configuration exceeds byte limit")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                           parse_constant=lambda value: (_ for _ in ()).throw(ConfigurationError("non-finite JSON number")))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ConfigurationError("invalid UTF-8 JSON configuration") from error
    if not isinstance(value, dict):
        raise ConfigurationError("configuration must be a JSON object")
    return value


def canonical_configuration_sha256(config: Mapping) -> str:
    """Hash the non-secret document with its own CRM hash field omitted."""
    payload = json.loads(json.dumps(config, allow_nan=False))
    profile = payload.get("crm_authentication_profile")
    if isinstance(profile, dict):
        profile.pop("canonical_config_sha256", None)
    return sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


# Tokens: str/nonempty string; pos/int > 0; nonneg/int >= 0; list[str];
# origin/canonical HTTPS origin; host/canonical DNS name; time/aware datetime;
# sha/lowercase SHA-256. Null is unresolved except the host-only cookie Domain.
def _fields(token: str, names: str) -> dict:
    return {name: token for name in names.split()}


AUTH = {
    **_fields("str", "application credential_method password_hasher password_work_factor_policy mfa_runtime_claim session_store session_cookie_name cookie_samesite cookie_path authentication_method_policy_ref"),
    **_fields("bool", "password_validators_required seed_passwords_allowed cookie_secure cookie_httponly csrf_required_for_unsafe_methods independent_from_crm client_clock_override_allowed"),
    **_fields("pos", "session_idle_timeout_seconds session_absolute_timeout_seconds max_attempt_limit failed_attempt_window_seconds failed_attempt_lockout_seconds"),
    "cookie_domain": "null",
}
AUTHORIZATION = {
    **_fields("bool", "deny_by_default check_current_scope_on_all_reads recheck_at_commit_export_download organization_guard_required expire_at_equal_timestamp permission_cache_enabled"),
    "seed_ref": "str",
}
EVIDENCE = {
    **_fields("pos", "max_file_bytes max_metadata_bytes max_request_bytes files_per_request max_parallel_uploads_per_principal max_parallel_uploads_per_host upload_read_timeout_seconds scan_timeout_seconds staging_orphan_grace_seconds max_staging_bytes minimum_free_disk_bytes"),
    **_fields("bool", "references_auto_fetch download_attachment_only staging_and_objects_same_filesystem committed_blob_auto_gc_enabled"),
    "download_cache_control": "str",
    "allowed_extension_mime_pairs": [{"extensions": "strings", "mime": "str", "extra_validation": "str"}],
}
SCANNER = {
    **_fields("str", "engine version_line patch_version transport socket_path signature_version freshclam_update_policy_ref error_timeout_stale_signatures encrypted_or_unscannable_content"),
    **_fields("pos", "max_parallel_scans signature_max_age_seconds resource_memory_limit_mib_estimate"),
    **_fields("bool", "clean_verdict_is_business_verification network_listener_exposed"),
}
CRM_EFFECTIVE = {
    **_fields("pos", "challenge_ttl_seconds max_attempt_limit failed_attempt_window_seconds failed_attempt_lockout_seconds session_idle_timeout_seconds session_absolute_timeout_seconds notification_delivery_max_seconds"),
    **_fields("nonneg", "reauth_max_age_seconds revocation_max_delay_seconds"),
    "rp_id": "host", "allowed_origins": "origins",
    **_fields("str", "enrollment_bootstrap_policy_ref credential_addition_policy_ref recovery_identity_verification_policy_ref recovery_approver_role_ref recovery_session_action notification_policy_ref notification_destination_ref"),
}
SCHEMA = {
    **_fields("str", "schema_version config_id created_on timezone_for_display purpose"),
    "readiness": {**_fields("str", "vdt_deployment crm_lab approved_by"), "approved_at": "time"},
    "deployment": {
        **_fields("str", "model organization_id os tls_certificate_strategy ca_trust_evidence_ref time_sync_source_ref database_dsn_secret_ref django_secret_key_ref evidence_root backup_target backup_key_secret_ref"),
        **_fields("pos", "vm_vcpu vm_ram_mib vm_disk_gib_estimate"),
        "public_origin": "origin", "allowed_hosts": "hosts", "trusted_proxy_addresses": "addresses",
    },
    "vdt": {
        "authentication": AUTH, "authorization": AUTHORIZATION, "evidence": EVIDENCE,
        "scanner": SCANNER,
        "http": _fields("pos", "application_request_timeout_seconds proxy_response_timeout_seconds request_header_timeout_seconds gunicorn_workers"),
        "database": {**_fields("pos", "major_version total_application_connection_limit shared_buffers_mib_estimate work_mem_mib_estimate statement_timeout_seconds lock_timeout_seconds bounded_transaction_retries"), "separate_migration_owner_required": "bool"},
        "jobs": {**_fields("pos", "worker_concurrency lease_seconds renew_lease_every_seconds attempt_limit job_deadline_seconds export_artifact_ttl_seconds"), **_fields("bool", "fencing_token_required publish_requires_fresh_authorization")},
        "retention": {**_fields("bool", "domain_history_auto_delete idempotency_key_tombstone_required_after_future_retention"), **_fields("str", "idempotency_results_retention backup_operator_identity_ref"), **_fields("pos", "audit_retention_days backup_interval_seconds backup_retention_count backup_rpo_seconds backup_rto_seconds")},
    },
    "crm_authentication_profile": {
        **_fields("str", "id application target_asset_id control_id status implementation_status"),
        "config_revision": "pos", "source_fixture_sha256": "sha", "canonical_config_sha256": "sha",
        "fixed_requirements": {**_fields("str", "primary_factor additional_factor user_verification"), **_fields("bool", "totp_fallback_enabled passwordless_enabled business_access_requires_both_factors password_only_enrollment_allowed password_only_recovery_allowed challenge_single_use old_credential_revoke_on_recovery")},
        "effective_values": CRM_EFFECTIVE,
        "illustrative_examples_not_effective": {**_fields("pos", "challenge_ttl_seconds max_attempt_limit session_idle_timeout_seconds"), "warning": "str"},
        "approval": {**_fields("str", "actor_id reason"), "approved_at": "time"},
    },
    "lab_environment": {
        **_fields("str", "crm_product_and_build crm_cookie_namespace network_scope_and_authorization_ref vpn_precondition_evidence_ref scope_owner_approval_ref test_data_manifest_ref export_policy_ref"),
        **_fields("origin", "crm_base_url receiver_base_url"),
        **_fields("strings", "interactive_login_routes receiver_allowed_destinations allowed_egress_protocols"),
        **_fields("time", "execution_clock fixture_clock"), "fixture_clock_may_override_runtime": "bool",
    },
    "readiness_rules": "strings",
    "runtime_test_status": _fields("str", "FLOW_01_to_10 TC_01_T01_to_T24 VALID_G_01"),
}


def valid_hostname(value: str) -> bool:
    if not isinstance(value, str) or len(value) > 253 or value != value.lower() or "." not in value:
        return False
    try:
        ip_address(value)
        return False
    except ValueError:
        pass
    return all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
               for label in value.split("."))


def canonical_https_origin(value: str) -> str:
    """Accept an exact canonical HTTPS origin; never strip unsafe URL content."""
    if not isinstance(value, str) or value.strip() != value or any(ord(char) <= 32 for char in value):
        raise ValueError("invalid origin")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or not valid_hostname(parsed.hostname)
            or parsed.username is not None or parsed.password is not None
            or parsed.path or parsed.query or parsed.fragment or "?" in value or "#" in value):
        raise ValueError("origin must be HTTPS scheme, DNS host and optional port only")
    port = parsed.port  # Reject invalid/non-numeric/out-of-range ports.
    if port == 0:
        raise ValueError("invalid origin port")
    normalized = "https://" + parsed.hostname + (f":{port}" if port not in (None, 443) else "")
    if normalized != value:
        raise ValueError("origin must already be canonical")
    return normalized


def _valid_token(value, token: str) -> bool:
    if token == "null":
        return value is None
    if token == "bool":
        return type(value) is bool
    if token in ("pos", "nonneg"):
        return type(value) is int and value >= (1 if token == "pos" else 0)
    if token == "str":
        return isinstance(value, str) and bool(value.strip())
    if token == "host":
        return valid_hostname(value)
    if token == "sha":
        return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None
    if token == "time":
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.tzinfo is not None and parsed.utcoffset() is not None
        except (AttributeError, TypeError, ValueError):
            return False
    if token == "origin":
        try:
            canonical_https_origin(value)
            return True
        except (TypeError, ValueError):
            return False
    if token in ("strings", "origins", "hosts", "addresses"):
        if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item.strip() for item in value):
            return False
        if len(value) != len(set(value)):
            return False
        if token == "origins":
            return all(_valid_token(item, "origin") for item in value)
        if token == "hosts":
            return all(valid_hostname(item) for item in value)
        if token == "addresses":
            try:
                return all(str(ip_address(item)) == item for item in value)
            except ValueError:
                return False
        return True
    raise AssertionError("unknown schema token")


def _validate(value, schema, path: str, issues: list[Issue]):
    if isinstance(schema, dict):
        if not isinstance(value, dict):
            issues.append(Issue(path, "TYPE_INVALID", "Expected an object."))
            return
        for key in sorted(set(value) - set(schema)):
            issues.append(Issue(f"{path}.{key}".lstrip("."), "UNKNOWN_KEY", "Unknown configuration key."))
        for key, child in schema.items():
            child_path = f"{path}.{key}".lstrip(".")
            if key not in value:
                issues.append(Issue(child_path, "REQUIRED_MISSING", "Required configuration key is missing."))
            else:
                _validate(value[key], child, child_path, issues)
    elif isinstance(schema, list):
        if not isinstance(value, list) or not value:
            issues.append(Issue(path, "TYPE_INVALID", "Expected a nonempty array."))
        else:
            for index, item in enumerate(value):
                _validate(item, schema[0], f"{path}[{index}]", issues)
    elif value is None and schema != "null":
        issues.append(Issue(path, "REQUIRED_UNSET", "Required value has not been set; no default was applied."))
    elif not _valid_token(value, schema):
        issues.append(Issue(path, "VALUE_INVALID", "Value violates its required type or format."))


def _get(value: Mapping, path: str):
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _relevant(path: str, target: str) -> bool:
    if target == "all":
        return True
    if path.startswith(("vdt", "deployment")) or path == "readiness.vdt_deployment":
        return target == "vdt"
    if path.startswith("crm_authentication_profile") or path == "readiness.crm_lab":
        return target in ("crm", "sc02")
    if path.startswith("lab_environment."):
        name = path.split(".")[1]
        if name in {"receiver_base_url", "receiver_allowed_destinations", "export_policy_ref", "allowed_egress_protocols"}:
            return target == "sc02"
        return target in ("crm", "sc02")
    if path == "lab_environment":
        return target in ("crm", "sc02")
    return True


def preflight(config: Mapping, target: str = "all", *,
              rp_id_validator: Callable[[str, str], bool] | None = None) -> PreflightResult:
    """Check relevant fields and return BLOCKED on any unresolved/error state.

    ``rp_id_validator(rp_id, origin)`` must be the trusted pinned CRM library's
    public-suffix-aware validator, supplied by the server adapter. It receives a
    syntactically validated canonical origin and must return exactly True. A mere
    string suffix comparison is insufficient and is deliberately not substituted.
    Checks of file ownership, release-manifest signatures, TLS/CA, live services,
    secret resolution and CRM runtime behavior belong to deployment/lab gates.
    """
    if target not in ("all", "vdt", "crm", "sc02"):
        raise ValueError("unknown preflight target")
    issues = []
    _validate(config, SCHEMA, "", issues)
    if not isinstance(config, dict):
        return PreflightResult("BLOCKED", tuple(issues), target)

    def require(path, expected):
        if _get(config, path) != expected or type(_get(config, path)) is not type(expected):
            issues.append(Issue(path, "POLICY_INVARIANT", "Value violates the selected policy."))

    fixed = {
        "schema_version": "0.1", "timezone_for_display": "Asia/Bangkok",
        "deployment.model": "ONE_SME_ONE_DEPLOYMENT",
        "vdt.authentication.application": "VDT",
        "vdt.authentication.credential_method": "LOCAL_USERNAME_PASSWORD",
        "vdt.authentication.password_hasher": "django.contrib.auth.hashers.PBKDF2PasswordHasher",
        "vdt.authentication.session_store": "POSTGRESQL",
        "vdt.authentication.session_cookie_name": "__Host-vdt_session",
        "vdt.authentication.cookie_samesite": "Lax", "vdt.authentication.cookie_path": "/",
        "vdt.authentication.cookie_domain": None,
        "vdt.authentication.mfa_runtime_claim": "NOT_IMPLEMENTED_OR_VERIFIED",
        "vdt.evidence.download_cache_control": "private, no-store",
        "vdt.scanner.engine": "ClamAV", "vdt.scanner.transport": "LOCAL_UNIX_SOCKET",
        "vdt.scanner.error_timeout_stale_signatures": "FAIL_CLOSED",
        "vdt.scanner.encrypted_or_unscannable_content": "REJECT",
        "crm_authentication_profile.application": "CRM",
        "crm_authentication_profile.fixed_requirements.primary_factor": "PASSWORD",
        "crm_authentication_profile.fixed_requirements.additional_factor": "WEBAUTHN",
        "crm_authentication_profile.fixed_requirements.user_verification": "required",
    }
    for path in (
        "vdt.authentication.password_validators_required vdt.authentication.cookie_secure vdt.authentication.cookie_httponly vdt.authentication.csrf_required_for_unsafe_methods vdt.authentication.independent_from_crm "
        "vdt.authorization.deny_by_default vdt.authorization.check_current_scope_on_all_reads vdt.authorization.recheck_at_commit_export_download vdt.authorization.organization_guard_required vdt.authorization.expire_at_equal_timestamp "
        "vdt.evidence.download_attachment_only vdt.evidence.staging_and_objects_same_filesystem vdt.database.separate_migration_owner_required vdt.jobs.fencing_token_required vdt.jobs.publish_requires_fresh_authorization "
        "vdt.retention.idempotency_key_tombstone_required_after_future_retention crm_authentication_profile.fixed_requirements.business_access_requires_both_factors crm_authentication_profile.fixed_requirements.challenge_single_use crm_authentication_profile.fixed_requirements.old_credential_revoke_on_recovery"
    ).split():
        fixed[path] = True
    for path in (
        "vdt.authentication.seed_passwords_allowed vdt.authentication.client_clock_override_allowed vdt.authorization.permission_cache_enabled vdt.evidence.references_auto_fetch vdt.evidence.committed_blob_auto_gc_enabled "
        "vdt.scanner.clean_verdict_is_business_verification vdt.scanner.network_listener_exposed vdt.retention.domain_history_auto_delete lab_environment.fixture_clock_may_override_runtime "
        "crm_authentication_profile.fixed_requirements.totp_fallback_enabled crm_authentication_profile.fixed_requirements.passwordless_enabled crm_authentication_profile.fixed_requirements.password_only_enrollment_allowed crm_authentication_profile.fixed_requirements.password_only_recovery_allowed"
    ).split():
        fixed[path] = False
    for path, expected in fixed.items():
        require(path, expected)

    # These are selected Step 05 ceilings, never implicit fallback values.
    ceilings = {
        "max_file_bytes": 20 * 1024 ** 2, "max_metadata_bytes": 64 * 1024,
        "max_request_bytes": 21 * 1024 ** 2, "files_per_request": 1,
        "max_parallel_uploads_per_principal": 1, "max_parallel_uploads_per_host": 2,
    }
    for name, ceiling in ceilings.items():
        path = "vdt.evidence." + name
        value = _get(config, path)
        if type(value) is int and value > ceiling:
            issues.append(Issue(path, "LIMIT_EXCEEDED", "Value exceeds the selected intake limit."))
    require("vdt.scanner.max_parallel_scans", 1)
    for larger, smaller, strict in (
        ("vdt.authentication.session_absolute_timeout_seconds", "vdt.authentication.session_idle_timeout_seconds", False),
        ("crm_authentication_profile.effective_values.session_absolute_timeout_seconds", "crm_authentication_profile.effective_values.session_idle_timeout_seconds", False),
        ("vdt.http.proxy_response_timeout_seconds", "vdt.http.application_request_timeout_seconds", True),
        ("vdt.evidence.max_request_bytes", "vdt.evidence.max_file_bytes", True),
        ("vdt.jobs.lease_seconds", "vdt.jobs.renew_lease_every_seconds", True),
    ):
        high, low = _get(config, larger), _get(config, smaller)
        if type(high) is int and type(low) is int and (high < low or (strict and high == low)):
            issues.append(Issue(larger, "LIMIT_RELATION_INVALID", "Related limits are inconsistent."))
    origin, hosts = _get(config, "deployment.public_origin"), _get(config, "deployment.allowed_hosts")
    if _valid_token(origin, "origin") and isinstance(hosts, list) and urlsplit(origin).hostname not in hosts:
        issues.append(Issue("deployment.allowed_hosts", "ORIGIN_HOST_NOT_ALLOWED", "Public origin host must be in allowed_hosts."))
    for path in ("readiness.vdt_deployment", "readiness.crm_lab"):
        require(path, "APPROVED")
    require("crm_authentication_profile.status", "APPROVED")

    rp_id = _get(config, "crm_authentication_profile.effective_values.rp_id")
    origins = _get(config, "crm_authentication_profile.effective_values.allowed_origins")
    if _valid_token(rp_id, "host") and _valid_token(origins, "origins"):
        if rp_id_validator is None:
            issues.append(Issue("crm_authentication_profile.effective_values.rp_id", "RP_VALIDATOR_REQUIRED", "Pinned CRM RP/origin validation has not been supplied."))
        else:
            for origin in origins:
                try:
                    accepted = rp_id_validator(rp_id, origin) is True
                except Exception:
                    accepted = False
                if not accepted:
                    issues.append(Issue("crm_authentication_profile.effective_values.allowed_origins", "RP_ORIGIN_INVALID", "RP ID and origin relationship was not validated."))
                    break
    issues = tuple(issue for issue in issues if _relevant(issue.path, target))
    return PreflightResult("BLOCKED" if issues else "CONFIG_VALID", issues, target)
