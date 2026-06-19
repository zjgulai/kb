---
title: "Consultant Role KB Staging Runtime Config Preflight"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/governance/consultant-agent/staging-runtime-config.template-20260619.json"
  - "shared/governance/consultant-agent/staging-runtime-config.schema-20260619.json"
scope: "external runtime configuration status before any future shared staging start"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local preflight only; no external configuration applied"
---

# Consultant Role KB Staging Runtime Config Preflight

## 0. Boundary

This preflight records external runtime configuration status only. It does not
configure secrets, approve security controls, deploy staging, call a provider,
or ingest into a live KB. Secret values, raw tokens, passwords, private keys,
and private contact details must remain outside repository artifacts.

## 1. Result

| field | value |
|---|---:|
| runtime_config_ready | false |
| status | blocked |
| blocker_count | 4 |
| failure_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |
| secret_value_logged | false |
| private_contact_detail_logged | false |

## 2. Runtime Status

| item | status |
|---|---|
| auth_token_hash | `missing` |
| audit_path | `missing` |
| rate_limit | `missing` |
| rollback_owner | `missing` |
| private_ingress | `localhost_only` |

## 3. Blockers

| blocker |
|---|
| `external_auth_token_hash_not_configured` |
| `external_audit_path_not_configured` |
| `rate_limit_not_configured` |
| `rollback_owner_not_recorded` |

## 4. Tencent Cloud Lighthouse Note

Tencent Cloud Lighthouse can be a future runtime target, but repository
artifacts must still contain only redacted status. Any raw `consult/` source
upload, credential material, private ingress configuration, or service start
requires separate legal, security, and deployment approval.
