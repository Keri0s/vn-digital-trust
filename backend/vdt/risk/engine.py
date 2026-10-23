"""Frozen RM-01-v0.4-r3 / CONDITIONAL-BASE-v0.4 arithmetic.

Confirmation flags are server-validated facts, never client assertions. The
application validates scoped evidence and authority before constructing inputs.
Domain errors produce null computed outputs; unknown evidence yields conservative
domains. Nothing here closes gaps, accepts risk, or changes source snapshots.
"""
from dataclasses import dataclass, field, fields
from types import MappingProxyType
from typing import Mapping

METHOD_VERSION = "RM-01-v0.4-r3"
PROFILE_VERSION = "CONDITIONAL-BASE-v0.4"
FACTORS = ("E", "F", "G", "C", "I_integrity", "A", "B")
IMPACTS = FACTORS[3:]
LEVELS = ("LOW", "MODERATE", "HIGH", "CRITICAL")
COVERAGES = ("VERIFIED_COVERED", "VERIFIED_UNCOVERED", "UNKNOWN")
FULL_DOMAIN = (1, 5)


def _ordinal(value):
    return type(value) is int and 1 <= value <= 5


def _bounds(value):
    return (isinstance(value, (tuple, list)) and len(value) == 2
            and all(_ordinal(v) for v in value) and value[0] <= value[1])


def _decimal(numerator, denominator=25):
    """Exact terminating decimal, independent of the Decimal context."""
    sign = "-" if numerator < 0 else ""
    whole, remainder = divmod(abs(numerator), denominator)
    decimals = ""
    while remainder:
        digit, remainder = divmod(remainder * 10, denominator)
        decimals += str(digit)
    return sign + str(whole) + ("." + decimals if decimals else "")


def score_r25(e, f, g, impact):
    """Exact score for a valid point. R25 is the authoritative stored value."""
    if not all(_ordinal(v) for v in (e, f, g, impact)):
        raise ValueError("Each factor must be an integer from 1 to 5.")
    return impact * (25 + (2 * e + 3 * f - 5) * g)


def raw_level(r25):
    if type(r25) is not int or not 25 <= r25 <= 625:
        raise ValueError("R25 must be an integer from 25 to 625.")
    return LEVELS[sum(r25 >= threshold for threshold in (125, 250, 425))]


def final_level(r25, impact):
    if not _ordinal(impact):
        raise ValueError("Impact must be an integer from 1 to 5.")
    raw = raw_level(r25)
    if impact == 1:
        return "LOW"
    return LEVELS[min(LEVELS.index(raw), 1)] if impact == 2 else raw


def format_r25(r25, *, upper=False):
    """Floor points/lower bounds and ceil upper bounds to one decimal place."""
    if type(r25) is not int or not 25 <= r25 <= 625:
        raise ValueError("R25 must be an integer from 25 to 625.")
    tenths = (2 * r25 + (4 if upper else 0)) // 5
    whole, remainder = divmod(tenths, 10)
    return f"{whole}.{remainder}"


def _gate(impact):
    return "I_EQ_1_LOW" if impact == 1 else "I_EQ_2_CAP_MODERATE" if impact == 2 else "NONE"


@dataclass(frozen=True)
class FactorInput:
    value: object = None
    bounds: tuple = FULL_DOMAIN
    confirmed: bool = False
    bounds_confirmed: bool = False
    disputed: bool = False

    def __post_init__(self):
        if isinstance(self.bounds, (tuple, list)):
            object.__setattr__(self, "bounds", tuple(self.bounds))


@dataclass(frozen=True)
class PathInput:
    path_id: str
    coverage: str = "UNKNOWN"
    g: object = None
    bounds: tuple = FULL_DOMAIN
    confirmed: bool = False
    bounds_confirmed: bool = False
    disputed: bool = False
    not_applicable: bool = False
    not_applicable_confirmed: bool = False
    not_applicable_reason: str | None = None

    def __post_init__(self):
        if isinstance(self.bounds, (tuple, list)):
            object.__setattr__(self, "bounds", tuple(self.bounds))


