-- VN Digital Trust / Step 05 / PostgreSQL 17 design DDL / 2026-10-20.
-- Reviewed design, NOT a deployed migration. Runtime/permission/fault tests: NOT_RUN.
-- One SME per database; UUIDs supplied by server, no identifier from filenames.
-- Apply with migration owner only. Runtime role must not own tables/functions,
-- disable triggers, issue DDL, TRUNCATE, or DELETE domain history.
BEGIN;
CREATE SCHEMA vdt;
SET search_path = vdt, pg_catalog;

CREATE DOMAIN sha256_hex AS text CHECK (VALUE ~ '^[0-9a-f]{64}$');
CREATE DOMAIN score_1_5 AS smallint CHECK (VALUE BETWEEN 1 AND 5);
CREATE DOMAIN nonempty_text AS text CHECK (length(btrim(VALUE)) > 0);
CREATE TYPE assessment_status AS ENUM ('EVALUATED','NEEDS_REVIEW');
CREATE TYPE assessment_mode AS ENUM ('SELF_ASSESSED','INDEPENDENT_REVIEWED');
CREATE TYPE review_outcome AS ENUM ('NONE','CONFIRMED','DISPUTED','ADJUSTED_NEW_SNAPSHOT');
CREATE TYPE risk_level AS ENUM ('LOW','MODERATE','HIGH','CRITICAL');
CREATE TYPE assessment_type AS ENUM ('CURRENT','INHERENT','ILLUSTRATIVE');
CREATE TYPE impact_dimension AS ENUM ('C','I_integrity','A','B');
CREATE TYPE control_result AS ENUM ('NOT_ASSESSED','SATISFIED','PARTIALLY_SATISFIED','NOT_SATISFIED','INSUFFICIENT_EVIDENCE');
CREATE TYPE execution_status AS ENUM ('PASS','FAIL','INCONCLUSIVE','NOT_READY');
CREATE TYPE confirmation_state AS ENUM ('PROPOSED','CONFIRMED');
CREATE TYPE storage_state AS ENUM ('STAGED','COMMITTED','INTEGRITY_FAILED','ORPHANED');
CREATE TYPE direction AS ENUM ('DOWN','UP','SAME','NOT_COMPARABLE');

