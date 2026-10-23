"""IMPACT-PROGRESS-v0.1: describe impact changes without closing review or gaps."""
from dataclasses import dataclass, fields
from itertools import product
from types import MappingProxyType
from typing import Mapping

from .engine import (
    IMPACTS, FactorInput, Issue, RiskResult, _bounds, _decimal,
    _validate_factor, factor_domain,
)

IMPACT_PROGRESS_VERSION = "IMPACT-PROGRESS-v0.1"


@dataclass(frozen=True)
class ComparisonContext:
    scenario: str
    scoring_type: str
    method: str
    profile: str
    ordinal_rubric: str
    event_scope: str
    assessment_scope: str
    preconditions: str
    intended_basis: str | None = None

    def missing_fields(self):
        required = (item.name for item in fields(self) if item.name != "intended_basis")
        missing = [name for name in required
                   if not isinstance(getattr(self, name), str) or not getattr(self, name).strip()]
        if self.scoring_type not in ("CURRENT", "INHERENT", "ILLUSTRATIVE"):
            missing.append("scoring_type")
        if self.scoring_type == "ILLUSTRATIVE" and self.intended_basis not in ("CURRENT", "INHERENT"):
            missing.append("intended_basis")
        return tuple(dict.fromkeys(missing))


@dataclass(frozen=True)
class ImpactSnapshot:
    snapshot_id: str
    context: ComparisonContext
    impacts: Mapping[str, FactorInput]
    risk: RiskResult | None = None
    assessment_status: str = "NEEDS_REVIEW"

    def __post_init__(self):
        object.__setattr__(self, "impacts", MappingProxyType(dict(self.impacts)))
        if not isinstance(self.snapshot_id, str) or not self.snapshot_id.strip():
            raise ValueError("A source snapshot ID is required.")
        if not isinstance(self.context, ComparisonContext):
            raise TypeError("Expected ComparisonContext.")
        if set(self.impacts) != set(IMPACTS):
            raise ValueError("Supply exactly C, I_integrity, A and B.")
        if any(not isinstance(value, FactorInput) for value in self.impacts.values()):
            raise TypeError("Every impact dimension must be a FactorInput.")
        if self.risk is not None and not isinstance(self.risk, RiskResult):
            raise TypeError("Expected an immutable RiskResult.")
        if self.assessment_status not in ("EVALUATED", "NEEDS_REVIEW"):
            raise ValueError("Unsupported assessment status.")


@dataclass(frozen=True)
class ImpactSummary:
    I_total: int | None = None
    I_total_range: tuple[int, int] | None = None
    max_dimension_count: int | None = None
    max_dimension_count_range: tuple[int, int] | None = None

    def to_dict(self):
        return {item.name: {"lo": value[0], "hi": value[1]} if isinstance(value, tuple) else value
                for item in fields(self) for value in (getattr(self, item.name),)}


def summarize_impact(domains) -> ImpactSummary:
    """Exact independent-domain max and count bounds (at most 625 completions)."""
    domains = tuple(domains)
    if len(domains) != 4 or not all(_bounds(domain) for domain in domains):
        raise ValueError("Four valid ordinal impact domains are required.")
    totals, counts = set(), set()
    for values in product(*(range(lo, hi + 1) for lo, hi in domains)):
        maximum = max(values)
        totals.add(maximum)
        counts.add(values.count(maximum))
    total_range, count_range = (min(totals), max(totals)), (min(counts), max(counts))
    return ImpactSummary(total_range[0] if len(totals) == 1 else None, total_range,
                         count_range[0] if len(counts) == 1 else None, count_range)


@dataclass(frozen=True)
class ImpactComparison:
    before_snapshot_id: str
    after_snapshot_id: str
    comparability: str
    comparability_reasons: tuple[str, ...]
    per_dimension: tuple[str, ...]
    impact_progress: str
    verified_worsening: bool | None
    impact_summary_before: ImpactSummary
    impact_summary_after: ImpactSummary
    comparison_review_status: str
    R_progress: str
    R25_change: int | None
    score_change: str | None
    score_before: str | None
    score_before_range: tuple[str, str] | None
    score_after: str | None
    score_after_range: tuple[str, str] | None
    treatment_attribution: str
    improved_dimensions: tuple[str, ...]
    worsened_dimensions: tuple[str, ...]
    unchanged_dimensions: tuple[str, ...]
    unresolved_dimensions: tuple[str, ...]
    evidence_gap_resolved_dimensions: tuple[str, ...]
    assessment_status_before: str
    assessment_status_after: str
    validation_issues: tuple[Issue, ...] = ()
    impact_progress_rule_version: str = IMPACT_PROGRESS_VERSION

    def to_dict(self):
        """Computed comparison data; persistence adds actor/review and source inputs."""
        output = {}
        for item in fields(self):
            value = getattr(self, item.name)
            if isinstance(value, ImpactSummary):
                value = value.to_dict()
            elif item.name == "validation_issues":
                value = [issue.to_dict() for issue in value]
            elif item.name.endswith("_range") and value is not None:
                value = {"lo": value[0], "hi": value[1]}
            elif isinstance(value, tuple):
                value = list(value)
            output[item.name] = value
        return output


