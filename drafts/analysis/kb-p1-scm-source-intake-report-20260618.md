---
title: "KB P1 SCM Source Intake Report"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "drafts/analysis/kb-p1-scm-source-register-candidates.md"
  - "drafts/analysis/kb-p1-poc-validation-plan.md"
  - "/Users/pray/project/ecom_ana_overview/scm/system_data"
scope: "readonly source-intake verification for supply-chain-kb P1"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB P1 SCM Source Intake Report

## 0. Boundary

本报告只做本地 source intake 只读核验，不执行知识库入库，不调用模型 provider，不部署服务，不修改 ERP/WMS/OMS/BI/渠道系统，不把任何来源升级为生产可用证据。

结论分层：

- 事实：本地文件存在、可读取、hash 已记录、部分字段已抽样。
- 推断：这些文件可以作为 P1 source register 的候选来源。
- 不确定项：业务 owner、系统 owner、导出参数、导出完整性、数据权限、字段口径审批均未完成。

## 1. Executive Finding

P1 SCM source intake 从“全量 `source_intake_pending`”推进到“发现一批可登记候选来源”。但当前没有任何来源达到 `ready_for_poc`。

主要原因：

1. `库存指标说明.md` 有完整库存口径描述，但 frontmatter 明确为 `status: draft`、`owner: self`、`source: human+ai`。
2. 多个 Excel 是真实本地导出文件，且 hash 可计算，但缺少导出参数、系统 owner review 和字段口径审批。
3. `kp03/kp04` 有 SOP 结构，但文档正文说明“本地重建，不等同于钉钉原文复制”，只能作为 C 级草稿参考。
4. 当前没有授权的生产系统 API、正式数据字典、审批记录或 owner-signed SOP。

因此，下一步应写入 `registered` 候选草稿，而不是写入 `ready_for_poc`。

Machine-editable draft:

`drafts/analysis/kb-p1-scm-source-register-intake-draft.csv`

## 2. Source Files Found

### 2.1 Metric and Field Definitions

| source_id | file | sha256 | observed content | current evidence status |
|---|---|---|---|---|
| `SRC-SCM-001` | `/Users/pray/project/ecom_ana_overview/scm/system_data/库存指标说明.md` | `4fa9dd87b740163662f84d83ce27c26de51d5d8d799e2b3777feeee1efef6525` | 中仓、FBA、Shopify、Walmart、TikTok、零售与渠道库存口径；含计划库存、在途库存、可用库存、预占库存、冻结库存、在库库存、在库良品库存、不良品库存等定义。 | `registered` candidate only; frontmatter is draft/self/human+ai. |
| `SRC-SCM-002` | `/Users/pray/project/ecom_ana_overview/scm/system_data/库存查询字段说明.xlsx` | `9224fbd8cb4237c316ce5656d732e21ee211118997edf69a4b3af9058f36bf18` | 16 non-empty rows after worksheet dimension reset; headers include `序号`、`字段`、`业务含义`。 | `registered` candidate only; field owner review pending. |

### 2.2 ERP/BI Export Samples

| source_id | file | sha256 | observed schema/sample | current evidence status |
|---|---|---|---|---|
| `SRC-SCM-004` | `/Users/pray/project/ecom_ana_overview/scm/system_data/库存周转-库龄20260601.xlsx` | `e51befcf62a99ab4b6425d5eaa45533ba3d00c1d3406889e49802685b1b01bc4` | Sheet `库存周转`; first 20,000 non-empty rows sampled; fields include GTM、品线、SKU、仓库、周转分类、滞销分类等。 | `registered` candidate only; export parameters and owner review pending. |
| `SRC-SCM-010` | `/Users/pray/project/ecom_ana_overview/scm/system_data/仓库资料导出_2026-06-04_20260604122810331.xlsx` | `a9b240cffe47c377c66deeafbdb1515d39c984f7325cf08cf9b786d9eda5d968` | 409 non-empty rows; fields include 仓库编码、仓库ID、仓库名称、仓库类型、国家/地区、状态、创建时间、更新时间。 | `registered` candidate only; system owner review pending. |
| `SRC-SCM-011` | `/Users/pray/project/ecom_ana_overview/scm/system_data/仓库库存列表_20260602190444851.xlsx` | `d5c2d2b5e8b84696023d8544dad6e04b645e3b0ffbf252ee2368f397c3b1075a` | First 20,000 non-empty rows sampled; fields include 供应链SKU、产品SKU、仓库、仓库类型、在途库存、良品库存、可用数量、预占数量、锁库数量。 | `registered` candidate only; export scope and owner review pending. |
| `SRC-SCM-021` | `/Users/pray/project/ecom_ana_overview/scm/system_data/fba计划库存_20260602190118540.xlsx` | `e7372a056b6ec8432b3c75493cd8e101ef23107c2ab10d70ffe315b295c3069d` | First 20,000 non-empty rows sampled; fields include 仓库、ASIN、MSKU、FNSKU、计划库存、在途库存、可用库存、预占库存、冻结库存。 | `registered` candidate only; companion FBT export also found. |
| `SRC-SCM-022` | `/Users/pray/project/ecom_ana_overview/scm/system_data/沃尔玛计划库存_20260602190140263.xlsx` | `a7bcedba2a2b98e5e461562230068a856249892000299c9354da8abafb4872a5` | 2,396 non-empty rows; fields include 仓库、ItemId、国家、MSKU、GTIN、计划库存、在途库存、可用库存、预占库存、冻结库存。 | `registered` candidate only; export parameters and owner review pending. |
| `SRC-SCM-023` | `/Users/pray/project/ecom_ana_overview/scm/system_data/Shopify计划库存_20260602190146714.xlsx` | `cef4b2d5fddc2444271a85e954c01ba27c83c82f93b24a737ffdf37e84daf282` | First 20,000 non-empty rows sampled; fields include 仓库、仓库地点、站点、供应链SKU、计划库存、在途库存、可用库存、预占库存。 | `registered` candidate only; export parameters and owner review pending. |
| `SRC-SCM-024` | `/Users/pray/project/ecom_ana_overview/scm/system_data/TikTok计划库存_20260602190147986.xlsx` | `132d64d38b4c211ffd4a4def2fe80b3fbcf06f6842a8862b7240772a51c7d40e` | 2,938 non-empty rows; fields include 仓库、MSKU、国家、站点、计划库存、在途库存、可用库存、预占库存。 | `registered` candidate only; export parameters and owner review pending. |
| `SRC-SCM-025` | `/Users/pray/project/ecom_ana_overview/scm/system_data/三方系统库存对账导出2026-06-02_20260602191334628.xlsx` | `29ff98fb582079ad65a6dc45d5de9eea63a6f5ed3e0e6a81060ed426c7d6f6c7` | 9,424 non-empty rows; multi-row header covers 富勒、ERP、积加库存对账字段。 | `registered` candidate only; reconciliation owner review pending. |

