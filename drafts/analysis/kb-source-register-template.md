---
title: "KB Source Register Template"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/kb-p1-poc-validation-plan.md"
  - "drafts/analysis/kb-evidence-register.md"
scope: "source register template for P1 enterprise knowledge-base PoC"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB Source Register Template

## 0. Boundary

This file defines the source register template for P1. It does not ingest documents, does not validate real ERP/WMS/API data, does not call a model provider, and does not write to any production knowledge base.

All rows in `drafts/analysis/kb-source-register.sample.csv` are examples unless a business/data owner later confirms the source, hash, version, and evidence grade.

## 1. Purpose

The source register is the intake gate before any knowledge can enter `supply-chain-kb`, `product-kb`, or `shared`.

It answers five questions:

1. Where did this knowledge come from?
2. Who owns the source?
3. What evidence grade can an Agent assign to it?
4. Which workspace and business domain can use it?
5. What actions must remain blocked even if the source is retrieved?

## 2. Required Columns

| column | required | allowed values / format | description |
|---|---|---|---|
| source_id | yes | `SRC-{DOMAIN}-{NNN}` | Stable source ID. Example: `SRC-SCM-001`. |
| source_title | yes | text | Human-readable source title. |
| domain | yes | `supply-chain-kb`, `product-kb`, `shared`, etc. | Target business domain. |
| layer | yes | `methodology`, `operations`, `metrics-and-data`, `crosswalk`, `governance`, `shared` | Domain template layer. |
| source_type | yes | `erp_export`, `api`, `system_page`, `approved_sop`, `metric_dictionary`, `field_dictionary`, `platform_policy`, `meeting_note`, `draft_analysis`, `external_reference`, `screenshot`, `unknown` | Source type. |
| source_uri | yes | file path, URL, system report name, or controlled path | Location of the source. Do not put secrets in this field. |
| source_owner | yes | person/team/role | Business or data owner. |
| owner_review_status | yes | `pending_review`, `owner_reviewed`, `approved`, `rejected` | Human review state. |
| evidence_grade | yes | `A`, `B`, `C`, `D` | Evidence grade. |
| workspace | yes | lowercase kebab-case | Strong isolation field. |
| version | yes | date/version/export timestamp | Source version. |
| collected_at | yes | ISO date or datetime | When the source was collected. |
| hash_sha256 | conditional | sha256 or `pending` | Required for files/exports. |
| record_count | optional | number or `unknown` | Number of records if tabular/export source. |
| pii_level | yes | `none`, `low`, `medium`, `high`, `unknown` | Data privacy level. |
| license_status | yes | `not_applicable`, `confirmed`, `pending_legal_review`, `restricted`, `unknown` | License/commercial use status. |
| allowed_agents | yes | comma-separated agent IDs | Agents allowed to retrieve this source. |
| blocked_actions | yes | comma-separated action IDs | Actions forbidden based on this source. |
| intake_status | yes | `source_intake_pending`, `registered`, `quarantined`, `ready_for_poc`, `rejected` | Intake status. |
| notes | optional | text | Clarifications, gaps, or pending questions. |

## 3. Evidence Grade Rules

| grade | source types | required condition | Agent usage |
|---|---|---|---|
| A | `erp_export`, `api`, approved system-of-record export, approved metric dictionary | owner reviewed, hash/version recorded | Can support factual claims. |
| B | `approved_sop`, owner-reviewed field dictionary, official platform policy | owner reviewed and versioned | Can support rule/process claims. |
| C | `meeting_note`, `draft_analysis`, unapproved business hypothesis | source owner known but not approved | Reference only; Agent must lower confidence. |
| D | unverified screenshot, copied text, unknown provenance | cannot be verified | Must not support final conclusion. |

### 3.1 Source Type Extension

`external_reference` is allowed for third-party reference materials such as consulting playbooks, diagnostic guides, slide templates, industry KPI libraries, acronym dictionaries, public policy references, or other externally authored documents that are useful for internal PoC extraction but are not system-of-record facts.

Rules for `external_reference`:

