"""One-time, local-only administrator provisioning; credentials never leave memory.

This is an operator bootstrap, not a business approval. No domain assessment,
CRM account, authentication profile or SME approval is created here.
"""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import unicodedata
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import connections, transaction

from vdt.core.models import AppUser
from vdt.core.rbac_catalog import catalog_id, canonical_hash, load_catalog, plan_catalog


BOOTSTRAP_LOCK_KEY = 0x5644540000060001
BRANCHES = (("BR-HCM", "Trụ sở HCM — giả lập"),
            ("BR-DN", "Chi nhánh Đà Nẵng — giả lập"))
SCOPE_DESCRIPTION = "Local bootstrap administrator; organization administration only."


class BootstrapError(ValueError):
    def __init__(self, code, detail):
        self.code = code
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True)
class BootstrapResult:
    username: str
    user_id: str
    organization_id: str
    assignment_id: str
    access_expires_at: str | None


def _text(value, *, label, maximum):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise BootstrapError("INVALID_INPUT", f"{label} must contain 1–{maximum} characters.")
    if value != value.strip() or any(unicodedata.category(c).startswith("C") for c in value):
        raise BootstrapError("INVALID_INPUT", f"{label} cannot contain control characters or outer whitespace.")
    return value


def validate_inputs(*, username, display_name, password, organization_code, organization_name):
    """Validate identifiers and Django password rules without database writes."""
    username = AppUser.normalize_username(username)
    username = _text(username, label="Username", maximum=150)
    UnicodeUsernameValidator()(username)
    display_name = _text(display_name, label="Display name", maximum=200)
    organization_code = _text(organization_code, label="Organization code", maximum=100)
    organization_name = _text(organization_name, label="Organization name", maximum=200)
    if not isinstance(password, str) or not password.strip() or not 12 <= len(password) <= 1024:
        raise BootstrapError("INVALID_PASSWORD", "Password must contain 12–1024 characters.")
    # Do not strip/normalize passwords: the exact entered value is hashed.
    validate_password(password, user=AppUser(login_name=username, display_name=display_name))
    return username, display_name, organization_code, organization_name


def require_local_database(using="default"):
    enabled = getattr(settings, "VDT_LOCAL_FOUNDATION_ONLY",
                      os.environ.get("VDT_LOCAL_FOUNDATION_ONLY", "").lower() == "true")
    if enabled is not True:
        raise BootstrapError("LOCAL_OPT_IN_REQUIRED", "Set VDT_LOCAL_FOUNDATION_ONLY=true for this local lab.")
    database = connections[using]
    if database.vendor != "postgresql":
        raise BootstrapError("POSTGRESQL_REQUIRED", "Bootstrap requires the migrated PostgreSQL local lab.")
    with database.cursor() as cursor:
        cursor.execute("SELECT current_database()")
        if cursor.fetchone()[0] != "vdt_step06":
            raise BootstrapError("LOCAL_DATABASE_REQUIRED", "Bootstrap is restricted to database vdt_step06.")
    return database


def _append_history(cursor, *, kind, entity_id, actor_id, scope_id, state, version=1):
    # Only explicit public state is passed here, never the AppUser model/password.
    cursor.execute("""INSERT INTO vdt.mutable_entity_history
        (id, entity_kind, entity_id, entity_version, schema_version, effective_at,
         actor_id, scope_id, state_snapshot, content_hash)
        VALUES (%s,%s,%s,%s,'LOCAL-BOOTSTRAP-v0.1',clock_timestamp(),%s,%s,%s::jsonb,%s)""",
        [uuid4(), kind, entity_id, version, actor_id, scope_id,
         json.dumps(state, ensure_ascii=False), canonical_hash(state)])


