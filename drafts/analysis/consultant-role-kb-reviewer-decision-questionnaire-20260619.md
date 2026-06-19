---
title: "Consultant Role KB Reviewer Decision Questionnaire"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/governance/consultant-agent/clearance-execution-checklist-20260619.csv"
  - "shared/governance/consultant-agent/legal-source-owner-review.queue-20260619.csv"
  - "shared/governance/consultant-agent/security-staging-control-review.queue-20260619.csv"
scope: "questionnaire pack for legal/source-owner and security/operations reviewers"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "questionnaire only; no approvals recorded"
---

# Consultant Role KB Reviewer Decision Questionnaire

## 0. Boundary

This pack turns the clearance checklist into reviewer-friendly questions. It
does not approve any source, approve any security control, edit the official
decision templates, configure secrets, deploy shared staging, call a provider,
or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| questionnaire_ready | true |
| questionnaire_row_count | 88 |
| legal_question_count | 80 |
| security_question_count | 8 |
| approval_effect_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. How To Use

1. Use `shared/governance/consultant-agent/reviewer-decision-questionnaire-20260619.csv` as the human-facing question list.
2. Copy final reviewer decisions into the official JSONL templates listed in the `official_template_path` column.
3. Keep secret values, private keys, raw tokens, passwords, and private contact details outside the repository.
4. Re-run the manual intake and shared-staging preflight after official decision files are filled.

## 3. Choice Mapping

Legal/source-owner choices map to the official legal decision schema:

- `approve_internal_staging_retrieval`: approve internal no-provider staging retrieval only.
- `approve_local_only`: keep source in local draft workflows only.
- `quarantine_source`: remove from staging path until discussion is resolved.
- `reject_source`: reject source for this KB runtime.
- `needs_discussion`: keep blocked pending discussion.
- `pending_review`: no decision yet.

Security/operations choices map to the official security control schema:

- `approved`: control is approved; external config evidence still stays outside Git.
- `rejected`: control is not accepted.
- `needs_discussion`: reviewer needs more information.
- `pending_review`: no decision yet.

## 4. Validation Commands

```bash
python3 tmp/consultant_role_kb_manual_decision_intake_preflight_20260619.py
python3 tmp/consultant_role_kb_shared_staging_readiness_preflight_20260619.py || true
```

Expected current state before real reviewer input: shared staging remains blocked
because official legal/source-owner and security/operations decisions are still
pending.
