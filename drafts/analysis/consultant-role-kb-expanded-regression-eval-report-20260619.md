---
title: "Consultant Role KB Expanded Regression Eval Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-expanded-cards-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
scope: "local regression eval for expanded consultant role KB cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local regression only; no live KB ingestion"
---

# Consultant Role KB Expanded Regression Eval Report

## 0. Boundary

This eval uses the expanded local cards and local BGE + source-prior reranking. It does not call a provider, ingest into a live KB, or prove production readiness.

## 1. Metrics

| metric | value |
|---|---:|
| indexed_card_count | 150 |
| eval_count | 50 |
| answerable_eval_count | 48 |
| all_eval source_recall@1 | 0.88 |
| all_eval source_recall@5 | 0.96 |
| all_eval anchored_citation@1 | 0.88 |
| all_eval anchored_citation@5 | 0.96 |
| answerable_eval anchored_citation@1 | 0.9167 |
| answerable_eval anchored_citation@5 | 1.0 |
| source_only_citation_violation_count | 0 |
| gate_threshold_pass | true |

## 2. Category Metrics

| category | count | source@1 | source@5 | anchored_citation@1 | anchored_citation@5 |
|---|---:|---:|---:|---:|---:|
| deliverable_workflow | 10 | 0.9 | 1.0 | 0.9 | 1.0 |
| diagnostic_planning | 10 | 1.0 | 1.0 | 1.0 | 1.0 |
| methodology_selection | 10 | 0.8 | 1.0 | 0.8 | 1.0 |
| refusal_unknown | 10 | 0.7 | 0.8 | 0.7 | 0.8 |
| source_lookup | 10 | 1.0 | 1.0 | 1.0 | 1.0 |

## 3. Answerable-Only Category Metrics

This table excludes eval items with no allowed registered source, because source recall is not the right metric for deliberate refusal/no-source prompts.

| category | count | source@1 | source@5 | anchored_citation@1 | anchored_citation@5 |
|---|---:|---:|---:|---:|---:|
| deliverable_workflow | 10 | 0.9 | 1.0 | 0.9 | 1.0 |
| diagnostic_planning | 10 | 1.0 | 1.0 | 1.0 | 1.0 |
| methodology_selection | 10 | 0.8 | 1.0 | 0.8 | 1.0 |
| refusal_unknown | 8 | 0.875 | 1.0 | 0.875 | 1.0 |
| source_lookup | 10 | 1.0 | 1.0 | 1.0 | 1.0 |

## 4. Remaining Answerable Top1 Failures

- `CONSULT-EVAL-014` expected `['SRC-CONSULT-009']`, top3 `[{'source_id': 'SRC-CONSULT-008', 'locator': 'page:29'}, {'source_id': 'SRC-CONSULT-009', 'locator': 'page:19'}, {'source_id': 'SRC-CONSULT-002', 'locator': 'slide:62'}]`.
- `CONSULT-EVAL-017` expected `['SRC-CONSULT-012']`, top3 `[{'source_id': 'SRC-CONSULT-002', 'locator': 'slide:18'}, {'source_id': 'SRC-CONSULT-012', 'locator': 'page:19'}, {'source_id': 'SRC-CONSULT-010', 'locator': 'page:19'}]`.
- `CONSULT-EVAL-038` expected `['SRC-CONSULT-004', 'SRC-CONSULT-007']`, top3 `[{'source_id': 'SRC-CONSULT-002', 'locator': 'slide:62'}, {'source_id': 'SRC-CONSULT-004', 'locator': 'slide:8'}, {'source_id': 'SRC-CONSULT-005', 'locator': 'paragraph:6'}]`.
- `CONSULT-EVAL-047` expected `['SRC-CONSULT-001', 'SRC-CONSULT-006', 'SRC-CONSULT-014']`, top3 `[{'source_id': 'SRC-CONSULT-005', 'locator': 'paragraph:33'}, {'source_id': 'SRC-CONSULT-002', 'locator': 'slide:101'}, {'source_id': 'SRC-CONSULT-009', 'locator': 'page:19'}]`.

## 5. Interpretation

Fact: the expanded set preserves unit-level locators in retrieved results.

Inference: expansion can proceed as a local draft artifact if answer-trace also remains green.

Unknown: this is still not human-approved citation precision and not production answer quality.
