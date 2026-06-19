---
title: "Consultant Role KB Security Staging Control Workflow"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md"
  - "drafts/analysis/consultant-role-kb-shared-staging-readiness-preflight-20260619.md"
  - "shared/governance/consultant-agent/security-staging-control-decision.schema-20260619.json"
scope: "structured security and operations decision intake for consultant-agent shared staging"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "decision workflow only; no security approval or shared staging deployment"
---

# Consultant Role KB Security Staging Control Workflow

## 0. Boundary

This workflow creates a review queue, pending decision template, and validation
summary for shared-staging security controls. It does not configure secrets,
approve staging, deploy shared staging, call a provider, or ingest into a live
KB.

## 1. Validation Summary

| metric | value |
|---|---:|
| control_count | 8 |
| decision_count | 8 |
| required_external_control_count | 6 |
| pending_review_count | 8 |
| approved_control_count | 0 |
| configured_external_control_count | 0 |
| shared_staging_security_controls_ready | false |
| secret_like_value_count | 0 |
| failure_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Artifacts

- Schema: `shared/governance/consultant-agent/security-staging-control-decision.schema-20260619.json`
- Queue: `shared/governance/consultant-agent/security-staging-control-review.queue-20260619.csv`
- Decision template: `shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl`
- Validation: `tmp/consultant-role-kb-security-staging-control-validation-20260619.json`

## 3. Required Control Areas

| control | area | pending evidence |
|---|---|---|
| `SEC-STG-001` | network_boundary | private ingress and network boundary approval |
| `SEC-STG-002` | secret_storage | external secret storage approval |
| `SEC-STG-003` | auth | bearer-token hash configured outside Git |
| `SEC-STG-004` | audit_storage | append-only audit path outside repository |
| `SEC-STG-005` | audit_retention | audit retention and access policy |
| `SEC-STG-006` | rate_limit | private ingress or middleware rate limit |
| `SEC-STG-007` | rollback | rollback owner and stop procedure |
| `SEC-STG-008` | rbac | operator roster and RBAC scope |

## 4. Interpretation

Fact: all required security controls now have pending decision rows and the
template validates with `failure_count = 0`.

Fact: no control has been approved, no external configuration has been
recorded, and shared-staging security readiness remains false.

Boundary: the decision template must not contain raw secret values, bearer
tokens, passwords, private keys, or private contact details.
