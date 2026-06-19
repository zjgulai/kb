---
title: "KB P1 SCM Ready-for-PoC Promotion Record"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "drafts/analysis/kb-p1-scm-owner-review-decision-log.csv"
  - "drafts/analysis/kb-p1-scm-source-register-intake-draft.csv"
  - "drafts/analysis/kb-p1-scm-promotion-gate-checklist-20260618.md"
scope: "promote SRC-SCM-001 and SRC-SCM-002 to ready_for_poc for readonly P1 only"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB P1 SCM Ready-for-PoC Promotion Record

## 0. Boundary

本记录响应当前线程用户指令：“同意下一步，升级”。

本次升级只适用于 P1 readonly PoC：

- 不代表生产可用。
- 不代表外部正式 owner 签核。
- 不调用模型 provider。
- 不写入正式知识库。
- 不连接或写入 ERP/WMS/OMS/BI/渠道系统。
- 不允许 Agent 创建采购单、更新库存、修改预测或写 ERP。

## 1. Promotion Result

| source_id | previous status | new status | previous grade | new grade | review basis |
|---|---|---|---|---|---|
| `SRC-SCM-001` | `registered` / `pending_review` | `ready_for_poc` / `approved` | C | B | current-thread user instruction |
| `SRC-SCM-002` | `registered` / `pending_review` | `ready_for_poc` / `approved` | C | B | current-thread user instruction |

## 2. Why Grade B, Not Grade A

B 级表示可用于 P1 readonly PoC 的 owner-approved working source。没有升到 A 级的原因：

1. `SRC-SCM-001` 的原文件仍是本地 `draft`、`owner: self`、`source: human+ai`。
2. `SRC-SCM-002` 虽然有 hash 和字段 profile，但仍缺正式导出页面、报表路径、导出筛选条件和外部系统 owner 签核。
3. 当前 approval 来自本 Codex 线程，不是外部审批系统、签名文档或工单。

## 3. Required Agent Constraints

任何基于这两条 source 的 P1 Agent 回答必须保留：

| constraint | required behavior |
|---|---|
| mode | readonly |
| allowed use | source lookup, metric explanation, field mapping, eval design |
| blocked action | `create_purchase_order` |
| blocked action | `update_inventory` |
| blocked action | `change_forecast` |
| blocked action | `write_erp` |
| uncertainty | 涉及生产动作、正式财务口径、系统写回时必须声明需要人工确认 |

## 4. Post-PoC Production Blockers

进入生产前仍需补齐：

1. 真实 SCM/data/ERP owner 姓名与角色。
2. 外部正式审批记录 URI。
3. ERP/WMS/BI 导出路径、筛选条件、时间范围。
4. 指标字典的生产版本号。
5. PII/security review。
6. Parser gate 全量通过记录。
7. Eval 结果和 citation precision 报告。
