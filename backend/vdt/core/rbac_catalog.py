"""Frozen, catalog-only projection of RBAC-05-v0.1; no Django or database I/O.

Role descriptions preserve application, abstract scope and the exact optional
scope constraint as descriptive text. They grant no object scope. UUIDv5 IDs are
stable under this versioned namespace. Permission descriptions are copied exactly.
Users, organizations, branches, assignments, credentials and approvals never enter
the projected catalog. The source hashes printed by the command retain provenance.
"""

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


SEED_CANONICAL_SHA256 = "5046d15db86db26dcebbed4754ae5de5b5a80459b8e6158de83c1b2bcdf7c0d5"
SOURCE_HASHES = {
    "LAB-v0.1": "854b6ea530a957ca0bd2830b4ecc15ba11ab0bbe755a2b8f2bdd546dc350aef1",
    "FLOW-03-v0.2-r1": "820fe1a8722c07ea81a61e4865c9f89457e78f95fbc1ff845528cf6b4708497a",
}
EXPECTED_ROLE_COUNTS = {"VDT_ADMIN": 3, "VDT_SECURITY": 9, "VDT_RISK_OWNER": 6, "VDT_REVIEWER": 4}
REQUIRED_PAIRS = frozenset({
    ("VDT_SECURITY", "evidence.read_assigned"), ("VDT_SECURITY", "evidence.verify"),
    ("VDT_REVIEWER", "evidence.read_assigned"), ("VDT_REVIEWER", "evidence.verify"),
    ("VDT_RISK_OWNER", "risk.priority_approve"),
})
NAMESPACE = uuid5(NAMESPACE_URL, "urn:vn-digital-trust:rbac-catalog:v0.1")
MAX_SEED_BYTES = 1_048_576


class CatalogError(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        super().__init__(f"{code}: {detail}")


def canonical_hash(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def catalog_id(kind: str, key: str) -> str:
    return str(uuid5(NAMESPACE, f"{kind}:{key}"))


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CatalogError("SEED_INVALID", "Duplicate JSON key.")
        result[key] = value
    return result


def _read_json(path: Path):
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_SEED_BYTES + 1)
        if len(raw) > MAX_SEED_BYTES:
            raise CatalogError("SEED_INVALID", "Input exceeds the size limit.")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                           parse_constant=lambda _: (_ for _ in ()).throw(CatalogError("SEED_INVALID", "Non-finite JSON number.")))
        if not isinstance(value, dict):
            raise CatalogError("SEED_INVALID", "Expected a JSON object.")
        return value, sha256(raw).hexdigest()
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise CatalogError("SEED_UNREADABLE", "Required seed or provenance source is missing or invalid.") from error


@dataclass(frozen=True)
class Catalog:
    # Database-shaped immutable rows: (id, code, description), links: (id, role_id, permission_id).
    permissions: tuple[tuple[str, str, str], ...]
    roles: tuple[tuple[str, str, str], ...]
    links: tuple[tuple[str, str, str], ...]
    seed_sha256: str
    canonical_sha256: str
    source_hashes: tuple[tuple[str, str], ...]

    def summary(self):
        return {
            "seed_id": "RBAC-05-v0.1", "seed_sha256": self.seed_sha256,
            "seed_canonical_sha256": self.canonical_sha256,
            "source_hashes": dict(self.source_hashes),
            "expected_counts": {"permissions": len(self.permissions), "roles": len(self.roles), "role_permissions": len(self.links)},
            "role_permission_counts": dict(EXPECTED_ROLE_COUNTS),
            "required_permissions": sorted({code for _, code in REQUIRED_PAIRS}),
            "accounts_created": 0, "role_assignments_created": 0,
        }


