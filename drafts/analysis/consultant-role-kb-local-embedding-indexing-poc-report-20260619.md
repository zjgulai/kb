---
title: "Consultant Role KB Local Embedding Indexing PoC Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-card-samples-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
scope: "local no-provider embedding and indexing PoC for consultant role KB typed cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local PoC only; no live KB ingestion"
---

# Consultant Role KB Local Embedding Indexing PoC Report

## 0. Boundary

This PoC uses a deterministic local hash embedding and an in-memory cosine search implementation. It does not use a provider, does not download a model, does not deploy a service, and does not write to a live KB.

This is a plumbing proof for typed-card indexing and source recall. It is not evidence that final semantic retrieval quality is good enough for production.

## 1. Inputs And Outputs

| artifact | path |
|---|---|
| input cards | `tmp/consultant-role-kb-card-samples-20260619.jsonl` |
| eval set | `drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl` |
| source register | `drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv` |
| local index metadata | `tmp/consultant-role-kb-local-hash-index-20260619.json` |
| retrieval eval result | `tmp/consultant-role-kb-local-retrieval-eval-20260619.json` |

## 2. Metrics

| metric | value |
|---|---:|
| indexed_card_count | 33 |
| eval_count | 50 |
| embedding_dimension | 1024 |
| source_recall_at_1 | 0.76 |
| source_recall_at_5 | 0.86 |

## 3. Category Metrics

| category | count | source_recall_at_1 | source_recall_at_5 |
|---|---:|---:|---:|
| deliverable_workflow | 10 | 0.9 | 0.9 |
| diagnostic_planning | 10 | 0.8 | 0.9 |
| methodology_selection | 10 | 0.8 | 0.9 |
| refusal_unknown | 10 | 0.4 | 0.6 |
| source_lookup | 10 | 0.9 | 1.0 |

## 4. Interpretation

The local index path is mechanically viable: typed cards can be embedded, indexed, searched, and evaluated by source recall while preserving `workspace`, `source_id`, `evidence_grade`, and blocked-action metadata.

Because the embedding is a deterministic hash embedding, any misses or hits should be treated as local plumbing evidence only. A future quality gate should replace this with the selected local embedding model and rerun the same eval set.

The `refusal_unknown` category has lower source recall because some refusal cases intentionally have no allowed source or primarily test policy routing rather than source retrieval. Future eval should score refusal-policy compliance separately from source recall.

## 5. Next Gates

1. Select a real local embedding model and lock dimensions before any durable index.
2. Re-run this eval with the real embedding model and compare source recall, citation precision, and refusal quality.
3. Keep all source rows at `evidence_grade=C` and `license_status=pending_legal_review` until legal/source-owner review is complete.
4. Do not promote this to production; permitted statement remains `local embedding/indexing PoC executed`.
