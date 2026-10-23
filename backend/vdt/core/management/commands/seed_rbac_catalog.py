"""Transactional PostgreSQL bootstrap of only the reviewed RBAC catalog."""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction

from vdt.core.rbac_catalog import CatalogError, load_catalog, plan_catalog


ADVISORY_LOCK_KEY = 0x5644540000050001


class Command(BaseCommand):
    help = "Validate and seed the frozen permission/role catalog; never provision accounts or assignments."
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("--seed", default=str(Path(settings.BASE_DIR) / "docs/design/rbac-seed-v0.1.json"))
        parser.add_argument("--database", default="default")
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument("--validate-only", action="store_true", help="Validate source files without opening a database connection.")
        mode.add_argument("--check", action="store_true", help="Require the database catalog already matches exactly; write nothing.")

    def handle(self, *args, **options):
        try:
            catalog = load_catalog(options["seed"])
            result = catalog.summary()
            if options["validate_only"]:
                result.update(status="VALIDATED", inserted={"permissions": 0, "roles": 0, "role_permissions": 0})
            else:
                alias = options["database"]
                database = connections[alias]
                if database.vendor != "postgresql":
                    raise CatalogError("POSTGRESQL_REQUIRED", "This seed requires the migrated PostgreSQL VDT schema.")
                with transaction.atomic(using=alias):
                    with database.cursor() as cursor:
                        cursor.execute("SET LOCAL lock_timeout = '5s'")
                        cursor.execute("SET LOCAL statement_timeout = '30s'")
                        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [ADVISORY_LOCK_KEY])
                        # Table locks also exclude writers that do not use our advisory lock.
                        # Assignment lock prevents a concurrent grant activating a partial catalog.
                        cursor.execute("LOCK TABLE vdt.permission, vdt.role, vdt.role_permission, vdt.role_assignment IN SHARE ROW EXCLUSIVE MODE")
                        cursor.execute("SELECT id, code, description FROM vdt.permission")
                        permissions = cursor.fetchall()
                        cursor.execute("SELECT id, code, description FROM vdt.role")
                        roles = cursor.fetchall()
                        cursor.execute("SELECT id, role_id, permission_id FROM vdt.role_permission")
                        links = cursor.fetchall()
                        plan = plan_catalog(catalog, permissions, roles, links)
                        if options["check"] and plan.changes:
                            raise CatalogError("CATALOG_INCOMPLETE", "Canonical catalog rows are missing; check mode writes nothing.")
                        if plan.changes:
                            cursor.execute("SELECT EXISTS (SELECT 1 FROM vdt.role_assignment)")
                            if cursor.fetchone()[0]:
                                raise CatalogError("BOOTSTRAP_HAS_ASSIGNMENTS", "Catalog changes require a separate authorized permission-change workflow once assignments exist.")
                            if plan.permissions:
                                cursor.executemany("INSERT INTO vdt.permission (id, code, description) VALUES (%s, %s, %s)", plan.permissions)
                            if plan.roles:
                                cursor.executemany("INSERT INTO vdt.role (id, code, description) VALUES (%s, %s, %s)", plan.roles)
                            if plan.links:
                                cursor.executemany("INSERT INTO vdt.role_permission (id, role_id, permission_id) VALUES (%s, %s, %s)", plan.links)
                        result.update(status="CHECKED" if options["check"] else ("APPLIED" if plan.changes else "UNCHANGED"), inserted=plan.counts())
                # Emit success only after transaction commit.
            self.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        except CatalogError as error:
            raise CommandError(str(error)) from error
