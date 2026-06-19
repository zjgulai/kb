---
title: "Consultant Role KB Legal Source Owner Decision Workflow"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv"
  - "shared/governance/consultant-agent/legal-source-owner-decision.schema-20260619.json"
scope: "structured legal and source-owner decision intake for consultant-agent corpus"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "decision workflow only; no legal approval recorded"
---

# Consultant Role KB Legal Source Owner Decision Workflow

## 0. Boundary

This workflow creates a review queue, pending decision template, and validation
summary. It does not approve source use, upgrade license status, deploy shared
staging, call a provider, or ingest into a live KB.

## 1. Validation Summary

| metric | value |
|---|---:|
| source_count | 81 |
| selected_source_count | 80 |
| decision_count | 81 |
| pending_review_count | 81 |
| selected_approved_internal_staging_count | 0 |
| selected_pending_review_count | 80 |
| shared_staging_legal_clearance_ready | false |
| failure_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Artifacts

- Schema: `shared/governance/consultant-agent/legal-source-owner-decision.schema-20260619.json`
- Queue: `shared/governance/consultant-agent/legal-source-owner-review.queue-20260619.csv`
- Decision template: `shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl`
- Validation: `tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json`

## 3. Interpretation

Fact: every registered source has one pending legal/source-owner decision row.

Fact: the current selected 80-source all-extractable runtime corpus has zero
approved internal-staging decisions.

Boundary: shared staging remains blocked until selected sources receive explicit
legal and source-owner approval for `internal_no_provider_staging`.
