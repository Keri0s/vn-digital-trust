"""Current-state authorization primitives for VDT.

The persistence adapter MUST resolve the complete authoritative object and parent
scope, including linked assessment/evidence membership, before calling this module.
Client scope arrays are constraints, never proof of membership. Broad grants must
be explicitly materialized by the adapter; empty grant arrays are not wildcards.
An organization-only target is suitable for organization administration, never as
a shortcut for reading domain objects. No ORM objects or permission caches live
here. Re-read state and call authorize again under the shared authorization guard
at commit, export publication, and download. ``now`` is trusted server/DB time.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Mapping


DIMENSIONS = (
    "branch_ids", "system_ids", "asset_ids", "data_asset_ids",
    "scenario_ids", "assessment_ids",
)


def _ids(values: Iterable[str]) -> frozenset[str]:
    if isinstance(values, (str, bytes)):
        raise ValueError("scope IDs must be a collection")
    result = frozenset(values)
    if any(not isinstance(value, str) or not value or value == "*" for value in result):
        raise ValueError("scope IDs must be nonempty explicit strings")
    return result


def _aware(value: datetime | None) -> bool:
    return value is None or (
        isinstance(value, datetime) and value.tzinfo is not None
        and value.utcoffset() is not None
    )


def _before(now: datetime, limit: datetime | None) -> bool:
    return _aware(limit) and (limit is None or now < limit)


@dataclass(frozen=True)
class Scope:
    organization_id: str
    branch_ids: frozenset[str] = field(default_factory=frozenset)
    system_ids: frozenset[str] = field(default_factory=frozenset)
    asset_ids: frozenset[str] = field(default_factory=frozenset)
    data_asset_ids: frozenset[str] = field(default_factory=frozenset)
    scenario_ids: frozenset[str] = field(default_factory=frozenset)
    assessment_ids: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self):
        if not isinstance(self.organization_id, str) or not self.organization_id or self.organization_id == "*":
            raise ValueError("an explicit organization is required")
        for dimension in DIMENSIONS:
            object.__setattr__(self, dimension, _ids(getattr(self, dimension)))

    @classmethod
    def from_mapping(cls, value: Mapping) -> "Scope":
        unknown = set(value) - {"organization_id", *DIMENSIONS}
        if unknown:
            raise ValueError("unknown scope dimensions")
        return cls(**value)

    def covers(self, target: "Scope") -> bool:
        """All IDs in every applicable target dimension need the same grant.

        Empty *target* dimensions mean inapplicable, as determined by the trusted
        adapter. In particular an organization-only administration target works.
        A populated target dimension cannot be covered by an empty grant array.
        """
        return self.organization_id == target.organization_id and all(
            getattr(target, dimension) <= getattr(self, dimension)
            for dimension in DIMENSIONS
        )


@dataclass(frozen=True)
class Principal:
    id: str
    organization_id: str
    is_active: bool = True
    expires_at: datetime | None = None
    revoked_at: datetime | None = None


@dataclass(frozen=True)
class Session:
    principal_id: str
    is_active: bool = True
    authenticated: bool = True
    expires_at: datetime | None = None
    idle_expires_at: datetime | None = None
    revoked_at: datetime | None = None


@dataclass(frozen=True)
class Grant:
    id: str
    principal_id: str
    permissions: frozenset[str]
    scope: Scope
    is_active: bool = True
    valid_from: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    assigned_assessment_ids: frozenset[str] = field(default_factory=frozenset)
    reviewer: bool = False
    assessment_access_expires_at: datetime | None = None

    def __post_init__(self):
        object.__setattr__(self, "permissions", _ids(self.permissions))
        object.__setattr__(self, "assigned_assessment_ids", _ids(self.assigned_assessment_ids))


@dataclass(frozen=True)
class Decision:
    allowed: bool
    code: str
    grant_ids: tuple[str, ...] = ()

    def __bool__(self):
        return self.allowed


def _identity_valid(principal: Principal, session: Session, now: datetime) -> bool:
    # Missing absolute session expiry is unresolved configuration, not infinity.
    return (
        isinstance(now, datetime) and _aware(now)
        and bool(principal.id) and bool(principal.organization_id)
        and principal.is_active is True and principal.revoked_at is None
        and _before(now, principal.expires_at)
        and session.authenticated is True and session.is_active is True
        and session.principal_id == principal.id and session.revoked_at is None
        and session.expires_at is not None and _before(now, session.expires_at)
        and _before(now, session.idle_expires_at)
    )


def effective_grants(
    principal: Principal, session: Session, grants: Iterable[Grant], *, now: datetime,
) -> tuple[Grant, ...]:
    """Return distinct current grants without unioning scope or permissions."""
    if not _identity_valid(principal, session, now):
        return ()
    return tuple(grant for grant in grants if (
        grant.principal_id == principal.id
        and grant.scope.organization_id == principal.organization_id
        and grant.is_active is True and grant.revoked_at is None
        and _aware(grant.valid_from)
        and (grant.valid_from is None or grant.valid_from <= now)
        and _before(now, grant.expires_at)
        and _before(now, grant.assessment_access_expires_at)
    ))


def authorize(
    principal: Principal,
    session: Session,
    grants: Iterable[Grant],
    required_permissions: str | Iterable[str],
    target_scope: Scope,
    *,
    now: datetime,
    assessment_id: str | None = None,
    require_reviewer: bool = False,
    independent_from: Iterable[str] = (),
) -> Decision:
    """Evaluate AND permission groups, with ``|`` denoting alternatives per group.

    Each permission must have a grant covering the *entire* authoritative target;
    different covering grants may provide separate AND permissions. Scope is never
    assembled across grants. Reviewer grants require their own exact assignment,
    even for visibility. ``require_reviewer`` also requires a covering reviewer
    grant; independence applies to actor IDs, regardless of how many roles exist.
    Link membership, ownership/delegation, business state and transaction locks
    remain the persistence/service adapter's responsibility.
    """
    if not _identity_valid(principal, session, now):
        return Decision(False, "AUTHENTICATION_REQUIRED")
    if principal.organization_id != target_scope.organization_id:
        return Decision(False, "OUTSIDE_SCOPE")
    if isinstance(independent_from, (str, bytes)):
        return Decision(False, "INVALID_POLICY_CONTEXT")
    if principal.id in set(independent_from):
        return Decision(False, "ACTOR_NOT_INDEPENDENT")
    requirements = (required_permissions,) if isinstance(required_permissions, str) else tuple(required_permissions)
    if not requirements or any(not isinstance(item, str) or not item for item in requirements):
        return Decision(False, "PERMISSION_REQUIRED")
    alternatives = tuple(frozenset(item.split("|")) for item in requirements)
    if any("" in group or any(code.strip() != code for code in group) for group in alternatives):
        return Decision(False, "PERMISSION_REQUIRED")
    if assessment_id is not None and assessment_id not in target_scope.assessment_ids:
        return Decision(False, "ASSESSMENT_NOT_ASSIGNED")
    candidates = []
    for grant in effective_grants(principal, session, grants, now=now):
        if not grant.scope.covers(target_scope):
            continue
        if grant.reviewer and (
            assessment_id is None
            or assessment_id not in grant.assigned_assessment_ids
            or not target_scope.assessment_ids <= grant.assigned_assessment_ids
        ):
            continue
        candidates.append(grant)
    if require_reviewer and not any(
        grant.reviewer and assessment_id is not None
        and assessment_id in grant.assigned_assessment_ids for grant in candidates
    ):
        return Decision(False, "ASSESSMENT_NOT_ASSIGNED")
    matched = set()
    for group in alternatives:
        covering = [grant for grant in candidates if group & grant.permissions]
        if not covering:
            return Decision(False, "PERMISSION_OR_SCOPE_DENIED")
        matched.update(grant.id for grant in covering)
    return Decision(True, "ALLOW", tuple(sorted(matched)))


__all__ = ["Scope", "Principal", "Session", "Grant", "Decision", "authorize", "effective_grants"]
