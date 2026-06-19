---
title: "Consultant Role KB Local Staging Auth Audit Smoke Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "agents/consultant-agent/runtime/staging_auth_audit.py"
  - "agents/consultant-agent/runtime/local_retrieval_api.py"
  - "shared/audit/consultant-agent/staging-audit-event.schema-20260619.json"
scope: "local smoke for consultant-agent staging auth and audit harness"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local validation only; no staging deployment"
---

# Consultant Role KB Local Staging Auth Audit Smoke Report

## 0. Boundary

This smoke runs a localhost-only staging harness. It does not deploy staging,
call a provider, write into a live KB, approve labels, or return raw source text.

## 1. Smoke Metrics

| metric | value |
|---|---:|
| record_count | 800 |
| allowed_http_status | 200 |
| policy_refusal_http_status | 200 |
| missing_token_status | 401 |
| rbac_denied_status | 403 |
| label_seed_match_at_5 | 1.0 |
| policy_refusal_pass_rate | 1.0 |
| audit_event_count | 5 |
| allowed_event_count | 2 |
| denied_event_count | 2 |
| policy_refusal_event_count | 1 |
| audit_schema_failure_count | 0 |
| audit_forbidden_leak_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |
| failure_count | 0 |

## 2. Interpretation

Fact: the local harness enforces bearer-token auth, role-gated endpoint access,
workspace/agent headers, and one audit event per protected request.

Fact: audit events validate against the staging audit schema and store only
hashed actor/query identifiers plus source/card/locator references.

Boundary: this is not a staging deployment and does not approve provider use,
live KB ingestion, source licensing, or human-gold label status.
