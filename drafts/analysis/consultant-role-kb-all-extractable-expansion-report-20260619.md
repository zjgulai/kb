---
title: "Consultant Role KB All-Extractable Expansion Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv"
scope: "local expansion to all currently extractable consultant-role sources"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local batch cards only; no live KB ingestion"
---

# Consultant Role KB All-Extractable Expansion Report

## 0. Boundary

This is local draft expansion only. It does not call a provider, ingest into a
live KB, deploy production code, approve source licensing, or reproduce long
source text.

## 1. Outputs

| artifact | path |
|---|---|
| source selection | `drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv` |
| all-extractable cards | `tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl` |
| gate eval | `tmp/consultant-role-kb-all-extractable-card-gate-eval-20260619.json` |

## 2. Gate Metrics

| metric | value |
|---|---:|
| selected_source_count | 78 |
| card_count | 780 |
| metadata_completeness | 1.0 |
| unit_locator_coverage | 1.0 |
| source_only_citation_violation_count | 0 |
| long_text_violation_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |
| skipped_duplicate_sources | 1 |
| skipped_insufficient_unit_sources | 2 |

## 3. Cards By Type

| card_type | card_count |
|---|---:|
| client_development_card | 20 |
| consult_method_card | 250 |
| consulting_kpi_card | 30 |
| deliverable_template_card | 70 |
| diagnostic_dimension_card | 110 |
| industry_analysis_card | 300 |

## 4. Skipped Sources

| source_id | reason | extractable_unit_count |
|---|---|---:|
| SRC-CONSULT-016 | duplicate_secondary |  |
| SRC-CONSULT-030 | insufficient_extractable_units | 0 |
| SRC-CONSULT-031 | insufficient_extractable_units | 0 |

## 5. Interpretation

Fact: all currently extractable non-duplicate sources were converted into local
draft cards with complete required metadata and unit locators.

Inference: this is the current full typed-card extraction ceiling under the
existing local parser/loader stack.

Unknown: legal/source-owner clearance, human-gold citation precision, and
online production answer quality are still not proven.