### 2.3 SOP and Rule Drafts

| source_id | file | sha256 | observed content | current evidence status |
|---|---|---|---|---|
| `SRC-SCM-003` | `/Users/pray/project/ecom_ana_overview/scm/供应链成本指标全链路优化/（tactic）课题一：kp03-计划排产执行方案.md` | `ea52973103b5dc3f8b2ca44ed0f517f1577cc929fb13b2e592d5910caefaa882` | PSI、PO、在途、冻结窗口、周会、异常流程、红线规则。 | C-grade draft reference only; not approved replenishment SOP. |
| `SRC-SCM-017` / `SRC-SCM-018` | `/Users/pray/project/ecom_ana_overview/scm/供应链成本指标全链路优化/（tactic）课题一：kp04-仓储与调拨协同执行方案.md` | `794fb5e37bcf5bb5d0b07e7f414a49255e352199887d44842c7151b1e0311a75` | 库龄治理、调拨候选、调拨 ROI、缺货/覆盖天数规则、返仓归因。 | C-grade draft reference only; not approved SOP. |
| `SRC-SCM-003` supporting raw extract | `/Users/pray/project/ecom_ana_overview/scm/drafts/analysis/stocking-inventory-rules-knowledge-base-draft-20260604/alidocs-stocking-inventory-planning-raw-extract-draft-20260604.md` | `8f8b7e2be4130c1c0b540f96b74372157d87c06e49ca875cc52c4cf92a51fd26` | Browser-rendered DingTalk fragments for 备货库存数据规划; includes milestone and inventory data-source planning text. | Draft browser-rendered evidence only; not a controlled export or approved source. |

## 3. Important Technical Observation

Several Excel workbooks have worksheet dimension metadata that reports `A1:A1`, which makes a naive reader think the sheet has only one cell. After `openpyxl` `reset_dimensions()`, the sheets expose actual rows and columns.

This matters for future ingestion:

- Parser must not rely only on workbook dimension metadata.
- Intake profile should record both raw workbook dimensions and recalculated row/column observations.
- If P1 later builds an Excel parser, it needs a table-quality gate before chunking.

## 4. Promotion Decision

| decision | result |
|---|---|
| Promote any source to `ready_for_poc` now | No. |
| Register candidate sources with hash evidence | Yes, in draft CSV only. |
| Use these sources for final Agent answers | No. They may only support P1 test design until owner review is complete. |
| Use these sources for readonly local PoC after approval | Possible, after owner review, export parameter confirmation, PII review, and parser quality check. |

## 5. Remaining Blockers

| blocker | impact | required action |
|---|---|---|
| Owner review missing | Cannot assign A/B evidence grade. | SCM/data/system owner confirms source, scope, and version. |
| Export parameters missing | Agent cannot know filter conditions, time range, or completeness. | Attach export screen, report config, or system export metadata. |
| PII/privacy not assessed | Some SKU/channel exports may contain sensitive operational data. | Mark PII/security level before ingest. |
| SOP approval missing | Replenishment/transfer actions cannot rely on drafts. | Provide approved SOP or approval matrix. |
| Parser quality not measured | Excel merged/malformed headers may corrupt chunks. | Run table profiling before ingestion. |

## 6. Next Step Plan

1. Ask SCM/data owner to review `SRC-SCM-001` and `SRC-SCM-002` first.
2. Add export metadata for `SRC-SCM-004`, `SRC-SCM-010`, `SRC-SCM-011`, and `SRC-SCM-021` to `SRC-SCM-025`.
3. Extract a minimal metric dictionary from `库存指标说明.md`, but keep it in `draft` until review.
4. Build an Excel table-profile script for P1 that records sheet names, recalculated row counts, headers, merged cells, and sample-value redaction status.
5. Only after review, change selected rows from `registered` to `ready_for_poc`.
