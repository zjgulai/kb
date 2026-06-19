---
title: "Enterprise KB Directory Blueprint"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "drafts/analysis/2026-06-18-enterprise-kb-taxonomy-agent-architecture.md"
  - "drafts/analysis/2026-06-18-KB_Platform_PRD_v2.1_business_agent_draft.md"
  - "drafts/analysis/kb-evidence-register.md"
scope: "enterprise knowledge-base directory and metadata blueprint"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# Enterprise KB Directory Blueprint

## 0. 边界

本文件是 `enterprise-kb` 目录蓝图草稿，不创建真实业务知识库，不导入数据，不移动现有文件，不代表生产结构已确认。正式落地前必须经过业务 owner、数据 owner、法务/安全和 Agent 评估 owner 确认。

## 1. Design Principles

1. 业务问题优先于文件类型：先按业务域归属，再按方法论、执行、指标、映射、治理分层。
2. shared ontology 优先于跨域复制：SKU、ASIN、MSKU、仓库、渠道、指标、系统字段只在 shared 层定义主口径。
3. Agent 调用优先于人工浏览：目录和 metadata 必须能支持 routing、evidence filtering、workspace isolation。
4. 证据等级优先于内容完整度：没有来源登记的内容不得进入正式索引。
5. P1 优先样板域：先供应链和商品，再扩展营销、运营、渠道、客服、财务、战略。

## 2. Top-Level Blueprint

```text
enterprise-kb/
├─ domains/
│  ├─ marketing-kb/
│  ├─ product-kb/
│  ├─ supply-chain-kb/
│  ├─ operations-kb/
│  ├─ channel-kb/
│  ├─ customer-service-kb/
│  ├─ finance-kb/
│  └─ strategy-kb/
├─ shared/
│  ├─ entity-dictionary/
│  ├─ metric-dictionary/
│  ├─ system-crosswalk/
│  ├─ business-event-taxonomy/
│  └─ relationship-model/
├─ agents/
│  ├─ replenishment-agent/
│  ├─ product-research-agent/
│  ├─ ad-optimization-agent/
│  ├─ listing-agent/
│  ├─ voc-agent/
│  └─ executive-strategy-agent/
└─ governance/
   ├─ source-register/
   ├─ evidence-grade/
   ├─ access-control/
   ├─ versioning/
   ├─ eval-sets/
   └─ quality-review/
```

## 3. Standard Domain Template

每个 `domain-kb` 使用同一内部结构，保证 Agent 可以稳定路由。

```text
domain-kb/
├─ methodology/
│  ├─ frameworks/
│  ├─ models/
│  └─ principles/
├─ operations/
│  ├─ sop/
│  ├─ workflows/
│  ├─ scenarios/
│  └─ exception-handling/
├─ metrics-and-data/
│  ├─ metric-definitions/
│  ├─ formulas/
│  ├─ fact-tables/
│  ├─ dimension-tables/
│  ├─ dashboards/
│  └─ algorithms/
├─ crosswalk/
│  ├─ system-fields/
│  ├─ platform-rules/
│  ├─ external-standards/
│  └─ terminology-mapping/
└─ governance/
   ├─ source-register/
   ├─ evidence-grade/
   ├─ version-history/
   ├─ permission-policy/
   └─ quality-gates/
```

## 4. P1 Directory Slice

P1 不建设全量目录，只建设最小可验证切片。

```text
enterprise-kb-p1/
├─ domains/
│  ├─ supply-chain-kb/
│  │  ├─ operations/
│  │  │  ├─ sop/
│  │  │  ├─ workflows/
│  │  │  └─ exception-handling/
│  │  ├─ metrics-and-data/
│  │  │  ├─ metric-definitions/
│  │  │  ├─ formulas/
│  │  │  └─ fact-tables/
│  │  ├─ crosswalk/
│  │  │  ├─ system-fields/
│  │  │  └─ terminology-mapping/
│  │  └─ governance/
│  │     ├─ source-register/
│  │     └─ evidence-grade/
│  └─ product-kb/
│     ├─ operations/
│     │  ├─ sop/
│     │  └─ scenarios/
│     ├─ metrics-and-data/
│     │  ├─ metric-definitions/
│     │  └─ dimension-tables/
│     ├─ crosswalk/
│     │  ├─ platform-rules/
│     │  └─ terminology-mapping/
│     └─ governance/
│        ├─ source-register/
│        └─ evidence-grade/
├─ shared/
│  ├─ entity-dictionary/
│  ├─ metric-dictionary/
│  └─ system-crosswalk/
├─ agents/
│  └─ replenishment-agent/
└─ governance/
   ├─ source-register/
   ├─ evidence-grade/
   ├─ access-control/
   └─ eval-sets/
```

## 5. Domain Ownership

| domain | primary owner | common source systems | first Agent consumers |
|---|---|---|---|
| marketing-kb | Marketing / Growth | Amazon Ads, TikTok Ads, Meta Ads, GA, BI | ad-optimization-agent, executive-strategy-agent |
| product-kb | Product / Merchandising | PIM, ERP SKU master, platform catalog, competitor research | product-research-agent, listing-agent, replenishment-agent |
| supply-chain-kb | Supply Chain / SCM | ERP, WMS, OMS, forecast, supplier docs | replenishment-agent, executive-strategy-agent |
| operations-kb | Marketplace Operations | Amazon Seller Central, Shopify, TikTok Shop, SOP docs | listing-agent, voc-agent |
| channel-kb | Channel / Sales | marketplace rules, channel reports, price policies | listing-agent, product-research-agent |
| customer-service-kb | Customer Service / CX | tickets, reviews, returns, chat scripts | voc-agent, product-research-agent |
| finance-kb | Finance | ERP finance, settlement, cost, margin reports | executive-strategy-agent, ad-optimization-agent |
| strategy-kb | Management / Strategy | strategy docs, OKR, market research, board materials | executive-strategy-agent |

