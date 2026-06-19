---
title: "Consultant Role KB Shared Staging Runbook"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "agents/consultant-agent/runtime/staging_auth_audit.py"
  - "drafts/analysis/consultant-role-kb-staging-auth-audit-design-20260619.md"
  - "drafts/analysis/consultant-role-kb-shared-staging-readiness-preflight-20260619.md"
  - "drafts/analysis/consultant-role-kb-security-staging-control-workflow-20260619.md"
scope: "operator runbook for a future security-approved no-provider shared staging pilot"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "draft runbook only; not approved for shared staging deployment"
---

# Consultant Role KB Shared Staging Runbook

## 0. Boundary

This runbook is a draft operating procedure for a future shared staging pilot.
It does not approve staging, does not deploy a service, does not call a
provider, does not ingest into a live KB, and does not approve source licensing
or human-gold labels.

## 1. Required Approvals Before Use

Do not run shared staging until all items are explicit and recorded:

| gate | required evidence |
|---|---|
| legal/source-owner clearance | recorded decision that staged retrieval may use the selected corpus |
| human locator labels | reviewer decisions recorded before claiming human-gold metrics |
| security owner | named staging owner and rollback owner |
| network boundary | VPN, internal reverse proxy, or localhost tunnel approved |
| security control decisions | all rows in `security-staging-control-decisions.template-20260619.jsonl` approved |
| external secrets | token hash configured outside Git |
| external audit storage | append-only path outside the repository |
| rate limiting | private ingress or middleware rate limit configured |
| provider boundary | provider calls remain disabled unless separately approved |
| live write boundary | live KB writes remain disabled unless separately approved |

## 2. Environment Contract

Required runtime environment variables:

| variable | purpose | repository rule |
|---|---|---|
| `KB_STAGING_AUTH_TOKEN_SHA256` | SHA-256 hash of bearer token | hash only; never commit raw token |
| `KB_STAGING_AUDIT_PATH` | append-only audit JSONL path | must resolve outside this repository |
| `KB_STAGING_RATE_LIMIT_CONFIGURED` | operator assertion for ingress/middleware limit | value only records configuration status |
| `KB_STAGING_ROLLBACK_OWNER` | accountable owner for stop/rollback | do not store private contact details in repo |

Required security decision artifacts:

| artifact | purpose |
|---|---|
| `shared/governance/consultant-agent/security-staging-control-review.queue-20260619.csv` | reviewer queue for staging controls |
| `shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl` | pending decision template; must be filled outside raw secret values |
| `tmp/consultant-role-kb-security-staging-control-validation-20260619.json` | validation consumed by the shared-staging preflight |

Optional runtime environment variables:

| variable | purpose |
|---|---|
| `KB_STAGING_HOST` | bind host; default remains `127.0.0.1` |
| `KB_STAGING_PORT` | bind port; choose an internal-only port |

## 3. Preflight

Run the local preflight before any shared staging start:

```bash
python3 tmp/consultant_role_kb_shared_staging_readiness_preflight_20260619.py
```

Expected result before approvals is `ready_for_shared_staging=false`. Treat
that as correct fail-closed behavior.

Shared staging can proceed only when the preflight produces
`ready_for_shared_staging=true` after the required human, legal/source-owner,
security, and external runtime configuration gates are recorded.

## 4. Start Command

Only after approval and preflight readiness:

```bash
python3 agents/consultant-agent/runtime/staging_auth_audit.py \
  --host "${KB_STAGING_HOST:-127.0.0.1}" \
  --port "${KB_STAGING_PORT:-8765}"
```

The default host is local-only. A shared pilot needs an approved private ingress
in front of the service; do not expose the process as a public anonymous
endpoint.

## 5. Smoke Checks

After start, run a protected retrieval smoke through the approved ingress:

| check | expected |
|---|---|
| `/health` | reports `record_count=800` and `staging_deployment=not deployed` if running locally |
| `/retrieve` with valid token and reviewer role | HTTP 200 and no raw source text |
| `/retrieve` without token | HTTP 401 and denied audit event |
| `/eval/label-seed` as `retrieval_reader` | HTTP 403 and denied audit event |
| audit JSONL | one event per protected request |
| provider/live write counters | both remain 0 |

## 6. Rollback

Rollback means immediately disabling shared access and stopping the process.

Minimum rollback sequence:

1. Disable private ingress route or tunnel.
2. Stop the running `staging_auth_audit.py` process.
3. Rotate bearer token and update only the external secret store.
4. Preserve audit logs in the external append-only path.
5. Record rollback reason, owner, time, and affected request IDs in the review
   packet or incident log.

Do not delete audit logs as part of rollback.

## 7. Stop Conditions

Stop shared staging immediately if any condition appears:

| condition | action |
|---|---|
| raw source text appears in API response or audit logs | stop service and preserve logs |
| provider_call_count becomes non-zero without approval | stop service |
| live_kb_write_count becomes non-zero without approval | stop service |
| public anonymous endpoint is exposed | disable ingress |
| invalid token request does not return 401 | stop service |
| role-forbidden endpoint does not return 403 | stop service |
| audit write fails or misses protected requests | stop service |

## 8. Current State

Current state remains blocked for shared staging. The local harness, security
decision workflow, and preflight are validation artifacts only.
