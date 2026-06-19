---
title: "Consultant Role KB Rerank Source Prior PoC Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-card-samples-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "tmp/consultant-role-kb-bge-small-zh-retrieval-eval-20260619.json"
scope: "local rerank and source-prior PoC for consultant role KB retrieval"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local PoC only; no live KB ingestion"
---

# Consultant Role KB Rerank Source Prior PoC Report

## 0. Boundary

This PoC reranks local BGE retrieval scores with deterministic source/card priors. It does not call a provider, deploy a service, ingest into a live KB, or use eval labels during ranking.

`allowed_source_ids` are used only after ranking to score recall. This avoids label leakage.

## 1. Rerank Method

Base vector score:

- `BAAI/bge-small-zh-v1.5`
- Snapshot `7999e1d3359715c523056ef9478215996d62a620`
- Dimension `512`

Source/card priors:

- source-title, source-note, and curated source-alias keyword overlap
- exact phrase matches for consulting workflow terms
- card-type fit by eval category
- generic penalties for KPI/acronym cards when the query is not KPI/acronym-oriented

## 2. Metrics

| metric | BGE only | BGE + source prior rerank |
|---|---:|---:|
| all_eval source_recall@1 | 0.66 | 0.92 |
| all_eval source_recall@5 | 0.9 | 0.96 |
| answerable_eval source_recall@1 | not separately reported in BGE baseline | 0.9583 |
| answerable_eval source_recall@5 | not separately reported in BGE baseline | 1.0 |
| hash_baseline all_eval source_recall@1 | 0.76 | n/a |
| hash_baseline all_eval source_recall@5 | 0.86 | n/a |

Counts:

- indexed_card_count: 33
- eval_count: 50
- answerable_eval_count: 48
- no_allowed_source_eval_count: 2
- answerable_top1_failures: 2
- answerable_top5_failures: 0

## 3. Category Metrics

| category | count | source_recall@1 | source_recall@5 |
|---|---:|---:|---:|
| deliverable_workflow | 10 | 1.0 | 1.0 |
| diagnostic_planning | 10 | 1.0 | 1.0 |
| methodology_selection | 10 | 1.0 | 1.0 |
| refusal_unknown | 10 | 0.6 | 0.8 |
| source_lookup | 10 | 1.0 | 1.0 |

## 4. Interpretation

The rerank/source-prior layer improves retrieval source recall in this local sample, especially by reducing generic KPI/acronym cards that were over-ranked for non-KPI questions.

This is still not production evidence. It uses a small 33-card synthetic sample and measures source recall only. It does not prove answer quality, citation precision, license clearance, or live KB behavior.

## 5. Remaining Failures

Answerable top1 failures remain useful for next iteration:

- `CONSULT-EVAL-043` expected `['SRC-CONSULT-010', 'SRC-CONSULT-011']`, top3 `['SRC-CONSULT-004', 'SRC-CONSULT-005', 'SRC-CONSULT-002']`.
- `CONSULT-EVAL-047` expected `['SRC-CONSULT-001', 'SRC-CONSULT-006', 'SRC-CONSULT-014']`, top3 `['SRC-CONSULT-002', 'SRC-CONSULT-005', 'SRC-CONSULT-001']`.

## 6. Next Gate

Do not expand extraction yet. First add page/slide/sheet anchors to typed cards and score citation precision, because improved source recall alone does not prove answerability or citation quality.
