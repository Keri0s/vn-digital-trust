"""Isolated PostgreSQL + Django HTTP auth checks, using only synthetic accounts.

Run via compose.auth-test.yaml. This runner refuses the normal local database
host. Requests use the restricted vdt_app database role. Owner access is retained
only for deliberate expiry/revocation fault injection in the disposable test DB.
It does not assert that browser TLS, CRM, WebAuthn or domain workflows passed.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import secrets
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


class CheckFailure(Exception):
    pass


def require(ok, message):
    if not ok:
        raise CheckFailure(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    # These checks precede every database connection and schema mutation.
    expected = {"VDT_AUTH_INTEGRATION_TEST": "true", "VDT_LOCAL_FOUNDATION_ONLY": "true",
                "PGHOST": "testdb", "PGDATABASE": "vdt_step06", "PGUSER": "vdt_owner"}
    if any(os.environ.get(key) != value for key, value in expected.items()):
        raise SystemExit("Refused: use the isolated compose.auth-test.yaml testdb service with explicit integration opt-in.")

    import psycopg
    import database
    params = database.parameters()
    checks = []

    def record(name, work):
        try:
            work()
        except CheckFailure as error:
            checks.append({"check": name, "passed": False, "detail": str(error)})
        except Exception as error:
            # Exception text/tracebacks can include database values or payloads.
            checks.append({"check": name, "passed": False, "detail": type(error).__name__})
        else:
            checks.append({"check": name, "passed": True})

    def write_result(setup_error=None):
        result = {"recorded_at": datetime.now(timezone.utc).isoformat(),
                  "scope": "DISPOSABLE_POSTGRESQL_DJANGO_AUTH_HTTP",
                  "database_host": "testdb", "http_database_role": "vdt_app",
                  "actual_browser_TLS": "NOT_RUN", "CRM_FLOW_TC_VALID_G": "NOT_RUN",
                  "synthetic_account_only": True, "checks": checks,
                  "passed": sum(item["passed"] for item in checks),
                  "failed": sum(not item["passed"] for item in checks)}
        if setup_error:
            result["setup_error"] = setup_error
            result["failed"] += 1
        serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized, encoding="utf-8")
        print(serialized)
        return bool(result["failed"])

    owner = None
    try:
        owner = psycopg.connect(**params, autocommit=True)
        # A persistent test database with accounts is not an acceptable target.
        exists = owner.execute("SELECT to_regclass('vdt.app_user')").fetchone()[0]
        if exists and owner.execute("SELECT EXISTS(SELECT 1 FROM vdt.app_user)").fetchone()[0]:
            raise CheckFailure("Test database already contains an account; recreate only the disposable testdb service.")
        database.migrate(params)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vdt.settings")
        import django
        django.setup()
        from django.conf import settings
        from django.core.management import call_command
        from django.contrib.auth.hashers import check_password
        from django.db import connection, connections
        from django.test import Client
        from vdt.core.local_bootstrap import BootstrapError, provision_admin
        from vdt.authn import service
        import yaml
        from jsonschema import Draft202012Validator, FormatChecker

        call_command("seed_rbac_catalog", stdout=io.StringIO())
        username = "synthetic-auth-check"
        password = secrets.token_urlsafe(36) + "-T7"
        new_password = secrets.token_urlsafe(36) + "-N8"
        wrong_password = secrets.token_urlsafe(36) + "-W9"
        admin = provision_admin(username=username, display_name="Synthetic integration administrator", password=password)
        user_id = admin.user_id
        org_id = admin.organization_id
        snapshot = owner.execute("SELECT password_hash FROM vdt.app_user WHERE id=%s", (user_id,)).fetchone()[0]
        record("Bootstrap stores a verifiable password hash without plaintext", lambda: require(
            check_password(password, snapshot) and snapshot != password, "Password was not safely hashed."))
        record("Bootstrap creates one synthetic admin and two branches", lambda: require(
            owner.execute("SELECT count(*) FROM vdt.app_user").fetchone()[0] == 1
            and owner.execute("SELECT count(*) FROM vdt.branch").fetchone()[0] == 2,
            "Unexpected account or branch count."))
        record("Bootstrap does not create business approvals or CRM profiles", lambda: require(
            owner.execute("SELECT (SELECT count(*) FROM vdt.authentication_profile_version)+(SELECT count(*) FROM vdt.priority_decision)+(SELECT count(*) FROM vdt.verification_decision)").fetchone()[0] == 0,
            "Unexpected business or CRM rows."))

        def repeated_bootstrap():
            before = owner.execute("SELECT count(*) FROM vdt.audit_event").fetchone()[0]
            try:
                provision_admin(username="second-admin", display_name="Second synthetic", password=password)
            except BootstrapError as error:
                require(error.code == "ADMIN_ALREADY_PROVISIONED", "Unexpected repeat-bootstrap refusal.")
            else:
                raise CheckFailure("Repeat bootstrap unexpectedly succeeded.")
            require(owner.execute("SELECT count(*) FROM vdt.audit_event").fetchone()[0] == before,
                    "Refused bootstrap changed audit rows.")
        record("Bootstrap refuses a second administrator atomically", repeated_bootstrap)

        # HTTP operations establish a real restricted login, not SET ROLE under
        # an owner connection. Keep owner only for test fault injection below.
        connection.close()
        connection.settings_dict["USER"] = "vdt_app"
        connection.settings_dict["PASSWORD"] = os.environ["VDT_DB_APP_PASSWORD"]
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_user, rolsuper FROM pg_roles WHERE rolname=current_user")
            runtime_identity = cursor.fetchone()
        record("All HTTP requests use a non-superuser vdt_app connection", lambda: require(
            runtime_identity == ("vdt_app", False), "Runtime database connection is not restricted."))
        require(service.policy().max_attempts == 5, "Expected the explicit five-attempt local policy.")
        contract = yaml.safe_load((ROOT / "docs/design/openapi-v0.1.yaml").read_text(encoding="utf-8"))
        session_schema = contract["components"]["schemas"]["Session"]
        session_validator = Draft202012Validator(session_schema, format_checker=FormatChecker())
        origin = "https://localhost:8443"
        cookie_name = settings.SESSION_COOKIE_NAME
        proxy_secret = settings.VDT_AUTH_PROXY_SECRET
        state = {"password": password}
        all_secret_values = [password, new_password, wrong_password, snapshot, proxy_secret,
                             settings.SECRET_KEY, os.environ["VDT_DB_APP_PASSWORD"], os.environ["PGPASSWORD"]]

        def client():
            return Client(enforce_csrf_checks=True, raise_request_exception=False)

        def headers(ip="198.51.100.10"):
            return dict(HTTP_HOST="localhost:8443", HTTP_X_VDT_PROXY_SECRET=proxy_secret,
                        HTTP_X_VDT_CLIENT_IP=ip, HTTP_ORIGIN=origin)

        def get(c, path="/api/v1/auth/session", *, ip="198.51.100.10", overrides=None):
            options = headers(ip)
            options.update(overrides or {})
            return c.get(path, secure=True, **options)

        def csrf(c, ip="198.51.100.10"):
            response = get(c, "/api/v1/auth/csrf", ip=ip)
            require(response.status_code == 200, "CSRF endpoint failed.")
            token = response.json()["csrf_token"]
            all_secret_values.append(token)
            return token

        def mutate(c, path, payload=None, *, method="post", ip="198.51.100.10", overrides=None, include_csrf=True):
            options = headers(ip)
            if include_csrf:
                options["HTTP_X_CSRFTOKEN"] = csrf(c, ip)
            options.update(overrides or {})
            return getattr(c, method)(path, data=json.dumps(payload or {}),
                content_type="application/json", secure=True, **options)

        def clear_rates():
            owner.execute("UPDATE vdt.auth_rate_bucket SET failures=0,window_started_at=clock_timestamp(),locked_until=NULL")

        def login(c=None, *, name=username, secret=None, ip="198.51.100.10"):
            c = c or client()
            response = mutate(c, "/api/v1/auth/session", {"username": name,
                "password": state["password"] if secret is None else secret}, ip=ip)
            if response.status_code == 200:
                all_secret_values.extend([c.cookies[cookie_name].value, response.json()["csrf_token"]])
            return c, response

        def authenticated(*, ip="198.51.100.10"):
            clear_rates()
            c, response = login(ip=ip)
            require(response.status_code == 200, "Valid login did not return 200.")
            return c, response

        def session_row(c):
            return owner.execute("SELECT id,issued_at,expires_at,last_seen_at,revoked_at FROM vdt.vdt_session WHERE session_token_hash=%s",
                                 (service.token_hash(c.cookies[cookie_name].value),)).fetchone()

        def edit_guarded(query, values):
            with owner.transaction():
                owner.execute("SELECT vdt.acquire_authorization_guard(%s)", (org_id,))
                owner.execute(query, values)
                owner.execute("UPDATE vdt.authorization_guard SET version=version+1 WHERE organization_id=%s", (org_id,))

        def valid_login():
            c, response = authenticated()
            session_validator.validate(response.json())
            require(set(response.json()["permissions"]) == {"organization.manage", "roles.assign", "users.manage"},
                    "Session permissions exceed or omit administrator permissions.")
            require(response["Cache-Control"] == "no-store" and response["X-Request-ID"], "Missing privacy/correlation headers.")
            cookie = response.cookies[cookie_name]
            require(bool(cookie["secure"]) and bool(cookie["httponly"]) and cookie["samesite"] == "Lax"
                    and cookie["path"] == "/" and not cookie["domain"], "Session cookie attributes are unsafe.")
            require(owner.execute("SELECT count(*) FROM vdt.vdt_session WHERE session_token_hash=%s",
                                  (c.cookies[cookie_name].value,)).fetchone()[0] == 0,
                    "Raw session key was stored in domain session table.")
        record("Valid login matches Session DTO, three admin permissions and secure cookie", valid_login)

        def no_get_touch():
            c, _ = authenticated()
            before = session_row(c)
            response = get(c)
            after = session_row(c)
            require(response.status_code == 200 and before[3] == after[3], "Session GET renewed the idle timer.")
        record("Session GET does not renew idle expiry", no_get_touch)

        def invalid_credentials():
            clear_rates()
            _, wrong = login(secret=wrong_password, ip="198.51.100.11")
            _, unknown = login(name="nonexistent-synthetic-user", secret=wrong_password, ip="198.51.100.12")
            edit_guarded("UPDATE vdt.app_user SET status='DISABLED',version=version+1 WHERE id=%s", (user_id,))
            try:
                _, disabled = login(ip="198.51.100.13")
            finally:
                edit_guarded("UPDATE vdt.app_user SET status='ACTIVE',version=version+1 WHERE id=%s", (user_id,))
            for response in (wrong, unknown, disabled):
                require(response.status_code == 401 and response.json()["code"] == "INVALID_CREDENTIALS",
                        "Credential failures did not share a generic 401 response.")
            require(wrong.json()["title"] == unknown.json()["title"] == disabled.json()["title"], "Credential responses disclose account status.")
        record("Wrong, unknown and disabled credentials share one generic denial", invalid_credentials)

        def missing_csrf():
            clear_rates()
            response = mutate(client(), "/api/v1/auth/session", {"username": username, "password": state["password"]}, include_csrf=False)
            require(response.status_code == 403 and response.json()["code"] == "CSRF_FAILED", "Missing CSRF was accepted.")
        record("Login requires CSRF even without an existing session", missing_csrf)

        def untrusted_origin():
            response = mutate(client(), "/api/v1/auth/session", {"username": username, "password": state["password"]},
                              overrides={"HTTP_ORIGIN": "https://outside.invalid"})
            require(response.status_code == 403 and response.json()["code"] == "ORIGIN_DENIED", "Untrusted origin was accepted.")
        record("Cross-origin login is denied", untrusted_origin)

        def bad_proxy():
            response = get(client(), "/api/v1/auth/csrf", overrides={"HTTP_X_VDT_PROXY_SECRET": "invalid-proxy"})
            require(response.status_code == 403 and response.json()["code"] == "TRUSTED_PROXY_REQUIRED", "Untrusted proxy was accepted.")
            response = get(client(), "/api/v1/auth/csrf", overrides={"HTTP_X_VDT_CLIENT_IP": "1.2.3.4, 5.6.7.8"})
            require(response.status_code == 403, "Ambiguous source IP was accepted.")
        record("Proxy secret and one literal source IP are required", bad_proxy)

        def no_domain_bypass():
            require(get(client(), "/api/v1/assessments").status_code == 401, "Anonymous domain API was accessible.")
            c, _ = authenticated()
            require(get(c, "/api/v1/assessments").status_code == 403, "Administrator gained domain assessment access.")
            require(get(c, "/api/v1/evidence-items").status_code == 503, "Unimplemented domain API reported success.")
        record("Authentication gate protects domain API while unfinished operations stay unavailable", no_domain_bypass)

        def idle_expiry():
            c, _ = authenticated()
            sid = session_row(c)[0]
            edit_guarded("UPDATE vdt.vdt_session SET last_seen_at=clock_timestamp()-(%s*interval '1 second'),version=version+1 WHERE id=%s",
                         (service.policy().idle_timeout_seconds + 1, sid))
            require(get(c).status_code == 401, "Idle-expired session remained usable.")
            require(owner.execute("SELECT revoked_at IS NOT NULL FROM vdt.vdt_session WHERE id=%s", (sid,)).fetchone()[0], "Expired session was not revoked.")
        record("Idle expiry revokes the database session", idle_expiry)

        def absolute_expiry():
            c, _ = authenticated()
            sid = session_row(c)[0]
            edit_guarded("UPDATE vdt.vdt_session SET issued_at=clock_timestamp()-interval '2 days',expires_at=clock_timestamp()-interval '1 second',version=version+1 WHERE id=%s", (sid,))
            require(get(c).status_code == 401, "Absolute-expired session remained usable.")
        record("Absolute expiry is enforced independently of Django cookie expiry", absolute_expiry)

        def disabled_session():
            c, _ = authenticated()
            edit_guarded("UPDATE vdt.app_user SET status='DISABLED',version=version+1 WHERE id=%s", (user_id,))
            try:
                require(get(c).status_code == 401, "Disabled account retained its existing session.")
            finally:
                edit_guarded("UPDATE vdt.app_user SET status='ACTIVE',version=version+1 WHERE id=%s", (user_id,))
        record("Disabling an account invalidates its existing session", disabled_session)

        def revoke_assignment():
            c, _ = authenticated()
            edit_guarded("UPDATE vdt.role_assignment SET revoked_at=clock_timestamp(),version=version+1 WHERE id=%s", (admin.assignment_id,))
            try:
                response = get(c)
                require(response.status_code == 200 and response.json()["permissions"] == [], "Revoked grant remained in current permissions.")
            finally:
                edit_guarded("UPDATE vdt.role_assignment SET revoked_at=NULL,version=version+1 WHERE id=%s", (admin.assignment_id,))
        record("Role revocation is reflected on the next session read", revoke_assignment)

        def logout_and_replay():
            c, _ = authenticated()
            key = c.cookies[cookie_name].value
            response = mutate(c, "/api/v1/auth/session", method="delete")
            require(response.status_code == 204 and response.cookies[cookie_name]["max-age"] == 0, "Logout did not clear the cookie.")
            replay = client()
            replay.cookies[cookie_name] = key
            require(get(replay).status_code == 401, "A logged-out cookie could be replayed.")
        record("Logout clears the secure cookie and prevents replay", logout_and_replay)

        def password_rotation():
            first, _ = authenticated(ip="198.51.100.31")
            second, response = login(ip="198.51.100.32")
            require(response.status_code == 200, "Second session was not established.")
            original_key = first.cookies[cookie_name].value
            original_deadline = session_row(first)[2]
            denied = mutate(first, "/api/v1/auth/password", {"current_password": wrong_password, "new_password": new_password}, ip="198.51.100.31")
            require(denied.status_code == 401, "Password changed without current credential.")
            response = mutate(first, "/api/v1/auth/password", {"current_password": state["password"], "new_password": new_password}, ip="198.51.100.31")
            require(response.status_code == 204, "Valid password change failed.")
            state["password"] = new_password
            require(first.cookies[cookie_name].value != original_key, "Password change did not rotate the session key.")
            require(session_row(first)[2] == original_deadline, "Password change extended absolute session lifetime.")
            require(get(first).status_code == 200 and get(second).status_code == 401, "Password change did not preserve only the rotated session.")
            replay = client()
            replay.cookies[cookie_name] = original_key
            require(get(replay).status_code == 401, "Pre-rotation session key could be replayed.")
            _, old = login(secret=password, ip="198.51.100.33")
            _, new = login(secret=new_password, ip="198.51.100.34")
            require(old.status_code == 401 and new.status_code == 200, "Password replacement was not effective.")
        record("Password change verifies current password, rotates session and revokes other sessions", password_rotation)

        def account_rate_limit():
            clear_rates()
            for i in range(5):
                _, response = login(secret=wrong_password, ip=f"198.51.100.{80+i}")
                require(response.status_code == 401, "Expected five credential-denial attempts.")
            _, response = login(ip="198.51.100.90")
            require(response.status_code == 429 and int(response["Retry-After"]) > 0,
                    "Account rate limit did not apply across source addresses.")
        record("Five account failures block the next attempt across source IPs", account_rate_limit)

        def source_rate_limit():
            clear_rates()
            for i in range(5):
                _, response = login(name=f"missing-source-{i}", secret=wrong_password, ip="198.51.100.100")
                require(response.status_code == 401, "Expected five source credential-denial attempts.")
            _, response = login(ip="198.51.100.100")
            require(response.status_code == 429 and response.json()["code"] == "RATE_LIMITED", "Source rate limit did not span account names.")
            clear_rates()
        record("Five source failures block attempts across account names", source_rate_limit)

        def concurrent_rate_limit():
            clear_rates()
            identity = "missing-concurrent-account"
            source = "198.51.100.110"

            def attempt(_):
                # ConnectionHandler is thread-local. Set credentials explicitly
                # rather than assuming the main thread connection is inherited.
                worker = connections["default"]
                worker.settings_dict["USER"] = "vdt_app"
                worker.settings_dict["PASSWORD"] = os.environ["VDT_DB_APP_PASSWORD"]
                try:
                    with worker.cursor() as cursor:
                        cursor.execute("SELECT current_user")
                        require(cursor.fetchone()[0] == "vdt_app", "Concurrent worker is not restricted.")
                    _, response = login(name=identity, secret=wrong_password, ip=source)
                    return response.status_code
                finally:
                    worker.close()

            with ThreadPoolExecutor(max_workers=8) as executor:
                statuses = list(executor.map(attempt, range(8)))
            require(statuses.count(401) == 5 and statuses.count(429) == 3,
                    "Concurrent attempts did not serialize to five denials and three rate limits.")
            keys = [service._bucket_key("login.account", identity), service._bucket_key("login.source", source)]
            rows = owner.execute("SELECT failures FROM vdt.auth_rate_bucket WHERE bucket_key=ANY(%s)", (keys,)).fetchall()
            require(len(rows) == 2 and all(row[0] == 5 for row in rows), "Concurrent limiter counters exceeded the threshold or lost updates.")
            clear_rates()
        record("Concurrent login attempts atomically enforce the five-failure account/source limit", concurrent_rate_limit)

        def audit_privacy():
            audit_rows = owner.execute("SELECT row_to_json(a)::text FROM vdt.audit_event a").fetchall()
            history_rows = owner.execute("SELECT state_snapshot::text FROM vdt.mutable_entity_history").fetchall()
            rate_rows = owner.execute("SELECT bucket_key FROM vdt.auth_rate_bucket").fetchall()
            serialized = "\n".join(row[0] for row in audit_rows + history_rows + rate_rows)
            require(not any(value and value in serialized for value in all_secret_values), "A credential/token/hash leaked into audit or history.")
            require("198.51.100." not in serialized, "Raw source addresses leaked into audit or rate bucket identities.")
            actions = {row[0] for row in owner.execute("SELECT DISTINCT action FROM vdt.audit_event").fetchall()}
            require({"local.admin.bootstrap", "auth.login", "auth.logout", "auth.password", "auth.session.invalidate"} <= actions,
                    "Expected authentication audit actions are absent.")
        record("Audit/history/rate metadata exclude credentials, tokens and raw source IPs", audit_privacy)

        connection.close()
        return write_result()
    except CheckFailure as error:
        return write_result(str(error))
    except Exception as error:
        return write_result(type(error).__name__)
    finally:
        if owner is not None:
            owner.close()


if __name__ == "__main__":
    raise SystemExit(main())
