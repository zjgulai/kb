---
title: "Consultant Role KB Card Sample Summary"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
  - "tmp/consultant-role-kb-card-samples-20260619.jsonl"
scope: "deterministic typed-card dry run summary for consultant role KB"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "sample dry run only; no live ingestion"
---

# Consultant Role KB Card Sample Summary

## 0. Boundary

This is a deterministic local sample dry run. It does not call a model provider, does not ingest data into a live KB, and does not assert production readiness.

## 1. Inputs

- Source register: `drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv`
- Source profile: `tmp/consult-role-kb-source-profile-20260619.json`
- Output cards: `tmp/consultant-role-kb-card-samples-20260619.jsonl`

## 2. Card Counts

| card_type | count |
|---|---:|
| `consult_method_card` | 5 |
| `diagnostic_dimension_card` | 3 |
| `deliverable_template_card` | 4 |
| `consulting_kpi_card` | 16 |
| `terminology_crosswalk_card` | 5 |
| total | 33 |

## 3. What This Proves

- The P1 role-KB can represent consulting knowledge as typed cards instead of raw document chunks.
- Source metadata, evidence grade, owner, workspace, allowed agent, blocked actions, and license boundary can be carried into every card.
- PPTX, PDF, DOCX, and XLSX can all produce at least a minimal card sample under the local parser route.
- KPI and acronym libraries should use row-level cards, while playbooks and toolkits should use method, diagnostic, or deliverable-template cards.

## 4. What This Does Not Prove

- It does not prove retrieval quality.
- It does not prove citation precision.
- It does not prove model answer quality.
- It does not resolve source license or redistribution rights.
- It does not create a production KB.

## 5. Parser Notes

PDF parsing produced non-fatal object-pointer warnings for some source files. The sample dry run still completed, but a real parser gate should record:

1. page coverage,
2. outline extraction coverage,
3. table extraction coverage,
4. image-only/page-layout misses,
5. whether sampled citations can be traced to page or slide location.

The first card generation pass also surfaced a table-header filtering issue in the acronym workbook. The header-like card was removed from the sample output; full extraction must explicitly filter header rows before producing row-level cards.

## 6. Next Gate

Before any retrieval or Agent eval run:

- Decide whether to add `external_reference` to the source-register enum.
- Create the consultant role shared ontology seed.
- Convert a reviewed subset of sample cards into a stable card schema.
- Approve whether local embedding/indexing is allowed.
