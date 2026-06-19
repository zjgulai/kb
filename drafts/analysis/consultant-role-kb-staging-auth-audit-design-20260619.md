---
title: "Consultant Role KB Staging Auth And Audit Design"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "agents/consultant-agent/runtime/local_retrieval_api.py"
  - "drafts/analysis/consultant-agent-runtime-adr-20260619.md"
  - "drafts/analysis/consultant-role-kb-legal-source-owner-review-packet-20260619.md"
  - "drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md"
  - "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/manifest.json"
scope: "draft staging auth and audit contract for consultant-agent no-provider retrieval API"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local harness implemented and smoke-validated; no staging deployment"
---

# Consultant Role KB Staging Auth And Audit Design

## 1. Boundary

This document defines the next private-staging contract for the
`consultant-agent` retrieval API. It does not deploy staging, does not authorize
provider generation, does not ingest into a live KB, and does not approve
client-ready usage.

Current facts:

- local API prototype exists at `agents/consultant-agent/runtime/local_retrieval_api.py`;
- local staging auth/audit harness exists at `agents/consultant-agent/runtime/staging_auth_audit.py`;
- durable local index has 800 all-extractable records and local BGE embeddings;
- human locator labels remain `pending_human_review`;
- all source licenses remain `pending_legal_review`;
- raw `consult/` files remain local-only and must not be committed.

## 2. Staging Topology

Recommended private-staging topology:

| layer | requirement |
|---|---|
| network ingress | private network, VPN, or localhost tunnel only; no public anonymous endpoint |
| service bind | default bind remains `127.0.0.1`; shared staging needs an internal reverse proxy |
| TLS | terminate at private ingress before user traffic |
| secrets | access tokens stored outside Git, e.g. `<external-secret-store>` |
| logs | audit log path outside the repository, e.g. `<external-audit-log-path>` |
| data boundary | no raw source text in API responses or audit logs |
| runtime boundary | no provider call and no live KB write by default |

## 3. Request Auth Contract

Every staging request to `/retrieve` and `/eval/label-seed` must include:

| header | requirement |
|---|---|
| `Authorization` | bearer token validated against external secret storage |
| `X-KB-Agent` | must equal `consultant-agent` |
| `X-KB-Workspace` | must equal `consultant-p1` |
| `X-KB-Reviewer` | reviewer or actor identifier; audit stores only a hash |
| `X-KB-Request-Id` | caller-provided idempotency/correlation ID |
| `X-KB-Role` | one of `retrieval_reader`, `reviewer`, or `admin` |

Fail-closed rules:

- missing or invalid bearer token returns `401`;
- unknown agent, workspace, or role returns `403`;
- missing `X-KB-Request-Id` returns `400`;
- auth failure must still emit a denied audit event without raw question text;
- no request may bypass audit event creation.

## 4. RBAC Contract

| role | allowed endpoints | notes |
|---|---|---|
| `retrieval_reader` | `/retrieve`, `/health` | read-only pilot retrieval |
| `reviewer` | `/retrieve`, `/eval/label-seed`, `/health` | can run label-seed checks; cannot approve labels through API |
| `admin` | `/retrieve`, `/eval/label-seed`, `/health` | operational use only; no source/license override |

RBAC is still constrained to:

- `agent_id=consultant-agent`;
- `workspace=consultant-p1`;
- `retrieval_mode=local_bge_vector_plus_deterministic_rerank`;
- `provider_call_count=0`;
- `live_kb_write_count=0`.

## 5. Audit Event Schema

Staging audit events are validated against:

`shared/audit/consultant-agent/staging-audit-event.schema-20260619.json`

The event stores:

- event identity: `event_id`, `ts`, `request_id`;
- hashed actor/query fields: `actor_id_hash`, `query_sha256`, `query_length`;
- access context: `agent_id`, `workspace`, `endpoint`, `actor_role`;
- retrieval context: `retrieval_mode`, optional `eval_id`, `result_count`;
- result references: `source_id`, `card_id`, `locator`, `evidence_grade`,
  `license_status`;
- governance counters: `provider_call_count`, `live_kb_write_count`,
  `source_text_returned`;
