---
title: "KB P1 PoC Validation Plan"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/2026-06-18-KB_Platform_PRD_v2.1_business_agent_draft.md"
  - "drafts/analysis/kb-evidence-register.md"
  - "drafts/analysis/kb-license-risk-register.md"
scope: "P1 readonly proof-of-concept validation plan"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call in this document; future PoC provider calls require explicit approval"
---

# KB P1 PoC Validation Plan

## 0. 边界

P1 不是生产上线，而是可验证闭环。本文只定义验证计划，不执行入库、不调用模型、不部署服务、不修改生产配置。

## 1. P1 Goal

P1 的目标是证明企业知识库的最小闭环可用：

1. 业务域 taxonomy 能承载真实跨境电商问题。
2. 样板知识能从合法来源进入 evidence/source register。
3. 文本/PDF 知识能被解析、分块、索引、检索并引用。
4. `replenishment-agent` 能 readonly 调用 `supply-chain-kb` 和 `shared ontology` 输出可审计答案。
5. Eval set 能量化回答准确率、引用准确率、拒答质量和跨域路由质量。

## 2. P1 Non-Goals

- 不自动生成采购单。
- 不写 ERP/WMS/OMS/广告平台。
- 不修改 Listing、预算、价格、库存、渠道规则。
- 不接入音频、视频、多模态大规模生产管线。
- 不把 `pending`、`draft_only`、`legal_review_pending` 当成已验证事实。
- 不把本地 PoC 通过写成生产可用。

## 3. P1 Scope

| scope_area | included | excluded |
|---|---|---|
| domains | `supply-chain-kb`, `product-kb` | marketing/customer-service/finance/strategy 全量建设 |
| shared | `entity-dictionary`, `metric-dictionary`, `system-crosswalk` | 完整 enterprise ontology |
| agents | `replenishment-agent` readonly mode | 自动执行、写回、审批流闭环 |
| sources | 20-50 个样板 SKU/文档/字段定义 | 全量历史文档和所有平台数据 |
| modalities | text, markdown, PDF/text extraction candidate | audio/video/image native pipeline |
| storage | minimal backend, preferably PostgreSQL all-in-one or equivalent minimal local stack | Milvus/Neo4j/Memgraph 生产拆分 |
| MCP | readonly `query`, `doc_status`, `health` | 30+ tools 或写操作 |

## 4. P1 Inputs

| input_id | content | minimum_count | source requirement | status |
|---|---|---|---|---|
| IN-SCM-001 | 供应链 SOP/流程/异常处理 | 5-10 docs | source register + owner + version | pending |
| IN-SCM-002 | 库存/补货/库龄/在途/可用库存指标定义 | 20 metrics | source register + system field mapping | pending |
| IN-SCM-003 | ERP/WMS 字段样例或导出字段说明 | 1-3 source extracts | hash + export time + owner | pending |
| IN-PROD-001 | SKU/MSKU/ASIN/SPU 映射样例 | 20-50 records | source register + field dictionary | pending |
| IN-PROD-002 | Listing/商品属性/类目规则样例 | 10-20 docs | source register + platform/version | pending |
| IN-SHARED-001 | entity dictionary seed | 30-50 entities | owner reviewed | pending |
| IN-SHARED-002 | metric dictionary seed | 20-30 metrics | formula + grain + source table | pending |
| IN-SHARED-003 | system crosswalk seed | 30-50 field mappings | system owner reviewed | pending |

## 5. Evidence Gate

每条入库知识必须具备以下字段。

| field | required | description |
|---|---|---|
| source_id | yes | 对应 `kb-evidence-register.md` 或 source-register |
| evidence_grade | yes | A/B/C/D |
| source_uri | yes | 文件、系统导出、页面、文档链接或受控路径 |
| source_owner | yes | 业务 owner 或系统 owner |
| version | yes | 文档版本、导出时间或系统版本 |
| extracted_at | yes | 抽取时间 |
| modality | yes | text/pdf/table/image/audio/video |
| workspace | yes | 强隔离字段 |
| allowed_agents | yes | 可调用的 Agent 清单 |
| blocked_actions | yes | 禁止自动执行动作 |

### 5.1 Evidence Grades

| grade | source | Agent usage |
|---|---|---|
| A | ERP/WMS/OMS/API/exported facts, signed policy, approved metric dictionary | 可作为事实引用 |
| B | approved SOP, owner-reviewed field definition, official platform policy | 可作为规则引用 |
| C | meeting note, draft analysis, business hypothesis | 只能作为参考，必须提示低置信 |
| D | unverified screenshot, copied text, memory-only description | 不得作为结论证据 |

## 6. Technical Validation Steps

### 6.1 Ingestion

| test_id | test | pass_condition | artifact |
|---|---|---|---|
| T-ING-001 | ingest 20-50 sample docs | all docs produce chunk manifest with source_id/source_uri/workspace | chunk manifest |
| T-ING-002 | preserve evidence metadata | 100% chunks carry evidence_grade/source_owner/version | metadata audit |
| T-ING-003 | reject missing source | source-less docs are blocked or marked quarantine | quarantine log |
| T-ING-004 | parser comparison | selected parser records error rate and page coverage | parser report |