def compare_impact(before: ImpactSnapshot, after: ImpactSnapshot, *,
                   treatment_link_confirmed=False, treatment_evidence_ids=(),
                   unresolved_comparison_disagreement=False) -> ImpactComparison:
    """Compare immutable snapshots; confirmation arguments require server validation.

    Assessment status is preserved separately from the impact comparison status.
    Unknown becoming verified is evidence progress, never an inferred reduction.
    SUPPORTED attribution applies only to verified comparable dimensions.
    """
    if not isinstance(before, ImpactSnapshot) or not isinstance(after, ImpactSnapshot):
        raise TypeError("Expected two ImpactSnapshot inputs.")
    if type(treatment_link_confirmed) is not bool or type(unresolved_comparison_disagreement) is not bool:
        raise TypeError("Confirmation and disagreement flags must be booleans.")
    treatment_evidence_ids = tuple(treatment_evidence_ids)
    if any(not isinstance(value, str) or not value.strip() for value in treatment_evidence_ids):
        raise ValueError("Treatment evidence references must be nonempty strings.")
    reasons = []
    for label, snapshot in (("before", before), ("after", after)):
        reasons.extend(f"{label}.{name}: missing or invalid context" for name in snapshot.context.missing_fields())
    reasons.extend(item.name + ": context differs" for item in fields(ComparisonContext)
                   if getattr(before.context, item.name) != getattr(after.context, item.name))
    comparable = not reasons
    issues, changes, resolved = [], [], []
    before_domains, after_domains = [], []
    invalid_before = invalid_after = False
    for name in IMPACTS:
        first, second = before.impacts[name], after.impacts[name]
        first_issues = _validate_factor(first, "before." + name)
        second_issues = _validate_factor(second, "after." + name)
        issues.extend(first_issues + second_issues)
        invalid_before |= bool(first_issues)
        invalid_after |= bool(second_issues)
        first_known = (not first_issues and first.value is not None and first.confirmed and not first.disputed)
        second_known = (not second_issues and second.value is not None and second.confirmed and not second.disputed)
        before_domains.append(factor_domain(first) if not first_issues else (1, 5))
        after_domains.append(factor_domain(second) if not second_issues else (1, 5))
        if comparable and not first_known and second_known and not first_issues:
            resolved.append(name)
        if not comparable or not first_known or not second_known:
            changes.append("NOT_COMPARABLE")
        else:
            changes.append("DOWN" if second.value < first.value else "UP" if second.value > first.value else "SAME")
    down = tuple(name for name, change in zip(IMPACTS, changes) if change == "DOWN")
    up = tuple(name for name, change in zip(IMPACTS, changes) if change == "UP")
    same = tuple(name for name, change in zip(IMPACTS, changes) if change == "SAME")
    unresolved = tuple(name for name, change in zip(IMPACTS, changes) if change == "NOT_COMPARABLE")
    overall = ("NOT_COMPARABLE" if not comparable else "INCOMPLETE" if unresolved else
               "MIXED" if down and up else "IMPROVED" if down else "WORSENED" if up else "UNCHANGED")
    worsening = None if not comparable else True if up else None if unresolved else False
    first_r25 = before.risk.R25 if before.risk and not invalid_before else None
    second_r25 = after.risk.R25 if after.risk and not invalid_after else None
    r_progress, r25_change = "NOT_COMPARABLE", None
    if comparable:
        if first_r25 is None or second_r25 is None:
            r_progress = "UNDETERMINED"
        else:
            r25_change = second_r25 - first_r25
            r_progress = "DOWN" if r25_change < 0 else "UP" if r25_change > 0 else "SAME"
    return ImpactComparison(
        before_snapshot_id=before.snapshot_id, after_snapshot_id=after.snapshot_id,
        comparability="COMPARABLE" if comparable else "NOT_COMPARABLE", comparability_reasons=tuple(reasons),
        per_dimension=tuple(changes), impact_progress=overall, verified_worsening=worsening,
        impact_summary_before=ImpactSummary() if invalid_before else summarize_impact(before_domains),
        impact_summary_after=ImpactSummary() if invalid_after else summarize_impact(after_domains),
        comparison_review_status="NEEDS_REVIEW" if unresolved or not comparable or unresolved_comparison_disagreement else "EVALUATED",
        R_progress=r_progress, R25_change=r25_change,
        score_change=_decimal(r25_change) if r25_change is not None else None,
        score_before=_decimal(first_r25) if first_r25 is not None else None,
        score_before_range=before.risk.score_range if before.risk and not invalid_before else None,
        score_after=_decimal(second_r25) if second_r25 is not None else None,
        score_after_range=after.risk.score_range if after.risk and not invalid_after else None,
        treatment_attribution="SUPPORTED" if comparable and treatment_link_confirmed and treatment_evidence_ids else "REVIEW_REQUIRED",
        improved_dimensions=down, worsened_dimensions=up, unchanged_dimensions=same, unresolved_dimensions=unresolved,
        evidence_gap_resolved_dimensions=tuple(resolved), assessment_status_before=before.assessment_status,
        assessment_status_after=after.assessment_status, validation_issues=tuple(issues),
    )