- Default evidence grade is `C` unless a formal owner/legal review upgrades it.
- Default `license_status` is `pending_legal_review` unless explicitly confirmed.
- Long source-text reproduction and redistribution must remain blocked unless separately approved.
- It can be `ready_for_poc` for internal local PoC when source owner, hash, workspace, allowed agents, and blocked actions are present.

## 4. Domain-Specific Minimum Sources

### 4.1 supply-chain-kb

| source_id seed | required source | minimum status before P1 ingest |
|---|---|---|
| SRC-SCM-001 | Inventory metric dictionary | `ready_for_poc` |
| SRC-SCM-002 | ERP/WMS field dictionary or export schema | `ready_for_poc` |
| SRC-SCM-003 | Replenishment SOP | `ready_for_poc` |
| SRC-SCM-004 | Inventory aging or stock movement report sample | `registered` |

The durable P1 vocabulary includes `计划库存`, `在途库存`, `可用库存`, `预占库存`, `冻结库存`, `在库库存`, `在库良品库存`, and `不良品库存`. These terms still require source-backed definitions before becoming Grade A/B knowledge.

### 4.2 product-kb

| source_id seed | required source | minimum status before P1 ingest |
|---|---|---|
| SRC-PROD-001 | SKU/MSKU/ASIN/SPU mapping sample | `ready_for_poc` |
| SRC-PROD-002 | Product attribute dictionary | `ready_for_poc` |
| SRC-PROD-003 | Listing rule or platform policy sample | `registered` |
| SRC-PROD-004 | Category taxonomy sample | `registered` |

### 4.3 shared

| source_id seed | required source | minimum status before P1 ingest |
|---|---|---|
| SRC-SHARED-001 | Entity dictionary seed | `ready_for_poc` |
| SRC-SHARED-002 | Metric dictionary seed | `ready_for_poc` |
| SRC-SHARED-003 | System crosswalk seed | `ready_for_poc` |

## 5. Intake Status Flow

```text
source_intake_pending
  -> registered
  -> ready_for_poc
  -> active_after_poc

source_intake_pending
  -> quarantined
  -> rejected
```

| status | meaning |
|---|---|
| source_intake_pending | Source is expected but not yet collected or verified. |
| registered | Basic metadata exists, but owner/hash/version/evidence checks may be incomplete. |
| quarantined | Source exists but cannot be used because provenance, PII, license, or quality is unresolved. |
| ready_for_poc | Source has enough metadata for P1 local PoC. |
| active_after_poc | Reserved for post-PoC promotion; not used in current draft. |
| rejected | Source should not be used. |

## 6. Blocked Actions Vocabulary

| action_id | meaning |
|---|---|
| create_purchase_order | Create purchase order. |
| update_inventory | Write inventory or stock status. |
| change_forecast | Change forecast values. |
| write_erp | Write ERP/WMS/OMS data. |
| publish_listing | Publish or update marketplace listing. |
| change_ad_budget | Change ad budget or campaign settings. |
| send_supplier_message | Send supplier communication. |
| expose_pii | Reveal PII or sensitive customer data. |
| publish_client_deliverable | Publish or mark a deliverable as client-final. |
| send_client_email | Send client-facing communication. |
| submit_rfp | Submit an RFP response or vendor proposal. |
| commit_budget | Commit budget, fees, or transaction capital. |
| approve_transaction | Approve a transaction, acquisition, investment, or integration decision. |
| redistribute_source_text | Redistribute or reproduce restricted source text. |

## 7. CSV Template

The machine-editable sample is:

`drafts/analysis/kb-source-register.sample.csv`

Header:

```csv
source_id,source_title,domain,layer,source_type,source_uri,source_owner,owner_review_status,evidence_grade,workspace,version,collected_at,hash_sha256,record_count,pii_level,license_status,allowed_agents,blocked_actions,intake_status,notes
```

## 8. P1 Promotion Checklist

A source can be used in P1 only when:

- `source_id` is stable and unique.
- `workspace` is present.
- `source_owner` is present.
- `evidence_grade` is not blank.
- Grade A/B sources have owner review.
- File/export sources have `hash_sha256`.
- `allowed_agents` and `blocked_actions` are explicit.
- `intake_status` is `ready_for_poc`.
