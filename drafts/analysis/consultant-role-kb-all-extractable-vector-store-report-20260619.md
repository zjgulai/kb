---
title: "Consultant Role KB All-Extractable Vector Store Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl"
  - "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/manifest.json"
scope: "durable local vector-store package for consultant-agent all-extractable cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local vector index only; no live KB ingestion"
---

# Consultant Role KB All-Extractable Vector Store Report

## 0. Boundary

This index is a local durable artifact. It does not call a provider, write into
a live KB, deploy production code, approve source licensing, or redistribute raw
source text.

## 1. Index Package

| artifact | path |
|---|---|
| manifest | `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/manifest.json` |
| records | `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/records.jsonl` |
| embeddings | `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/embeddings.float32.npy` |
| checksums | `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/checksums.json` |
| smoke | `tmp/consultant-role-kb-all-extractable-vector-store-smoke-20260619.json` |

## 2. Build Metrics

| metric | value |
|---|---:|
| indexed_card_count | 780 |
| embedding_rows | 780 |
| embedding_dimension | 512 |
| answerable_vector_source_recall@1 | 0.5833 |
| answerable_vector_source_recall@5 | 0.75 |
| answerable_reranked_source_recall@1 | 0.9583 |
| answerable_reranked_source_recall@5 | 1.0 |
| fixture_answerable_reranked_source_recall@5 | 1.0 |
| top1_unit_anchor_rate | 1.0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 3. Interpretation

Fact: the all-extractable card set now has a reusable local vector-store package
with row-aligned metadata, routing text, and normalized BGE embeddings.

Inference: the raw vector index should be used with the deterministic rerank
layer for agent retrieval; raw vector-only recall is recorded as a lower-bound
diagnostic, not the acceptance path.

Unknown: this does not prove production readiness, legal clearance, human-gold
locator precision, or provider-backed answer quality.
