---
title: "KB P1 SCM Owner Review Request"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "drafts/analysis/kb-p1-scm-owner-review-pack-20260618.md"
  - "drafts/analysis/kb-p1-scm-source-register-intake-draft.csv"
  - "drafts/analysis/kb-p1-excel-table-profile-summary-20260618.md"
scope: "review request message for SRC-SCM-001 and SRC-SCM-002"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB P1 SCM Owner Review Request

## 0. Boundary

这是给 SCM 业务 owner、ERP/WMS/data owner 的评审请求草稿。它不代表 owner 已确认，不改变 source register，不升级 evidence grade，不触发知识库入库。

## 1. Request Message

请协助评审企业知识库 P1 样板源中的两条 SCM 来源：

1. `SRC-SCM-001`：库存指标口径，来源文件为 `库存指标说明.md`。
2. `SRC-SCM-002`：库存查询字段说明，来源文件为 `库存查询字段说明.xlsx`。

当前这两条来源只处于 `registered` / `pending_review` / C 级状态，不能作为 AI Agent 的最终业务结论依据。我们希望确认它们是否可以进入 P1 readonly PoC，并明确哪些指标、字段、默认值、一对多映射和导出参数需要修正。

请重点确认：

- 这些口径是否来自当前正式 ERP/SRM/积加/渠道系统规则。
- 每个指标的 source system、字段、粒度、刷新频率是否准确。
- `计划库存`、`在途库存`、`可用库存`、`预占库存`、`冻结库存`、`在库库存`、`在库良品库存`、`不良品库存` 的定义是否可被业务采用。
- `冻结库存=0`、`预占库存=0` 等默认值是否是业务规则，而不是缺数据。
- Walmart `GTIN -> ItemID`、TikTok `供应链SKU -> MSKU` 等一对多映射风险是否需要在 Agent 回答中提示。
- Excel 字段字典是否覆盖 P1 Agent 所需字段，是否需要补充导出页面、报表路径、导出时间和筛选条件。
- 基于这些来源，Agent 是否仍必须禁止 `create_purchase_order`、`update_inventory`、`change_forecast`、`write_erp`。

评审输出请按以下格式返回：

```yaml
review_date:
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

## 2. Attachments to Send

| attachment | purpose |
|---|---|
| `drafts/analysis/kb-p1-scm-owner-review-pack-20260618.md` | 评审问题、指标表、字段表、升级条件。 |
| `drafts/analysis/kb-p1-scm-source-register-intake-draft.csv` | 当前 source register 草稿，所有行仍是 `registered` / `pending_review` / C 级。 |
| `drafts/analysis/kb-p1-excel-table-profile-summary-20260618.md` | Excel 结构 profile 摘要和 parser gate。 |
| `tmp/kb-p1-excel-profile-20260618.json` | 只读结构 profile JSON，不含业务明细行。 |

## 3. Review Deadline Suggestion

建议先评审 `SRC-SCM-001` 和 `SRC-SCM-002`，因为它们决定 P1 replenishment-agent 能否正确理解库存指标和字段 crosswalk。若这两条无法确认，后续所有库存导出只能继续保留为 eval 设计材料，不能进入 `ready_for_poc`。

## 4. Decision Boundary

只有收到 owner 明确返回后，才能更新：

- `source_owner`
- `owner_review_status`
- `evidence_grade`
- `intake_status`
- `notes`

在此之前，不允许把任何行写成 `ready_for_poc`。
