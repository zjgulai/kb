---
title: "Consultant Role KB Runtime Config Redacted Fixture Smoke"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant_role_kb_staging_runtime_config_preflight_20260619.py"
  - "shared/governance/consultant-agent/staging-runtime-config.schema-20260619.json"
scope: "redacted fixture validation for future shared-staging runtime configuration"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "fixture smoke only; no external configuration applied"
---

# Consultant Role KB Runtime Config Redacted Fixture Smoke

## 0. Boundary

This smoke validates runtime configuration status handling with temporary
fixtures. It does not configure secrets, approve security controls, deploy
shared staging, call a provider, or ingest into a live KB. Scenario outputs
record status and counts only; raw secret-like values and private contacts are
not retained.

## 1. Result

| field | value |
|---|---:|
| ok | true |
| scenario_count | 3 |
| pass_count | 3 |
| fail_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Scenarios

| scenario | ok | runtime_config_ready | blocker_count | secret_like_input_count | private_contact_like_input_count | redaction_leak_count |
|---|---:|---:|---:|---:|---:|---:|
| default_missing_config | true | false | 4 | 0 | 0 | 0 |
| redacted_ready_fixture | true | true | 0 | 0 | 0 | 0 |
| secret_like_rejected_fixture | true | false | 3 | 1 | 1 | 0 |

## 3. Interpretation

Fact: the default configuration remains blocked.

Fact: a fully redacted ready fixture can pass runtime-config checks without
logging raw secret values or private contact details.

Fact: a secret-like/private-contact fixture remains blocked and the raw values
are not emitted in the smoke output.

Boundary: even a ready redacted fixture is not a security approval, not an
external configuration action, and not a shared-staging deployment.
