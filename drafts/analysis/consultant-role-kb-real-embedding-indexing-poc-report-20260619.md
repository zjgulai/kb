---
title: "Consultant Role KB Real Local Embedding Indexing PoC Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-card-samples-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
scope: "real local embedding and indexing PoC for consultant role KB typed cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local PoC only; no live KB ingestion"
---

# Consultant Role KB Real Local Embedding Indexing PoC Report

## 0. Boundary

This PoC uses a local cached embedding model through local Python dependencies. It does not call a provider, does not deploy a service, and does not write to a live KB.

The index is a local artifact for evaluating typed-card retrieval plumbing and source recall. It is not production-ready.

## 1. Model Lock

| field | value |
|---|---|
| model_id | `BAAI/bge-small-zh-v1.5` |
| model_snapshot | `7999e1d3359715c523056ef9478215996d62a620` |
| model_license | `MIT` |
| embedding_dimension | 512 |
| query_instruction | `为这个句子生成表示以用于检索相关文章：` |
| runtime_python | `/opt/homebrew/opt/python@3.12/bin/python3.12` |
| torch_version | `2.10.0` |
| transformers_version | `5.0.0` |
| sentence_transformers_version | `5.2.2` |

## 2. Inputs And Outputs

| artifact | path |
|---|---|
| input cards | `tmp/consultant-role-kb-card-samples-20260619.jsonl` |
| eval set | `drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl` |
| source register | `drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv` |
| local index metadata | `tmp/consultant-role-kb-bge-small-zh-index-20260619.json` |
| retrieval eval result | `tmp/consultant-role-kb-bge-small-zh-retrieval-eval-20260619.json` |

## 3. Metrics

| metric | value |
|---|---:|
| indexed_card_count | 33 |
| eval_count | 50 |
| elapsed_seconds | 1.104 |
| source_recall_at_1 | 0.66 |
| source_recall_at_5 | 0.9 |
| hash_baseline_source_recall_at_1 | 0.76 |
| hash_baseline_source_recall_at_5 | 0.86 |

## 4. Category Metrics

| category | count | source_recall_at_1 | source_recall_at_5 |
|---|---:|---:|---:|
| deliverable_workflow | 10 | 0.6 | 0.9 |
| diagnostic_planning | 10 | 0.9 | 1.0 |
| methodology_selection | 10 | 0.7 | 0.9 |
| refusal_unknown | 10 | 0.3 | 0.7 |
| source_lookup | 10 | 0.8 | 1.0 |

## 5. Interpretation

The real local embedding path is executable with the cached BGE model and preserves typed-card metadata through indexing and retrieval eval.

This still does not prove production readiness. The eval measures source recall over 33 synthetic typed-card samples, not answer quality, citation precision, legal clearance, or live KB behavior.

`refusal_unknown` should continue to be scored with refusal-policy compliance in addition to retrieval source recall, because several refusal cases intentionally have no allowed source or test blocked-action routing.

## 6. Next Gates

1. Treat `BAAI/bge-small-zh-v1.5` with 512 dimensions as the locked P1 local embedding candidate unless a formal ADR replaces it.
2. Expand card extraction beyond 33 samples only after schema review.
3. Add citation precision checks once cards carry page/slide/sheet anchors.
4. Keep all sources at `evidence_grade=C` and `license_status=pending_legal_review`.
5. Do not promote this to production; permitted statement remains `real local embedding/indexing PoC executed`.
