---
title: "Consultant Role KB All-Extractable Regression Eval Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
scope: "local regression eval for all-extractable consultant role KB cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local regression only; no live KB ingestion"
---

# Consultant Role KB All-Extractable Regression Eval Report

## 0. Boundary

This eval uses the all-extractable local cards and local BGE + source-prior reranking. It does not call a provider, ingest into a live KB, or prove production readiness.

## 1. Metrics

| metric | value |
|---|---:|
| indexed_card_count | 800 |
| eval_count | 50 |
| answerable_eval_count | 48 |
| all_eval source_recall@1 | 0.94 |
| all_eval source_recall@5 | 0.96 |
| all_eval anchored_citation@1 | 0.94 |
| all_eval anchored_citation@5 | 0.96 |
| answerable_eval anchored_citation@1 | 0.9792 |
| answerable_eval anchored_citation@5 | 1.0 |
| source_only_citation_violation_count | 0 |
| gate_threshold_pass | true |

## 2. Category Metrics

| category | count | source@1 | source@5 | anchored_citation@1 | anchored_citation@5 |
|---|---:|---:|---:|---:|---:|
| deliverable_workflow | 10 | 1.0 | 1.0 | 1.0 | 1.0 |
| diagnostic_planning | 10 | 1.0 | 1.0 | 1.0 | 1.0 |
| methodology_selection | 10 | 0.9 | 1.0 | 0.9 | 1.0 |
| refusal_unknown | 10 | 0.8 | 0.8 | 0.8 | 0.8 |
| source_lookup | 10 | 1.0 | 1.0 | 1.0 | 1.0 |

## 3. Answerable-Only Category Metrics

This table excludes eval items with no allowed registered source, because source recall is not the right metric for deliberate refusal/no-source prompts.

| category | count | source@1 | source@5 | anchored_citation@1 | anchored_citation@5 |
|---|---:|---:|---:|---:|---:|
| deliverable_workflow | 10 | 1.0 | 1.0 | 1.0 | 1.0 |
| diagnostic_planning | 10 | 1.0 | 1.0 | 1.0 | 1.0 |
| methodology_selection | 10 | 0.9 | 1.0 | 0.9 | 1.0 |
| refusal_unknown | 8 | 1.0 | 1.0 | 1.0 | 1.0 |
| source_lookup | 10 | 1.0 | 1.0 | 1.0 | 1.0 |

## 4. Remaining Answerable Top1 Failures

- `CONSULT-EVAL-016` expected `['SRC-CONSULT-011']`, top3 `[{'source_id': 'SRC-CONSULT-010', 'locator': 'page:6'}, {'source_id': 'SRC-CONSULT-011', 'locator': 'page:15'}, {'source_id': 'SRC-CONSULT-002', 'locator': 'slide:14'}]`.

## 5. Interpretation

Fact: the expanded set preserves unit-level locators in retrieved results.

Inference: expansion can proceed as a local draft artifact if answer-trace also remains green.

Unknown: this is still not human-approved citation precision and not production answer quality.
