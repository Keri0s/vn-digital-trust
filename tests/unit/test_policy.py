"""Pure policy boundaries; these tests do not exercise PostgreSQL or HTTP."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import unittest

from vdt.policy import Grant, Principal, Scope, Session, authorize, effective_grants


NOW = datetime(2026, 10, 23, 9, tzinfo=timezone.utc)
LATER = NOW + timedelta(hours=1)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.principal = Principal("user-1", "org-1")
        self.session = Session("user-1", expires_at=LATER, idle_expires_at=LATER)
        self.scope = Scope("org-1", branch_ids={"branch-1"}, asset_ids={"asset-1"},
                           scenario_ids={"scenario-1"}, assessment_ids={"assessment-1"})
        self.grant = Grant("grant-1", "user-1", {"evidence.read_assigned", "evidence.verify"}, self.scope)

    def decide(self, **overrides):
        arguments = dict(principal=self.principal, session=self.session,
                         grants=[self.grant], required_permissions="evidence.read_assigned",
                         target_scope=self.scope, now=NOW, assessment_id="assessment-1")
        arguments.update(overrides)
        return authorize(**arguments)

    def test_explicit_covering_grant_allows(self):
        self.assertTrue(self.decide())
        self.assertEqual(self.decide().grant_ids, ("grant-1",))

    def test_no_grant_or_no_permission_denies(self):
        self.assertFalse(self.decide(grants=[]))
        self.assertFalse(self.decide(required_permissions=[]))
        self.assertFalse(self.decide(required_permissions="risk.accept"))

    def test_each_expiry_denies_at_equality_and_after(self):
        for expiry in (NOW, NOW - timedelta(microseconds=1)):
            for kwargs in (
                {"principal": replace(self.principal, expires_at=expiry)},
                {"session": replace(self.session, expires_at=expiry)},
                {"session": replace(self.session, idle_expires_at=expiry)},
                {"grants": [replace(self.grant, expires_at=expiry)]},
                {"grants": [replace(self.grant, assessment_access_expires_at=expiry)]},
            ):
                with self.subTest(kwargs=kwargs):
                    self.assertFalse(self.decide(**kwargs))
        self.assertTrue(self.decide(grants=[replace(self.grant, expires_at=NOW + timedelta(microseconds=1))]))

    def test_active_authenticated_identity_and_matching_session_required(self):
        for kwargs in (
            {"principal": replace(self.principal, is_active=False)},
            {"principal": replace(self.principal, revoked_at=NOW)},
            {"session": replace(self.session, is_active=False)},
            {"session": replace(self.session, authenticated=False)},
            {"session": replace(self.session, revoked_at=NOW)},
            {"session": replace(self.session, principal_id="someone-else")},
            {"session": replace(self.session, expires_at=None)},
            {"grants": [replace(self.grant, is_active=False)]},
            {"grants": [replace(self.grant, revoked_at=NOW)]},
            {"grants": [replace(self.grant, principal_id="someone-else")]},
            {"grants": [replace(self.grant, valid_from=LATER)]},
        ):
            with self.subTest(kwargs=kwargs):
                self.assertFalse(self.decide(**kwargs))

    def test_naive_clock_or_expiry_is_denied(self):
        self.assertFalse(self.decide(now=NOW.replace(tzinfo=None)))
        self.assertFalse(self.decide(grants=[replace(self.grant, expires_at=LATER.replace(tzinfo=None))]))

    def test_organization_and_each_object_dimension_intersect(self):
        self.assertFalse(self.decide(target_scope=replace(self.scope, organization_id="org-2")))
        for dimension in ("branch_ids", "system_ids", "asset_ids", "data_asset_ids", "scenario_ids", "assessment_ids"):
            with self.subTest(dimension=dimension):
                self.assertFalse(self.decide(target_scope=replace(self.scope, **{dimension: {"not-granted"}})))

    def test_scope_cannot_be_assembled_across_grants(self):
        first = replace(self.grant, id="a", scope=replace(self.scope, asset_ids={"other-asset"}))
        second = replace(self.grant, id="b", scope=replace(self.scope, branch_ids={"other-branch"}))
        self.assertFalse(self.decide(grants=[first, second]))
        target = replace(self.scope, branch_ids={"branch-1", "branch-2"})
        second = replace(self.grant, id="b", scope=replace(self.scope, branch_ids={"branch-2"}))
        self.assertFalse(self.decide(grants=[self.grant, second], target_scope=target))

    def test_empty_grant_dimension_is_not_wildcard(self):
        self.assertFalse(self.decide(grants=[replace(self.grant, scope=Scope("org-1"))]))

    def test_empty_client_assessment_does_not_establish_reviewer_access(self):
        reviewer = replace(self.grant, reviewer=True, assigned_assessment_ids={"assessment-1"})
        self.assertFalse(self.decide(grants=[reviewer], target_scope=replace(self.scope, assessment_ids=set()), assessment_id=None))

    def test_reviewer_visibility_requires_exact_active_assignment(self):
        reviewer = replace(self.grant, reviewer=True, assigned_assessment_ids={"assessment-1"}, expires_at=LATER)
        self.assertTrue(self.decide(grants=[reviewer]))
        self.assertFalse(self.decide(grants=[reviewer], assessment_id=None))
        self.assertFalse(self.decide(grants=[replace(reviewer, assigned_assessment_ids={"other"})]))
        self.assertFalse(self.decide(grants=[replace(reviewer, expires_at=NOW)]))
        self.assertFalse(self.decide(grants=[reviewer], target_scope=replace(self.scope, assessment_ids={"assessment-1", "other"})))

    def test_independence_is_actor_identity_not_role_count(self):
        reviewer = replace(self.grant, reviewer=True, permissions={"assessment.review"}, assigned_assessment_ids={"assessment-1"})
        args = dict(grants=[reviewer, self.grant], required_permissions="assessment.review", require_reviewer=True)
        self.assertTrue(self.decide(**args, independent_from={"assessor-other"}))
        self.assertFalse(self.decide(**args, independent_from={"user-1"}))
        self.assertFalse(self.decide(require_reviewer=True))

    def test_verification_needs_each_permission_with_full_scope(self):
        verify = replace(self.grant, permissions={"evidence.verify"})
        self.assertFalse(self.decide(grants=[verify], required_permissions=["evidence.verify", "evidence.read_assigned"]))
        read = replace(self.grant, id="read", permissions={"evidence.read_assigned"})
        self.assertTrue(self.decide(grants=[verify, read], required_permissions=["evidence.verify", "evidence.read_assigned"]))
        read = replace(read, scope=replace(self.scope, asset_ids={"other"}))
        self.assertFalse(self.decide(grants=[verify, read], required_permissions=["evidence.verify", "evidence.read_assigned"]))

    def test_or_groups_and_admin_have_no_implied_domain_access(self):
        admin = replace(self.grant, permissions={"organization.manage"}, scope=Scope("org-1", branch_ids={"branch-1"}))
        self.assertTrue(self.decide(grants=[admin], required_permissions="organization.manage", target_scope=Scope("org-1"), assessment_id=None))
        self.assertFalse(self.decide(grants=[admin]))
        self.assertTrue(self.decide(required_permissions="report.read|evidence.read_assigned"))

    def test_effective_grants_preserve_separate_scopes_and_refresh(self):
        other = replace(self.grant, id="other", scope=replace(self.scope, branch_ids={"branch-2"}))
        grants = effective_grants(self.principal, self.session, [self.grant, other], now=NOW)
        self.assertEqual(len(grants), 2)
        self.assertNotEqual(grants[0].scope, grants[1].scope)
        self.assertFalse(effective_grants(self.principal, self.session, [replace(self.grant, revoked_at=NOW)], now=NOW))

    def test_scope_rejects_wildcard_unknown_dimension_or_string_array(self):
        for value in ({"organization_id": "*"}, {"organization_id": "org", "branch_ids": "branch"},
                      {"organization_id": "org", "branch_ids": ["*"]}, {"organization_id": "org", "user_ids": []}):
            with self.assertRaises(ValueError):
                Scope.from_mapping(value)
