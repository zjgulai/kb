---
title: "Consultant Role KB Human Label Candidate Promotion Preflight"
status: "draft"
created_at: "2026-06-20"
source_documents:
  - "tmp/consultant-role-kb-human-label-questionnaire-derived-decisions-20260619.jsonl"
  - "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
scope: "fail-closed preflight before accepting reviewed human-label candidates into the official decision record"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "preflight only; official decision template unchanged"
---

# Consultant Role KB Human Label Candidate Promotion Preflight

## 0. Boundary

This preflight validates whether a human-label candidate JSONL is safe to
accept into the official decision record. It does not overwrite the official
template, create human-gold labels, call a provider, deploy staging, or ingest
into a live KB.

## 1. Result

| field | value |
|---|---:|
| status | blocked |
| blocker_count | 4 |
| candidate_decision_count | 50 |
| candidate_pending_count | 50 |
| candidate_non_pending_count | 0 |
| candidate_approved_count | 0 |
| changed_row_count | 0 |
| full_human_gold_ready | false |
| human_gold_metrics_claimable | false |
| official_template_write_count | 0 |
| approval_effect_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Promotion Checklist

- Checklist CSV: `shared/eval/consultant-agent/human-gold-locator-label-promotion-checklist-20260620.csv`
- Candidate: `tmp/consultant-role-kb-human-label-questionnaire-derived-decisions-20260619.jsonl`
- Official template: `shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl`

## 3. Current Blockers

```json
[
  "no_reviewed_candidate_decisions",
  "candidate_has_pending_decisions",
  "candidate_not_ready_for_human_gold_metrics",
  "explicit_acceptance_authorization_missing"
]
```

## 4. Acceptance Rule

The preflight is ready only when the candidate passes schema/logic validation,
the decision ID set matches the official template, all 50 labels are reviewed
and approved or overridden, no labels remain pending, and the operator supplies
explicit acceptance authorization:

```bash
KB_HUMAN_LABEL_PROMOTION_ACCEPTANCE=accept-reviewed-human-label-candidate python3 tmp/consultant_role_kb_human_label_candidate_promotion_preflight_20260620.py
```

Boundary: even an authorized ready preflight is evidence for acceptance
readiness; the official decision file must be updated by a deliberate,
reviewed step, not by this preflight script.
