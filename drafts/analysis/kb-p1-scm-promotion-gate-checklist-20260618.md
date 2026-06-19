---
title: "KB P1 SCM Promotion Gate Checklist"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "drafts/analysis/kb-p1-scm-owner-review-pack-20260618.md"
  - "drafts/analysis/kb-p1-scm-owner-review-decision-log.csv"
  - "drafts/analysis/kb-source-register-template.md"
scope: "promotion gate checklist for SRC-SCM-001 and SRC-SCM-002"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB P1 SCM Promotion Gate Checklist

## 0. Boundary

本清单定义升级门槛，并记录 2026-06-18 当前线程用户授权后的 P1 PoC 升级结果。当前 `SRC-SCM-001` 和 `SRC-SCM-002` 已升级为 `ready_for_poc` / `approved` / B 级，但仅限 P1 readonly PoC；这不是生产可用、不是外部正式 owner 签核，也不允许自动写 ERP/WMS/OMS。

## 1. Gate A: Owner Identity

| check | required result | current status |
|---|---|---|
| 真实 SCM business owner 已填写 | name + role | current_thread_user / project_owner_by_current_thread_instruction |
| 真实 ERP/WMS/data owner 已填写 | name + role | current_thread_user / project_owner_by_current_thread_instruction |
| reviewer 与 source owner 关系清楚 | owner / delegate / reviewer | current-thread project owner instruction; external formal role not independently verified |
| review decision 有可追溯 URI | doc/comment/ticket/link | `drafts/analysis/kb-p1-scm-ready-for-poc-promotion-record-20260618.md` |

## 2. Gate B: Source Authority

| check | required result | current status |
|---|---|---|
| `SRC-SCM-001` 口径来源被确认 | formal rule / current operational rule / rejected | approved for P1 readonly PoC; external production authority pending |
| `SRC-SCM-002` 字段字典来源被确认 | system export / report dictionary / rejected | approved for P1 readonly PoC; export provenance before production pending |
| 版本或适用日期明确 | date/version | source file versions retained |
| 导出路径、报表名或系统页面明确 | controlled path | local source paths retained; formal system path pending before production |

## 3. Gate C: Metric and Field Completeness

| check | required result | current status |
|---|---|---|
| 计划库存字段映射明确 | source system + field + grain | accepted for P1 readonly PoC |
| 在途库存字段映射明确 | source system + field + grain | accepted for P1 readonly PoC |
| 可用库存字段映射明确 | source system + field + grain | accepted for P1 readonly PoC |
| 预占库存字段映射明确 | source system + field + grain | accepted for P1 readonly PoC |
| 冻结库存字段映射明确 | source system + field + grain | accepted for P1 readonly PoC |
| 在库库存公式明确 | formula + exceptions | accepted for P1 readonly PoC |
| 在库良品库存公式明确 | formula + exceptions | accepted for P1 readonly PoC |
| 不良品库存字段映射明确 | source system + field + grain | accepted for P1 readonly PoC |

## 4. Gate D: Data Quality and Parser Readiness

| check | required result | current status |
|---|---|---|
| Excel dimension warning 已解释 | yes | partially profiled |
| 多行表头处理规则明确 | yes / not applicable | accepted for P1 parser gate; production hardening pending |
| 空值、0、缺失字段规则明确 | yes | accepted for P1 readonly PoC; production hardening pending |
| 一对多映射风险规则明确 | yes | accepted for P1 readonly PoC; answer must disclose uncertainty |
| profile JSON hash 和 source hash 已复核 | yes | done for current files |
| 不输出业务明细行的 profile 策略被接受 | yes | accepted for P1 readonly PoC |

## 5. Gate E: Agent Safety

| check | required result | current status |
|---|---|---|
| Agent mode 仍为 readonly | confirmed | confirmed for P1 |
| `create_purchase_order` blocked | confirmed | confirmed for P1 |
| `update_inventory` blocked | confirmed | confirmed for P1 |
| `change_forecast` blocked | confirmed | confirmed for P1 |
| `write_erp` blocked | confirmed | confirmed for P1 |
| 缺证据时回答 unknown/refusal | confirmed | confirmed for P1 |

## 6. Promotion Decision Rule

2026-06-18 当前线程用户已授权将 `SRC-SCM-001` 和 `SRC-SCM-002` 从：

```text
registered / pending_review / C
```

升级为：

```text
ready_for_poc / owner_reviewed or approved / A or B
```

该升级只允许用于 P1 readonly PoC。进入生产、写入正式知识库、允许 Agent 进行动作建议或写回系统前，仍需外部正式 owner 角色、正式审批记录、导出参数和生产级数据治理补齐。
