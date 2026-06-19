---
title: "Consultant Role KB Legal Security Official Decision Promotion Preflight"
status: "draft"
created_at: "2026-06-20"
source_documents:
  - "tmp/consultant-role-kb-reviewer-questionnaire-derived-legal-decisions-20260619.jsonl"
  - "tmp/consultant-role-kb-reviewer-questionnaire-derived-security-decisions-20260619.jsonl"
  - "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
  - "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"
scope: "fail-closed preflight before accepting legal/source-owner and security reviewer candidates into official decision records"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "preflight only; official decision templates unchanged"
---

# Consultant Role KB Legal Security Official Decision Promotion Preflight

## 0. Boundary

This preflight validates whether legal/source-owner and security candidate
JSONL files are safe to accept into their official decision records. It does
not overwrite official templates, approve sources, approve controls, configure
secrets, deploy shared staging, call a provider, or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| status | blocked |
| blocker_count | 5 |
| changed_row_count | 0 |
| candidate_non_pending_count | 0 |
| legal_selected_approved_internal_staging_count | 0/80 |
| security_approved_control_count | 0/8 |
| shared_staging_ready_after_candidate | false |
| official_template_write_count | 0 |
| approval_effect_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Promotion Checklist

- Checklist CSV: `shared/governance/consultant-agent/legal-security-official-decision-promotion-checklist-20260620.csv`
- Legal candidate: `tmp/consultant-role-kb-reviewer-questionnaire-derived-legal-decisions-20260619.jsonl`
- Security candidate: `tmp/consultant-role-kb-reviewer-questionnaire-derived-security-decisions-20260619.jsonl`

## 3. Current Blockers

```json
[
  "no_reviewed_legal_or_security_candidate_decisions",
  "no_candidate_changes_to_accept",
  "legal_selected_sources_still_pending",
  "security_controls_still_pending",
  "explicit_acceptance_authorization_missing"
]
```

## 4. Acceptance Rule

The preflight becomes acceptance-ready only when candidate files pass the
existing legal/security validators, contain reviewed non-pending changes, keep
source/control ID sets aligned with official templates, and the operator
supplies explicit authorization:

```bash
KB_LEGAL_SECURITY_DECISION_PROMOTION_ACCEPTANCE=accept-reviewed-legal-security-candidate python3 tmp/consultant_role_kb_legal_security_official_decision_promotion_preflight_20260620.py
```

Boundary: even an authorized ready preflight is evidence for acceptance
readiness only. The official decision files must be updated by a later
deliberate, reviewed write step.