def load_catalog(seed_path: str | Path) -> Catalog:
    """Validate exact canonical seed plus source hashes and reconstruct its merge."""
    seed_path = Path(seed_path)
    seed, raw_hash = _read_json(seed_path)
    # Give NOTE-08 omissions a useful diagnostic before the full pinned-hash check.
    roles = seed.get("roles")
    permissions = seed.get("permission_catalog")
    if not isinstance(roles, list) or not isinstance(permissions, list):
        raise CatalogError("SEED_INVALID", "Missing role or permission catalog.")
    try:
        pairs = {(role["id"], code) for role in roles for code in role["permissions"]}
    except (KeyError, TypeError) as error:
        raise CatalogError("SEED_INVALID", "Invalid role permissions.") from error
    if not REQUIRED_PAIRS <= pairs:
        raise CatalogError("REQUIRED_PERMISSION_MISSING", "Required evidence or priority permission mapping is absent.")
    if canonical_hash(seed) != SEED_CANONICAL_SHA256:
        raise CatalogError("SEED_HASH_MISMATCH", "Seed differs from the reviewed RBAC-05-v0.1 document.")

    sources = {}
    verified_hashes = {}
    for source in seed["source_fixtures"]:
        source_id = source["id"]
        document, actual_hash = _read_json(seed_path.parent / source["path"])
        if source_id not in SOURCE_HASHES or actual_hash != SOURCE_HASHES[source_id] or actual_hash != source["sha256"]:
            raise CatalogError("SOURCE_HASH_MISMATCH", "Provenance source differs from its reviewed hash.")
        sources[source_id] = document
        verified_hashes[source_id] = actual_hash
    if set(sources) != set(SOURCE_HASHES):
        raise CatalogError("SOURCE_MISSING", "Both reviewed source fixtures are required.")
    baseline, flow = sources["LAB-v0.1"], sources["FLOW-03-v0.2-r1"]
    if flow["base_sha256"] != verified_hashes["LAB-v0.1"]:
        raise CatalogError("BASE_HASH_MISMATCH", "FLOW does not reference the reviewed baseline.")
    merged = {role["id"]: set(role["permissions"]) for role in baseline["roles"] if role["application"] == "VDT"}
    baseline_scopes = {role["id"]: role["scope"] for role in baseline["roles"] if role["application"] == "VDT"}
    known_codes = {permission["code"] for permission in permissions}
    for addition in flow["permission_additions"] + seed["step05_permission_extensions"]:
        if addition["role_id"] not in merged or not set(addition["permissions"]) <= known_codes:
            raise CatalogError("MERGE_INVALID", "Unknown role or permission in source additions.")
        merged[addition["role_id"]].update(addition["permissions"])
    for role in roles:
        if role["application"] != "VDT" or role["scope"] != baseline_scopes[role["id"]] or set(role["permissions"]) != merged[role["id"]]:
            raise CatalogError("MERGE_INVALID", "Role differs from the baseline and reviewed additions.")
        if len(role["permissions"]) != len(set(role["permissions"])):
            raise CatalogError("DUPLICATE_PERMISSION", "Duplicate role permission.")
    if len(permissions) != 19 or len(roles) != 4 or len(pairs) != 22:
        raise CatalogError("COUNT_MISMATCH", "Expected 19 permissions, 4 roles and 22 links.")
    for permission in permissions:
        if permission["application"] != "VDT" or set(permission["roles"]) != {role for role, code in pairs if code == permission["code"]}:
            raise CatalogError("MERGE_INVALID", "Reverse permission mapping does not match role mappings.")
    permission_rows = tuple(sorted((catalog_id("permission", item["code"]), item["code"], item["description"]) for item in permissions))
    role_rows = []
    for role in roles:
        description = f"application={role['application']}; scope={role['scope']}"
        if role.get("scope_constraint"):
            description += "; scope_constraint=" + role["scope_constraint"]
        role_rows.append((catalog_id("role", role["id"]), role["id"], description))
    link_rows = tuple(sorted((catalog_id("role_permission", f"{role}:{permission}"), catalog_id("role", role),
                              catalog_id("permission", permission)) for role, permission in pairs))
    return Catalog(permission_rows, tuple(sorted(role_rows)), link_rows, raw_hash,
                   SEED_CANONICAL_SHA256, tuple(sorted(verified_hashes.items())))


@dataclass(frozen=True)
class CatalogPlan:
    permissions: tuple[tuple[str, str, str], ...]
    roles: tuple[tuple[str, str, str], ...]
    links: tuple[tuple[str, str, str], ...]

    @property
    def changes(self) -> bool:
        return bool(self.permissions or self.roles or self.links)

    def counts(self):
        return {"permissions": len(self.permissions), "roles": len(self.roles), "role_permissions": len(self.links)}


def plan_catalog(catalog: Catalog, permission_rows, role_rows, link_rows) -> CatalogPlan:
    """Existing rows must be an exact subset; never rewrite or delete drift.

    Caller must hold a transaction and table locks while reading/applying this plan.
    UUIDs, code/description content, every mapping and unexpected extra records are
    checked, so matching row counts alone cannot conceal changed permissions.
    """
    missing = []
    for label, expected_rows, existing_rows in (
        ("permission", catalog.permissions, permission_rows),
        ("role", catalog.roles, role_rows),
        ("role_permission", catalog.links, link_rows),
    ):
        expected = set(expected_rows)
        existing = {tuple(str(value) for value in row) for row in existing_rows}
        if existing - expected:
            raise CatalogError("CATALOG_DRIFT", f"Existing {label} rows differ from the frozen catalog; no changes were applied.")
        missing.append(tuple(sorted(expected - existing)))
    return CatalogPlan(*missing)