## 6. Shared Ontology Minimum Schema

### 6.1 Entity Dictionary

| field | required | example |
|---|---|---|
| entity_id | yes | `sku:ABC-001` |
| entity_type | yes | `sku`, `asin`, `msku`, `warehouse`, `channel`, `supplier`, `campaign` |
| canonical_name | yes | `ABC-001 Travel Adapter` |
| aliases | yes | `["ABC001", "MSKU-ABC-001"]` |
| source_system | yes | `ERP` |
| source_id | yes | `SRC-PROD-001` |
| owner | yes | `product_data_owner` |
| status | yes | `active`, `deprecated`, `pending_review` |

### 6.2 Metric Dictionary

| field | required | example |
|---|---|---|
| metric_id | yes | `metric:available_inventory` |
| canonical_name | yes | `可用库存` |
| business_definition | yes | `可用于销售或分配的库存口径` |
| formula | yes | `on_hand - allocated - frozen` |
| grain | yes | `sku x warehouse x date` |
| source_table_or_report | yes | `ERP warehouse inventory export` |
| refresh_frequency | yes | `daily` |
| owner | yes | `scm_data_owner` |
| evidence_grade | yes | `A` |

### 6.3 System Crosswalk

| field | required | example |
|---|---|---|
| crosswalk_id | yes | `xwalk:erp_available_inventory` |
| business_term | yes | `可用库存` |
| source_system | yes | `ERP` |
| source_field | yes | `available_qty` |
| target_entity_or_metric | yes | `metric:available_inventory` |
| transform_rule | yes | `cast numeric; exclude frozen qty` |
| owner | yes | `scm_data_owner` |
| version | yes | `2026-06-18` |

## 7. File Metadata Contract

每个正式知识文件必须有 frontmatter。

```yaml
---
title: ""
status: "draft | active | deprecated | archived"
workspace: ""
domain: ""
layer: "methodology | operations | metrics-and-data | crosswalk | governance | shared | agent"
source_id: ""
evidence_grade: "A | B | C | D"
source_owner: ""
version: ""
created_at: ""
updated_at: ""
allowed_agents: []
blocked_actions: []
production_impact: "production unchanged"
---
```

## 8. Naming Rules

| object | naming rule | example |
|---|---|---|
| domain folder | lowercase kebab-case + `-kb` | `supply-chain-kb` |
| agent folder | lowercase kebab-case + `-agent` | `replenishment-agent` |
| source id | `SRC-{DOMAIN}-{NNN}` | `SRC-SCM-001` |
| evidence id | `EV-{TYPE}-{NNN}` | `EV-LR-001` |
| metric id | `metric:{canonical_slug}` | `metric:available_inventory` |
| entity id | `{entity_type}:{stable_key}` | `sku:ABC-001` |
| crosswalk id | `xwalk:{source}_{term}` | `xwalk:erp_available_inventory` |

## 9. Agent Routing Implications

| question_type | primary domain | required shared layer | default Agent |
|---|---|---|---|
| 补货、缺货、库龄、在途、库存异常 | supply-chain-kb | entity, metric, system-crosswalk | replenishment-agent |
| 选品、竞品、属性、卖点 | product-kb | entity, relationship-model | product-research-agent |
| 广告预算、ACOS、转化、投放诊断 | marketing-kb | metric, entity, system-crosswalk | ad-optimization-agent |
| Listing 标题、五点、类目合规 | product-kb + channel-kb | entity, platform-rules | listing-agent |
| 差评、退货、客服问题归因 | customer-service-kb + product-kb | entity, business-event-taxonomy | voc-agent |
| 经营诊断、战略风险、跨域汇总 | strategy-kb + finance-kb | all shared layers | executive-strategy-agent |

## 10. Governance Gates

| gate | requirement | blocking level |
|---|---|---|
| source-register | source_id, owner, version, source_uri, evidence_grade | P0 |
| access-control | workspace and allowed_agents present | P0 |
| license | dependency and model license registered | P0 for technical components |
| eval | domain eval set exists before Agent release | P1 |
| quality-review | owner-reviewed active docs only | P1 |
| versioning | update history and deprecation policy | P1 |

## 11. Open Decisions

| decision_id | question | recommendation | status |
|---|---|---|---|
| DEC-001 | 是否创建真实 `enterprise-kb/` 目录 | 先不创建；先用本蓝图和样板文件确认 taxonomy | pending |
| DEC-002 | P1 source register 用 Markdown 还是 CSV/JSONL | 先 Markdown 审阅，PoC 前转 JSONL/CSV | pending |
| DEC-003 | shared ontology 是否单独成库 | P1 用 shared folder；P2 再决定图数据库或关系表 | pending |
| DEC-004 | Agent playbook 放 `agents/` 还是平台配置 | P1 放 Markdown/YAML 草稿；实现期再转配置 | pending |
| DEC-005 | 是否回写主 PRD | 等 evidence/register/license/P1 plan 审阅后再回写 | pending |
