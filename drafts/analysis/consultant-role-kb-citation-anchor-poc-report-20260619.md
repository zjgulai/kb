---
title: "Consultant Role KB Citation Anchor PoC Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-card-samples-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
scope: "local citation anchor precision PoC for consultant role KB typed cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local PoC only; no live KB ingestion"
---

# Consultant Role KB Citation Anchor PoC Report

## 0. Boundary

This PoC adds locator anchors to existing typed-card samples. It does not ingest into a live KB, does not call a provider, does not expand extraction scope, and does not reproduce long source text.

## 1. Anchor Schema

Each card can carry `source_anchors` with:

- `source_id`
- `locator_type`: `page`, `slide`, `sheet_row`, or `paragraph`
- `locator`: for example `page:3`, `slide:5`, `sheet:Library of KPIs by Function#row:12`
- `anchor_label`: short label only, not a long source excerpt
- `matched_terms`
- `anchor_confidence`

## 2. Outputs

| artifact | path |
|---|---|
| anchored card samples | `tmp/consultant-role-kb-card-samples-anchored-20260619.jsonl` |
| anchor eval result | `tmp/consultant-role-kb-citation-anchor-eval-20260619.json` |

## 3. Citation Precision Readiness

| metric | value |
|---|---:|
| card_count | 33 |
| citation_precision_ready_count | 33 |
| citation_precision_ready_rate | 1.0 |

## 4. By Modality

| modality | card_count | ready_count | ready_rate | status_counts |
|---|---:|---:|---:|---|
| docx | 1 | 1 | 1.0 | `{"resolved": 1}` |
| pdf | 7 | 7 | 1.0 | `{"resolved": 7}` |
| pptx | 4 | 4 | 1.0 | `{"resolved": 4}` |
| xlsx | 21 | 21 | 1.0 | `{"resolved": 21}` |

## 5. Interpretation

This proves the card schema can carry citation anchors at unit granularity for the current 33-card local sample.

It still does not prove answer quality or production readiness. The next retrieval/eval run should use anchored cards and score whether retrieved citations include the expected locator, not only the expected source.

## 6. Next Gate

Run anchored retrieval/citation eval using the anchored card file. Keep `source_only` citations out of final answer scoring, because source-level citation is too coarse for this PRD gate.
