---
title: "Consultant Role KB Batch-30 Expansion Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-batch30-source-selection-20260619.csv"
scope: "local batch expansion from 15 to 30 consultant-role sources"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local batch cards only; no live KB ingestion"
---

# Consultant Role KB Batch-30 Expansion Report

## 0. Boundary

This is local draft expansion only. It does not call a provider, ingest into a
live KB, deploy production code, approve source licensing, or reproduce long
source text.

## 1. Outputs

| artifact | path |
|---|---|
| source selection | `drafts/analysis/consultant-role-kb-batch30-source-selection-20260619.csv` |
| batch-30 cards | `tmp/consultant-role-kb-batch30-cards-20260619.jsonl` |
| gate eval | `tmp/consultant-role-kb-batch30-card-gate-eval-20260619.json` |

## 2. Gate Metrics

| metric | value |
|---|---:|
| source_count | 30 |
| card_count | 300 |
| metadata_completeness | 1.0 |
| unit_locator_coverage | 1.0 |
| source_only_citation_violation_count | 0 |
| long_text_violation_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 3. Cards By Type

| card_type | card_count |
|---|---:|
| client_development_card | 20 |
| consult_method_card | 120 |
| consulting_kpi_card | 20 |
| deliverable_template_card | 70 |
| diagnostic_dimension_card | 60 |
| industry_analysis_card | 10 |

## 4. Interpretation

Fact: the batch-30 expansion produced source-balanced cards with complete
required metadata and unit locators.

Inference: batch-30 can proceed to card QA and local retrieval/citation
regression as a draft artifact.

Unknown: legal/source-owner clearance and human-gold citation precision are
still not proven.
