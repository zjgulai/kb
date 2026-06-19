---
title: "Consultant Role KB Shared Staging Readiness Preflight"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-staging-auth-audit-design-20260619.md"
  - "drafts/analysis/consultant-role-kb-legal-source-owner-review-packet-20260619.md"
  - "tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json"
  - "tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json"
  - "tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json"
scope: "preflight gate before any security-approved shared staging deployment"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local readiness check only; no shared staging deployment"
---

# Consultant Role KB Shared Staging Readiness Preflight

## 0. Boundary

This preflight is a local evidence check. It does not deploy staging, call a
provider, ingest into a live KB, approve labels, or clear source licensing.

## 1. Result

| field | value |
|---|---:|
| ready_for_shared_staging | false |
| status | blocked |
| check_count | 20 |
| pass_count | 14 |
| warning_count | 0 |
| blocker_count | 6 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Blockers

| check | evidence | detail |
|---|---|---|
| `human_labels_approved` | tmp/consultant-role-kb-human-label-review-workflow-validation-20260619.json | approved_decision_count=0; manual reviewer decisions are required before claiming human-gold labels |
| `legal_source_owner_clearance` | tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json | selected_approved_internal_staging_count=0/80; legal/source-owner clearance remains pending |
| `external_auth_token_hash_configured` | environment:KB_STAGING_AUTH_TOKEN_SHA256 | token hash status=missing; secret value is not logged |
| `external_audit_path_configured` | environment:KB_STAGING_AUDIT_PATH | audit path status=missing; environment variable is not set |
| `rate_limit_configured` | environment:KB_STAGING_RATE_LIMIT_CONFIGURED | rate limiting must be configured at private ingress or middleware before shared staging |
| `rollback_owner_recorded` | environment:KB_STAGING_ROLLBACK_OWNER | rollback owner is not recorded in local environment; value is not logged |

## 3. All Checks

| check | status | evidence |
|---|---|---|
| `local_api_smoke_green` | pass | tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json |
| `local_api_800_record_alignment` | pass | tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json |
| `local_api_policy_refusal_green` | pass | tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json |
| `local_harness_smoke_green` | pass | tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json |
| `local_harness_denies_missing_token` | pass | tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json |
| `local_harness_denies_rbac` | pass | tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json |
| `audit_contract_green` | pass | tmp/consultant-role-kb-staging-auth-audit-contract-validation-20260619.json |
| `audit_no_forbidden_leak` | pass | tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json |
| `no_provider_calls` | pass | multiple smoke outputs |
| `no_live_kb_writes` | pass | multiple smoke outputs |
| `human_label_workflow_generated` | pass | tmp/consultant-role-kb-human-label-review-workflow-validation-20260619.json |
| `legal_source_owner_workflow_generated` | pass | tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json |
| `human_labels_approved` | blocker | tmp/consultant-role-kb-human-label-review-workflow-validation-20260619.json |
| `legal_source_owner_clearance` | blocker | tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json |
| `raw_consult_not_tracked` | pass | git ls-files consult |
| `rollback_runbook_exists` | pass | drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md |
| `external_auth_token_hash_configured` | blocker | environment:KB_STAGING_AUTH_TOKEN_SHA256 |
| `external_audit_path_configured` | blocker | environment:KB_STAGING_AUDIT_PATH |
| `rate_limit_configured` | blocker | environment:KB_STAGING_RATE_LIMIT_CONFIGURED |
| `rollback_owner_recorded` | blocker | environment:KB_STAGING_ROLLBACK_OWNER |

## 4. Interpretation

Fact: local retrieval API, local auth/audit harness, audit schema validation,
no-provider boundary, no-live-write boundary, and raw-source Git exclusion are
green.

Fact: shared staging remains blocked by missing legal/source-owner clearance,
missing approved human-gold labels, and missing external staging controls such
as secret configuration, external audit path, rate limit configuration, and
rollback ownership.

Boundary: this is not a staging deployment and should not be described as
online agent launch readiness.