### 6.2 Retrieval

| test_id | test | pass_condition | artifact |
|---|---|---|---|
| T-RET-001 | single-domain query | top results come from expected domain and cite source_id | eval run |
| T-RET-002 | cross-domain query | result uses domain + shared ontology when required | trace log |
| T-RET-003 | evidence-grade filtering | D-grade evidence is not used for final conclusion | answer audit |
| T-RET-004 | rerank comparison | compare recall/precision/latency with rerank on/off | benchmark report |

### 6.3 Workspace Isolation

| test_id | test | pass_condition | artifact |
|---|---|---|---|
| T-ISO-001 | query without workspace | rejected | access log |
| T-ISO-002 | query wrong workspace | no cross-workspace data returned | isolation report |
| T-ISO-003 | agent unauthorized domain | denied or routed to human review | policy trace |

### 6.4 MCP Readonly Tools

P1 只要求最小 readonly MCP。

| tool | purpose | pass_condition |
|---|---|---|
| `query` | readonly search/answer | accepts workspace, domain, question; returns citations |
| `doc_status` | source/chunk/index status | returns source_id, status, evidence_grade |
| `health` | service health | returns dependency status without secrets |

## 7. Agent Validation

### 7.1 Replenishment Agent Routing Policy

```yaml
agent: replenishment-agent
mode: readonly
allowed_domains:
  - supply-chain-kb
  - product-kb
required_shared_layers:
  - shared/entity-dictionary
  - shared/metric-dictionary
  - shared/system-crosswalk
must_return:
  - answer
  - evidence
  - assumptions
  - confidence
  - blocked_actions
blocked_actions:
  - create_purchase_order
  - update_inventory
  - change_forecast
  - write_erp
  - send_supplier_message
```

### 7.2 Agent Output Contract

Agent 回答必须包含：

| section | required | rule |
|---|---|---|
| conclusion | yes | 简短回答，不能超过证据 |
| evidence | yes | source_id/evidence_id + citation |
| assumptions | yes | 明确推断 |
| uncertainty | yes | 缺数据时说明 |
| confidence | yes | high/medium/low |
| blocked_actions | yes | 列出需要人工审批的动作 |
| next_human_action | yes | 给业务 owner 的下一步 |

## 8. Eval Set Design

P1 最小 50 题。

| category | count | example |
|---|---:|---|
| source lookup | 10 | “可用库存的定义是什么，来自哪个系统字段？” |
| metric reasoning | 10 | “为什么 SKU A 看起来缺货但 ERP 可用库存不低？” |
| SOP retrieval | 10 | “什么情况下补货建议需要人工审批？” |
| cross-domain reasoning | 10 | “广告放量前需要检查哪些供应链约束？” |
| refusal/unknown | 10 | “没有来源的截图能否作为采购依据？” |

## 9. Metrics

| metric | target for P1 | note |
|---|---:|---|
| answer correctness | >= 80% on curated eval | 人工评分 |
| citation precision | >= 90% | 引用必须支持结论 |
| source coverage | >= 90% chunks have source_id | 缺来源不入正式索引 |
| evidence-grade compliance | 100% | D 级不得作为结论 |
| workspace isolation | 100% pass | P0 gate |
| refusal quality | >= 90% | 不足证据时必须拒答或降置信 |
| P95 latency | measured, no hard target in draft | 先测基线 |

## 10. P1 Exit Criteria

P1 通过必须同时满足：

1. `supply-chain-kb` 和 `product-kb` 样板域完成五层结构试填。
2. `shared/entity-dictionary`、`shared/metric-dictionary`、`shared/system-crosswalk` 有最小样例。
3. 所有样板知识有 source_id、evidence_grade、owner、version。
4. 50 题 eval 可重复运行，并生成结果报告。
5. `replenishment-agent` readonly trace 可审计。
6. workspace 隔离测试 100% 通过。
7. 许可证风险登记完成，MinerU/Neo4j/Memgraph 不被写成无风险。
8. 结论仍标记为 `P1 PoC validated`，不得写成 `production ready`。

## 11. Stop Conditions

出现以下情况，停止推进并回到人工确认：

| stop_condition | reason |
|---|---|
| source_id 缺失 | 无法审计来源 |
| license risk unresolved for selected parser | 可能影响商业部署 |
| workspace isolation fails | P0 安全问题 |
| eval citation precision below target | Agent 可能错误引用 |
| Agent attempts write action | 超出 readonly 边界 |
| data owner cannot confirm source | 证据等级不足 |

## 12. Work Plan

| phase | task | artifact |
|---|---|---|
| P1-A | source register and evidence-grade seed | source register draft |
| P1-B | taxonomy sample fill for supply-chain/product | domain sample folders or markdown blueprint |
| P1-C | shared ontology seed | entity/metric/crosswalk tables |
| P1-D | ingestion and chunk manifest | local PoC report |
| P1-E | retrieval and rerank benchmark | eval result report |
| P1-F | replenishment-agent readonly trace | agent trace samples |
| P1-G | final review | P1 PoC validation summary |
