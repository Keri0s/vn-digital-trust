"""Offline catalog validation and drift planning; no PostgreSQL result claimed."""

from copy import deepcopy
from io import BytesIO
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from vdt.core.rbac_catalog import (
    CatalogError, REQUIRED_PAIRS, SEED_CANONICAL_SHA256, canonical_hash,
    catalog_id, load_catalog, plan_catalog,
)


ROOT = Path(os.environ.get("VDT_TEST_REPO_ROOT", Path(__file__).resolve().parents[2]))
SEED_PATH = ROOT / "docs/design/rbac-seed-v0.1.json"


class RbacCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog(SEED_PATH)
        self.seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    def test_frozen_seed_and_sources_validate_as_exact_catalog(self):
        self.assertEqual(self.catalog.canonical_sha256, SEED_CANONICAL_SHA256)
        self.assertEqual(len(self.catalog.permissions), 19)
        self.assertEqual(len(self.catalog.roles), 4)
        self.assertEqual(len(self.catalog.links), 22)
        self.assertEqual(len(self.catalog.source_hashes), 2)
        self.assertEqual(self.catalog.summary()["accounts_created"], 0)
        self.assertEqual(self.catalog.summary()["role_assignments_created"], 0)

    def test_required_evidence_and_priority_permissions_have_exact_role_mappings(self):
        permissions = {row[0]: row[1] for row in self.catalog.permissions}
        roles = {row[0]: row[1] for row in self.catalog.roles}
        pairs = {(roles[role_id], permissions[permission_id]) for _, role_id, permission_id in self.catalog.links}
        self.assertTrue(REQUIRED_PAIRS <= pairs)
        self.assertEqual({role for role, permission in pairs if permission == "risk.priority_approve"}, {"VDT_RISK_OWNER"})
        self.assertNotIn(("VDT_ADMIN", "evidence.read_assigned"), pairs)
        self.assertNotIn(("VDT_REVIEWER", "risk.priority_approve"), pairs)

    def test_missing_required_mapping_is_explicitly_rejected(self):
        for role_code, permission in REQUIRED_PAIRS:
            seed = deepcopy(self.seed)
            next(role for role in seed["roles"] if role["id"] == role_code)["permissions"].remove(permission)
            with self.subTest(role=role_code, permission=permission):
                with patch("vdt.core.rbac_catalog._read_json", return_value=(seed, "unused")):
                    with self.assertRaises(CatalogError) as error:
                        load_catalog(SEED_PATH)
                    self.assertEqual(error.exception.code, "REQUIRED_PERMISSION_MISSING")

    def test_unreviewed_seed_change_cannot_preserve_acceptance_with_same_counts(self):
        self.seed["permission_catalog"][0]["description"] = "Changed permission meaning"
        with patch("vdt.core.rbac_catalog._read_json", return_value=(self.seed, "unused")):
            with self.assertRaises(CatalogError) as error:
                load_catalog(SEED_PATH)
            self.assertEqual(error.exception.code, "SEED_HASH_MISMATCH")

    def test_source_hash_drift_blocks_before_database_work(self):
        with patch("vdt.core.rbac_catalog._read_json", side_effect=[(self.seed, "unused"), ({}, "0" * 64)]):
            with self.assertRaises(CatalogError) as error:
                load_catalog(SEED_PATH)
            self.assertEqual(error.exception.code, "SOURCE_HASH_MISMATCH")

    def test_json_duplicate_key_and_nonfinite_are_rejected(self):
        for raw in (b'{"roles":[],"roles":[]}', b'{"x":NaN}'):
            with patch.object(Path, "open", return_value=BytesIO(raw)), self.assertRaises(CatalogError):
                load_catalog(SEED_PATH)

    def test_missing_source_is_not_silently_skipped(self):
        with patch.object(Path, "open", side_effect=FileNotFoundError), self.assertRaises(CatalogError) as error:
            load_catalog(SEED_PATH)
        self.assertEqual(error.exception.code, "SEED_UNREADABLE")

    def test_uuid_projection_and_role_descriptions_are_deterministic(self):
        repeated = load_catalog(SEED_PATH)
        self.assertEqual(self.catalog, repeated)
        security = next(row for row in self.catalog.roles if row[1] == "VDT_SECURITY")
        self.assertEqual(security[0], catalog_id("role", "VDT_SECURITY"))
        self.assertEqual(security[2], "application=VDT; scope=organization; scope_constraint=" + self.seed["roles"][1]["scope_constraint"])
        self.assertEqual(canonical_hash(dict(reversed(list(self.seed.items())))), SEED_CANONICAL_SHA256)

    def test_empty_catalog_plans_only_three_catalog_collections(self):
        plan = plan_catalog(self.catalog, [], [], [])
        self.assertTrue(plan.changes)
        self.assertEqual(plan.counts(), {"permissions": 19, "roles": 4, "role_permissions": 22})
        self.assertEqual(set(vars(plan)), {"permissions", "roles", "links"})

    def test_second_seed_is_noop_and_partial_exact_catalog_can_complete(self):
        plan = plan_catalog(self.catalog, self.catalog.permissions, self.catalog.roles, self.catalog.links)
        self.assertFalse(plan.changes)
        self.assertEqual(plan.counts(), {"permissions": 0, "roles": 0, "role_permissions": 0})
        partial = plan_catalog(self.catalog, self.catalog.permissions, self.catalog.roles, self.catalog.links[:-1])
        self.assertEqual(partial.counts(), {"permissions": 0, "roles": 0, "role_permissions": 1})

    def test_description_id_and_extra_rows_all_refuse_drift_without_mutating_inputs(self):
        changed = list(self.catalog.permissions)
        changed[0] = (changed[0][0], changed[0][1], "wrong description")
        wrong_id = list(self.catalog.permissions)
        wrong_id[0] = (catalog_id("permission", "wrong"), wrong_id[0][1], wrong_id[0][2])
        extra = [*self.catalog.permissions, (catalog_id("permission", "extra"), "extra.permission", "unrelated")]
        for permissions in (changed, wrong_id, extra):
            original = deepcopy(permissions)
            with self.subTest(rows=permissions), self.assertRaises(CatalogError) as error:
                plan_catalog(self.catalog, permissions, self.catalog.roles, self.catalog.links)
            self.assertEqual(error.exception.code, "CATALOG_DRIFT")
            self.assertEqual(permissions, original)

    def test_extra_permission_link_cannot_be_silently_removed_or_accepted(self):
        extra = (catalog_id("role_permission", "extra"), catalog_id("role", "VDT_ADMIN"), catalog_id("permission", "evidence.verify"))
        with self.assertRaises(CatalogError) as error:
            plan_catalog(self.catalog, self.catalog.permissions, self.catalog.roles, [*self.catalog.links, extra])
        self.assertEqual(error.exception.code, "CATALOG_DRIFT")


if __name__ == "__main__":
    unittest.main()