@dataclass(frozen=True)
class RiskInput:
    factors: Mapping[str, FactorInput]
    paths: tuple[PathInput, ...] | None = None
    essential_context_complete: bool = True
    path_inventory_complete: bool = True
    unresolved_reviewer_disagreement: bool = False
    essential_context_disputed: bool = False
    method_version: str = METHOD_VERSION
    profile_version: str = PROFILE_VERSION

    def __post_init__(self):
        object.__setattr__(self, "factors", MappingProxyType(dict(self.factors)))
        if self.paths is not None:
            object.__setattr__(self, "paths", tuple(self.paths))


@dataclass(frozen=True)
class Issue:
    code: str
    field: str
    message: str

    def to_dict(self):
        return {"code": self.code, "field": self.field, "message": self.message}


@dataclass(frozen=True)
class PathDomain:
    path_id: str
    bounds: tuple[int, int]
    coverage: str


@dataclass(frozen=True)
class RiskResult:
    P: str | None = None
    P_range: tuple[str, str] | None = None
    L: str | None = None
    L_range: tuple[str, str] | None = None
    G: int | None = None
    G_range: tuple[int, int] | None = None
    I_total: int | None = None
    I_total_range: tuple[int, int] | None = None
    R25: int | None = None
    R25_range: tuple[int, int] | None = None
    score: str | None = None
    score_range: tuple[str, str] | None = None
    display_score: str | None = None
    display_score_range: tuple[str, str] | None = None
    raw_level: str | None = None
    risk_level: str | None = None
    level_range: tuple[str, str] | None = None
    impact_gate_reason: str | None = None
    score_determined: bool = False
    status: str = "NEEDS_REVIEW"
    determination_reasons: tuple[str, ...] = ()
    missing_factors: tuple[str, ...] = ()
    missing_paths: tuple[str, ...] = ()
    validation_issues: tuple[Issue, ...] = ()
    raw_level_range: tuple[str, str] | None = None
    possible_impact_gates: tuple[str, ...] = ()
    # Audit data is separate from the frozen RiskComputed transport schema.
    reason: str | None = None
    domains: Mapping = field(default_factory=lambda: MappingProxyType({}))
    normalized_factors: Mapping = field(default_factory=lambda: MappingProxyType({}))
    path_domains: tuple[PathDomain, ...] = ()
    ignored_unconfirmed_bounds: tuple[str, ...] = ()
    control_failure_paths: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "domains", MappingProxyType(dict(self.domains)))
        object.__setattr__(self, "normalized_factors", MappingProxyType(dict(self.normalized_factors)))

    def to_dict(self):
        """Return a fresh JSON-ready RiskComputed object; the result stays frozen."""
        excluded = {"reason", "domains", "normalized_factors", "path_domains",
                    "ignored_unconfirmed_bounds", "control_failure_paths"}
        output = {}
        for item in fields(self):
            if item.name in excluded:
                continue
            value = getattr(self, item.name)
            output[item.name] = ([v.to_dict() for v in value] if item.name == "validation_issues"
                                 else {"lo": value[0], "hi": value[1]}
                                 if item.name.endswith("_range") and value is not None
                                 else list(value) if isinstance(value, tuple) else value)
        return output


def factor_domain(factor):
    """Call only after validation. A confirmed bound does not verify a value."""
    known = factor.value is not None and factor.confirmed and not factor.disputed
    return ((factor.value, factor.value) if known else
            tuple(factor.bounds) if factor.bounds_confirmed else FULL_DOMAIN)


def _validate_factor(factor, name):
    issues = []
    if not isinstance(factor, FactorInput):
        return [Issue("RM_INPUT_INVALID", name, "Expected a FactorInput.")]
    if factor.value is not None and not _ordinal(factor.value):
        issues.append(Issue("RM_DOMAIN_INVALID", name + ".value", "Value must be an integer from 1 to 5."))
    if not _bounds(factor.bounds):
        issues.append(Issue("RM_BOUND_INVALID", name + ".bounds", "Bounds must be ordered integers from 1 to 5."))
    elif _ordinal(factor.value) and not factor.bounds[0] <= factor.value <= factor.bounds[1]:
        issues.append(Issue("RM_DOMAIN_CONFLICT", name, "The supplied value is outside its supplied bounds."))
    for key in ("confirmed", "bounds_confirmed", "disputed"):
        if type(getattr(factor, key)) is not bool:
            issues.append(Issue("RM_INPUT_INVALID", name + "." + key, "Expected a validated boolean."))
    return issues


