---
title: "KB P1 SCM Owner Review Pack"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "drafts/analysis/kb-p1-scm-source-intake-report-20260618.md"
  - "drafts/analysis/kb-p1-scm-source-register-intake-draft.csv"
  - "/Users/pray/project/ecom_ana_overview/scm/system_data/库存指标说明.md"
  - "/Users/pray/project/ecom_ana_overview/scm/system_data/库存查询字段说明.xlsx"
scope: "owner review packet for SRC-SCM-001 and SRC-SCM-002"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB P1 SCM Owner Review Pack

## 0. Boundary

本文件是 `SRC-SCM-001` 和 `SRC-SCM-002` 的 owner review 包。它不执行入库、不调用模型、不连接 ERP/WMS/OMS/BI、不修改生产系统。

当前状态仍是：

| source_id | current_status | current_grade | reason |
|---|---|---|---|
| `SRC-SCM-001` | `registered` | C | 本地草稿口径存在，但 frontmatter 是 `status: draft`、`owner: self`、`source: human+ai`。 |
| `SRC-SCM-002` | `registered` | C | 字段字典 Excel 存在且 hash 已记录，但系统 owner review、导出来源和字段审批未完成。 |

P1 之前的唯一目标是把这两条来源从“候选草稿”推进到“可被 owner 审核的来源包”。是否升级为 `ready_for_poc` 必须由 owner review 和后续验证决定。

## 1. Review Roles

| role | responsibility | required decision |
|---|---|---|
| SCM business owner | 确认库存业务口径是否符合当前业务管理规则。 | approve / reject / request changes |
| ERP/WMS/data owner | 确认字段、系统来源、导出参数和刷新频率。 | approve / reject / request changes |
| Knowledge-base governor | 确认 source register、evidence grade、agent blocked actions。 | promote / keep registered / quarantine |

## 2. SRC-SCM-001 Inventory Metric Dictionary

### 2.1 Observed Facts

| field | value |
|---|---|
| file | `/Users/pray/project/ecom_ana_overview/scm/system_data/库存指标说明.md` |
| sha256 | `4fa9dd87b740163662f84d83ce27c26de51d5d8d799e2b3777feeee1efef6525` |
| observed status | `draft` |
| observed owner | `self` |
| observed source | `human+ai` |
| covered channels | 中仓、FBA、Shopify、Walmart、TikTok、零售与渠道 |
| covered metrics | 计划库存、在途库存、采购未交库存、可用库存、预占库存、冻结库存、在库库存、在库良品库存、不良品库存 |

### 2.2 Owner Questions

| review_area | question | required answer |
|---|---|---|
| authority | 这份口径是否来自当前正式 ERP/SRM/积加/渠道系统规则？ | yes / no / partial |
| version | 当前口径适用日期和版本是什么？ | date or version |
| source systems | 每个指标对应的 source system 是否准确？ | confirm or correct |
| formula | `在库库存 = 可用库存 + 预占库存 + 冻结库存 + 不良品库存` 是否适用于全部渠道？ | confirm or list exceptions |
| default zero | `冻结库存`、`预占库存` 等字段被写成默认 0 的场景是否是业务规则，而不是缺数据？ | confirm or correct |
| one-to-many mapping | Walmart `GTIN -> ItemID`、TikTok `供应链SKU -> MSKU` 的一对多风险是否需要在 Agent 回答中提示？ | yes / no / conditions |
| refresh cadence | 每小时整点、实时更新等描述是否仍准确？ | confirm or update |
| blocked actions | 基于该口径，Agent 是否仍必须禁止自动创建采购单、写库存、改预测？ | confirm or change |

### 2.3 Metric-Level Approval Table

| metric | current source description | owner decision | correction_needed |
|---|---|---|---|
| 计划库存 | SRM 需求池/采购订单、调拨单、渠道仓规则等，按渠道不同。 | pending | pending |
| 在途库存 | FBA 货件、物流跟踪表、调拨单/发货单等，按渠道不同。 | pending | pending |
| 采购未交库存 | SRM 采购订单明细和送货单明细。 | pending | pending |
| 可用库存 | 积加产品库存、FBA 本地可售、三方仓可用量、平台同步库存等。 | pending | pending |
| 预占库存 | 积加预占字段、FBA 预留买家订单、三方仓预占量等。 | pending | pending |
| 冻结库存 | 部分渠道默认为 0，FBA 使用运营中心相关预留字段。 | pending | pending |
| 在库库存 | 可用、预占、冻结、不良品库存合计。 | pending | pending |
| 在库良品库存 | 可用、预占、冻结库存合计。 | pending | pending |
| 不良品库存 | 积加不可售、FBA 不可售、三方仓次品量、Walmart 拒收损坏等。 | pending | pending |