CREATE TABLE organization (
  id uuid PRIMARY KEY, code nonempty_text UNIQUE NOT NULL,
  name nonempty_text NOT NULL,
  singleton boolean NOT NULL DEFAULT true CHECK (singleton),
  UNIQUE (singleton), version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE branch (
  id uuid PRIMARY KEY, organization_id uuid NOT NULL REFERENCES organization,
  code nonempty_text NOT NULL UNIQUE, name nonempty_text NOT NULL,
  active boolean NOT NULL DEFAULT true, version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE app_user (
  id uuid PRIMARY KEY, organization_id uuid NOT NULL REFERENCES organization,
  code nonempty_text UNIQUE, login_name nonempty_text NOT NULL UNIQUE,
  display_name nonempty_text NOT NULL,
  status text NOT NULL CHECK (status IN ('ACTIVE','PENDING','DISABLED','EXPIRED')),
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE user_branch (
  id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES app_user,
  branch_id uuid NOT NULL REFERENCES branch, UNIQUE (user_id,branch_id)
);
CREATE TABLE authorization_guard (
  id uuid PRIMARY KEY, organization_id uuid NOT NULL UNIQUE REFERENCES organization,
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE vdt_session (
  id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES app_user,
  session_token_hash sha256_hex NOT NULL UNIQUE,
  issued_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
  last_seen_at timestamptz NOT NULL, revoked_at timestamptz,
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
  CHECK (expires_at > issued_at)
);
CREATE TABLE role (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE, description text NOT NULL
);
CREATE TABLE permission (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE, description text NOT NULL
);
CREATE TABLE role_permission (
  id uuid PRIMARY KEY, role_id uuid NOT NULL REFERENCES role,
  permission_id uuid NOT NULL REFERENCES permission,
  UNIQUE (role_id,permission_id)
);

CREATE TABLE information_system (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE, name nonempty_text NOT NULL,
  owner_id uuid REFERENCES app_user, purpose text NOT NULL,
  hosting text, exposure text, criticality text, facts jsonb NOT NULL DEFAULT '{}',
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE asset (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE, name nonempty_text NOT NULL,
  asset_type nonempty_text NOT NULL, owner_id uuid REFERENCES app_user,
  branch_id uuid REFERENCES branch, status nonempty_text NOT NULL,
  facts jsonb NOT NULL DEFAULT '{}', version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE data_asset (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE, name nonempty_text NOT NULL,
  owner_id uuid REFERENCES app_user, branch_id uuid REFERENCES branch,
  sensitivity text, description text NOT NULL,
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE vendor (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE, name nonempty_text NOT NULL,
  owner_id uuid REFERENCES app_user, service_description text NOT NULL,
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE system_asset (
  id uuid PRIMARY KEY, system_id uuid NOT NULL REFERENCES information_system,
  asset_id uuid NOT NULL REFERENCES asset, relationship text NOT NULL,
  UNIQUE (system_id,asset_id)
);
CREATE TABLE system_data_asset (
  id uuid PRIMARY KEY, system_id uuid NOT NULL REFERENCES information_system,
  data_asset_id uuid NOT NULL REFERENCES data_asset,
  UNIQUE (system_id,data_asset_id)
);
CREATE TABLE system_vendor (
  id uuid PRIMARY KEY, system_id uuid NOT NULL REFERENCES information_system,
  vendor_id uuid NOT NULL REFERENCES vendor, dependency text NOT NULL,
  UNIQUE (system_id,vendor_id)
);
CREATE TABLE data_flow (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE,
  source_asset_id uuid NOT NULL REFERENCES asset,
  destination_asset_id uuid NOT NULL REFERENCES asset,
  data_asset_id uuid NOT NULL REFERENCES data_asset,
  channel text, trust_boundary text NOT NULL, destination_policy text,
  facts jsonb NOT NULL DEFAULT '{}', version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE risk_scenario (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE, owner_id uuid REFERENCES app_user,
  event nonempty_text NOT NULL, preconditions text, consequence text NOT NULL,
  status text NOT NULL CHECK (status IN ('DRAFT','ACTIVE','RETIRED')),
  source jsonb NOT NULL DEFAULT '{}', version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE scenario_target (
  id uuid PRIMARY KEY, scenario_id uuid NOT NULL REFERENCES risk_scenario,
  system_id uuid REFERENCES information_system, asset_id uuid REFERENCES asset,
  CHECK (num_nonnulls(system_id,asset_id)=1),
  UNIQUE NULLS NOT DISTINCT (scenario_id,system_id,asset_id)
);
CREATE TABLE assessment (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE,
  owner_id uuid NOT NULL REFERENCES app_user,
  scenario_id uuid REFERENCES risk_scenario,
  workflow_state text NOT NULL CHECK (workflow_state IN ('OPEN','ARCHIVED')),
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);

-- Scope is an immutable selector set. No wildcard is inferred from an empty set.
-- resource_kind distinguishes selectors; branches intersect explicit object scope.
CREATE TABLE scope (
  id uuid PRIMARY KEY, organization_id uuid NOT NULL REFERENCES organization,
  scope_kind text NOT NULL CHECK (scope_kind IN ('ORGANIZATION','SELECTED')),
  description nonempty_text NOT NULL, content_hash sha256_hex NOT NULL,
  created_txid bigint NOT NULL DEFAULT txid_current()
);
CREATE TABLE scope_branch (
  id uuid PRIMARY KEY, scope_id uuid NOT NULL REFERENCES scope,
  branch_id uuid NOT NULL REFERENCES branch, UNIQUE(scope_id,branch_id)
);
CREATE TABLE scope_object (
  id uuid PRIMARY KEY, scope_id uuid NOT NULL REFERENCES scope,
  system_id uuid REFERENCES information_system, asset_id uuid REFERENCES asset,
  data_asset_id uuid REFERENCES data_asset, scenario_id uuid REFERENCES risk_scenario,
  assessment_id uuid REFERENCES assessment,
  CHECK (num_nonnulls(system_id,asset_id,data_asset_id,scenario_id,assessment_id)=1),
  UNIQUE NULLS NOT DISTINCT (scope_id,system_id,asset_id,data_asset_id,scenario_id,assessment_id)
);
CREATE TABLE role_assignment (
  id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES app_user,
  role_id uuid NOT NULL REFERENCES role, scope_id uuid NOT NULL REFERENCES scope,
  valid_from timestamptz NOT NULL, access_expires_at timestamptz,
  revoked_at timestamptz, granted_by uuid NOT NULL REFERENCES app_user,
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
  CHECK (access_expires_at IS NULL OR access_expires_at > valid_from)
);
CREATE TABLE assignment_assessment (
  id uuid PRIMARY KEY, assignment_id uuid NOT NULL REFERENCES role_assignment,
  assessment_id uuid NOT NULL REFERENCES assessment,
  UNIQUE(assignment_id,assessment_id)
);

-- All committed snapshots and their children are inserted in one transaction.
-- created_txid + append-only triggers below prevent later child additions.
CREATE TABLE snapshot_registry (
  id uuid PRIMARY KEY, snapshot_kind nonempty_text NOT NULL,
  scope_id uuid NOT NULL REFERENCES scope,
  created_by uuid NOT NULL REFERENCES app_user, created_at timestamptz NOT NULL,
  content_hash sha256_hex NOT NULL,
  created_txid bigint NOT NULL DEFAULT txid_current()
);
CREATE TABLE context_snapshot (
  id uuid PRIMARY KEY REFERENCES snapshot_registry,
  assessment_id uuid REFERENCES assessment,
  scenario_id uuid REFERENCES risk_scenario,
  scenario_version bigint CHECK (scenario_version > 0),
  schema_version nonempty_text NOT NULL, facts jsonb NOT NULL,
  scenario_description nonempty_text,
  preconditions jsonb NOT NULL, unknown_facts text[] NOT NULL DEFAULT '{}',
  input_versions jsonb NOT NULL, environment_fingerprint text,
  CHECK (jsonb_typeof(facts)='object'), CHECK (jsonb_typeof(input_versions)='object')
);
CREATE TABLE control_definition_version (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL, version nonempty_text NOT NULL,
  objective nonempty_text NOT NULL, source jsonb NOT NULL,
  content_hash sha256_hex NOT NULL, created_txid bigint NOT NULL DEFAULT txid_current(),
  UNIQUE(code,version)
);
CREATE TABLE control_criterion_version (
  id uuid PRIMARY KEY, control_version_id uuid NOT NULL REFERENCES control_definition_version,
  code nonempty_text NOT NULL, version nonempty_text NOT NULL,
  mandatory boolean NOT NULL, requirement nonempty_text NOT NULL,
  evidence_expectation jsonb NOT NULL, content_hash sha256_hex NOT NULL,
  UNIQUE(control_version_id,code,version)
);
CREATE TABLE test_case_version (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL, version nonempty_text NOT NULL,
  preconditions jsonb NOT NULL, action nonempty_text NOT NULL,
  expected_result nonempty_text NOT NULL, content_hash sha256_hex NOT NULL,
  created_txid bigint NOT NULL DEFAULT txid_current(), UNIQUE(code,version)
);
CREATE TABLE test_case_criterion (
  id uuid PRIMARY KEY, test_case_version_id uuid NOT NULL REFERENCES test_case_version,
  criterion_version_id uuid NOT NULL REFERENCES control_criterion_version,
  UNIQUE(test_case_version_id,criterion_version_id)
);
CREATE TABLE risk_method_version (
  id uuid PRIMARY KEY, method_code nonempty_text NOT NULL,
  document_revision nonempty_text NOT NULL, calculation_profile nonempty_text NOT NULL,
  rubric_version nonempty_text NOT NULL, progress_rule_version nonempty_text NOT NULL,
  definition jsonb NOT NULL, content_hash sha256_hex NOT NULL,
  UNIQUE(method_code,document_revision,calculation_profile,rubric_version)
);
CREATE TABLE control_implementation (
  id uuid PRIMARY KEY, control_version_id uuid NOT NULL REFERENCES control_definition_version,
  owner_id uuid NOT NULL REFERENCES app_user, scope_id uuid NOT NULL REFERENCES scope,
  declared_status nonempty_text NOT NULL, rationale text NOT NULL,
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0)
);
CREATE TABLE scenario_control (
  id uuid PRIMARY KEY, scenario_id uuid NOT NULL REFERENCES risk_scenario,
  control_version_id uuid NOT NULL REFERENCES control_definition_version,
  implementation_id uuid REFERENCES control_implementation, rationale nonempty_text NOT NULL,
  UNIQUE NULLS NOT DISTINCT(scenario_id,control_version_id,implementation_id)
);
CREATE TABLE authentication_profile_version (
  id uuid PRIMARY KEY REFERENCES snapshot_registry,
  code nonempty_text NOT NULL, revision_number integer NOT NULL CHECK (revision_number > 0),
  system_id uuid NOT NULL REFERENCES information_system,
  configuration_state text NOT NULL CHECK (configuration_state IN ('TO_SET_BEFORE_LAB','PROPOSED','APPROVED')),
  implementation_status text NOT NULL,
  challenge_ttl_seconds integer CHECK (challenge_ttl_seconds > 0),
  max_attempt_limit integer CHECK (max_attempt_limit > 0),
  session_idle_timeout_seconds integer CHECK (session_idle_timeout_seconds > 0),
  session_absolute_timeout_seconds integer CHECK (session_absolute_timeout_seconds > 0),
  failed_attempt_window_seconds integer CHECK (failed_attempt_window_seconds > 0),
  failed_attempt_lockout_seconds integer CHECK (failed_attempt_lockout_seconds > 0),
  reauth_max_age_seconds integer CHECK (reauth_max_age_seconds >= 0),
  revocation_max_delay_seconds integer CHECK (revocation_max_delay_seconds >= 0),
  rp_id text, allowed_origins text[],
  authentication_factors text[] NOT NULL DEFAULT ARRAY['PASSWORD','WEBAUTHN'],
  user_verification_required boolean NOT NULL DEFAULT true CHECK (user_verification_required),
  totp_fallback_enabled boolean NOT NULL DEFAULT false CHECK (NOT totp_fallback_enabled),
  passwordless_enabled boolean NOT NULL DEFAULT false CHECK (NOT passwordless_enabled),
  enrollment_policy jsonb, recovery_policy jsonb, notification_policy jsonb,
  approved_by uuid REFERENCES app_user, approved_at timestamptz,
  UNIQUE(code,revision_number),
  CHECK(authentication_factors = ARRAY['PASSWORD','WEBAUTHN']),
  CHECK(configuration_state <> 'APPROVED' OR
    (challenge_ttl_seconds IS NOT NULL AND max_attempt_limit IS NOT NULL
     AND session_idle_timeout_seconds IS NOT NULL AND rp_id IS NOT NULL
     AND allowed_origins IS NOT NULL AND cardinality(allowed_origins)>0
     AND approved_by IS NOT NULL AND approved_at IS NOT NULL))
);

CREATE TABLE evidence_item (
  id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE,
  owner_id uuid NOT NULL REFERENCES app_user, assessment_id uuid NOT NULL REFERENCES assessment,
  scope_id uuid NOT NULL REFERENCES scope, source_description nonempty_text NOT NULL,
  version bigint NOT NULL DEFAULT 1 CHECK(version > 0)
);
CREATE TABLE evidence_revision (
  id uuid PRIMARY KEY REFERENCES snapshot_registry,
  evidence_item_id uuid NOT NULL REFERENCES evidence_item,
  revision_number integer NOT NULL CHECK (revision_number > 0),
  previous_revision_id uuid REFERENCES evidence_revision,
  evidence_kind text NOT NULL CHECK (evidence_kind IN ('FILE','REFERENCE')),
  collected_at timestamptz NOT NULL, valid_until timestamptz,
  source_description nonempty_text NOT NULL, provenance jsonb NOT NULL,
  redaction_manifest jsonb NOT NULL, environment_snapshot jsonb NOT NULL,
  content_sha256 sha256_hex, size_bytes bigint CHECK (size_bytes >= 0),
  media_type text, original_filename text, reference_uri text,
  UNIQUE(evidence_item_id,revision_number),
  CHECK(valid_until IS NULL OR valid_until > collected_at),
  CHECK((evidence_kind='FILE' AND content_sha256 IS NOT NULL AND size_bytes IS NOT NULL AND reference_uri IS NULL)
     OR (evidence_kind='REFERENCE' AND reference_uri IS NOT NULL AND size_bytes IS NULL)),
  CHECK(previous_revision_id IS NULL OR previous_revision_id <> id)
);
CREATE TABLE evidence_storage (
  id uuid PRIMARY KEY, evidence_revision_id uuid NOT NULL UNIQUE REFERENCES evidence_revision,
  storage_state storage_state NOT NULL,
  blob_key text UNIQUE, scanner_verdict text,
  verified_hash sha256_hex, last_checked_at timestamptz, failure_reason text,
  version bigint NOT NULL DEFAULT 1 CHECK(version > 0)
);
CREATE TABLE verification_decision (
  id uuid PRIMARY KEY REFERENCES snapshot_registry,
  evidence_revision_id uuid NOT NULL REFERENCES evidence_revision,
  previous_decision_id uuid REFERENCES verification_decision,
  conclusion text NOT NULL CHECK (conclusion IN ('VERIFIED','REJECTED')),
  verification_mode assessment_mode NOT NULL,
  valid_until timestamptz, reason nonempty_text NOT NULL,
  source_checks jsonb NOT NULL, provenance_checks jsonb NOT NULL,
  UNIQUE(id,evidence_revision_id),
  CHECK(previous_decision_id IS NULL OR previous_decision_id <> id)
);
CREATE TABLE evidence_link (
  id uuid PRIMARY KEY REFERENCES snapshot_registry,
  evidence_revision_id uuid NOT NULL REFERENCES evidence_revision,
  implementation_id uuid NOT NULL REFERENCES control_implementation,
  criterion_version_id uuid REFERENCES control_criterion_version,
  rationale nonempty_text NOT NULL
);
CREATE TABLE test_execution (
  id uuid PRIMARY KEY REFERENCES snapshot_registry,
  assessment_id uuid NOT NULL REFERENCES assessment,
  test_case_version_id uuid NOT NULL REFERENCES test_case_version,
  authentication_profile_version_id uuid REFERENCES authentication_profile_version,
  execution_status execution_status NOT NULL,
  started_at timestamptz, finished_at timestamptz,
  environment jsonb NOT NULL, preconditions jsonb NOT NULL,
  expected_result nonempty_text NOT NULL, observation text NOT NULL,
  telemetry_status nonempty_text NOT NULL,
  CHECK(finished_at IS NULL OR (started_at IS NOT NULL AND finished_at >= started_at)),
  CHECK(execution_status='NOT_READY' OR started_at IS NOT NULL)
);
CREATE TABLE test_execution_evidence (
  id uuid PRIMARY KEY, test_execution_id uuid NOT NULL REFERENCES test_execution,
  evidence_revision_id uuid NOT NULL REFERENCES evidence_revision,
  verification_decision_id uuid NOT NULL,
  FOREIGN KEY(verification_decision_id,evidence_revision_id)
    REFERENCES verification_decision(id,evidence_revision_id),
  UNIQUE(test_execution_id,evidence_revision_id,verification_decision_id)
);

CREATE TABLE control_assessment (
  id uuid PRIMARY KEY REFERENCES snapshot_registry,
  assessment_id uuid NOT NULL REFERENCES assessment,
  context_snapshot_id uuid NOT NULL REFERENCES context_snapshot,
  control_version_id uuid NOT NULL REFERENCES control_definition_version,
  implementation_id uuid REFERENCES control_implementation,
  implementation_snapshot jsonb NOT NULL,
  result control_result NOT NULL, status assessment_status NOT NULL,
  score_determined boolean NOT NULL DEFAULT false CHECK(NOT score_determined),
  score_applicability text NOT NULL DEFAULT 'NOT_APPLICABLE' CHECK(score_applicability='NOT_APPLICABLE'),
  assessment_mode assessment_mode NOT NULL, review_outcome review_outcome NOT NULL DEFAULT 'NONE',
  supersedes_id uuid REFERENCES control_assessment,
  reasoning nonempty_text NOT NULL, unresolved_issues jsonb NOT NULL DEFAULT '[]',
  CHECK(supersedes_id IS NULL OR supersedes_id <> id)
);
CREATE TABLE control_assessment_criterion (
  id uuid PRIMARY KEY, control_assessment_id uuid NOT NULL REFERENCES control_assessment,
  criterion_version_id uuid NOT NULL REFERENCES control_criterion_version,
  scope_id uuid NOT NULL REFERENCES scope, result control_result NOT NULL,
  execution_status execution_status NOT NULL, observation text NOT NULL,
  reasoning nonempty_text NOT NULL,
  UNIQUE(control_assessment_id,criterion_version_id,scope_id)
);
CREATE TABLE criterion_evidence (
  id uuid PRIMARY KEY, criterion_result_id uuid NOT NULL REFERENCES control_assessment_criterion,
  evidence_revision_id uuid NOT NULL REFERENCES evidence_revision,
  verification_decision_id uuid NOT NULL,
  FOREIGN KEY(verification_decision_id,evidence_revision_id)
    REFERENCES verification_decision(id,evidence_revision_id),
  UNIQUE(criterion_result_id,evidence_revision_id,verification_decision_id)
);
CREATE TABLE criterion_test_execution (
  id uuid PRIMARY KEY, criterion_result_id uuid NOT NULL REFERENCES control_assessment_criterion,
  test_execution_id uuid NOT NULL REFERENCES test_execution,
  UNIQUE(criterion_result_id,test_execution_id)
);

-- RM-01: invalid numeric input is retained in raw_input; effective typed factors
-- exist only after validation. Integer R25 is canonical; exact decimals derived.
CREATE TABLE risk_evaluation (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 assessment_id uuid NOT NULL REFERENCES assessment,
 context_snapshot_id uuid NOT NULL REFERENCES context_snapshot,
 method_version_id uuid NOT NULL REFERENCES risk_method_version,
 assessment_type assessment_type NOT NULL, intended_basis text,
 precondition_snapshot jsonb NOT NULL, horizon_start timestamptz, horizon_end timestamptz,
 plausibility text NOT NULL CHECK(plausibility IN ('LOW','MEDIUM','HIGH','UNKNOWN')),
 plausibility_reason nonempty_text NOT NULL, confidence jsonb NOT NULL,
 input_valid boolean NOT NULL, raw_input jsonb NOT NULL,
 status assessment_status NOT NULL, score_determined boolean NOT NULL,
 assessment_mode assessment_mode NOT NULL, review_outcome review_outcome NOT NULL DEFAULT 'NONE',
 e_lo score_1_5, e_hi score_1_5, f_lo score_1_5, f_hi score_1_5,
 g_lo score_1_5, g_hi score_1_5, i_total_lo score_1_5, i_total_hi score_1_5,
 e score_1_5, f score_1_5, g score_1_5, i_total score_1_5,
 p_lo numeric(4,2), p_hi numeric(4,2), l_lo numeric(5,2), l_hi numeric(5,2),
 r25_lo integer, r25_hi integer, r25 integer,
 score numeric(5,2) GENERATED ALWAYS AS (r25::numeric/25) STORED,
 score_lo numeric(5,2) GENERATED ALWAYS AS (r25_lo::numeric/25) STORED,
 score_hi numeric(5,2) GENERATED ALWAYS AS (r25_hi::numeric/25) STORED,
 raw_level risk_level, risk_level risk_level,
 raw_level_lo risk_level, raw_level_hi risk_level, level_lo risk_level, level_hi risk_level,
 impact_gate_reason text, impact_gate_possibilities jsonb NOT NULL DEFAULT '[]',
 path_inventory_confirmed boolean NOT NULL, path_inventory_reason nonempty_text NOT NULL,
 missing_factors text[] NOT NULL DEFAULT '{}', missing_paths text[] NOT NULL DEFAULT '{}',
 determination_reasons text[] NOT NULL DEFAULT '{}', review_reasons text[] NOT NULL DEFAULT '{}',
 supersedes_id uuid REFERENCES risk_evaluation,
 CHECK(horizon_end IS NULL OR (horizon_start IS NOT NULL AND horizon_end>horizon_start)),
 CHECK(assessment_type<>'ILLUSTRATIVE' OR intended_basis IS NOT NULL),
 CHECK(supersedes_id IS NULL OR supersedes_id<>id),
 CHECK((NOT input_valid AND status='NEEDS_REVIEW' AND NOT score_determined
  AND num_nonnulls(e_lo,e_hi,f_lo,f_hi,g_lo,g_hi,i_total_lo,i_total_hi,e,f,g,i_total,p_lo,p_hi,l_lo,l_hi,r25_lo,r25_hi,r25,raw_level,risk_level,raw_level_lo,raw_level_hi,level_lo,level_hi,impact_gate_reason)=0)
 OR (input_valid AND num_nonnulls(e_lo,e_hi,f_lo,f_hi,g_lo,g_hi,i_total_lo,i_total_hi,p_lo,p_hi,l_lo,l_hi,r25_lo,r25_hi,raw_level_lo,raw_level_hi,level_lo,level_hi)=18
  AND e_lo<=e_hi AND f_lo<=f_hi AND g_lo<=g_hi AND i_total_lo<=i_total_hi
  AND r25_lo BETWEEN 25 AND 625 AND r25_hi BETWEEN r25_lo AND 625
  AND p_lo=(2*e_lo+3*f_lo)::numeric/5 AND p_hi=(2*e_hi+3*f_hi)::numeric/5
  AND l_lo=1+(p_lo-1)*g_lo/5 AND l_hi=1+(p_hi-1)*g_hi/5
  AND r25_lo=i_total_lo*(25+(2*e_lo+3*f_lo-5)*g_lo)
  AND r25_hi=i_total_hi*(25+(2*e_hi+3*f_hi-5)*g_hi)
  AND score_determined=(r25_lo=r25_hi)
  AND ((score_determined AND r25 IS NOT NULL AND r25=r25_lo AND raw_level IS NOT NULL AND risk_level IS NOT NULL AND impact_gate_reason IS NOT NULL)
   OR (NOT score_determined AND r25 IS NULL AND raw_level IS NULL AND risk_level IS NULL AND impact_gate_reason IS NULL)))),
 CHECK(NOT input_valid OR ((e IS NOT NULL AND e_lo=e_hi AND e=e_lo) OR (e IS NULL AND e_lo<e_hi))),
 CHECK(NOT input_valid OR ((f IS NOT NULL AND f_lo=f_hi AND f=f_lo) OR (f IS NULL AND f_lo<f_hi))),
 CHECK(NOT input_valid OR ((g IS NOT NULL AND g_lo=g_hi AND g=g_lo) OR (g IS NULL AND g_lo<g_hi))),
 CHECK(NOT input_valid OR ((i_total IS NOT NULL AND i_total_lo=i_total_hi AND i_total=i_total_lo) OR (i_total IS NULL AND i_total_lo<i_total_hi))),
 CHECK(status<>'EVALUATED' OR (input_valid AND score_determined AND path_inventory_confirmed
  AND cardinality(missing_factors)=0 AND cardinality(missing_paths)=0 AND cardinality(review_reasons)=0)),
 CHECK(review_outcome<>'DISPUTED' OR status='NEEDS_REVIEW')
);
CREATE TABLE risk_factor (
 id uuid PRIMARY KEY, risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 factor_code text NOT NULL CHECK(factor_code IN ('E','F')),
 value score_1_5, lower_bound score_1_5 NOT NULL, upper_bound score_1_5 NOT NULL,
 source_kind text NOT NULL CHECK(source_kind IN ('EVIDENCE','OWNER_DECLARATION','TEMPLATE','ILLUSTRATIVE','UNKNOWN')),
 confirmation confirmation_state NOT NULL, bounds_confirmation confirmation_state NOT NULL,
 confirmed_by uuid REFERENCES app_user, confirmed_at timestamptz,
 bounds_confirmed_by uuid REFERENCES app_user, bounds_confirmed_at timestamptz,
 disputed boolean NOT NULL, rationale nonempty_text NOT NULL, source jsonb NOT NULL,
 UNIQUE(risk_evaluation_id,factor_code), CHECK(lower_bound<=upper_bound),
 CHECK(value IS NULL OR (value=lower_bound AND value=upper_bound AND confirmation='CONFIRMED' AND NOT disputed)),
 CHECK(value IS NOT NULL OR (lower_bound=1 AND upper_bound=5) OR bounds_confirmation='CONFIRMED'),
 CHECK(confirmation<>'CONFIRMED' OR (confirmed_by IS NOT NULL AND confirmed_at IS NOT NULL)),
 CHECK(bounds_confirmation<>'CONFIRMED' OR (bounds_confirmed_by IS NOT NULL AND bounds_confirmed_at IS NOT NULL))
);
CREATE TABLE excluded_control (
 id uuid PRIMARY KEY, risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 control_version_id uuid NOT NULL REFERENCES control_definition_version,
 exclusion_kind text NOT NULL CHECK(exclusion_kind IN ('F_COUNTERFACTUAL','INHERENT')),
 rationale nonempty_text NOT NULL, UNIQUE(risk_evaluation_id,control_version_id,exclusion_kind)
);
CREATE TABLE risk_path (
 id uuid PRIMARY KEY, risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 path_code nonempty_text NOT NULL, description nonempty_text NOT NULL,
 coverage text NOT NULL CHECK(coverage IN ('VERIFIED_COVERED','VERIFIED_UNCOVERED','UNKNOWN')),
 strength text NOT NULL CHECK(strength IN ('PREVENTS','STRONG','SIGNIFICANT','MINOR','NONE','UNKNOWN')),
 applicable boolean NOT NULL, applicability_confirmation confirmation_state NOT NULL,
 applicability_confirmed_by uuid REFERENCES app_user, applicability_reason nonempty_text NOT NULL,
 g score_1_5, g_lo score_1_5, g_hi score_1_5,
 confirmation confirmation_state NOT NULL, bounds_confirmation confirmation_state NOT NULL,
 confirmed_by uuid REFERENCES app_user, confirmed_at timestamptz,
 bounds_confirmed_by uuid REFERENCES app_user, bounds_confirmed_at timestamptz,
 disputed boolean NOT NULL, rationale nonempty_text NOT NULL, source jsonb NOT NULL,
 UNIQUE(risk_evaluation_id,path_code),
 CHECK((applicable AND g_lo IS NOT NULL AND g_hi IS NOT NULL AND g_lo<=g_hi)
  OR (NOT applicable AND g IS NULL AND g_lo IS NULL AND g_hi IS NULL
   AND applicability_confirmation='CONFIRMED' AND applicability_confirmed_by IS NOT NULL)),
 CHECK(g IS NULL OR (g=g_lo AND g=g_hi AND confirmation='CONFIRMED' AND NOT disputed)),
 CHECK(NOT applicable OR g IS NOT NULL OR (g_lo=1 AND g_hi=5) OR bounds_confirmation='CONFIRMED'),
 CHECK(coverage<>'VERIFIED_UNCOVERED' OR (g IS NOT NULL AND g=5 AND strength='NONE')),
 CHECK(confirmation<>'CONFIRMED' OR (confirmed_by IS NOT NULL AND confirmed_at IS NOT NULL)),
 CHECK(bounds_confirmation<>'CONFIRMED' OR (bounds_confirmed_by IS NOT NULL AND bounds_confirmed_at IS NOT NULL))
);
CREATE TABLE risk_path_control (
 id uuid PRIMARY KEY, risk_path_id uuid NOT NULL REFERENCES risk_path,
 control_assessment_id uuid NOT NULL REFERENCES control_assessment,
 criterion_result_id uuid REFERENCES control_assessment_criterion,
 coverage_reason nonempty_text NOT NULL, strength_reason nonempty_text NOT NULL,
 UNIQUE NULLS NOT DISTINCT(risk_path_id,control_assessment_id,criterion_result_id)
);
CREATE TABLE impact_factor (
 id uuid PRIMARY KEY, risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 dimension impact_dimension NOT NULL, value score_1_5,
 lower_bound score_1_5 NOT NULL, upper_bound score_1_5 NOT NULL,
 confirmation confirmation_state NOT NULL, bounds_confirmation confirmation_state NOT NULL,
 confirmed_by uuid REFERENCES app_user, confirmed_at timestamptz,
 bounds_confirmed_by uuid REFERENCES app_user, bounds_confirmed_at timestamptz,
 disputed boolean NOT NULL, rationale nonempty_text NOT NULL, source jsonb NOT NULL,
 UNIQUE(risk_evaluation_id,dimension), CHECK(lower_bound<=upper_bound),
 CHECK(value IS NULL OR (value=lower_bound AND value=upper_bound AND confirmation='CONFIRMED' AND NOT disputed)),
 CHECK(value IS NOT NULL OR (lower_bound=1 AND upper_bound=5) OR bounds_confirmation='CONFIRMED'),
 CHECK(confirmation<>'CONFIRMED' OR (confirmed_by IS NOT NULL AND confirmed_at IS NOT NULL)),
 CHECK(bounds_confirmation<>'CONFIRMED' OR (bounds_confirmed_by IS NOT NULL AND bounds_confirmed_at IS NOT NULL))
);
CREATE TABLE factor_evidence (
 id uuid PRIMARY KEY, risk_factor_id uuid REFERENCES risk_factor,
 risk_path_id uuid REFERENCES risk_path, impact_factor_id uuid REFERENCES impact_factor,
 evidence_revision_id uuid NOT NULL REFERENCES evidence_revision,
 verification_decision_id uuid NOT NULL,
 CHECK(num_nonnulls(risk_factor_id,risk_path_id,impact_factor_id)=1),
 FOREIGN KEY(verification_decision_id,evidence_revision_id) REFERENCES verification_decision(id,evidence_revision_id)
);
CREATE TABLE risk_validation_issue (
 id uuid PRIMARY KEY, risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 issue_code nonempty_text NOT NULL, field_path nonempty_text NOT NULL,
 message nonempty_text NOT NULL, source jsonb NOT NULL
);

CREATE TABLE gap (
 id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE,
 assessment_id uuid NOT NULL REFERENCES assessment, scope_id uuid NOT NULL REFERENCES scope,
 gap_kind text NOT NULL CHECK(gap_kind IN ('CONTROL_GAP','EVIDENCE_GAP')),
 source_control_assessment_id uuid REFERENCES control_assessment,
 source_risk_evaluation_id uuid REFERENCES risk_evaluation,
 criterion_version_id uuid REFERENCES control_criterion_version,
 owner_id uuid NOT NULL REFERENCES app_user, description nonempty_text NOT NULL,
 state text NOT NULL CHECK(state IN ('OPEN','IN_PROGRESS','CLOSED')),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 CHECK(num_nonnulls(source_control_assessment_id,source_risk_evaluation_id)>=1)
);
CREATE TABLE treatment_plan (
 id uuid PRIMARY KEY, code nonempty_text NOT NULL UNIQUE,
 assessment_id uuid NOT NULL REFERENCES assessment, owner_id uuid NOT NULL REFERENCES app_user,
 scope_id uuid NOT NULL REFERENCES scope, objective nonempty_text NOT NULL,
 response text NOT NULL CHECK(response IN ('MITIGATE','AVOID','TRANSFER','ACCEPT')),
 state text NOT NULL CHECK(state IN ('DRAFT','ACTIVE','COMPLETED','CANCELLED')),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0)
);
CREATE TABLE treatment_task (
 id uuid PRIMARY KEY, plan_id uuid NOT NULL REFERENCES treatment_plan,
 code nonempty_text NOT NULL UNIQUE, owner_id uuid NOT NULL REFERENCES app_user,
 description nonempty_text NOT NULL, due_at timestamptz,
 state text NOT NULL CHECK(state IN ('OPEN','IN_PROGRESS','READY_FOR_RETEST','CLOSED','CANCELLED')),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0)
);
CREATE TABLE task_gap (
 id uuid PRIMARY KEY, task_id uuid NOT NULL REFERENCES treatment_task,
 gap_id uuid NOT NULL REFERENCES gap, UNIQUE(task_id,gap_id)
);
CREATE TABLE retest_request (
 id uuid PRIMARY KEY, task_id uuid REFERENCES treatment_task,
 assessment_id uuid NOT NULL REFERENCES assessment, scope_id uuid NOT NULL REFERENCES scope,
 baseline_control_assessment_id uuid REFERENCES control_assessment,
 baseline_risk_evaluation_id uuid REFERENCES risk_evaluation,
 requested_by uuid NOT NULL REFERENCES app_user, requested_at timestamptz NOT NULL,
 state text NOT NULL CHECK(state IN ('REQUESTED','IN_PROGRESS','COMPLETED','CANCELLED')),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0)
);
CREATE TABLE retest_result (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 request_id uuid NOT NULL REFERENCES retest_request,
 control_assessment_id uuid NOT NULL REFERENCES control_assessment,
 risk_evaluation_id uuid REFERENCES risk_evaluation,
 conclusion nonempty_text NOT NULL, reason nonempty_text NOT NULL
);
CREATE TABLE assessment_comparison (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 before_risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 after_risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 progress_rule_version_id uuid NOT NULL REFERENCES risk_method_version,
 treatment_plan_id uuid REFERENCES treatment_plan,
 comparable boolean NOT NULL, comparability_checks jsonb NOT NULL,
 comparability_reasons text[] NOT NULL,
 r_progress text NOT NULL CHECK(r_progress IN ('DOWN','UP','SAME','NOT_COMPARABLE','UNDETERMINED')),
 impact_progress text NOT NULL CHECK(impact_progress IN ('NOT_COMPARABLE','INCOMPLETE','MIXED','IMPROVED','WORSENED','UNCHANGED')),
 verified_worsening boolean, assessment_mode assessment_mode NOT NULL,
 treatment_attribution text NOT NULL CHECK(treatment_attribution IN ('SUPPORTED','REVIEW_REQUIRED')),
 attribution_reason nonempty_text NOT NULL,
 attribution_confirmed_by uuid REFERENCES app_user, attribution_confirmed_at timestamptz,
 comparison_review_status assessment_status NOT NULL,
 review_outcome review_outcome NOT NULL DEFAULT 'NONE',
 CHECK(before_risk_evaluation_id<>after_risk_evaluation_id),
 CHECK(comparable OR (r_progress='NOT_COMPARABLE' AND impact_progress='NOT_COMPARABLE' AND verified_worsening IS NULL)),
 CHECK(comparable OR cardinality(comparability_reasons)>0),
 CHECK(impact_progress NOT IN ('NOT_COMPARABLE','INCOMPLETE') OR comparison_review_status='NEEDS_REVIEW'),
 CHECK(treatment_attribution<>'SUPPORTED' OR (assessment_mode='INDEPENDENT_REVIEWED' AND review_outcome='CONFIRMED' AND attribution_confirmed_by IS NOT NULL AND attribution_confirmed_at IS NOT NULL)),
 CHECK(review_outcome<>'DISPUTED' OR comparison_review_status='NEEDS_REVIEW')
);
CREATE TABLE comparison_impact_dimension (
 id uuid PRIMARY KEY, comparison_id uuid NOT NULL REFERENCES assessment_comparison,
 dimension impact_dimension NOT NULL,
 before_factor_id uuid NOT NULL REFERENCES impact_factor,
 after_factor_id uuid NOT NULL REFERENCES impact_factor,
 direction direction NOT NULL, rationale nonempty_text NOT NULL,
 UNIQUE(comparison_id,dimension)
);
CREATE TABLE comparison_impact_summary (
 id uuid PRIMARY KEY, comparison_id uuid NOT NULL REFERENCES assessment_comparison,
 side text NOT NULL CHECK(side IN ('BEFORE','AFTER')),
 i_total score_1_5, i_total_lo score_1_5, i_total_hi score_1_5,
 max_dimension_count smallint CHECK(max_dimension_count BETWEEN 1 AND 4),
 max_dimension_count_lo smallint CHECK(max_dimension_count_lo BETWEEN 1 AND 4),
 max_dimension_count_hi smallint CHECK(max_dimension_count_hi BETWEEN 1 AND 4),
 UNIQUE(comparison_id,side),
 CHECK((num_nonnulls(i_total_lo,i_total_hi,max_dimension_count_lo,max_dimension_count_hi)=0 AND i_total IS NULL AND max_dimension_count IS NULL)
  OR (num_nonnulls(i_total_lo,i_total_hi,max_dimension_count_lo,max_dimension_count_hi)=4
   AND i_total_lo<=i_total_hi AND max_dimension_count_lo<=max_dimension_count_hi)),
 CHECK((i_total IS NOT NULL AND i_total_lo=i_total_hi AND i_total=i_total_lo)
  OR (i_total IS NULL AND (i_total_lo IS NULL OR i_total_lo<i_total_hi))),
 CHECK((max_dimension_count IS NOT NULL AND max_dimension_count_lo=max_dimension_count_hi AND max_dimension_count=max_dimension_count_lo)
  OR (max_dimension_count IS NULL AND (max_dimension_count_lo IS NULL OR max_dimension_count_lo<max_dimension_count_hi)))
);
CREATE TABLE comparison_gap (
 id uuid PRIMARY KEY, comparison_id uuid NOT NULL REFERENCES assessment_comparison,
 gap_id uuid NOT NULL REFERENCES gap,
 progress text NOT NULL CHECK(progress IN ('CLOSED','STILL_OPEN','NEW')),
 state_before text, state_after text NOT NULL, reason nonempty_text NOT NULL,
 UNIQUE(comparison_id,gap_id)
);

-- Pending workflow is mutable; decisions and their resulting snapshots are not.
ALTER TABLE snapshot_registry ADD CONSTRAINT snapshot_registry_id_kind UNIQUE(id,snapshot_kind);
CREATE TABLE review_request (
 id uuid PRIMARY KEY, target_snapshot_id uuid NOT NULL,
 target_kind text NOT NULL CHECK(target_kind IN ('CONTROL_ASSESSMENT','RISK_EVALUATION','COMPARISON')),
 requested_by uuid NOT NULL REFERENCES app_user,
 reviewer_assignment_id uuid NOT NULL REFERENCES role_assignment,
 requested_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
 lifecycle text NOT NULL CHECK(lifecycle IN ('PENDING','COMPLETED','CANCELLED','EXPIRED')),
 reason nonempty_text NOT NULL, version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 FOREIGN KEY(target_snapshot_id,target_kind) REFERENCES snapshot_registry(id,snapshot_kind),
 CHECK(expires_at>requested_at)
);
CREATE TABLE review_decision (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 request_id uuid NOT NULL UNIQUE REFERENCES review_request,
 original_snapshot_id uuid NOT NULL REFERENCES snapshot_registry,
 resulting_snapshot_id uuid NOT NULL REFERENCES snapshot_registry,
 outcome text NOT NULL CHECK(outcome IN ('CONFIRMED','DISPUTED')),
 confirmed_treatment_attribution boolean,
 original_opinion jsonb NOT NULL, reviewer_opinion jsonb NOT NULL,
 reason nonempty_text NOT NULL, evidence_basis jsonb NOT NULL,
 CHECK(original_snapshot_id<>resulting_snapshot_id)
);
CREATE TABLE adjudication_decision (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 review_decision_id uuid NOT NULL REFERENCES review_decision,
 original_snapshot_id uuid NOT NULL REFERENCES snapshot_registry,
 disputed_snapshot_id uuid NOT NULL REFERENCES snapshot_registry,
 replacement_snapshot_id uuid NOT NULL REFERENCES snapshot_registry,
 resulting_snapshot_id uuid NOT NULL REFERENCES snapshot_registry,
 outcome review_outcome NOT NULL DEFAULT 'ADJUSTED_NEW_SNAPSHOT' CHECK(outcome='ADJUSTED_NEW_SNAPSHOT'),
 reason nonempty_text NOT NULL,
 CHECK(original_snapshot_id<>disputed_snapshot_id),
 CHECK(resulting_snapshot_id NOT IN (original_snapshot_id,disputed_snapshot_id,replacement_snapshot_id))
);
CREATE TABLE priority_proposal (
 id uuid PRIMARY KEY, assessment_id uuid NOT NULL REFERENCES assessment,
 proposed_by uuid NOT NULL REFERENCES app_user, proposed_at timestamptz NOT NULL,
 proposal jsonb NOT NULL, reason nonempty_text NOT NULL,
 created_txid bigint NOT NULL DEFAULT txid_current()
);
CREATE TABLE priority_proposal_member (
 id uuid PRIMARY KEY, proposal_id uuid NOT NULL REFERENCES priority_proposal,
 risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 proposed_rank integer CHECK(proposed_rank>0), UNIQUE(proposal_id,risk_evaluation_id)
);
CREATE TABLE priority_decision (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 proposal_id uuid REFERENCES priority_proposal,
 previous_decision_id uuid REFERENCES priority_decision,
 priority_decision text NOT NULL CHECK(priority_decision IN ('NOT_RANKED','RANKED')),
 decision_type text NOT NULL CHECK(decision_type IN ('REVIEWER_DETERMINATION','RISK_OWNER_APPROVAL')),
 user_confirmation text NOT NULL CHECK(user_confirmation IN ('NOT_RECORDED','CONFIRMED','CHANGED')),
 reason nonempty_text NOT NULL,
 CHECK(priority_decision<>'RANKED' OR (decision_type='RISK_OWNER_APPROVAL' AND user_confirmation<>'NOT_RECORDED')),
 CHECK(previous_decision_id IS NULL OR previous_decision_id<>id)
);
CREATE TABLE priority_decision_member (
 id uuid PRIMARY KEY, decision_id uuid NOT NULL REFERENCES priority_decision,
 risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 approved_rank integer CHECK(approved_rank>0), rationale nonempty_text NOT NULL,
 UNIQUE(decision_id,risk_evaluation_id)
);
CREATE TABLE risk_acceptance (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 previous_acceptance_id uuid REFERENCES risk_acceptance,
 valid_from timestamptz NOT NULL, valid_until timestamptz NOT NULL,
 conditions nonempty_text NOT NULL, residual_limitations nonempty_text NOT NULL,
 reason nonempty_text NOT NULL, approval_state text NOT NULL CHECK(approval_state IN ('ACCEPTED','REVOKED')),
 CHECK(valid_until>valid_from), CHECK(previous_acceptance_id IS NULL OR previous_acceptance_id<>id)
);
CREATE TABLE closure_decision (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 gap_id uuid REFERENCES gap, task_id uuid REFERENCES treatment_task,
 control_assessment_id uuid NOT NULL REFERENCES control_assessment,
 retest_result_id uuid REFERENCES retest_result,
 outcome text NOT NULL CHECK(outcome IN ('APPROVED','REJECTED')),
 criteria_met boolean NOT NULL, reason nonempty_text NOT NULL,
 outstanding_limitations jsonb NOT NULL,
 CHECK(num_nonnulls(gap_id,task_id)=1), CHECK(outcome<>'APPROVED' OR criteria_met)
);
CREATE TABLE closure_evidence (
 id uuid PRIMARY KEY, closure_decision_id uuid NOT NULL REFERENCES closure_decision,
 evidence_revision_id uuid NOT NULL REFERENCES evidence_revision,
 verification_decision_id uuid NOT NULL,
 FOREIGN KEY(verification_decision_id,evidence_revision_id) REFERENCES verification_decision(id,evidence_revision_id),
 UNIQUE(closure_decision_id,evidence_revision_id,verification_decision_id)
);
ALTER TABLE gap ADD COLUMN closure_decision_id uuid REFERENCES closure_decision;
ALTER TABLE gap ADD CHECK(state<>'CLOSED' OR closure_decision_id IS NOT NULL);
ALTER TABLE treatment_task ADD COLUMN closure_decision_id uuid REFERENCES closure_decision;
ALTER TABLE treatment_task ADD CHECK(state<>'CLOSED' OR closure_decision_id IS NOT NULL);
ALTER TABLE comparison_gap ADD COLUMN closure_decision_id uuid REFERENCES closure_decision;
ALTER TABLE comparison_gap ADD CHECK(progress<>'CLOSED' OR closure_decision_id IS NOT NULL);

CREATE TABLE report_snapshot (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 assessment_id uuid NOT NULL REFERENCES assessment,
 as_of timestamptz NOT NULL, schema_version nonempty_text NOT NULL,
 title nonempty_text NOT NULL, limitations text[] NOT NULL,
 frozen_context jsonb NOT NULL,
 CHECK(jsonb_typeof(frozen_context)='object')
);
CREATE TABLE report_snapshot_member (
 id uuid PRIMARY KEY, report_snapshot_id uuid NOT NULL REFERENCES report_snapshot,
 referenced_snapshot_id uuid NOT NULL REFERENCES snapshot_registry,
 section_code nonempty_text NOT NULL,
 UNIQUE(report_snapshot_id,referenced_snapshot_id,section_code),
 CHECK(report_snapshot_id<>referenced_snapshot_id)
);
CREATE TABLE report_gap_snapshot (
 id uuid PRIMARY KEY, report_snapshot_id uuid NOT NULL REFERENCES report_snapshot,
 gap_id uuid NOT NULL REFERENCES gap, source_version bigint NOT NULL CHECK(source_version>0),
 gap_kind text NOT NULL CHECK(gap_kind IN ('CONTROL_GAP','EVIDENCE_GAP')),
 state text NOT NULL CHECK(state IN ('OPEN','IN_PROGRESS','CLOSED')),
 owner_id uuid NOT NULL REFERENCES app_user, description nonempty_text NOT NULL,
 closure_decision_id uuid REFERENCES closure_decision,
 UNIQUE(report_snapshot_id,gap_id), CHECK(state<>'CLOSED' OR closure_decision_id IS NOT NULL)
);
CREATE TABLE report_task_snapshot (
 id uuid PRIMARY KEY, report_snapshot_id uuid NOT NULL REFERENCES report_snapshot,
 task_id uuid NOT NULL REFERENCES treatment_task, source_version bigint NOT NULL CHECK(source_version>0),
 state text NOT NULL CHECK(state IN ('OPEN','IN_PROGRESS','READY_FOR_RETEST','CLOSED','CANCELLED')),
 owner_id uuid NOT NULL REFERENCES app_user, description nonempty_text NOT NULL, due_at timestamptz,
 closure_decision_id uuid REFERENCES closure_decision,
 UNIQUE(report_snapshot_id,task_id), CHECK(state<>'CLOSED' OR closure_decision_id IS NOT NULL)
);
CREATE TABLE audit_event (
 id uuid PRIMARY KEY, recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 actor_id uuid REFERENCES app_user, session_id uuid REFERENCES vdt_session,
 action nonempty_text NOT NULL, target_kind nonempty_text NOT NULL, target_id uuid,
 outcome text NOT NULL CHECK(outcome IN ('ALLOWED','DENIED','FAILED')),
 reason_code nonempty_text NOT NULL, correlation_id uuid NOT NULL,
 scope_id uuid REFERENCES scope, authorization_version bigint,
 gate_checked_at timestamptz, safe_metadata jsonb NOT NULL DEFAULT '{}',
 CHECK(jsonb_typeof(safe_metadata)='object')
);
CREATE TABLE storage_event (
 id uuid PRIMARY KEY, storage_id uuid NOT NULL REFERENCES evidence_storage,
 from_state storage_state, to_state storage_state NOT NULL,
 audit_event_id uuid NOT NULL REFERENCES audit_event,
 recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 reason nonempty_text NOT NULL, observed_hash sha256_hex
);
CREATE TABLE idempotency_operation (
 id uuid PRIMARY KEY, organization_id uuid NOT NULL REFERENCES organization,
 principal_id uuid NOT NULL REFERENCES app_user,
 method text NOT NULL CHECK(method IN ('POST','PATCH','PUT','DELETE')),
 canonical_path nonempty_text NOT NULL, idempotency_key uuid NOT NULL,
 request_hash sha256_hex NOT NULL, expected_version bigint,
 state text NOT NULL CHECK(state IN ('PROCESSING','SUCCEEDED','RETRYABLE_FAILED','TERMINAL_FAILED')),
 lease_until timestamptz, created_at timestamptz NOT NULL, updated_at timestamptz NOT NULL,
 result_status integer CHECK(result_status BETWEEN 100 AND 599),
 result_resource_ids uuid[] NOT NULL DEFAULT '{}', result_metadata jsonb NOT NULL DEFAULT '{}',
 version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 UNIQUE(organization_id,principal_id,method,canonical_path,idempotency_key),
 CHECK(state<>'SUCCEEDED' OR (result_status IS NOT NULL AND result_status BETWEEN 200 AND 299))
);
CREATE TABLE upload_operation (
 id uuid PRIMARY KEY, idempotency_operation_id uuid NOT NULL UNIQUE REFERENCES idempotency_operation,
 evidence_item_id uuid NOT NULL REFERENCES evidence_item, evidence_revision_id uuid UNIQUE REFERENCES evidence_revision,
 state text NOT NULL CHECK(state IN ('RECEIVING','SCANNING','STAGED','COMMITTED','FAILED','ORPHANED')),
 temporary_key text, expected_final_key text, actual_hash sha256_hex,
 actual_size_bytes bigint CHECK(actual_size_bytes>=0), expected_item_version bigint NOT NULL,
 lease_until timestamptz NOT NULL, scan_engine_version text, scan_signature_version text,
 failure_reason text, version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 CHECK(state<>'COMMITTED' OR evidence_revision_id IS NOT NULL)
);
CREATE TABLE background_job (
 id uuid PRIMARY KEY, requested_by uuid NOT NULL REFERENCES app_user,
 idempotency_operation_id uuid NOT NULL REFERENCES idempotency_operation,
 job_kind text NOT NULL CHECK(job_kind IN ('EXPORT','RECONCILE_STORAGE','BACKUP_MANIFEST')),
 scope_id uuid NOT NULL REFERENCES scope, payload_schema_version nonempty_text NOT NULL,
 payload jsonb NOT NULL, state text NOT NULL CHECK(state IN ('QUEUED','RUNNING','SUCCEEDED','FAILED','CANCELLED')),
 attempt_count integer NOT NULL DEFAULT 0 CHECK(attempt_count>=0),
 lease_until timestamptz, deadline timestamptz NOT NULL, failure_reason text,
 version bigint NOT NULL DEFAULT 1 CHECK(version>0)
);
CREATE TABLE export_artifact (
 id uuid PRIMARY KEY, job_id uuid NOT NULL UNIQUE REFERENCES background_job,
 report_snapshot_id uuid NOT NULL REFERENCES report_snapshot,
 requested_by uuid NOT NULL REFERENCES app_user, scope_id uuid NOT NULL REFERENCES scope,
 storage_key nonempty_text NOT NULL UNIQUE, content_hash sha256_hex NOT NULL,
 size_bytes bigint NOT NULL CHECK(size_bytes>=0), created_at timestamptz NOT NULL,
 expires_at timestamptz NOT NULL,
 state text NOT NULL CHECK(state IN ('AVAILABLE','EXPIRED','REMOVED','INTEGRITY_FAILED')),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0), CHECK(expires_at>created_at)
);
CREATE TABLE mutable_entity_history (
 id uuid PRIMARY KEY, entity_kind text NOT NULL, entity_id uuid NOT NULL,
 entity_version bigint NOT NULL CHECK(entity_version>0),
 schema_version nonempty_text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 effective_at timestamptz, actor_id uuid NOT NULL REFERENCES app_user,
 scope_id uuid NOT NULL REFERENCES scope, state_snapshot jsonb NOT NULL,
 content_hash sha256_hex NOT NULL,
 UNIQUE(entity_kind,entity_id,entity_version), CHECK(jsonb_typeof(state_snapshot)='object')
);

-- Typed links preserve predecessor membership and the committed head identity.
ALTER TABLE evidence_revision ADD CONSTRAINT revision_id_item UNIQUE(id,evidence_item_id);
ALTER TABLE evidence_revision ADD FOREIGN KEY(previous_revision_id,evidence_item_id) REFERENCES evidence_revision(id,evidence_item_id);
ALTER TABLE evidence_item ADD COLUMN head_revision_id uuid;
ALTER TABLE evidence_item ADD FOREIGN KEY(head_revision_id,id) REFERENCES evidence_revision(id,evidence_item_id);
ALTER TABLE verification_decision ADD FOREIGN KEY(previous_decision_id,evidence_revision_id) REFERENCES verification_decision(id,evidence_revision_id);
ALTER TABLE control_assessment_criterion ADD CONSTRAINT criterion_id_assessment UNIQUE(id,control_assessment_id);
ALTER TABLE risk_path_control ADD FOREIGN KEY(criterion_result_id,control_assessment_id) REFERENCES control_assessment_criterion(id,control_assessment_id);

-- Indexes support scoped lookups, decision selection, audit/as_of and queue leases.
CREATE INDEX role_assignment_active_idx ON role_assignment(user_id,role_id,scope_id,access_expires_at) WHERE revoked_at IS NULL;
CREATE INDEX snapshot_as_of_idx ON snapshot_registry(scope_id,created_at,id);
CREATE INDEX evidence_item_assessment_idx ON evidence_item(assessment_id,scope_id);
CREATE INDEX evidence_revision_item_idx ON evidence_revision(evidence_item_id,revision_number DESC);
CREATE INDEX verification_revision_idx ON verification_decision(evidence_revision_id);
CREATE INDEX control_assessment_context_idx ON control_assessment(assessment_id,context_snapshot_id);
CREATE INDEX risk_evaluation_context_idx ON risk_evaluation(assessment_id,context_snapshot_id);
CREATE INDEX gap_open_idx ON gap(assessment_id,gap_kind,state);
CREATE INDEX audit_actor_time_idx ON audit_event(actor_id,recorded_at);
CREATE INDEX audit_target_idx ON audit_event(target_kind,target_id,recorded_at);
CREATE INDEX mutable_history_asof_idx ON mutable_entity_history(entity_kind,entity_id,recorded_at);
CREATE INDEX job_claim_idx ON background_job(state,lease_until,deadline);
CREATE INDEX upload_lease_idx ON upload_operation(state,lease_until);


-- Final integration 2026-10-20: API resource roundtrip, immutable sealing.
ALTER TABLE app_user ADD COLUMN password_hash text NOT NULL DEFAULT '!';
ALTER TABLE app_user ADD COLUMN last_login timestamptz;
ALTER TABLE app_user ADD COLUMN email text;
-- Map this table to a custom Django AbstractBaseUser. '!' is unusable password,
-- not a default credential. Framework password validators/hashers remain mandatory.
ALTER TABLE authentication_profile_version ADD COLUMN approval_reason text;
ALTER TABLE authentication_profile_version ADD COLUMN environment jsonb NOT NULL DEFAULT '{}';
ALTER TABLE authentication_profile_version ADD COLUMN scope_owner_approval_reference jsonb;
ALTER TABLE authentication_profile_version ADD CHECK(configuration_state<>'APPROVED' OR
 (approval_reason IS NOT NULL AND length(btrim(approval_reason))>0));
ALTER TABLE snapshot_registry ADD COLUMN revision_number integer NOT NULL DEFAULT 1 CHECK(revision_number>0);
ALTER TABLE snapshot_registry ADD COLUMN lineage_id uuid NOT NULL;
ALTER TABLE snapshot_registry ADD CONSTRAINT snapshot_lineage_revision UNIQUE(lineage_id,revision_number);
-- lineage_id is a server generated identity shared only by replacements of the
-- same logical snapshot, not by unrelated kinds. Service checks predecessor chain.
CREATE TABLE assessment_scenario (
 id uuid PRIMARY KEY, assessment_id uuid NOT NULL REFERENCES assessment,
 scenario_id uuid NOT NULL REFERENCES risk_scenario, UNIQUE(assessment_id,scenario_id)
);
CREATE TABLE scenario_snapshot (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 scenario_id uuid NOT NULL REFERENCES risk_scenario, source_version bigint NOT NULL CHECK(source_version>0),
 context_snapshot_id uuid NOT NULL REFERENCES context_snapshot,
 code nonempty_text NOT NULL, name nonempty_text NOT NULL, event nonempty_text NOT NULL,
 consequences nonempty_text NOT NULL, owner_id uuid REFERENCES app_user,
 attack_metadata jsonb NOT NULL, sources jsonb NOT NULL, target_snapshot jsonb NOT NULL,
 UNIQUE(scenario_id,source_version)
);
ALTER TABLE risk_scenario ADD COLUMN context_snapshot_id uuid REFERENCES context_snapshot;
ALTER TABLE risk_scenario ADD COLUMN name text;
ALTER TABLE risk_scenario ADD CHECK(status<>'ACTIVE' OR owner_id IS NOT NULL);
ALTER TABLE risk_evaluation ADD COLUMN scenario_snapshot_id uuid NOT NULL REFERENCES scenario_snapshot;
-- assessment.scenario_id is optional primary display scenario; the junction
-- is authoritative membership. Evaluations must match that membership.
CREATE TABLE input_confirmation (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 assessment_id uuid NOT NULL REFERENCES assessment,
 target_snapshot_id uuid NOT NULL REFERENCES snapshot_registry,
 target_type text NOT NULL CHECK(target_type IN ('FACTOR_BOUND','PATH_BOUND','PATH_NOT_APPLICABLE')),
 field_path nonempty_text NOT NULL, lower_bound score_1_5, upper_bound score_1_5,
 reason nonempty_text NOT NULL,
 CHECK((target_type='PATH_NOT_APPLICABLE' AND lower_bound IS NULL AND upper_bound IS NULL)
  OR (target_type<>'PATH_NOT_APPLICABLE' AND lower_bound IS NOT NULL AND upper_bound IS NOT NULL AND lower_bound<=upper_bound))
);
CREATE TABLE input_confirmation_evidence (
 id uuid PRIMARY KEY, confirmation_id uuid NOT NULL REFERENCES input_confirmation,
 evidence_revision_id uuid NOT NULL REFERENCES evidence_revision,
 verification_decision_id uuid NOT NULL,
 FOREIGN KEY(verification_decision_id,evidence_revision_id) REFERENCES verification_decision(id,evidence_revision_id),
 UNIQUE(confirmation_id,evidence_revision_id,verification_decision_id)
);
CREATE TABLE risk_input_confirmation (
 id uuid PRIMARY KEY, risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 confirmation_id uuid NOT NULL REFERENCES input_confirmation,
 field_path nonempty_text NOT NULL, UNIQUE(risk_evaluation_id,confirmation_id,field_path)
);
CREATE TABLE impact_confirmation (
 id uuid PRIMARY KEY REFERENCES snapshot_registry,
 risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation, reason nonempty_text NOT NULL
);
CREATE TABLE impact_confirmation_dimension (
 id uuid PRIMARY KEY, confirmation_id uuid NOT NULL REFERENCES impact_confirmation,
 dimension impact_dimension NOT NULL, factor_id uuid NOT NULL REFERENCES impact_factor,
 UNIQUE(confirmation_id,dimension)
);
CREATE TABLE risk_impact_confirmation (
 id uuid PRIMARY KEY, risk_evaluation_id uuid NOT NULL REFERENCES risk_evaluation,
 confirmation_id uuid NOT NULL REFERENCES impact_confirmation,
 UNIQUE(risk_evaluation_id,confirmation_id)
);
CREATE TABLE evidence_request (
 id uuid PRIMARY KEY REFERENCES snapshot_registry, assessment_id uuid NOT NULL REFERENCES assessment,
 requested_from_user_id uuid NOT NULL REFERENCES app_user,
 description nonempty_text NOT NULL, due_at timestamptz
);
CREATE TABLE evidence_request_criterion (
 id uuid PRIMARY KEY, request_id uuid NOT NULL REFERENCES evidence_request,
 criterion_version_id uuid NOT NULL REFERENCES control_criterion_version,
 UNIQUE(request_id,criterion_version_id)
);
ALTER TABLE treatment_task ALTER COLUMN plan_id DROP NOT NULL;
ALTER TABLE treatment_task ADD COLUMN scenario_id uuid NOT NULL REFERENCES risk_scenario;
ALTER TABLE treatment_task ADD COLUMN scope_id uuid NOT NULL REFERENCES scope;
ALTER TABLE treatment_task ADD COLUMN expected_retest_evidence text[] NOT NULL;
ALTER TABLE treatment_task ADD CHECK(cardinality(expected_retest_evidence)>0);
-- Plans are optional groupings; API v0.1 supports standalone tasks.
CREATE TABLE treatment_approval (
 id uuid PRIMARY KEY REFERENCES snapshot_registry, task_id uuid NOT NULL REFERENCES treatment_task,
 task_version bigint NOT NULL CHECK(task_version>0),
 decision text NOT NULL CHECK(decision IN ('APPROVED','REJECTED')), reason nonempty_text NOT NULL
);
ALTER TABLE review_request ADD COLUMN due_at timestamptz;
-- due_at is a requested deadline. expires_at is server bounded by assignment.
-- No assignment expiry => explicit bounded review lifetime required, never null.
ALTER TABLE retest_request ADD COLUMN context_snapshot_id uuid NOT NULL REFERENCES context_snapshot;
ALTER TABLE retest_request ADD COLUMN reason nonempty_text NOT NULL;
-- Existing singular baseline columns remain optional primary display references;
-- membership is held in the typed children below.
CREATE TABLE retest_baseline_control (
 id uuid PRIMARY KEY, request_id uuid NOT NULL REFERENCES retest_request,
 control_assessment_id uuid NOT NULL REFERENCES control_assessment,
 UNIQUE(request_id,control_assessment_id)
);
CREATE TABLE retest_task (
 id uuid PRIMARY KEY, request_id uuid NOT NULL REFERENCES retest_request,
 task_id uuid NOT NULL REFERENCES treatment_task, UNIQUE(request_id,task_id)
);
CREATE TABLE retest_evidence (
 id uuid PRIMARY KEY, request_id uuid NOT NULL REFERENCES retest_request,
 evidence_revision_id uuid NOT NULL REFERENCES evidence_revision, UNIQUE(request_id,evidence_revision_id)
);
ALTER TABLE retest_result ALTER COLUMN control_assessment_id DROP NOT NULL;
CREATE TABLE retest_result_control (
 id uuid PRIMARY KEY, result_id uuid NOT NULL REFERENCES retest_result,
 control_assessment_id uuid NOT NULL REFERENCES control_assessment, UNIQUE(result_id,control_assessment_id)
);
-- API ASSESSMENTS_RECORDED maps losslessly to DB retest_request.COMPLETED.
ALTER TABLE adjudication_decision ALTER COLUMN review_decision_id DROP NOT NULL;
ALTER TABLE adjudication_decision ADD COLUMN resolved_fields jsonb NOT NULL;
CREATE TABLE adjudication_review (
 id uuid PRIMARY KEY, adjudication_id uuid NOT NULL REFERENCES adjudication_decision,
 review_decision_id uuid NOT NULL REFERENCES review_decision, UNIQUE(adjudication_id,review_decision_id)
);
ALTER TABLE closure_decision ALTER COLUMN control_assessment_id DROP NOT NULL;
ALTER TABLE closure_decision ADD COLUMN target_version_before bigint NOT NULL CHECK(target_version_before>0);
ALTER TABLE closure_decision ADD COLUMN target_version_after bigint NOT NULL CHECK(target_version_after>0);
ALTER TABLE closure_decision ADD CHECK(
 (outcome='APPROVED' AND target_version_after=target_version_before+1)
 OR (outcome='REJECTED' AND target_version_after=target_version_before));
CREATE TABLE closure_criterion (
 id uuid PRIMARY KEY, closure_decision_id uuid NOT NULL REFERENCES closure_decision,
 criterion_version_id uuid NOT NULL REFERENCES control_criterion_version,
 control_assessment_id uuid NOT NULL REFERENCES control_assessment,
 satisfied boolean NOT NULL, reason nonempty_text NOT NULL,
 UNIQUE(closure_decision_id,criterion_version_id,control_assessment_id)
);
CREATE TABLE closure_criterion_evidence (
 id uuid PRIMARY KEY, closure_criterion_id uuid NOT NULL REFERENCES closure_criterion,
 evidence_revision_id uuid NOT NULL REFERENCES evidence_revision, verification_decision_id uuid NOT NULL,
 FOREIGN KEY(verification_decision_id,evidence_revision_id) REFERENCES verification_decision(id,evidence_revision_id),
 UNIQUE(closure_criterion_id,evidence_revision_id,verification_decision_id)
);
ALTER TABLE background_job ADD COLUMN fencing_token bigint NOT NULL DEFAULT 1 CHECK(fencing_token>0);
ALTER TABLE background_job ADD COLUMN requesting_session_id uuid REFERENCES vdt_session;
ALTER TABLE snapshot_registry ADD CONSTRAINT valid_snapshot_kind CHECK(snapshot_kind IN (
 'CONTEXT','SCENARIO','AUTHENTICATION_PROFILE','EVIDENCE_REVISION','VERIFICATION_DECISION',
 'EVIDENCE_LINK','TEST_EXECUTION','CONTROL_ASSESSMENT','RISK_EVALUATION','RETEST_RESULT',
 'COMPARISON','REVIEW_DECISION','ADJUDICATION_DECISION','PRIORITY_DECISION',
 'RISK_ACCEPTANCE','CLOSURE_DECISION','REPORT','INPUT_CONFIRMATION','IMPACT_CONFIRMATION',
 'EVIDENCE_REQUEST','TREATMENT_APPROVAL'));

CREATE FUNCTION reject_history_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 RAISE EXCEPTION 'immutable history: % %', TG_TABLE_NAME,TG_OP USING ERRCODE='55000';
END $$;
CREATE FUNCTION stamp_transaction() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 NEW.created_txid := txid_current();
 IF TG_TABLE_NAME='snapshot_registry' THEN NEW.created_at := clock_timestamp(); END IF;
 RETURN NEW;
END $$;
CREATE FUNCTION require_open_parent() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE parent_id uuid; parent_tx bigint;
BEGIN
 parent_id := (to_jsonb(NEW)->>TG_ARGV[0])::uuid;
 IF parent_id IS NULL THEN RETURN NEW; END IF;
 EXECUTE TG_ARGV[1] INTO parent_tx USING parent_id;
 IF parent_tx IS DISTINCT FROM txid_current() THEN
  RAISE EXCEPTION 'sealed or missing parent on %',TG_TABLE_NAME USING ERRCODE='55000';
 END IF;
 RETURN NEW;
END $$;
CREATE FUNCTION require_snapshot_kind() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE row_kind text; row_tx bigint;
BEGIN
 SELECT snapshot_kind,created_txid INTO row_kind,row_tx FROM vdt.snapshot_registry WHERE id=NEW.id;
 IF row_kind IS DISTINCT FROM TG_ARGV[0] OR row_tx IS DISTINCT FROM txid_current() THEN
  RAISE EXCEPTION 'snapshot kind/transaction mismatch on %',TG_TABLE_NAME USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
-- Deferred validation ensures no registry row is committed without its payload.
CREATE FUNCTION require_snapshot_payload() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE tbl text; found_id uuid;
BEGIN
 tbl := CASE NEW.snapshot_kind
 WHEN 'CONTEXT' THEN 'context_snapshot' WHEN 'SCENARIO' THEN 'scenario_snapshot'
 WHEN 'AUTHENTICATION_PROFILE' THEN 'authentication_profile_version'
 WHEN 'EVIDENCE_REVISION' THEN 'evidence_revision' WHEN 'VERIFICATION_DECISION' THEN 'verification_decision'
 WHEN 'EVIDENCE_LINK' THEN 'evidence_link' WHEN 'TEST_EXECUTION' THEN 'test_execution'
 WHEN 'CONTROL_ASSESSMENT' THEN 'control_assessment' WHEN 'RISK_EVALUATION' THEN 'risk_evaluation'
 WHEN 'RETEST_RESULT' THEN 'retest_result' WHEN 'COMPARISON' THEN 'assessment_comparison'
 WHEN 'REVIEW_DECISION' THEN 'review_decision' WHEN 'ADJUDICATION_DECISION' THEN 'adjudication_decision'
 WHEN 'PRIORITY_DECISION' THEN 'priority_decision' WHEN 'RISK_ACCEPTANCE' THEN 'risk_acceptance'
 WHEN 'CLOSURE_DECISION' THEN 'closure_decision' WHEN 'REPORT' THEN 'report_snapshot'
 WHEN 'INPUT_CONFIRMATION' THEN 'input_confirmation' WHEN 'IMPACT_CONFIRMATION' THEN 'impact_confirmation'
 WHEN 'EVIDENCE_REQUEST' THEN 'evidence_request' WHEN 'TREATMENT_APPROVAL' THEN 'treatment_approval' END;
 IF tbl IS NULL THEN RAISE EXCEPTION 'unknown snapshot kind' USING ERRCODE='23514'; END IF;
 EXECUTE format('SELECT id FROM vdt.%I WHERE id=$1',tbl) INTO found_id USING NEW.id;
 IF found_id IS NULL THEN RAISE EXCEPTION 'snapshot payload missing' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER snapshot_has_payload AFTER INSERT ON snapshot_registry
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_snapshot_payload();
CREATE FUNCTION check_version_increment() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.version <> OLD.version+1 THEN
  RAISE EXCEPTION 'mutable version must advance exactly once' USING ERRCODE='40001';
 END IF;
 RETURN NEW;
END $$;
CREATE FUNCTION check_storage_transition() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF OLD.storage_state<>NEW.storage_state AND NOT (
  (OLD.storage_state='STAGED' AND NEW.storage_state IN ('COMMITTED','ORPHANED'))
  OR (OLD.storage_state='COMMITTED' AND NEW.storage_state='INTEGRITY_FAILED')
  OR (OLD.storage_state='INTEGRITY_FAILED' AND NEW.storage_state='COMMITTED')
 ) THEN RAISE EXCEPTION 'invalid storage transition' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER storage_transition BEFORE UPDATE ON evidence_storage FOR EACH ROW EXECUTE FUNCTION check_storage_transition();
-- Services acquire this lock BEFORE user/session/assignment/entity row locks,
-- including all grant/revoke/session changes. Holding it for streaming is forbidden.
CREATE FUNCTION acquire_authorization_guard(org uuid) RETURNS bigint LANGUAGE plpgsql AS $$
DECLARE current_version bigint;
BEGIN
 SELECT version INTO current_version FROM vdt.authorization_guard
 WHERE organization_id=org FOR UPDATE;
 IF current_version IS NULL THEN RAISE EXCEPTION 'authorization guard not provisioned'; END IF;
 RETURN current_version;
END $$;

CREATE TRIGGER immutable_adjudication_decision BEFORE UPDATE OR DELETE ON adjudication_decision FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_adjudication_review BEFORE UPDATE OR DELETE ON adjudication_review FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_assessment_comparison BEFORE UPDATE OR DELETE ON assessment_comparison FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_audit_event BEFORE UPDATE OR DELETE ON audit_event FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_authentication_profile_version BEFORE UPDATE OR DELETE ON authentication_profile_version FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_closure_criterion BEFORE UPDATE OR DELETE ON closure_criterion FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_closure_criterion_evidence BEFORE UPDATE OR DELETE ON closure_criterion_evidence FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_closure_decision BEFORE UPDATE OR DELETE ON closure_decision FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_closure_evidence BEFORE UPDATE OR DELETE ON closure_evidence FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_comparison_gap BEFORE UPDATE OR DELETE ON comparison_gap FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_comparison_impact_dimension BEFORE UPDATE OR DELETE ON comparison_impact_dimension FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_comparison_impact_summary BEFORE UPDATE OR DELETE ON comparison_impact_summary FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_context_snapshot BEFORE UPDATE OR DELETE ON context_snapshot FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_control_assessment BEFORE UPDATE OR DELETE ON control_assessment FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_control_assessment_criterion BEFORE UPDATE OR DELETE ON control_assessment_criterion FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_control_criterion_version BEFORE UPDATE OR DELETE ON control_criterion_version FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_control_definition_version BEFORE UPDATE OR DELETE ON control_definition_version FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_criterion_evidence BEFORE UPDATE OR DELETE ON criterion_evidence FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_criterion_test_execution BEFORE UPDATE OR DELETE ON criterion_test_execution FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_evidence_link BEFORE UPDATE OR DELETE ON evidence_link FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_evidence_request BEFORE UPDATE OR DELETE ON evidence_request FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_evidence_request_criterion BEFORE UPDATE OR DELETE ON evidence_request_criterion FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_evidence_revision BEFORE UPDATE OR DELETE ON evidence_revision FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_excluded_control BEFORE UPDATE OR DELETE ON excluded_control FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_factor_evidence BEFORE UPDATE OR DELETE ON factor_evidence FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_impact_confirmation BEFORE UPDATE OR DELETE ON impact_confirmation FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_impact_confirmation_dimension BEFORE UPDATE OR DELETE ON impact_confirmation_dimension FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_impact_factor BEFORE UPDATE OR DELETE ON impact_factor FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_input_confirmation BEFORE UPDATE OR DELETE ON input_confirmation FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_input_confirmation_evidence BEFORE UPDATE OR DELETE ON input_confirmation_evidence FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_mutable_entity_history BEFORE UPDATE OR DELETE ON mutable_entity_history FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_priority_decision BEFORE UPDATE OR DELETE ON priority_decision FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_priority_decision_member BEFORE UPDATE OR DELETE ON priority_decision_member FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_priority_proposal BEFORE UPDATE OR DELETE ON priority_proposal FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_priority_proposal_member BEFORE UPDATE OR DELETE ON priority_proposal_member FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_report_gap_snapshot BEFORE UPDATE OR DELETE ON report_gap_snapshot FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_report_snapshot BEFORE UPDATE OR DELETE ON report_snapshot FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_report_snapshot_member BEFORE UPDATE OR DELETE ON report_snapshot_member FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_report_task_snapshot BEFORE UPDATE OR DELETE ON report_task_snapshot FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_retest_result BEFORE UPDATE OR DELETE ON retest_result FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_retest_result_control BEFORE UPDATE OR DELETE ON retest_result_control FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_review_decision BEFORE UPDATE OR DELETE ON review_decision FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_risk_acceptance BEFORE UPDATE OR DELETE ON risk_acceptance FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_risk_evaluation BEFORE UPDATE OR DELETE ON risk_evaluation FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_risk_factor BEFORE UPDATE OR DELETE ON risk_factor FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_risk_impact_confirmation BEFORE UPDATE OR DELETE ON risk_impact_confirmation FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_risk_input_confirmation BEFORE UPDATE OR DELETE ON risk_input_confirmation FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_risk_method_version BEFORE UPDATE OR DELETE ON risk_method_version FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_risk_path BEFORE UPDATE OR DELETE ON risk_path FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_risk_path_control BEFORE UPDATE OR DELETE ON risk_path_control FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_risk_validation_issue BEFORE UPDATE OR DELETE ON risk_validation_issue FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_scenario_snapshot BEFORE UPDATE OR DELETE ON scenario_snapshot FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_scope BEFORE UPDATE OR DELETE ON scope FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_scope_branch BEFORE UPDATE OR DELETE ON scope_branch FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_scope_object BEFORE UPDATE OR DELETE ON scope_object FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_snapshot_registry BEFORE UPDATE OR DELETE ON snapshot_registry FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_storage_event BEFORE UPDATE OR DELETE ON storage_event FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_test_case_criterion BEFORE UPDATE OR DELETE ON test_case_criterion FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_test_case_version BEFORE UPDATE OR DELETE ON test_case_version FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_test_execution BEFORE UPDATE OR DELETE ON test_execution FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_test_execution_evidence BEFORE UPDATE OR DELETE ON test_execution_evidence FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_treatment_approval BEFORE UPDATE OR DELETE ON treatment_approval FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER immutable_verification_decision BEFORE UPDATE OR DELETE ON verification_decision FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER stamp_snapshot_registry BEFORE INSERT ON snapshot_registry FOR EACH ROW EXECUTE FUNCTION stamp_transaction();
CREATE TRIGGER stamp_scope BEFORE INSERT ON scope FOR EACH ROW EXECUTE FUNCTION stamp_transaction();
CREATE TRIGGER stamp_control_definition_version BEFORE INSERT ON control_definition_version FOR EACH ROW EXECUTE FUNCTION stamp_transaction();
CREATE TRIGGER stamp_test_case_version BEFORE INSERT ON test_case_version FOR EACH ROW EXECUTE FUNCTION stamp_transaction();
CREATE TRIGGER stamp_priority_proposal BEFORE INSERT ON priority_proposal FOR EACH ROW EXECUTE FUNCTION stamp_transaction();
CREATE TRIGGER kind_context_snapshot BEFORE INSERT ON context_snapshot FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('CONTEXT');
CREATE TRIGGER kind_scenario_snapshot BEFORE INSERT ON scenario_snapshot FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('SCENARIO');
CREATE TRIGGER kind_authentication_profile_version BEFORE INSERT ON authentication_profile_version FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('AUTHENTICATION_PROFILE');
CREATE TRIGGER kind_evidence_revision BEFORE INSERT ON evidence_revision FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('EVIDENCE_REVISION');
CREATE TRIGGER kind_verification_decision BEFORE INSERT ON verification_decision FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('VERIFICATION_DECISION');
CREATE TRIGGER kind_evidence_link BEFORE INSERT ON evidence_link FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('EVIDENCE_LINK');
CREATE TRIGGER kind_test_execution BEFORE INSERT ON test_execution FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('TEST_EXECUTION');
CREATE TRIGGER kind_control_assessment BEFORE INSERT ON control_assessment FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('CONTROL_ASSESSMENT');
CREATE TRIGGER kind_risk_evaluation BEFORE INSERT ON risk_evaluation FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('RISK_EVALUATION');
CREATE TRIGGER kind_retest_result BEFORE INSERT ON retest_result FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('RETEST_RESULT');
CREATE TRIGGER kind_assessment_comparison BEFORE INSERT ON assessment_comparison FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('COMPARISON');
CREATE TRIGGER kind_review_decision BEFORE INSERT ON review_decision FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('REVIEW_DECISION');
CREATE TRIGGER kind_adjudication_decision BEFORE INSERT ON adjudication_decision FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('ADJUDICATION_DECISION');
CREATE TRIGGER kind_priority_decision BEFORE INSERT ON priority_decision FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('PRIORITY_DECISION');
CREATE TRIGGER kind_risk_acceptance BEFORE INSERT ON risk_acceptance FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('RISK_ACCEPTANCE');
CREATE TRIGGER kind_closure_decision BEFORE INSERT ON closure_decision FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('CLOSURE_DECISION');
CREATE TRIGGER kind_report_snapshot BEFORE INSERT ON report_snapshot FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('REPORT');
CREATE TRIGGER kind_input_confirmation BEFORE INSERT ON input_confirmation FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('INPUT_CONFIRMATION');
CREATE TRIGGER kind_impact_confirmation BEFORE INSERT ON impact_confirmation FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('IMPACT_CONFIRMATION');
CREATE TRIGGER kind_evidence_request BEFORE INSERT ON evidence_request FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('EVIDENCE_REQUEST');
CREATE TRIGGER kind_treatment_approval BEFORE INSERT ON treatment_approval FOR EACH ROW EXECUTE FUNCTION require_snapshot_kind('TREATMENT_APPROVAL');
CREATE TRIGGER seal_scope_branch BEFORE INSERT ON scope_branch FOR EACH ROW EXECUTE FUNCTION require_open_parent('scope_id','SELECT created_txid FROM vdt.scope WHERE id=$1');
CREATE TRIGGER seal_scope_object BEFORE INSERT ON scope_object FOR EACH ROW EXECUTE FUNCTION require_open_parent('scope_id','SELECT created_txid FROM vdt.scope WHERE id=$1');
CREATE TRIGGER seal_control_criterion_version BEFORE INSERT ON control_criterion_version FOR EACH ROW EXECUTE FUNCTION require_open_parent('control_version_id','SELECT created_txid FROM vdt.control_definition_version WHERE id=$1');
CREATE TRIGGER seal_test_case_criterion BEFORE INSERT ON test_case_criterion FOR EACH ROW EXECUTE FUNCTION require_open_parent('test_case_version_id','SELECT created_txid FROM vdt.test_case_version WHERE id=$1');
CREATE TRIGGER seal_priority_proposal_member BEFORE INSERT ON priority_proposal_member FOR EACH ROW EXECUTE FUNCTION require_open_parent('proposal_id','SELECT created_txid FROM vdt.priority_proposal WHERE id=$1');
CREATE TRIGGER seal_test_execution_evidence BEFORE INSERT ON test_execution_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('test_execution_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_control_assessment_criterion BEFORE INSERT ON control_assessment_criterion FOR EACH ROW EXECUTE FUNCTION require_open_parent('control_assessment_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_risk_factor BEFORE INSERT ON risk_factor FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_evaluation_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_excluded_control BEFORE INSERT ON excluded_control FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_evaluation_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_risk_path BEFORE INSERT ON risk_path FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_evaluation_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_impact_factor BEFORE INSERT ON impact_factor FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_evaluation_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_risk_validation_issue BEFORE INSERT ON risk_validation_issue FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_evaluation_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_comparison_impact_dimension BEFORE INSERT ON comparison_impact_dimension FOR EACH ROW EXECUTE FUNCTION require_open_parent('comparison_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_comparison_impact_summary BEFORE INSERT ON comparison_impact_summary FOR EACH ROW EXECUTE FUNCTION require_open_parent('comparison_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_comparison_gap BEFORE INSERT ON comparison_gap FOR EACH ROW EXECUTE FUNCTION require_open_parent('comparison_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_priority_decision_member BEFORE INSERT ON priority_decision_member FOR EACH ROW EXECUTE FUNCTION require_open_parent('decision_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_closure_evidence BEFORE INSERT ON closure_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('closure_decision_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_report_snapshot_member BEFORE INSERT ON report_snapshot_member FOR EACH ROW EXECUTE FUNCTION require_open_parent('report_snapshot_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_report_gap_snapshot BEFORE INSERT ON report_gap_snapshot FOR EACH ROW EXECUTE FUNCTION require_open_parent('report_snapshot_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_report_task_snapshot BEFORE INSERT ON report_task_snapshot FOR EACH ROW EXECUTE FUNCTION require_open_parent('report_snapshot_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_input_confirmation_evidence BEFORE INSERT ON input_confirmation_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('confirmation_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_risk_input_confirmation BEFORE INSERT ON risk_input_confirmation FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_evaluation_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_impact_confirmation_dimension BEFORE INSERT ON impact_confirmation_dimension FOR EACH ROW EXECUTE FUNCTION require_open_parent('confirmation_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_risk_impact_confirmation BEFORE INSERT ON risk_impact_confirmation FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_evaluation_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_evidence_request_criterion BEFORE INSERT ON evidence_request_criterion FOR EACH ROW EXECUTE FUNCTION require_open_parent('request_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_retest_result_control BEFORE INSERT ON retest_result_control FOR EACH ROW EXECUTE FUNCTION require_open_parent('result_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_adjudication_review BEFORE INSERT ON adjudication_review FOR EACH ROW EXECUTE FUNCTION require_open_parent('adjudication_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_closure_criterion BEFORE INSERT ON closure_criterion FOR EACH ROW EXECUTE FUNCTION require_open_parent('closure_decision_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER seal_criterion_evidence BEFORE INSERT ON criterion_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('criterion_result_id','SELECT s.created_txid FROM vdt.control_assessment_criterion c JOIN vdt.snapshot_registry s ON s.id=c.control_assessment_id WHERE c.id=$1');
CREATE TRIGGER seal_criterion_test_execution BEFORE INSERT ON criterion_test_execution FOR EACH ROW EXECUTE FUNCTION require_open_parent('criterion_result_id','SELECT s.created_txid FROM vdt.control_assessment_criterion c JOIN vdt.snapshot_registry s ON s.id=c.control_assessment_id WHERE c.id=$1');
CREATE TRIGGER seal_risk_path_control BEFORE INSERT ON risk_path_control FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_path_id','SELECT s.created_txid FROM vdt.risk_path p JOIN vdt.snapshot_registry s ON s.id=p.risk_evaluation_id WHERE p.id=$1');
CREATE TRIGGER seal_closure_criterion_evidence BEFORE INSERT ON closure_criterion_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('closure_criterion_id','SELECT s.created_txid FROM vdt.closure_criterion c JOIN vdt.snapshot_registry s ON s.id=c.closure_decision_id WHERE c.id=$1');
CREATE TRIGGER seal_factor_evidence_risk_factor_id BEFORE INSERT ON factor_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_factor_id','SELECT s.created_txid FROM vdt.risk_factor f JOIN vdt.snapshot_registry s ON s.id=f.risk_evaluation_id WHERE f.id=$1');
CREATE TRIGGER seal_factor_evidence_risk_path_id BEFORE INSERT ON factor_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('risk_path_id','SELECT s.created_txid FROM vdt.risk_path f JOIN vdt.snapshot_registry s ON s.id=f.risk_evaluation_id WHERE f.id=$1');
CREATE TRIGGER seal_factor_evidence_impact_factor_id BEFORE INSERT ON factor_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('impact_factor_id','SELECT s.created_txid FROM vdt.impact_factor f JOIN vdt.snapshot_registry s ON s.id=f.risk_evaluation_id WHERE f.id=$1');
CREATE TRIGGER version_organization BEFORE UPDATE ON organization FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_branch BEFORE UPDATE ON branch FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_app_user BEFORE UPDATE ON app_user FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_authorization_guard BEFORE UPDATE ON authorization_guard FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_vdt_session BEFORE UPDATE ON vdt_session FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_information_system BEFORE UPDATE ON information_system FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_asset BEFORE UPDATE ON asset FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_data_asset BEFORE UPDATE ON data_asset FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_vendor BEFORE UPDATE ON vendor FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_data_flow BEFORE UPDATE ON data_flow FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_risk_scenario BEFORE UPDATE ON risk_scenario FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_assessment BEFORE UPDATE ON assessment FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_role_assignment BEFORE UPDATE ON role_assignment FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_control_implementation BEFORE UPDATE ON control_implementation FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_evidence_item BEFORE UPDATE ON evidence_item FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_evidence_storage BEFORE UPDATE ON evidence_storage FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_gap BEFORE UPDATE ON gap FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_treatment_plan BEFORE UPDATE ON treatment_plan FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_treatment_task BEFORE UPDATE ON treatment_task FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_retest_request BEFORE UPDATE ON retest_request FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_review_request BEFORE UPDATE ON review_request FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_idempotency_operation BEFORE UPDATE ON idempotency_operation FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_upload_operation BEFORE UPDATE ON upload_operation FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_background_job BEFORE UPDATE ON background_job FOR EACH ROW EXECUTE FUNCTION check_version_increment();
CREATE TRIGGER version_export_artifact BEFORE UPDATE ON export_artifact FOR EACH ROW EXECUTE FUNCTION check_version_increment();

-- Application role is provisioned separately from migration owner; names are
-- deployment configuration. It receives no CREATE/ALTER/TRUNCATE/BYPASSRLS,
-- table ownership, trigger-disable or DELETE privileges on immutable tables.
-- Grant only SELECT/INSERT for immutable data and the required mutable commands.
-- Trigger protections do not defend against the migration owner/superuser.
-- Transaction service still validates: current permissions/clock/CSRF, snapshot
-- completeness, cross-row scope/kind/criteria membership, all RM labels/status,
-- independent actor decisions, criteria closure, exact file hashes, every
-- referenced version and audit/history atomicity. Verify these in step 06.
-- Roundtrip and request sealing review 2026-10-21.
-- Canonical API DTO retains structured UNKNOWN/source metadata; typed FKs remain authoritative.
ALTER TABLE information_system ADD COLUMN api_payload_schema_version text NOT NULL DEFAULT 'v0.1';
ALTER TABLE information_system ADD COLUMN api_payload jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(api_payload)='object');
-- Canonical API DTO retains structured UNKNOWN/source metadata; typed FKs remain authoritative.
ALTER TABLE asset ADD COLUMN api_payload_schema_version text NOT NULL DEFAULT 'v0.1';
ALTER TABLE asset ADD COLUMN api_payload jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(api_payload)='object');
-- Canonical API DTO retains structured UNKNOWN/source metadata; typed FKs remain authoritative.
ALTER TABLE data_asset ADD COLUMN api_payload_schema_version text NOT NULL DEFAULT 'v0.1';
ALTER TABLE data_asset ADD COLUMN api_payload jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(api_payload)='object');
-- Canonical API DTO retains structured UNKNOWN/source metadata; typed FKs remain authoritative.
ALTER TABLE vendor ADD COLUMN api_payload_schema_version text NOT NULL DEFAULT 'v0.1';
ALTER TABLE vendor ADD COLUMN api_payload jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(api_payload)='object');
-- Canonical API DTO retains structured UNKNOWN/source metadata; typed FKs remain authoritative.
ALTER TABLE data_flow ADD COLUMN api_payload_schema_version text NOT NULL DEFAULT 'v0.1';
ALTER TABLE data_flow ADD COLUMN api_payload jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(api_payload)='object');
-- Canonical API DTO retains structured UNKNOWN/source metadata; typed FKs remain authoritative.
ALTER TABLE risk_scenario ADD COLUMN api_payload_schema_version text NOT NULL DEFAULT 'v0.1';
ALTER TABLE risk_scenario ADD COLUMN api_payload jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(api_payload)='object');
-- Canonical API DTO retains structured UNKNOWN/source metadata; typed FKs remain authoritative.
ALTER TABLE assessment ADD COLUMN api_payload_schema_version text NOT NULL DEFAULT 'v0.1';
ALTER TABLE assessment ADD COLUMN api_payload jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(api_payload)='object');

ALTER TABLE control_assessment_criterion ADD COLUMN raw_input jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(raw_input)='object');
ALTER TABLE control_assessment_criterion ADD COLUMN missing_reasons text[] NOT NULL DEFAULT '{}';
ALTER TABLE control_assessment_criterion ADD COLUMN verified_failure boolean NOT NULL DEFAULT false;
ALTER TABLE control_assessment_criterion ADD COLUMN test_run_reference text;
ALTER TABLE control_assessment_criterion ADD COLUMN test_case_codes text[] NOT NULL DEFAULT '{}';
-- API APPROVE/REJECT is distinct from resulting RANKED/NOT_RANKED.
ALTER TABLE priority_decision ADD COLUMN approval_action text CHECK(approval_action IN ('APPROVE','REJECT'));
ALTER TABLE priority_decision ADD CHECK(
 (decision_type='RISK_OWNER_APPROVAL' AND approval_action IS NOT NULL)
 OR (decision_type='REVIEWER_DETERMINATION' AND approval_action IS NULL));
ALTER TABLE priority_decision ADD CHECK(approval_action IS DISTINCT FROM 'REJECT' OR priority_decision='NOT_RANKED');
ALTER TABLE retest_request ADD COLUMN created_txid bigint NOT NULL DEFAULT txid_current();
CREATE TRIGGER stamp_retest_request BEFORE INSERT ON retest_request FOR EACH ROW EXECUTE FUNCTION stamp_transaction();
CREATE FUNCTION protect_retest_inputs() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF (to_jsonb(NEW)-ARRAY['state','version']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['state','version']) THEN
  RAISE EXCEPTION 'retest request inputs are immutable' USING ERRCODE='55000';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER protect_retest_inputs BEFORE UPDATE ON retest_request FOR EACH ROW EXECUTE FUNCTION protect_retest_inputs();
CREATE TRIGGER immutable_retest_baseline_control BEFORE UPDATE OR DELETE ON retest_baseline_control FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER seal_retest_baseline_control BEFORE INSERT ON retest_baseline_control FOR EACH ROW EXECUTE FUNCTION require_open_parent('request_id','SELECT created_txid FROM vdt.retest_request WHERE id=$1');
CREATE TRIGGER immutable_retest_task BEFORE UPDATE OR DELETE ON retest_task FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER seal_retest_task BEFORE INSERT ON retest_task FOR EACH ROW EXECUTE FUNCTION require_open_parent('request_id','SELECT created_txid FROM vdt.retest_request WHERE id=$1');
CREATE TRIGGER immutable_retest_evidence BEFORE UPDATE OR DELETE ON retest_evidence FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER seal_retest_evidence BEFORE INSERT ON retest_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('request_id','SELECT created_txid FROM vdt.retest_request WHERE id=$1');

-- Final contract review corrections 2026-10-21.
-- Canonical validated input is retained for roundtrip/provenance; DTO adapters also
-- populate typed columns/FKs below. JSON is never a replacement for scope checks.
ALTER TABLE snapshot_registry ADD COLUMN api_payload_schema_version text NOT NULL DEFAULT 'v0.1';
ALTER TABLE snapshot_registry ADD COLUMN api_payload jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(api_payload)='object');
ALTER TABLE control_implementation ADD COLUMN authentication_profile_version_id uuid REFERENCES authentication_profile_version;
ALTER TABLE scenario_control ADD COLUMN scope_id uuid NOT NULL REFERENCES scope;
ALTER TABLE scenario_control ADD COLUMN created_by uuid NOT NULL REFERENCES app_user;
ALTER TABLE scenario_control ADD COLUMN created_at timestamptz NOT NULL DEFAULT clock_timestamp();
ALTER TABLE scenario_control ADD COLUMN api_payload jsonb NOT NULL DEFAULT '{}' CHECK(jsonb_typeof(api_payload)='object');
CREATE TRIGGER immutable_scenario_control BEFORE UPDATE OR DELETE ON scenario_control FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TABLE evidence_link_criterion (
 id uuid PRIMARY KEY, evidence_link_id uuid NOT NULL REFERENCES evidence_link,
 criterion_version_id uuid NOT NULL REFERENCES control_criterion_version,
 UNIQUE(evidence_link_id,criterion_version_id)
);
CREATE TABLE comparison_treatment (
 id uuid PRIMARY KEY, comparison_id uuid NOT NULL REFERENCES assessment_comparison,
 task_id uuid NOT NULL REFERENCES treatment_task, task_version bigint NOT NULL CHECK(task_version>0),
 UNIQUE(comparison_id,task_id)
);
CREATE TABLE comparison_attribution_evidence (
 id uuid PRIMARY KEY, comparison_id uuid NOT NULL REFERENCES assessment_comparison,
 evidence_revision_id uuid NOT NULL REFERENCES evidence_revision, verification_decision_id uuid NOT NULL,
 purpose nonempty_text NOT NULL,
 FOREIGN KEY(verification_decision_id,evidence_revision_id) REFERENCES verification_decision(id,evidence_revision_id),
 UNIQUE(comparison_id,evidence_revision_id,verification_decision_id)
);
-- SUPPORTED requires exact tasks/evidence and independent confirmation; historical
-- task_version must resolve in mutable_entity_history and per-dimension causality
-- remains a transaction-service check. Optional treatment_plan_id is grouping only.
CREATE FUNCTION require_supported_attribution() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.treatment_attribution='SUPPORTED' AND (
  NOT EXISTS (SELECT 1 FROM vdt.comparison_treatment WHERE comparison_id=NEW.id)
  OR NOT EXISTS (SELECT 1 FROM vdt.comparison_attribution_evidence WHERE comparison_id=NEW.id)
 ) THEN RAISE EXCEPTION 'SUPPORTED attribution requires tasks and evidence' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER supported_attribution_payload AFTER INSERT ON assessment_comparison
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_supported_attribution();
CREATE TRIGGER immutable_evidence_link_criterion BEFORE UPDATE OR DELETE ON evidence_link_criterion FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER seal_evidence_link_criterion BEFORE INSERT ON evidence_link_criterion FOR EACH ROW EXECUTE FUNCTION require_open_parent('evidence_link_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER immutable_comparison_treatment BEFORE UPDATE OR DELETE ON comparison_treatment FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER seal_comparison_treatment BEFORE INSERT ON comparison_treatment FOR EACH ROW EXECUTE FUNCTION require_open_parent('comparison_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');
CREATE TRIGGER immutable_comparison_attribution_evidence BEFORE UPDATE OR DELETE ON comparison_attribution_evidence FOR EACH ROW EXECUTE FUNCTION reject_history_change();
CREATE TRIGGER seal_comparison_attribution_evidence BEFORE INSERT ON comparison_attribution_evidence FOR EACH ROW EXECUTE FUNCTION require_open_parent('comparison_id','SELECT created_txid FROM vdt.snapshot_registry WHERE id=$1');

COMMIT;
