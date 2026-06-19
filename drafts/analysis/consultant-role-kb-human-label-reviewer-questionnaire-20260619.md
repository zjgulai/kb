---
title: "Consultant Role KB Human Label Reviewer Questionnaire"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/eval/consultant-agent/human-gold-locator-label-review.queue-20260619.csv"
scope: "human-facing questionnaire for pending human-gold label review"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "questionnaire only; no human-gold approvals recorded"
---

# Consultant Role KB Human Label Reviewer Questionnaire

## 0. Boundary

This questionnaire supports human review of machine-seeded locator labels. It
does not approve labels, edit official decision templates, call a provider,
deploy staging, or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| questionnaire_ready | true |
| questionnaire_row_count | 50 |
| locator_question_count | 48 |
| refusal_question_count | 2 |
| approval_effect_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Use

Fill `shared/eval/consultant-agent/human-gold-locator-label-review.questionnaire-20260619.csv`
only after real human review. Then run:

```bash
python3 tmp/consultant_role_kb_human_label_questionnaire_intake_20260619.py
```

The converter writes a temporary candidate JSONL under `tmp/`; candidate files
are not human-gold evidence until accepted into the official decision file.
