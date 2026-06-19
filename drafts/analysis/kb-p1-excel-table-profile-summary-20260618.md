---
title: "KB P1 Excel Table Profile Summary"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "drafts/analysis/tools/kb_p1_excel_table_profile.py"
  - "tmp/kb-p1-excel-profile-20260618.json"
  - "drafts/analysis/kb-p1-scm-source-register-intake-draft.csv"
scope: "readonly structural profile summary for SCM P1 Excel sources"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB P1 Excel Table Profile Summary

## 0. Boundary

本摘要只记录 Excel 结构 profile 结果，不输出 SKU、产品、库存数量等业务明细值，不执行知识库入库，不调用模型，不连接生产系统。

Profile JSON:

`tmp/kb-p1-excel-profile-20260618.json`

Profile script:

`drafts/analysis/tools/kb_p1_excel_table_profile.py`

## 1. Run Evidence

```bash
/Users/pray/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  drafts/analysis/tools/kb_p1_excel_table_profile.py \
  --source-register drafts/analysis/kb-p1-scm-source-register-intake-draft.csv \
  --output-json tmp/kb-p1-excel-profile-20260618.json \
  --max-rows 20000 \
  --max-sheets 3
```

Observed run result: exit code `0`.

Read policy recorded in JSON: `readonly; headers and structural metadata only; no business data rows emitted`.

## 2. Workbook Profile Results

| source_id | workbook | observed_rows | observed_cols | dimension_warning | key headers |
|---|---|---:|---:|---|---|
| `SRC-SCM-002` | `库存查询字段说明.xlsx` | 16 | 3 | yes | 序号、字段、业务含义 |
| `SRC-SCM-004` | `库存周转-库龄20260601.xlsx` | 20000 | 49 | yes | GTM组、品线、SKU编码、仓库名称、周转分类 |
| `SRC-SCM-010` | `仓库资料导出_2026-06-04_20260604122810331.xlsx` | 409 | 18 | yes | 仓库编码、仓库ID、仓库名称、仓库类型、国家/地区 |
| `SRC-SCM-011` | `仓库库存列表_20260602190444851.xlsx` | 20000 | 15 | yes | 供应链SKU、产品SKU、仓库、仓库类型、在途库存、可用数量 |
| `SRC-SCM-021` | `fba计划库存_20260602190118540.xlsx` | 20000 | 15 | yes | 仓库、ASIN、MSKU、FNSKU、计划库存、在途库存、可用库存 |
| `SRC-SCM-022` | `沃尔玛计划库存_20260602190140263.xlsx` | 2396 | 16 | yes | 仓库、ItemId、国家、MSKU、GTIN、计划库存、可用库存 |
| `SRC-SCM-023` | `Shopify计划库存_20260602190146714.xlsx` | 20000 | 16 | yes | 仓库、仓库地点、站点、供应链SKU、计划库存、可用库存 |
| `SRC-SCM-024` | `TikTok计划库存_20260602190147986.xlsx` | 2938 | 15 | yes | 仓库、MSKU、国家、站点、供应链SKU、计划库存、可用库存 |
| `SRC-SCM-025` | `三方系统库存对账导出2026-06-02_20260602191334628.xlsx` | 9424 | 23 | no | 日期、时间、供应链SKU、产品名称、富勒、ERP |

`observed_rows` 受 `--max-rows 20000` 限制；等于 20000 的文件只表示“前 20000 行已扫描且仍有结构”，不是全量行数结论。

## 3. Findings

### 3.1 Worksheet Dimension Metadata Is Unreliable

多个 workbook 的 reported dimension 是 `A1:A1`，但 reset dimensions 后能读到真实表结构。后续 parser 不能只依赖 `ws.max_row`、`ws.max_column` 或 `calculate_dimension()` 的初始值。

### 3.2 Headers Are Mostly Detectable

除 `SRC-SCM-025` 是多行表头外，其他候选源的首个非空行基本可作为 header seed。`SRC-SCM-025` 同时覆盖富勒、ERP、积加三套库存字段，需要多行 header 合并规则，否则 chunk 会丢失系统上下文。

### 3.3 Current Evidence Grade Should Not Upgrade

Profile 证明的是“文件可读、字段可见、hash 可复核”，不是“字段口径已审批”。所有 Excel source 仍应保持：

- `intake_status`: `registered`
- `owner_review_status`: `pending_review`
- `evidence_grade`: `C`

## 4. Parser Gate Requirements

P1 Excel ingestion 前，parser gate 至少需要检查：

1. Reset worksheet dimensions before row/column profiling.
2. Record reported dimension and observed dimension mismatch.
3. Detect single-row versus multi-row headers.
4. Keep business row values out of governance summaries unless explicitly approved.
5. Record source hash, file size, profiled sheet count, row scan limit, observed rows, observed cols.
6. Reject or quarantine sheets with empty headers, duplicate critical headers, or unexplained multi-row tables.
7. For capped scans, label row count as observed sample count rather than full record count.

## 5. Next Promotion Step

`SRC-SCM-001` and `SRC-SCM-002` should enter owner review first. Excel sources can support review questions and parser design, but they should not be used as final Agent evidence until owner review and export metadata are complete.
