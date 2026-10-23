#!/usr/bin/env python3
"""Read-only, portable RM-01 v0.4 verification; Python 3.9+, standard library.

Never regenerates fixture expectations. Exit 0 = every assertion passed;
exit 1 = mismatch, invalid fixture, or missing required fixture file.
Optional --json-output writes only the requested result file.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

KEYS = ('E', 'F', 'G', 'C', 'I_integrity', 'A', 'B')
IMPACTS = KEYS[3:]
LEVELS = ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')


def require(condition, explanation):
    if not condition:
        raise AssertionError(explanation)


def same(actual, expected, label):
    require(actual == expected, '%s: got %r; expected %r' % (label, actual, expected))


def ordinal(x):
    return type(x) is int and 1 <= x <= 5


def interval(x):
    return isinstance(x, (list, tuple)) and len(x) == 2 and all(map(ordinal, x)) and x[0] <= x[1]


def decimal(x):
    """Exact decimal text for terminating fractions in these fixtures."""
    x = Q(x)
    sign = '-' if x < 0 else ''
    x = abs(x)
    whole, remainder = divmod(x.numerator, x.denominator)
    digits = ''
    seen = set()
    while remainder:
        require(remainder not in seen, 'Non-terminating decimal requested')
        seen.add(remainder)
        digit, remainder = divmod(10 * remainder, x.denominator)
        digits += str(digit)
    return sign + str(whole) + ('.' + digits if digits else '')


def score(e, f, g, impact, e_weight=Q(2, 5)):
    """Independent literal fractional formula, not integer implementation."""
    potential = e_weight * e + (1 - e_weight) * f
    likelihood = 1 + (potential - 1) * Q(g, 5)
    return likelihood * impact


def integer_score(e, f, g, impact):
    return impact * (25 + (2 * e + 3 * f - 5) * g)


def raw_level(value):
    return LEVELS[sum(value >= threshold for threshold in (5, 10, 17))]


def final_level(value, impact):
    index = LEVELS.index(raw_level(value))
    return LEVELS[0 if impact == 1 else min(index, 1) if impact == 2 else index]


def display(value, up=False):
    scaled = 10 * Q(value)
    tenths = -(-scaled.numerator // scaled.denominator) if up else scaled.numerator // scaled.denominator
    return '%d.%d' % divmod(tenths, 10)


def normalize(case):
    """Derive domains from input only; never consume stored expected domains."""
    if not case.get('essential_context_complete', True):
        return {'error': 'MISSING_ESSENTIAL_CONTEXT'}
    supplied = dict(case['factors'])
    same(set(supplied), set(KEYS), case['id'] + ': seven input keys')
    if any(v is not None and not ordinal(v) for v in supplied.values()):
        return {'error': 'INVALID_INPUT'}
    constraints = case.get('evidence_bound_constraints', {})
    if any(k not in KEYS or not interval(b) for k, b in constraints.items()):
        return {'error': 'INVALID_BOUND_INPUT'}
    for key in case.get('unconfirmed_factors', []):
        supplied[key] = None
    ignored = list(case.get('unconfirmed_bounds', []))
    domains = {}
    for key in KEYS:
        value = supplied[key]
        domains[key] = [value, value] if value is not None else (
            list(constraints[key]) if key in constraints and key not in ignored else [1, 5])
    gaps = [key for key in KEYS if supplied[key] is None]
    path_domains, path_gaps = [], []
    if 'paths' in case:
        paths = deepcopy(case['paths'])
        if not paths or not case.get('path_inventory_complete', True):
            paths.append({'path_id': 'UNASSESSED_SCOPE', 'coverage': 'UNKNOWN', 'g': None})
        for path in paths:
            value, bounds = path.get('g'), path.get('bounds', [1, 5])
            if (value is not None and not ordinal(value)) or not interval(bounds):
                return {'error': 'INVALID_PATH_INPUT'}
            if path.get('coverage') == 'VERIFIED_UNCOVERED' and value != 5:
                return {'error': 'UNCOVERED_PATH_REQUIRES_G5'}
            if path.get('coverage') == 'UNKNOWN' or not path.get('confirmed', True):
                value = None
            if value is None:
                path_gaps.append(path['path_id'])
                domain = list(bounds) if path.get('bounds_confirmed', False) else [1, 5]
                if bounds != [1, 5] and not path.get('bounds_confirmed', False):
                    ignored.append(path['path_id'])
            else:
                domain = [value, value]
            path_domains.append({'path_id': path['path_id'], 'bounds': domain, 'coverage': path.get('coverage')})
        domains['G'] = [max(p['bounds'][i] for p in path_domains) for i in (0, 1)]
        gaps = [key for key in gaps if key != 'G']
        if path_gaps:
            gaps.append('G_PATH_EVIDENCE')
    return {'domains': domains, 'normalized_factors': supplied, 'missing_factors': gaps,
            'missing_paths': path_gaps, 'path_domains': path_domains,
            'ignored_unconfirmed_bounds': ignored}


def verify_result(case, stored, label, baseline=None):
    inputs = normalize(case)
    if 'error' in inputs:
        same(stored['reason'], inputs['error'], label + '.reason')
        same(stored['status'], 'NEEDS_REVIEW', label + '.status')
        same(stored['score_determined'], False, label + '.score_determined')
        for key in ('score', 'score_range', 'R25', 'R25_range', 'raw_level', 'risk_level',
                    'level_range', 'raw_level_range', 'impact_gate_reason'):
            same(stored[key], None, label + '.' + key)
        return 0
    domains = inputs['domains']
    lo = [domains[key][0] for key in KEYS]
    hi = [domains[key][1] for key in KEYS]
    impacts = [max(lo[3:]), max(hi[3:])]
    # Exhaustive completions validate interval claims against the literal formula.
    values, labels = [], []
    for completion in product(*(range(domains[k][0], domains[k][1] + 1) for k in KEYS)):
        impact = max(completion[3:])
        value = score(*completion[:3], impact)
        values.append(value)
        labels.append(LEVELS.index(final_level(value, impact)))
    bounds = [min(values), max(values)]
    r25_bounds = [int(x * 25) for x in bounds]
    determined = bounds[0] == bounds[1]
    calc = dict(inputs)
    gaps = inputs['missing_factors']
    path_gaps = inputs['missing_paths']
    calc.update(status='NEEDS_REVIEW' if gaps or path_gaps else 'EVALUATED',
                reason='INCOMPLETE_EVIDENCE' if gaps or path_gaps else None,
                score=decimal(bounds[0]) if determined else None,
                R25=r25_bounds[0] if determined else None,
                score_range=list(map(decimal, bounds)), R25_range=r25_bounds,
                score_determined=determined,
                raw_level=raw_level(bounds[0]) if determined else None,
                risk_level=final_level(bounds[0], impacts[0]) if determined else None,
                raw_level_range=list(map(raw_level, bounds)),
                level_range=[LEVELS[min(labels)], LEVELS[max(labels)]],
                impact_gate_reason=('I_EQ_1_LOW' if impacts[0] == 1 else 'I_EQ_2_CAP_MODERATE'
                                    if impacts[0] == 2 else 'NONE') if determined else None,
                aggregate_values={'G': domains['G'][0] if domains['G'][0] == domains['G'][1] else None,
                                  'G_range': domains['G'], 'I_total': impacts[0] if impacts[0] == impacts[1] else None,
                                  'I_total_range': impacts},
                P_range=[decimal(Q(2, 5) * v[0] + Q(3, 5) * v[1]) for v in (lo, hi)],
                L_range=[decimal(score(*v[:3], 1)) for v in (lo, hi)],
                display={'score': display(bounds[0]) if determined else None,
                         'score_range': [display(bounds[0]), display(bounds[1], up=True)],
                         'rule': 'POINT_FLOOR_1DP_RANGE_OUTWARD_1DP_LABEL_FROM_EXACT_R25'})
    reasons = []
    if determined:
        reasons.append('EXACT_MODEL_BOUNDS_COLLAPSE')
        if domains['G'] == [5, 5] and path_gaps:
            reasons.append('G_MAX_5_ABSORBS_UNKNOWN_PATH')
        elif domains['G'][0] == domains['G'][1] and path_gaps:
            reasons.append('G_MAX_BOUND_DOMINATES_UNKNOWN_PATH')
        if impacts == [5, 5] and any(inputs['normalized_factors'][key] is None for key in IMPACTS):
            reasons.append('IMPACT_MAX_5_ABSORBS_UNKNOWN')
        if domains['E'] == domains['F'] == [1, 1] and domains['G'][0] != domains['G'][1]:
            reasons.append('P_EQ_1_SCORE_INDEPENDENT_OF_G')
    calc['determination_reasons'] = reasons
    if baseline is not None:
        calc.update(counterfactual_probe_only=True,
                    baseline_missing_factors=baseline['missing_factors'],
                    baseline_missing_paths=baseline['missing_paths'])
        if baseline['status'] == 'NEEDS_REVIEW':
            calc.update(status='NEEDS_REVIEW', reason='COUNTERFACTUAL_ENDPOINT_DOES_NOT_CLOSE_BASELINE_EVIDENCE_GAPS',
                        missing_factors=sorted(set(gaps + baseline['missing_factors'])),
                        missing_paths=sorted(set(path_gaps + baseline['missing_paths'])))
    same(stored, calc, label)
    return len(values)


def verify_main(data):
    same(data['profile'], 'CONDITIONAL-BASE-v0.4', 'profile')
    same(data['weights'], {'E': '0.40', 'F': '0.60'}, 'weights')
    cases = data['cases']
    same([case['id'] for case in cases], ['MF-%02d' % i for i in range(1, 27)], 'fixed case IDs')
    completions = sum(verify_result(case, case['expected'], case['id']) for case in cases)
    points = {}
    edges, gate_changes = 0, []
    for p in product(range(1, 6), repeat=4):
        value, n = score(*p), integer_score(*p)
        same(value, Q(n, 25), 'literal vs R25 ' + str(p))
        require(1 <= value <= 25, 'Score range')
        require(p[3] > 2 or LEVELS.index(final_level(value, p[3])) <= 1, 'Low impact gate')
        require(final_level(value, p[3]) != 'CRITICAL' or p[3] >= 4, 'Critical requires I>=4')
        require(p[2] != 1 or value <= 9, 'G1 upper bound')
        require(p[:2] != (1, 1) or value == p[3], 'P1 independence of G')
        same(raw_level(Q(display(value))), raw_level(value), 'Point display label preservation')
        same(int(10 * Q(display(value))), (2 * n) // 5, 'Integer display formula')
        if raw_level(value) != final_level(value, p[3]):
            gate_changes.append(list(p))
        points[p] = (n, LEVELS.index(final_level(value, p[3])))
    same(gate_changes, [[5, 5, 5, 1], [5, 5, 5, 2]], 'Exactly two impact gate changes')
    for p, result in points.items():
        for axis in range(4):
            if p[axis] < 5:
                neighbour = list(p)
                neighbour[axis] += 1
                new = points[tuple(neighbour)]
                require(new[0] >= result[0] and new[1] >= result[1], 'Monotonic edge')
                edges += 1
    boundaries = [(25, 'LOW'), (124, 'LOW'), (125, 'MODERATE'), (249, 'MODERATE'),
                  (250, 'HIGH'), (424, 'HIGH'), (425, 'CRITICAL'), (625, 'CRITICAL')]
    for n, expected in boundaries:
        same(raw_level(Q(n, 25)), expected, 'Raw boundary %d' % n)
    intervals = [(lo, hi) for lo in range(1, 6) for hi in range(lo, 6)]
    boxes = collapsed = box_completions = g_independent_boxes = 0
    for box in product(intervals, repeat=4):
        lower, upper = tuple(d[0] for d in box), tuple(d[1] for d in box)
        observed = [points[v] for v in product(*(range(d[0], d[1] + 1) for d in box))]
        same((min(v[0] for v in observed), max(v[0] for v in observed)),
             (points[lower][0], points[upper][0]), 'Box score bounds')
        same((min(v[1] for v in observed), max(v[1] for v in observed)),
             (points[lower][1], points[upper][1]), 'Box final label bounds')
        if points[lower][0] == points[upper][0]:
            require(all(lower[j] == upper[j] for j in (0, 1, 3)), 'Collapsed box determines E/F/I_total')
            same(points[lower][1], points[upper][1], 'Collapsed box determines final level')
            if lower[2] != upper[2]:
                same(lower[:2], (1, 1), 'Only P1 can absorb unknown G')
                g_independent_boxes += 1
            collapsed += 1
        boxes += 1
        box_completions += len(observed)
    by_id = {case['id']: case for case in cases}
    same([group['case_id'] for group in data['sensitivity']], list(by_id), 'Sensitivity case IDs')
    sensitivity_rows = probes = 0
    for group in data['sensitivity']:
        case = by_id[group['case_id']]
        baseline = case['expected']
        same(group['baseline'], baseline, case['id'] + ': sensitivity baseline')
        same([row['factor'] for row in group['factors']], list(KEYS), 'Sensitivity factors')
        for row in group['factors']:
            sensitivity_rows += 1
            key = row['factor']
            if baseline['score_range'] is None:
                same(row, {'factor': key, 'minus': None, 'plus': None,
                           'mode': 'NOT_RUN_INVALID_CONTEXT_OR_INPUT', 'original_value': case['factors'][key]},
                     case['id'] + ': invalid-input sensitivity')
                continue
            d = baseline['domains'][key]
            original = d[0] if d[0] == d[1] else None
            same(row['original_value'], original, case['id'] + ': original ' + key)
            same(row['mode'], 'ONE_AT_A_TIME_PLUS_MINUS_1' if original is not None else 'UNKNOWN_DOMAIN_ENDPOINTS',
                 case['id'] + ': sensitivity mode')
            if key == 'G' and 'paths' in case:
                same(row['scope_note'], 'AGGREGATE_G_COUNTERFACTUAL_PATH_EVIDENCE_NOT_MODIFIED', 'G probe scope')
            for direction, value in [('minus', original - 1 if original is not None else d[0]),
                                     ('plus', original + 1 if original is not None else d[1])]:
                if not ordinal(value):
                    same(row[direction], None, 'Outside-domain sensitivity')
                    continue
                probe = deepcopy(case)
                probe['factors'] = deepcopy(baseline['normalized_factors'])
                probe['factors'][key] = value
                probe['unconfirmed_factors'] = [k for k in case.get('unconfirmed_factors', []) if k != key]
                if key == 'G':
                    probe.pop('paths', None)
                verify_result(probe, row[direction], case['id'] + '.' + key + '.' + direction, baseline)
                probes += 1
    weights = (Q(3, 10), Q(4, 10), Q(1, 2))
    same(len(data['weight_sensitivity']), 3, 'Stored weight variants')
    for row, weight in zip(data['weight_sensitivity'], weights):
        result = score(5, 3, 4, 4, weight)
        same(row, {'case_id': 'MF-03', 'E_weight': decimal(weight), 'F_weight': decimal(1 - weight),
                   'score': decimal(result), 'delta': decimal(result - score(5, 3, 4, 4))}, 'MF03 stored weights')
    counts = {'fixed_cases': len(cases), 'raw_boundaries': len(boundaries), 'factor_lattice_combinations': len(points),
              'monotonic_edges': edges, 'bounded_boxes': boxes, 'collapsed_boxes': collapsed,
              'box_completions': box_completions, 'fixture_completions': completions,
              'sensitivity_rows': sensitivity_rows, 'weight_variants': len(weights), 'result': 'PASS'}
    same(counts, data['validation'], 'Recomputed counts vs stored validation')
    return counts, {'sensitivity_probes_checked': probes, 'gate_change_tuples_E_F_G_I_total': gate_changes,
                    'collapsed_boxes_with_unknown_G': g_independent_boxes}


def impact_summary(domains):
    """Describe one snapshot; an established max does not establish its count."""
    totals, counts = set(), set()
    for values in product(*(range(lo, hi + 1) for lo, hi in domains)):
        total = max(values)
        totals.add(total)
        counts.add(values.count(total))
    total_range, count_range = [min(totals), max(totals)], [min(counts), max(counts)]
    return {'I_total': total_range[0] if len(totals) == 1 else None,
            'I_total_range': total_range,
            'max_dimension_count': count_range[0] if len(counts) == 1 else None,
            'max_dimension_count_range': count_range}


def verify_supplement(data):
    """Review-contract fixtures; not an implementation of the future application."""
    same(data['rule_id'], 'IMPACT-PROGRESS-v0.1', 'Impact progress rule')
    same(data['fixture_revision'], 'v0.1-r2', 'Impact fixture revision')
    same(data['score_profile'], 'CONDITIONAL-BASE-v0.4', 'Unchanged score profile')
    same(data['impact_order'], list(IMPACTS), 'Impact dimension order')
    baseline = data['baseline']
    base_context = baseline['context']
    required_context = {'scenario', 'scoring_type', 'method', 'profile', 'ordinal_rubric',
                        'event_scope', 'assessment_scope', 'preconditions'}
    same(set(base_context), required_context, 'Comparable context dimensions')
    same(baseline['verified_dimensions'], list(IMPACTS), 'Verified baseline assumption')
    require(baseline['snapshot_id'] and len(baseline['evidence_ids']) == 4, 'Baseline traceability')
    base_score = score(*baseline['EFG'], max(baseline['impact']))
    same(decimal(base_score), '12.32', 'MF04 baseline')
    examples = []
    for supplied in data['cases']:
        original_case = deepcopy(supplied)
        case = dict(data['case_defaults'], **supplied)
        require(case['snapshot_id'] and case['reason'], case['id'] + ': snapshot and rationale required')
        after = case['after_impact']
        require(len(after) == 4 and all(v is None or ordinal(v) for v in after), 'Impact domain')
        context = dict(base_context, **case['context_overrides'])
        comparable = context == base_context
        before_impact = case.get('before_impact_override', baseline['impact'])
        before_verified = case.get('before_verified_dimensions_override', baseline['verified_dimensions'])
        per_dimension, domains, before_domains, resolved = [], [], [], []
        for i, key in enumerate(IMPACTS):
            before, value = before_impact[i], after[i]
            before_known = before is not None and key in before_verified
            known = value is not None and key in case['after_verified_dimensions'] and key not in case['after_disputed_dimensions']
            before_domains.append([before, before] if before_known else [1, 5])
            domains.append([value, value] if known else [1, 5])
            if comparable and not before_known and known:
                resolved.append(key)
            if not comparable or not before_known or not known:
                per_dimension.append('NOT_COMPARABLE')
            else:
                per_dimension.append('DOWN' if value < before else 'UP' if value > before else 'SAME')
        down = [key for key, state in zip(IMPACTS, per_dimension) if state == 'DOWN']
        up = [key for key, state in zip(IMPACTS, per_dimension) if state == 'UP']
        unresolved = 'NOT_COMPARABLE' in per_dimension
        overall = ('NOT_COMPARABLE' if not comparable else 'INCOMPLETE' if unresolved else
                   'MIXED' if down and up else 'IMPROVED' if down else 'WORSENED' if up else 'UNCHANGED')
        verified_worsening = (None if not comparable else True if up else None if unresolved else False)
        summary_before, summary_after = impact_summary(before_domains), impact_summary(domains)
        efg = case.get('EFG_override', baseline['EFG'])
        efg_bounds = [(v, v) if v is not None else (1, 5) for v in efg]
        efg_lo, efg_hi = [b[0] for b in efg_bounds], [b[1] for b in efg_bounds]
        before_bounds = [score(*v, max(domain[i] for domain in before_domains))
                         for i, v in enumerate((efg_lo, efg_hi))]
        before_score = before_bounds[0] if before_bounds[0] == before_bounds[1] else None
        after_bounds = [score(*v, max(domain[i] for domain in domains)) for i, v in enumerate((efg_lo, efg_hi))]
        after_score = after_bounds[0] if after_bounds[0] == after_bounds[1] else None
        change = ('NOT_COMPARABLE' if not comparable or before_score is None or after_score is None else
                  'DOWN' if after_score < before_score else 'UP' if after_score > before_score else 'SAME')
        attribution = 'SUPPORTED' if comparable and case['treatment_link_confirmed'] and case['treatment_evidence_id'] else 'REVIEW_REQUIRED'
        expected = {'per_dimension': per_dimension, 'overall': overall,
                    'verified_worsening': verified_worsening,
                    'impact_summary_before': summary_before, 'impact_summary_after': summary_after,
                    'comparison_review_status': 'NEEDS_REVIEW' if unresolved or not comparable else 'EVALUATED',
                    'score_after': decimal(after_score) if after_score is not None else None,
                    'score_after_range': list(map(decimal, after_bounds)), 'score_change': change,
                    'treatment_attribution': attribution}
        if 'evidence_gap_resolved_dimensions' in supplied['expected']:
            expected['evidence_gap_resolved_dimensions'] = resolved
        same(expected, supplied['expected'], case['id'])
        same(supplied, original_case, case['id'] + ': source snapshot is immutable')
        same(case['remaining_control_gaps'], data['case_defaults']['remaining_control_gaps'],
             case['id'] + ': progress cannot close a control gap')
        if case['id'] == 'IP-15':
            same(case['assessment_status_before'], 'NEEDS_REVIEW', 'Original G gap before')
            same(case['assessment_status_after'], 'NEEDS_REVIEW', 'Original G gap after')
            same(expected['comparison_review_status'], 'EVALUATED', 'Separate impact comparison review status')
            same(overall, 'IMPROVED', 'Known impact improvement despite unknown G')
        examples.append({'id': case['id'], 'overall': overall, 'improved_dimensions': down,
                         'worsened_dimensions': up, 'score_change': change,
                         'verified_worsening': verified_worsening,
                         'impact_summary_before': summary_before, 'impact_summary_after': summary_after,
                         'assessment_status_before_preserved': case['assessment_status_before'],
                         'assessment_status_after_preserved': case['assessment_status_after'],
                         'evidence_gap_resolved_dimensions': resolved,
                         'treatment_attribution_scope': 'VERIFIED_COMPARABLE_DIMENSIONS_ONLY'})
    pairs = []
    for row in data['weight_pair_cases']:
        weight = Q(row['E_weight'])
        same(1 - weight, Q(row['F_weight']), 'Weight sum')
        three, four = score(5, 3, 4, 4, weight), score(3, 4, 4, 4, weight)
        order = 'MF03_LT_MF04' if three < four else 'MF03_GT_MF04' if three > four else 'EQUAL'
        same(decimal(three), row['expected_MF03'], 'MF03 weight sensitivity')
        same(decimal(four), row['expected_MF04'], 'MF04 weight sensitivity')
        same(order, row['expected_numeric_order'], 'Pair ordering')
        pairs.append({'E_weight': row['E_weight'], 'F_weight': row['F_weight'],
                      'MF03': decimal(three), 'MF04': decimal(four), 'numeric_order': order})
    same(score(5, 3, 4, 4, Q(1, 3)), score(3, 4, 4, 4, Q(1, 3)), 'Pair weights cross at E=1/3')
    actual_display, pure_formatter = data['display_cases']
    bounds = [score(*actual_display['EFG'], impact) for impact in actual_display['I_total_range']]
    same(list(map(decimal, bounds)), actual_display['expected_exact_range'], 'Attainable exact display range')
    same([display(bounds[0]), display(bounds[1], up=True)], actual_display['expected_display_range'], 'Outward display range')
    same([final_level(v, i) for v, i in zip(bounds, actual_display['I_total_range'])],
         actual_display['expected_level_range'], 'Exact labels before display rounding')
    formatter_value = Q(pure_formatter['R25'], 25)
    same(display(formatter_value, up=True), pure_formatter['expected_upper_display'], 'Formatter synthetic boundary')
    same(raw_level(formatter_value), pure_formatter['expected_raw_level'], 'Formatter exact raw level')
    lattice = {score(*v) for v in product(range(1, 6), repeat=4)}
    require(formatter_value not in lattice, '9.96 must not be called attainable in the baseline profile')
    same(max(v for v in lattice if v < 10), Q('9.8'), 'Largest attainable value below 10')
    same(max(v for v in lattice if v < 17), Q('16.8'), 'Largest attainable value below 17')
    disagreement = data['review_disagreement_case']
    disputed_scores = [score(*disagreement['EF'], g, disagreement['I_total']) for g in disagreement['G_candidates']]
    same(min(disputed_scores), max(disputed_scores), 'Disagreement may coexist with determined score')
    same(decimal(disputed_scores[0]), disagreement['expected_score'], 'Disagreement determined score')
    same(final_level(disputed_scores[0], disagreement['I_total']), disagreement['expected_risk_level'], 'Disagreement label')
    same('NEEDS_REVIEW' if disagreement['unresolved_reviewer_disagreement'] else 'EVALUATED',
         disagreement['expected_status'], 'Unresolved disagreement review gate')
    return {'fixture_revision': data['fixture_revision'],
            'impact_progress_cases': len(data['cases']), 'weight_pair_cases': len(pairs),
            'display_cases': len(data['display_cases']), 'review_disagreement_cases': 1,
            'weight_pair_results': pairs, 'impact_progress_results': examples}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json-output', type=Path, help='Optional path for machine-readable results')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    paths = [folder / 'risk-method-fixtures-v0.4.json', folder / 'impact-progress-fixtures-v0.1.json']
    if args.json_output:
        protected = {path.resolve() for path in paths + [Path(__file__)]}
        require(args.json_output.resolve() not in protected,
                '--json-output must not overwrite an input fixture or this script')
    data = json.loads(paths[0].read_text(encoding='utf-8-sig'))
    counts, additional = verify_main(data)
    supplemental = verify_supplement(json.loads(paths[1].read_text(encoding='utf-8-sig')))
    result = {'result': 'PASS', 'profile': data['profile'], 'verification_date': '2026-10-12',
              'scope': 'Arithmetic and synthetic design fixtures only; no CRM/lab evidence or human agreement.',
              'counts': counts, 'additional_checks': additional, 'supplemental_checks': supplemental,
              'sha256': {p.name: sha256(p.read_bytes()).hexdigest() for p in paths + [Path(__file__)]}}
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.json_output:
        args.json_output.write_text(text, encoding='utf-8')
    print(text, end='')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, ValueError, KeyError, OSError, TypeError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        sys.exit(1)
