---
title: "KB P1 Eval Set 50 Index"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/kb-p1-eval-set-template.md"
  - "drafts/analysis/kb-p1-scm-source-register-candidates.md"
scope: "50-question draft eval set index for P1 readonly replenishment-agent validation"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB P1 Eval Set 50 Index

## 0. Boundary

This file indexes the 50-question draft eval set. It does not run evaluation, call providers, or claim that source evidence is ready. Because the source register remains `source_intake_pending`, many expected behaviors require the Agent to answer `unknown`, refuse unsafe actions, or ask for owner-reviewed evidence.

Machine-editable JSONL:

`drafts/analysis/kb-p1-eval-set-50.draft.jsonl`

## 1. Distribution

| category | count | eval IDs |
|---|---:|---|
| source_lookup | 10 | P1-EVAL-001 to P1-EVAL-010 |
| metric_reasoning | 10 | P1-EVAL-011 to P1-EVAL-020 |
| sop_retrieval | 10 | P1-EVAL-021 to P1-EVAL-030 |
| cross_domain_reasoning | 10 | P1-EVAL-031 to P1-EVAL-040 |
| refusal_unknown | 10 | P1-EVAL-041 to P1-EVAL-050 |

## 2. Current Status

All questions are `draft`. Promotion to `ready_for_poc` requires the referenced sources to be promoted in the source register first.