def evaluate_risk(inputs: RiskInput) -> RiskResult:
    """Use monotonic integer endpoints for independent factor domains.

    Supplied paths determine G. Omitted paths support explicit aggregate G for
    model calculations; production assessments should always supply their path
    inventory, including an empty tuple when unknown.
    """
    if not isinstance(inputs, RiskInput):
        raise TypeError("Expected RiskInput.")
    issues, reason = [], None
    for name in ("essential_context_complete", "path_inventory_complete",
                 "unresolved_reviewer_disagreement", "essential_context_disputed"):
        if type(getattr(inputs, name)) is not bool:
            issues.append(Issue("RM_INPUT_INVALID", name, "Expected a validated boolean."))
    if not inputs.essential_context_complete or inputs.essential_context_disputed:
        reason = "MISSING_ESSENTIAL_CONTEXT" if not inputs.essential_context_complete else "DISPUTED_ESSENTIAL_CONTEXT"
        issues.append(Issue("RM_CONTEXT_INCOMPLETE", "context", "Essential scenario, scope, owner, type and preconditions must be established."))
    if inputs.method_version != METHOD_VERSION or inputs.profile_version != PROFILE_VERSION:
        reason = reason or "UNSUPPORTED_METHOD_PROFILE"
        issues.append(Issue("RM_PROFILE_UNSUPPORTED", "profile_version", "Only the frozen method/profile is supported."))
    required = set(FACTORS) - ({"G"} if inputs.paths is not None else set())
    if not required <= set(inputs.factors) or set(inputs.factors) - set(FACTORS):
        issues.append(Issue("RM_INPUT_INVALID", "factors", "Supply all factor keys; G may be omitted only when paths are supplied."))
    for name, factor in inputs.factors.items():
        issues.extend(_validate_factor(factor, name))
    path_ids = set()
    for index, path in enumerate(inputs.paths or ()):
        name = f"paths[{index}]"
        if not isinstance(path, PathInput):
            issues.append(Issue("RM_PATH_INVALID", name, "Expected a PathInput."))
            continue
        if (not isinstance(path.path_id, str) or not path.path_id.strip()
                or path.path_id in path_ids or path.path_id == "UNASSESSED_SCOPE"):
            issues.append(Issue("RM_PATH_INVALID", name + ".path_id", "Path IDs must be nonempty, unique and not reserved."))
        if isinstance(path.path_id, str):
            path_ids.add(path.path_id)
        if path.coverage not in COVERAGES:
            issues.append(Issue("RM_PATH_INVALID", name + ".coverage", "Unsupported path coverage."))
        numeric = _validate_factor(FactorInput(path.g, path.bounds, path.confirmed,
                                              path.bounds_confirmed, path.disputed), name)
        issues.extend(Issue("RM_PATH_INVALID", issue.field, issue.message) for issue in numeric)
        if path.coverage == "VERIFIED_UNCOVERED" and path.g != 5:
            reason = reason or "UNCOVERED_PATH_REQUIRES_G5"
            issues.append(Issue("RM_UNCOVERED_REQUIRES_G5", name + ".g", "A verified uncovered path requires g=5."))
        for key in ("not_applicable", "not_applicable_confirmed"):
            if type(getattr(path, key)) is not bool:
                issues.append(Issue("RM_PATH_INVALID", name + "." + key, "Expected a validated boolean."))
    if issues:
        if reason is None:
            reason = ("INVALID_PATH_INPUT" if any(i.code == "RM_PATH_INVALID" for i in issues) else
                      "INVALID_BOUND_INPUT" if any(i.code == "RM_BOUND_INVALID" for i in issues) else "INVALID_INPUT")
        return RiskResult(reason=reason, validation_issues=tuple(issues))

    normalized, domains, ignored, gaps = {}, {}, [], []
    for name in FACTORS:
        factor = inputs.factors.get(name, FactorInput())
        known = factor.value is not None and factor.confirmed and not factor.disputed
        normalized[name] = factor.value if known else None
        domains[name] = factor_domain(factor)
        if not known:
            gaps.append(name)
        if factor.bounds != FULL_DOMAIN and not factor.bounds_confirmed and not known:
            ignored.append(name)

    path_domains, path_gaps, failures = [], [], []
    if inputs.paths is not None:
        for path in inputs.paths:
            if (path.not_applicable and path.not_applicable_confirmed
                    and isinstance(path.not_applicable_reason, str) and path.not_applicable_reason.strip()
                    and not path.disputed):
                continue
            unsupported_na = path.not_applicable
            known = (path.g is not None and path.confirmed and not path.disputed
                     and path.coverage != "UNKNOWN" and not unsupported_na)
            domain = ((path.g, path.g) if known else
                      tuple(path.bounds) if path.bounds_confirmed and not unsupported_na else FULL_DOMAIN)
            if not known:
                path_gaps.append(path.path_id)
            if path.bounds != FULL_DOMAIN and not path.bounds_confirmed and not known:
                ignored.append(path.path_id)
            if known and path.g == 5:
                failures.append(path.path_id)
            path_domains.append(PathDomain(path.path_id, domain, path.coverage))
        if not path_domains or not inputs.path_inventory_complete:
            path_domains.append(PathDomain("UNASSESSED_SCOPE", FULL_DOMAIN, "UNKNOWN"))
            path_gaps.append("UNASSESSED_SCOPE")
        domains["G"] = tuple(max(p.bounds[i] for p in path_domains) for i in (0, 1))
        gaps = [name for name in gaps if name != "G"]
        if path_gaps:
            gaps.append("G_PATH_EVIDENCE")

    lo, hi = ([domains[name][endpoint] for name in FACTORS] for endpoint in (0, 1))
    impacts = (max(lo[3:]), max(hi[3:]))
    r25 = (score_r25(*lo[:3], impacts[0]), score_r25(*hi[:3], impacts[1]))
    determined = r25[0] == r25[1]
    scores = tuple(_decimal(n) for n in r25)
    potential = tuple(_decimal(2 * v[0] + 3 * v[1], 5) for v in (lo, hi))
    likelihood = tuple(_decimal(score_r25(*v[:3], 1)) for v in (lo, hi))
    incomplete = bool(gaps or path_gaps or inputs.unresolved_reviewer_disagreement)
    reasons = []
    if determined:
        reasons.append("EXACT_MODEL_BOUNDS_COLLAPSE")
        if domains["G"] == (5, 5) and path_gaps:
            reasons.append("G_MAX_5_ABSORBS_UNKNOWN_PATH")
        elif domains["G"][0] == domains["G"][1] and path_gaps:
            reasons.append("G_MAX_BOUND_DOMINATES_UNKNOWN_PATH")
        if impacts == (5, 5) and any(normalized[name] is None for name in IMPACTS):
            reasons.append("IMPACT_MAX_5_ABSORBS_UNKNOWN")
        if domains["E"] == domains["F"] == (1, 1) and domains["G"][0] != domains["G"][1]:
            reasons.append("P_EQ_1_SCORE_INDEPENDENT_OF_G")
    return RiskResult(
        P=potential[0] if potential[0] == potential[1] else None, P_range=potential,
        L=likelihood[0] if likelihood[0] == likelihood[1] else None, L_range=likelihood,
        G=domains["G"][0] if domains["G"][0] == domains["G"][1] else None,
        G_range=domains["G"], I_total=impacts[0] if impacts[0] == impacts[1] else None,
        I_total_range=impacts, R25=r25[0] if determined else None, R25_range=r25,
        score=scores[0] if determined else None, score_range=scores,
        display_score=format_r25(r25[0]) if determined else None,
        display_score_range=(format_r25(r25[0]), format_r25(r25[1], upper=True)),
        raw_level=raw_level(r25[0]) if determined else None,
        risk_level=final_level(r25[0], impacts[0]) if determined else None,
        level_range=(final_level(r25[0], impacts[0]), final_level(r25[1], impacts[1])),
        impact_gate_reason=_gate(impacts[0]) if determined else None,
        score_determined=determined, status="NEEDS_REVIEW" if incomplete else "EVALUATED",
        determination_reasons=tuple(reasons), missing_factors=tuple(gaps), missing_paths=tuple(path_gaps),
        raw_level_range=tuple(raw_level(n) for n in r25),
        possible_impact_gates=tuple(dict.fromkeys(_gate(i) for i in range(impacts[0], impacts[1] + 1))),
        reason=("UNRESOLVED_REVIEWER_DISAGREEMENT" if inputs.unresolved_reviewer_disagreement else
                "INCOMPLETE_EVIDENCE" if incomplete else None),
        domains=domains, normalized_factors=normalized, path_domains=tuple(path_domains),
        ignored_unconfirmed_bounds=tuple(ignored), control_failure_paths=tuple(failures),
    )
