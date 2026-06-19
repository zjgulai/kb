---
title: "Consultant Role KB Expanded Answer Trace Fixture Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-expanded-anchored-retrieval-citation-eval-20260619.json"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
scope: "local deterministic answer trace fixture for expanded consultant role KB"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local fixture only; no live KB ingestion"
---

# Consultant Role KB Expanded Answer Trace Fixture Report

## 0. Boundary

This fixture uses deterministic template answers over expanded-card retrieval results. It does not call a provider, does not ingest into a live KB, and does not prove production answer quality.

## 1. Metrics

| metric | value |
|---|---:|
| trace_count | 12 |
| trace_pass_count | 12 |
| trace_pass_rate | 1.0 |
| source_selection_pass_rate | 1.0 |
| locator_citation_pass_rate | 1.0 |
| boundary_checks_pass_rate | 1.0 |
| blocked_action_pass_rate | 1.0 |
| refusal_pass_rate | 1.0 |
| long_text_reproduction_pass_rate | 1.0 |
| workspace_isolation_pass_rate | 1.0 |

## 2. Category Summary

| category | count | trace_pass_rate | source_selection_pass_rate | locator_citation_pass_rate |
|---|---:|---:|---:|---:|
| deliverable_workflow | 2 | 1.0 | 1.0 | 1.0 |
| diagnostic_planning | 1 | 1.0 | 1.0 | 1.0 |
| methodology_selection | 2 | 1.0 | 1.0 | 1.0 |
| refusal_unknown | 5 | 1.0 | 1.0 | 1.0 |
| source_lookup | 2 | 1.0 | 1.0 | 1.0 |

## 3. Failed Traces

- None.

## 4. Interpretation

The fixture verifies that expanded-card retrieval can still feed answers with selected unit locators and governance boundary language.
