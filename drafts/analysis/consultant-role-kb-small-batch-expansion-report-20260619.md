---
title: "Consultant Role KB Small-Batch Expansion Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
  - "drafts/analysis/consultant-role-kb-small-batch-expansion-gate-20260619.md"
scope: "controlled local expansion from 33 consultant-role cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local expanded cards only; no live KB ingestion"
---

# Consultant Role KB Small-Batch Expansion Report

## 0. Boundary

This expansion is local draft work only. It does not call a provider, ingest into a live KB, deploy production code, or approve source licensing. Cards preserve source metadata and unit locators while avoiding long source text reproduction.

## 1. Outputs

| artifact | path |
|---|---|
| expanded cards | `tmp/consultant-role-kb-expanded-cards-20260619.jsonl` |
| gate eval | `tmp/consultant-role-kb-expanded-card-gate-eval-20260619.json` |

## 2. Gate Metrics

| metric | value |
|---|---:|
| card_count | 150 |
| metadata_completeness | 1.0 |
| unit_locator_coverage | 1.0 |
| source_only_citation_violation_count | 0 |
| long_text_violation_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 3. Cards By Source

| source_id | card_count |
|---|---:|
| SRC-CONSULT-001 | 10 |
| SRC-CONSULT-002 | 10 |
| SRC-CONSULT-003 | 10 |
| SRC-CONSULT-004 | 10 |
| SRC-CONSULT-005 | 10 |
| SRC-CONSULT-006 | 10 |
| SRC-CONSULT-007 | 10 |
| SRC-CONSULT-008 | 10 |
| SRC-CONSULT-009 | 10 |
| SRC-CONSULT-010 | 10 |
| SRC-CONSULT-011 | 10 |
| SRC-CONSULT-012 | 10 |
| SRC-CONSULT-013 | 10 |
| SRC-CONSULT-014 | 10 |
| SRC-CONSULT-015 | 10 |

## 4. Cards By Type

| card_type | card_count |
|---|---:|
| consult_method_card | 50 |
| consulting_kpi_card | 20 |
| deliverable_template_card | 40 |
| diagnostic_dimension_card | 30 |
| terminology_crosswalk_card | 10 |

## 5. Interpretation

Fact: the controlled expansion produced source-balanced cards with complete required metadata and unit locators.

Inference: the expanded set is ready for local retrieval/citation regression, while still remaining a draft evidence artifact.

Unknown: answer quality and source-selection quality must be checked by the expanded retrieval/citation eval and answer-trace fixture before any PRD addendum or live KB planning.
