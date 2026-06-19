---
title: "Consultant Role KB Card QA Validation Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-expanded-cards-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "tmp/consultant-role-kb-parser-unit-manifest-20260619.jsonl"
scope: "card QA gate for consultant-agent extraction pipeline"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local QA only; no live KB ingestion"
---

# Consultant Role KB Card QA Validation Report

## 0. Boundary

This QA pass validates local draft cards. It does not approve source licensing,
write cards to a live KB, call a provider, or deploy production.

## 1. Outputs

| artifact | path |
|---|---|
| QA result JSON | `tmp/consultant-role-kb-batch60-card-qa-validation-20260619.json` |

## 2. Gate Metrics

| metric | value |
|---|---:|
| card_count | 600 |
| metadata_completeness | 1.0 |
| registered_source_coverage | 1.0 |
| metadata_match_rate | 1.0 |
| unit_locator_coverage | 1.0 |
| locator_manifest_coverage | 1.0 |
| source_only_citation_violation_count | 0 |
| long_text_violation_count | 0 |
| blocked_actions_complete_rate | 1.0 |
| high_risk_card_count | 540 |
| high_risk_review_routed_rate | 1.0 |
| failure_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 3. Cards By Type

| card_type | count |
|---|---:|
| client_development_card | 20 |
| consult_method_card | 150 |
| consulting_kpi_card | 30 |
| deliverable_template_card | 70 |
| diagnostic_dimension_card | 60 |
| industry_analysis_card | 270 |

## 4. Failures

- None.

## 5. Interpretation

Fact: this validator checks cards against the full source register and parser
unit manifest before any indexing or online agent use.

Inference: if this gate stays green during full extraction batches, the project
has a repeatable metadata/citation QA layer.

Unknown: this gate does not score semantic answer quality, human citation gold
labels, or legal clearance.
