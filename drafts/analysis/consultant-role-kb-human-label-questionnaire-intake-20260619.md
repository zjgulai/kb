---
title: "Consultant Role KB Human Label Questionnaire Intake"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/eval/consultant-agent/human-gold-locator-label-review.questionnaire-20260619.csv"
  - "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
scope: "local conversion and validation of answered human-label questionnaire rows"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "candidate JSONL only; official human-label decisions unchanged"
---

# Consultant Role KB Human Label Questionnaire Intake

## 0. Boundary

This intake converts answered human-label questionnaire rows into a temporary
candidate decision JSONL under `tmp/`. It does not overwrite the official
decision template, create human-gold labels, call a provider, deploy staging,
or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| ok | true |
| status | valid_candidate |
| questionnaire_row_count | 50 |
| answered_response_count | 0 |
| pending_decision_count | 50 |
| approved_decision_count | 0 |
| official_template_write_count | 0 |
| approval_effect_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Candidate Output

- Candidate decisions: `tmp/consultant-role-kb-human-label-questionnaire-derived-decisions-20260619.jsonl`
- Validation: `tmp/consultant-role-kb-human-label-questionnaire-intake-validation-20260619.json`

## 3. Interpretation

Fact: with the current unfilled questionnaire, all derived decisions remain
pending and no official decision template is updated.

Boundary: candidate files under `tmp/` are not human-gold evidence until a
human reviewer accepts them and the official decision file is filled or supplied
to manual intake through a reviewed path.