- outcome: `decision`, optional `blocked_reason`, `production_impact`.

The audit event must not store raw prompt text, raw source text, bearer tokens,
private keys, passwords, personal contact details, or payment identifiers.

## 6. Retention

Default private-pilot retention:

- audit events: 30 days unless legal/security specifies a different period;
- raw prompt text: not stored by default;
- query diagnostics: hash and length only;
- denied requests: retained with hashed actor and blocked reason;
- label review decisions: stored separately from audit logs and require manual
  reviewer sign-off.

## 7. API Migration Plan

To move the local prototype into private staging:

1. Add auth middleware before `LocalRetrievalService.retrieve`.
2. Map validated headers into `actor_role`, `actor_id_hash`, `request_id`,
   `agent_id`, and `workspace`.
3. Generate one audit event for every allowed or denied `/retrieve` and
   `/eval/label-seed` request.
4. Write audit events to an external append-only path outside the repository.
5. Keep `public_result` unchanged on source-text boundary: return source IDs,
   locators, evidence grade, license status, and checksums, but no raw source
   text.
6. Re-run local API smoke plus audit contract validation before any shared
   staging pilot.

## 8. Acceptance Gates Before Any Shared Staging Pilot

| gate | required status |
|---|---|
| legal/source-owner review | explicit outcome recorded |
| locator labels | reviewer decisions recorded before claiming human-gold metrics |
| auth secrets | token source configured outside repo |
| audit path | append-only path configured outside repo |
| audit schema validation | local validation failure_count = 0 |
| API smoke | failure_count = 0 |
| rate limit | configured at ingress or middleware |
| rollback | documented stop command and traffic disable path |
| provider calls | still disabled unless separately approved |
| live KB writes | still disabled unless separately approved |

## 9. Validation Evidence

Local contract validator:

- script: `tmp/consultant_role_kb_staging_auth_audit_contract_20260619.py`;
- output: `tmp/consultant-role-kb-staging-auth-audit-contract-validation-20260619.json`;
- sample events: `tmp/consultant-role-kb-staging-auth-audit-sample-events-20260619.jsonl`.

The validator checks that sample allowed and denied events:

- match required schema fields;
- store hashed actor/query identifiers rather than raw values;
- include no raw source text;
- keep `provider_call_count=0`;
- keep `live_kb_write_count=0`;
- keep `source_text_returned=false`;
- preserve `production_impact=production unchanged`.

Local staging harness smoke:

- module: `agents/consultant-agent/runtime/staging_auth_audit.py`;
- smoke script: `tmp/consultant_role_kb_local_staging_auth_audit_smoke_20260619.py`;
- smoke output: `tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json`;
- audit events: `tmp/consultant-role-kb-local-staging-audit-events-20260619.jsonl`;
- report: `drafts/analysis/consultant-role-kb-local-staging-auth-audit-smoke-report-20260619.md`.
- shared staging runbook: `drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md`.

Smoke result:

- record_count = 800;
- allowed_http_status = 200;
- policy_refusal_http_status = 200;
- missing_token_status = 401;
- rbac_denied_status = 403;
- label_seed_match_at_5 = 1.0;
- policy_refusal_pass_rate = 1.0;
- audit_event_count = 5;
- allowed_event_count = 2;
- denied_event_count = 2;
- policy_refusal_event_count = 1;
- audit_schema_failure_count = 0;
- audit_forbidden_leak_count = 0;
- provider_call_count = 0;
- live_kb_write_count = 0;
- failure_count = 0.

The harness validates bearer-token auth with a runtime token hash, requires
agent/workspace/reviewer/request/role headers on protected endpoints, and emits
one audit event for allowed, denied, and policy-refusal requests. The smoke also
checks that audit output does not contain the runtime token, bearer header, raw
questions, or raw source text.

## 10. Open Decisions

- Which secret store and token issuer will be used for private staging?
- Which private ingress pattern should be used: VPN-only, internal reverse
  proxy, or localhost tunnel for a single reviewer?
- Who is the initial reviewer for `pending_human_review` locator labels?
- Whether audit retention remains 30 days or must follow a stricter legal
  schedule.
