---
title: "Consultant Role KB Parser Unit Manifest Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
scope: "parser unit manifest coverage for full consultant-agent source register"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local parser manifests only; no live KB ingestion"
---

# Consultant Role KB Parser Unit Manifest Report

## 0. Boundary

The manifest records structural locators, unit counts, text lengths, and parser
diagnostics. It intentionally does not persist raw source text.

## 1. Outputs

| artifact | path |
|---|---|
| unit manifest JSONL | `tmp/consultant-role-kb-parser-unit-manifest-20260619.jsonl` |
| summary JSON | `tmp/consultant-role-kb-parser-unit-manifest-summary-20260619.json` |

## 2. Coverage Metrics

| metric | value |
|---|---:|
| source_count | 81 |
| parse_success_count | 81 |
| parse_error_count | 0 |
| total_unit_count | 23310 |
| empty_unit_count | 29 |
| empty_unit_rate | 0.0012 |
| sources_with_warnings | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 3. Units By Locator Type

| locator_type | count |
|---|---:|
| csv_row | 1178 |
| page | 9407 |
| paragraph | 36 |
| section | 5 |
| sheet_row | 12112 |
| slide | 572 |

## 4. Sources By Suffix

| suffix | count |
|---|---:|
| .csv | 2 |
| .docx | 1 |
| .epub | 1 |
| .pdf | 68 |
| .pptx | 6 |
| .xlsx | 3 |

## 5. Parse Errors

- None.

## 6. Interpretation

Fact: the full registered source set now has structural parser manifests that
can be used by card QA and later extraction batches.

Inference: source registration and parser coverage are ready for batch-level
full extraction planning, subject to legal/source-owner gates.

Unknown: this manifest does not prove extracted card quality or answer quality.
