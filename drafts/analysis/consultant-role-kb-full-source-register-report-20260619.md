---
title: "Consultant Role KB Full Source Register Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consult-role-kb-source-profile-20260619.json"
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
scope: "full 81-source draft registration for consultant-agent"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "draft source registration only; no live KB ingestion"
---

# Consultant Role KB Full Source Register Report

## 0. Boundary

This register is a draft planning artifact. It does not approve legal use,
persist derived cards into a live KB, call a provider, or redistribute raw
source material.

## 1. Outputs

| artifact | path |
|---|---|
| full source register | `drafts/analysis/consultant-role-kb-full-source-register-20260619.csv` |

## 2. Register Summary

| metric | value |
|---|---:|
| total_sources | 81 |
| profiled_sources | 81 |
| ready_for_poc_seed_sources | 15 |
| registered_pending_review_sources | 66 |
| duplicate_groups | 1 |
| sources_with_high_risk_flags | 75 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 3. Sources By Suffix

| suffix | count |
|---|---:|
| .csv | 2 |
| .docx | 1 |
| .epub | 1 |
| .pdf | 68 |
| .pptx | 6 |
| .xlsx | 3 |

## 4. Sources By Intake Status

| intake_status | count |
|---|---:|
| ready_for_poc | 15 |
| registered | 66 |

## 5. Sources By Extraction Batch

| extraction_batch | count |
|---|---:|
| batch-01-delivery-craft | 4 |
| batch-01-methodology-playbooks | 19 |
| batch-02-diagnostics | 11 |
| batch-03-industry-analysis | 29 |
| batch-04-transaction-advisory | 4 |
| batch-05-reference-data | 6 |
| batch-06-client-development | 5 |
| batch-99-needs-human-triage | 3 |

## 6. Interpretation

Fact: all profiled `consult/` files now have draft source-register rows,
including stable source IDs, hash, parser route, license status, allowed agent,
blocked actions, extraction batch, high-risk flags, and duplicate policy.

Inference: the project can now run parser manifest generation across the full
library without starting from unregistered files.

Unknown: legal/license clearance and persistent derived-card storage remain
pending human review.
