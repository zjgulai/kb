---
title: "Consultant Role KB Legal Security Official Decision Apply Gate"
status: "draft"
created_at: "2026-06-20"
source_documents:
  - "tmp/consultant-role-kb-legal-security-official-decision-promotion-preflight-20260620.json"
  - "tmp/consultant-role-kb-reviewer-questionnaire-derived-legal-decisions-20260619.jsonl"
  - "tmp/consultant-role-kb-reviewer-questionnaire-derived-security-decisions-20260619.jsonl"
scope: "guarded write gate for official legal/source-owner and security decision records"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "dry-run blocked unless all explicit gates pass"
---

# Consultant Role KB Legal Security Official Decision Apply Gate

## 0. Boundary

This apply gate runs the promotion preflight and blocks by default. It does not
write official decision templates unless the candidate files are ready, the
promotion acceptance environment variable is set, and the explicit apply mode
is set. It does not configure secrets, deploy shared staging, call a provider,
or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| status | blocked |
| write_performed | false |
| apply_mode | dry_run |
| blocker_count | 4 |
| official_template_write_count | 0 |
| approval_effect_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Current Blockers

```json
[
  "promotion_preflight_not_ready",
  "promotion_acceptance_authorization_missing",
  "promotion_authorization_env_missing",
  "apply_mode_authorization_missing"
]
```

## 3. Write Command

Only after reviewed candidates pass preflight:

```bash
KB_LEGAL_SECURITY_DECISION_PROMOTION_ACCEPTANCE=accept-reviewed-legal-security-candidate \
KB_LEGAL_SECURITY_DECISION_APPLY_MODE=write-official-decision-templates \
python3 tmp/consultant_role_kb_legal_security_official_decision_apply_gate_20260620.py
```

Boundary: this command updates only the two official decision JSONL templates.
It is not legal/source-owner clearance unless the candidate itself contains
valid reviewer approvals, and it is not shared-staging deployment.