## 3. SRC-SCM-002 ERP/WMS Inventory Field Dictionary

### 3.1 Observed Facts

| field | value |
|---|---|
| file | `/Users/pray/project/ecom_ana_overview/scm/system_data/库存查询字段说明.xlsx` |
| sha256 | `9224fbd8cb4237c316ce5656d732e21ee211118997edf69a4b3af9058f36bf18` |
| observed rows | 16 non-empty rows after worksheet dimension reset |
| observed headers | `序号`、`字段`、`业务含义` |
| parser note | Workbook dimension metadata reports `A1:A1`; profiling must reset dimensions before reading. |

### 3.2 Owner Questions

| review_area | question | required answer |
|---|---|---|
| source authority | 该 Excel 是否是当前 ERP/WMS 库存查询字段的正式字典或导出说明？ | yes / no / partial |
| export provenance | 文件来自哪个系统页面、菜单、报表或导出任务？ | controlled path or report name |
| field completeness | 16 行字段是否覆盖 P1 Agent 所需的全部库存字段？ | yes / no / missing fields |
| field grain | 字段粒度是 SKU、仓库、渠道、国家、MSKU、ASIN 还是组合粒度？ | specify grain |
| field aliases | `可用数量`、`可用库存`、`良品库存` 等是否存在同义或跨系统差异？ | list aliases |
| null/default rules | 空值、0、缺失字段分别代表什么？ | define rule |
| PII/security | 该字段字典和后续样例是否包含敏感运营数据或 PII？ | none / low / medium / high |

### 3.3 Field Dictionary Approval Table

| field_category | examples | owner decision | correction_needed |
|---|---|---|---|
| SKU identifiers | 供应链SKU、产品SKU、MSKU、FNSKU、ASIN、ItemId、GTIN | pending | pending |
| warehouse identifiers | 仓库、仓库名称、仓库编码、仓库ID、仓库类型、国家 | pending | pending |
| inventory quantities | 计划库存、在途库存、可用库存、预占库存、冻结库存、在库库存、良品库存、不良品库存 | pending | pending |
| channel/site dimensions | Shopify 站点、TikTok 国家、Walmart ItemId、FBA 仓库 | pending | pending |
| update/version fields | 更新时间、导出时间、快照日期 | pending | pending |

## 4. Promotion Criteria

`SRC-SCM-001` 和 `SRC-SCM-002` 只有同时满足以下条件，才允许从 `registered` 升级到 `ready_for_poc`：

1. `source_owner` 从占位 owner 改成真实业务或系统 owner。
2. `owner_review_status` 变成 `owner_reviewed` 或 `approved`。
3. 每个核心指标都有 source system、field mapping、grain、refresh cadence。
4. 默认 0、空值、字段缺失和一对多映射风险都有明确规则。
5. `blocked_actions` 仍覆盖 `create_purchase_order`、`update_inventory`、`change_forecast`、`write_erp` 等高风险动作。
6. Excel table-profile 通过，不存在无法解释的空表、错表、合并表头或字段丢失。

## 5. Proposed Review Outcome Template

```yaml
review_date: 2026-__-__
reviewer_name:
reviewer_role:
source_id:
decision: approve | reject | request_changes
approved_evidence_grade: A | B | C | D
approved_intake_status: registered | ready_for_poc | quarantined | rejected
required_corrections:
  - item:
blocked_actions_confirmed:
  - create_purchase_order
  - update_inventory
  - change_forecast
  - write_erp
notes:
```

## 6. Knowledge-Base Governor Note

在 review 完成前，Agent 必须按低置信引用处理这些来源：可以用来设计 eval 题、字段核验清单和 owner review 问题，但不得作为最终业务结论、采购建议、库存写入或补货动作依据。
