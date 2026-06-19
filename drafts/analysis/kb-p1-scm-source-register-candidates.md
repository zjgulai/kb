---
title: "KB P1 SCM Source Register Candidates"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/kb-source-register-template.md"
  - "drafts/analysis/kb-p1-poc-validation-plan.md"
scope: "candidate source register rows for supply-chain-kb P1 intake"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB P1 SCM Source Register Candidates

## 0. Boundary

This file expands the first P1 source-register candidates for `supply-chain-kb`. It does not claim that any ERP/WMS/API/SOP source has been collected or validated. All rows remain `source_intake_pending` until the business or data owner supplies the real source, hash/version evidence, and review status.

The machine-editable CSV is:

`drafts/analysis/kb-p1-scm-source-register-candidates.csv`

## 1. Candidate Scope

The first SCM batch covers three P1 intake groups:

| group | candidate IDs | purpose |
|---|---|---|
| Inventory metrics | `SRC-SCM-001` to `SRC-SCM-015` | Establish source-backed definitions for inventory and replenishment metrics. |
| SOP and exception handling | `SRC-SCM-016` to `SRC-SCM-020` | Establish owner-reviewed replenishment, stockout, slow-moving, and transfer workflows. |
| Channel/system exports | `SRC-SCM-021` to `SRC-SCM-025` | Register channel inventory exports and reconciliation sources needed for cross-domain reasoning. |

## 2. Important Interpretation Rule

`evidence_grade` in the CSV is the expected grade after owner review and source validation. It is not active evidence while `intake_status` is `source_intake_pending`.

An Agent must treat every row in this file as unavailable for final conclusions until:

1. `source_uri` points to a real controlled source.
2. `hash_sha256` is recorded for files or exports.
3. `source_owner` confirms the source.
4. `owner_review_status` becomes `owner_reviewed` or `approved`.
5. `intake_status` becomes `ready_for_poc`.

## 3. SCM Metric Vocabulary

The candidate register includes the durable P1 vocabulary:

| business term | source requirement |
|---|---|
| 计划库存 | Must be defined against ERP/WMS/channel planning source. |
| 在途库存 | Must specify purchase, transfer, or platform inbound source. |
| 可用库存 | Must define exclusions such as allocated, frozen, defective, or reserved stock. |
| 预占库存 | Must map to order allocation or reservation fields. |
| 冻结库存 | Must map to quality hold, compliance hold, or platform lock fields. |
| 在库库存 | Must specify warehouse and ownership boundary. |
| 在库良品库存 | Must distinguish sellable good stock from defective or pending-inspection stock. |
| 不良品库存 | Must define quality status and whether it can be sold, repaired, or scrapped. |

## 4. P1 Intake Priority

| priority | source_id | reason |
|---|---|---|
| P0 | `SRC-SCM-001` | Without inventory metric definitions, eval answers must stay unknown. |
| P0 | `SRC-SCM-002` | Without ERP/WMS field mapping, Agent cannot cite system facts. |
| P0 | `SRC-SCM-003` | Without replenishment SOP, Agent cannot answer approval/blocked-action questions. |
| P1 | `SRC-SCM-004` to `SRC-SCM-015` | Needed for metric reasoning and inventory anomaly diagnosis. |
| P1 | `SRC-SCM-016` to `SRC-SCM-020` | Needed for SOP retrieval and exception workflow answers. |
| P2 | `SRC-SCM-021` to `SRC-SCM-025` | Needed for channel inventory reconciliation and cross-domain cases. |

## 5. Current Status

Current status is `draft`. No row is ready for P1 ingest yet.