def provision_admin(*, username, display_name, password, organization_code="ORG-ABC",
                    organization_name="ABC Trading (lab)", using="default"):
    """Create the first administrator atomically; caller supplies password in memory.

    Refuses any existing account, organization/branch drift, incomplete catalog,
    or wrong database. The initial grant starts at the database clock and has no
    assignment expiry; authenticated sessions still expire independently. Calling
    inside an outer atomic block is supported for rollback-only integration tests.
    """
    database = require_local_database(using)
    username, display_name, organization_code, organization_name = validate_inputs(
        username=username, display_name=display_name, password=password,
        organization_code=organization_code, organization_name=organization_name)
    catalog = load_catalog(Path(settings.BASE_DIR) / "docs/design/rbac-seed-v0.1.json")
    password_hash = make_password(password)
    user_id, scope_id, assignment_id = uuid4(), uuid4(), uuid4()
    with transaction.atomic(using=using):
        with database.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout = '5s'")
            cursor.execute("SET LOCAL statement_timeout = '30s'")
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", [BOOTSTRAP_LOCK_KEY])
            cursor.execute("SELECT id, code, name FROM vdt.organization")
            organizations = cursor.fetchall()
            if organizations and (len(organizations) != 1 or organizations[0][1:] != (organization_code, organization_name)):
                raise BootstrapError("ORGANIZATION_MISMATCH", "Existing organization differs from the requested local lab.")
            new_organization = not organizations
            organization_id = organizations[0][0] if organizations else uuid4()
            if new_organization:
                cursor.execute("INSERT INTO vdt.organization (id,code,name) VALUES (%s,%s,%s)",
                               [organization_id, organization_code, organization_name])
            cursor.execute("""INSERT INTO vdt.authorization_guard (id,organization_id)
                VALUES (%s,%s) ON CONFLICT (organization_id) DO NOTHING""", [uuid4(), organization_id])
            cursor.execute("SELECT vdt.acquire_authorization_guard(%s)", [organization_id])
            cursor.fetchone()
            # The guard is held before locking users or assignments. Table locks
            # also protect the zero-user bootstrap condition from other writers.
            cursor.execute("""LOCK TABLE vdt.app_user, vdt.branch, vdt.role,
                vdt.permission, vdt.role_permission, vdt.role_assignment IN SHARE ROW EXCLUSIVE MODE""")
            cursor.execute("SELECT EXISTS (SELECT 1 FROM vdt.app_user)")
            if cursor.fetchone()[0]:
                raise BootstrapError("ADMIN_ALREADY_PROVISIONED", "An account already exists. Bootstrap never resets or adds an administrator.")
            cursor.execute("SELECT id,code,description FROM vdt.permission")
            permission_rows = cursor.fetchall()
            cursor.execute("SELECT id,code,description FROM vdt.role")
            role_rows = cursor.fetchall()
            cursor.execute("SELECT id,role_id,permission_id FROM vdt.role_permission")
            plan = plan_catalog(catalog, permission_rows, role_rows, cursor.fetchall())
            if plan.changes:
                raise BootstrapError("CATALOG_INCOMPLETE", "Run seed_rbac_catalog before provisioning the administrator.")
            cursor.execute("SELECT id,organization_id,code,name,active FROM vdt.branch")
            branch_rows = cursor.fetchall()
            expected_names = dict(BRANCHES)
            for branch in branch_rows:
                if (branch[1] != organization_id or branch[2] not in expected_names
                        or branch[3] != expected_names[branch[2]] or branch[4] is not True):
                    raise BootstrapError("BRANCH_MISMATCH", "Existing branches differ from the synthetic local lab.")
            existing_codes = {row[2] for row in branch_rows}
            new_branches = []
            for code, name in BRANCHES:
                if code not in existing_codes:
                    branch_id = uuid4()
                    cursor.execute("INSERT INTO vdt.branch (id,organization_id,code,name) VALUES (%s,%s,%s,%s)",
                                   [branch_id, organization_id, code, name])
                    new_branches.append((branch_id, code, name))
            cursor.execute("""INSERT INTO vdt.app_user
                (id,organization_id,login_name,display_name,status,password_hash)
                VALUES (%s,%s,%s,%s,'ACTIVE',%s)""",
                [user_id, organization_id, username, display_name, password_hash])
            selectors = {"organization_id": str(organization_id), "branch_ids": [],
                         "system_ids": [], "asset_ids": [], "data_asset_ids": [],
                         "scenario_ids": [], "assessment_ids": []}
            scope_state = {"scope_kind": "ORGANIZATION", "description": SCOPE_DESCRIPTION,
                           "selectors": selectors}
            cursor.execute("""INSERT INTO vdt.scope
                (id,organization_id,scope_kind,description,content_hash)
                VALUES (%s,%s,'ORGANIZATION',%s,%s)""",
                [scope_id, organization_id, SCOPE_DESCRIPTION, canonical_hash(scope_state)])
            # No scope_branch/scope_object or user_branch rows: admin authority
            # is organization administration and does not imply domain access.
            cursor.execute("SELECT clock_timestamp()")
            valid_from = cursor.fetchone()[0]
            expires_at = None
            role_id = catalog_id("role", "VDT_ADMIN")
            cursor.execute("""INSERT INTO vdt.role_assignment
                (id,user_id,role_id,scope_id,valid_from,access_expires_at,granted_by)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                [assignment_id, user_id, role_id, scope_id, valid_from, expires_at, user_id])
            cursor.execute("""UPDATE vdt.authorization_guard SET version=version+1
                WHERE organization_id=%s RETURNING version""", [organization_id])
            authorization_version = cursor.fetchone()[0]
            if new_organization:
                _append_history(cursor, kind="organization", entity_id=organization_id,
                    actor_id=user_id, scope_id=scope_id, state={"id": str(organization_id),
                    "code": organization_code, "name": organization_name, "version": 1, "synthetic": True})
            for branch_id, code, name in new_branches:
                _append_history(cursor, kind="branch", entity_id=branch_id,
                    actor_id=user_id, scope_id=scope_id, state={"id": str(branch_id),
                    "organization_id": str(organization_id), "code": code, "name": name,
                    "active": True, "version": 1, "synthetic": True})
            _append_history(cursor, kind="user", entity_id=user_id, actor_id=user_id,
                scope_id=scope_id, state={"id": str(user_id), "organization_id": str(organization_id),
                "username": username, "display_name": display_name, "status": "ACTIVE", "version": 1})
            _append_history(cursor, kind="role_assignment", entity_id=assignment_id,
                actor_id=user_id, scope_id=scope_id, state={"id": str(assignment_id), "user_id": str(user_id),
                "role_id": role_id, "scope_id": str(scope_id), "valid_from": valid_from.isoformat(),
                "access_expires_at": None, "granted_by": str(user_id),
                "revoked_at": None, "version": 1})
            cursor.execute("""INSERT INTO vdt.audit_event
                (id,actor_id,action,target_kind,target_id,outcome,reason_code,
                 correlation_id,scope_id,authorization_version,gate_checked_at,safe_metadata)
                VALUES (%s,%s,'local.admin.bootstrap','user',%s,'ALLOWED',
                'LOCAL_OPERATOR_BOOTSTRAP',%s,%s,%s,clock_timestamp(),%s::jsonb)""",
                [uuid4(), user_id, user_id, uuid4(), scope_id, authorization_version,
                 json.dumps({"synthetic_environment": True, "role_code": "VDT_ADMIN",
                     "assignment_expiry": "NONE", "business_approval_created": False})])
    return BootstrapResult(username, str(user_id), str(organization_id), str(assignment_id), None)
