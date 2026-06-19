---
title: "Consultant Role KB Anchored Retrieval Citation Eval Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-card-samples-anchored-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "tmp/consultant-role-kb-bge-source-prior-rerank-eval-20260619.json"
scope: "local anchored retrieval and citation eval for consultant role KB typed cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local PoC only; no live KB ingestion"
---

# Consultant Role KB Anchored Retrieval Citation Eval Report

## 0. Boundary

This eval uses anchored typed cards and local BGE + source-prior reranking. It does not call a provider, ingest into a live KB, or prove production readiness.

`allowed_source_ids` are used only after ranking to score eval results. The citation score is a proxy: it verifies that the retrieved typed card carries a unit-level locator, not that a human has approved the exact locator for a final answer.

## 1. Metrics

| metric | value |
|---|---:|
| indexed_card_count | 33 |
| eval_count | 50 |
| answerable_eval_count | 48 |
| all_eval source_recall@1 | 0.92 |
| all_eval source_recall@5 | 0.96 |
| all_eval anchored_citation@1 | 0.92 |
| all_eval anchored_citation@5 | 0.96 |
| answerable_eval anchored_citation@1 | 0.9583 |
| answerable_eval anchored_citation@5 | 1.0 |
| top1_has_unit_anchor | 1.0 |
| source_only_citation_violation_count | 0 |

## 2. Category Metrics

| category | count | source@1 | source@5 | anchored_citation@1 | anchored_citation@5 |
|---|---:|---:|---:|---:|---:|
| deliverable_workflow | 10 | 1.0 | 1.0 | 1.0 | 1.0 |
| diagnostic_planning | 10 | 1.0 | 1.0 | 1.0 | 1.0 |
| methodology_selection | 10 | 1.0 | 1.0 | 1.0 | 1.0 |
| refusal_unknown | 10 | 0.6 | 0.8 | 0.6 | 0.8 |
| source_lookup | 10 | 1.0 | 1.0 | 1.0 | 1.0 |

## 3. Remaining Failures

Answerable anchored-citation top1 failures:

- `CONSULT-EVAL-043` expected `['SRC-CONSULT-010', 'SRC-CONSULT-011']`, top3 `[{'source_id': 'SRC-CONSULT-004', 'locator': 'slide:3'}, {'source_id': 'SRC-CONSULT-005', 'locator': 'paragraph:7'}, {'source_id': 'SRC-CONSULT-002', 'locator': 'slide:3'}]`.
- `CONSULT-EVAL-047` expected `['SRC-CONSULT-001', 'SRC-CONSULT-006', 'SRC-CONSULT-014']`, top3 `[{'source_id': 'SRC-CONSULT-002', 'locator': 'slide:3'}, {'source_id': 'SRC-CONSULT-005', 'locator': 'paragraph:7'}, {'source_id': 'SRC-CONSULT-001', 'locator': 'slide:3'}]`.

## 4. Interpretation

The anchored eval confirms that retrieval results can carry unit-level citation locators instead of source-only references. The remaining failures are source-selection failures at rank 1, not missing-anchor failures.

This still does not prove final answer quality or human-approved citation precision. The next gate should be a small answer-trace fixture that checks whether generated answers cite the selected locator and preserve evidence boundaries.
