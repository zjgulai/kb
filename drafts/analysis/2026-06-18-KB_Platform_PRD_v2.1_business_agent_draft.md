---
title: "多模态企业知识库平台 PRD v2.1"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/2026-06-18-enterprise-kb-taxonomy-agent-architecture.md"
  - "drafts/analysis/2026-06-18-kb-secondary-verification.md"
  - "drafts/analysis/2026-06-18-kb-remediation-plan-v2.md"
scope: "business architecture plus technical baseline revision draft"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# 多模态企业知识库平台 PRD v2.1

## 0. 文档状态

| 字段 | 内容 |
|---|---|
| 文档名称 | 多模态企业知识库平台 PRD v2.1 |
| 状态 | draft · architecture proposal · secondary verification completed · implementation not verified |
| 本版目标 | 在原技术架构 PRD 上补齐企业知识分类、shared ontology、Agent 调用架构、治理和评估体系 |
| 本版边界 | docs-only draft；不代表已实现、不代表生产可用、不改生产配置 |
| 原始技术 PRD | `KB_Platform_PRD.md` |
| 关键新增 | 企业业务域 taxonomy、每域五层结构、shared ontology、Agent playbooks、P1 样板域、评估集 |

## 1. 背景与问题重定义

原 `KB_Platform_PRD.md` 已经覆盖解析、向量化、图谱、检索、MCP、部署和监控等技术底座。但跨境电商企业要建设的不是单纯 RAG 系统，而是可被 AI Agent 稳定调用的企业知识基础设施。

因此，v2.1 将项目目标从“多模态知识库训练平台”扩展为：

> 建设一套面向跨境电商企业经营决策和业务执行的多域知识库平台，使 AI Agent 能按业务问题准确检索、推理、引用证据、识别不确定性，并在需要人工审批时停止自动执行。

### 1.1 当前 v2.0 的主要缺口

| 缺口 | 影响 |
|---|---|
| 缺少企业级业务域分类 | 知识会按文件或技术模块堆积，Agent 不知道应查哪个业务域 |
| 缺少 shared ontology | SKU、ASIN、MSKU、仓库、渠道、指标口径在各域漂移 |
| 缺少 Agent playbook | Agent 只能做语义搜索，不能稳定执行诊断路径 |
| 缺少业务证据等级 | Agent 无法区分系统事实、正式 SOP、会议纪要和草稿 |
| 缺少业务评估集 | 无法证明 Agent 是否真的提升业务问题解决准确率 |

## 2. 设计目标

### 2.1 产品目标

1. 建立企业级业务知识分类，让营销、商品、供应链、运营、渠道、客服、财务、战略等知识有稳定归属。
2. 建立跨域共享语义层，统一实体、指标、业务事件和系统字段映射。
3. 建立 Agent 调用架构，让不同智能体按问题类型选择知识库、检索顺序和输出边界。
4. 建立证据等级和评估集，持续衡量知识库对 AI 准确率的贡献。

### 2.2 非目标

- 不在本阶段自动生成采购单、调预算、改 Listing、修改 ERP/WMS 数据。
- 不把未验证草稿或会议纪要作为高置信事实。
- 不在没有法务确认前把 AGPL/GPL/BSL 组件写成商业无风险。
- 不把技术 PoC 通过等同于业务知识库完成。

## 3. 企业知识库总体架构

推荐采用“业务域分库 + shared ontology + Agent playbook + governance”的混合架构。

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

### 3.1 设计理由

| 层 | 作用 | 为什么必须独立 |
|---|---|---|
| domains | 存放业务知识本体 | 业务 owner 易维护，权限边界清晰 |
| shared | 统一实体、指标、字段、事件 | 避免跨域问题中概念漂移 |
| agents | 定义智能体如何调用知识 | 让 Agent 从“搜索资料”变成“按 playbook 解决问题” |
| governance | 管来源、权限、版本、评估 | 避免低质量知识污染高置信答案 |

## 4. 业务域 taxonomy

| 业务域 | 核心问题 | 典型知识 |
|---|---|---|
| marketing-kb | 投放、内容、活动、增长 | 广告策略、活动复盘、投放 SOP、素材方法论、预算规则 |
| product-kb | 选品、定价、生命周期、Listing | 商品属性、竞品分析、类目规则、Listing 优化、生命周期策略 |
| supply-chain-kb | 预测、备货、补货、库存、物流 | 供应链理论、补货 SOP、库存指标、ERP/WMS 字段映射 |
| operations-kb | 订单、履约、异常、平台运营 | 店铺 SOP、平台规则、异常处理、账号健康 |
| channel-kb | Amazon、Walmart、TikTok、Shopify 等渠道 | 平台政策、类目规则、流量机制、履约方式 |
| customer-service-kb | 售后、评价、VOC、工单 | 客诉分类、话术、VOC 标签、Zendesk/评论映射 |
| finance-kb | 毛利、费用、现金流、预算 | 利润模型、费用口径、现金流规则、预算控制 |
| strategy-kb | 品类、市场、竞品、组织战略 | 市场研究、品类战略、年度规划、竞品情报 |

## 5. 每个业务域的标准五层结构

每个 `domain-kb` 统一采用以下结构：

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

### 5.1 五层结构的 Agent 价值

| 层 | Agent 调用价值 |
|---|---|
| methodology | 给出原则、模型和框架，支持复杂判断 |
| operations | 给出 SOP、流程和异常处理，支持执行建议 |
| metrics-and-data | 给出指标口径、公式和数据血缘，支持事实计算 |
| crosswalk | 把业务概念映射到 ERP/WMS/平台字段，支持查数和对账 |
| governance | 判断来源、版本、权限和证据等级，支持可信输出 |

## 6. shared ontology

### 6.1 entity-dictionary

必须统一以下实体：

| 实体 | 说明 |
|---|---|
| SPU | 产品族或产品概念 |
| SKU | 内部销售/库存管理单位 |
| MSKU | 平台或仓储渠道下的库存单位 |
| ASIN | Amazon 商品实体 |
| Listing | 渠道货架表达 |
| Store | 店铺 |
| Channel | Amazon、Walmart、TikTok、Shopify 等 |
| Warehouse | FBA、WFS、3PL、自有仓 |
| Supplier | 供应商 |
| Campaign | 广告活动 |
| Review / Ticket | 评论和工单 |

### 6.2 metric-dictionary

第一阶段必须统一：

| 指标域 | 核心指标 |
|---|---|
| 销售 | GMV、订单数、销量、ASP、CVR |
| 广告 | Spend、ROAS、ACOS、CTR、CPC、CPA |
| 库存 | 可用库存、在途库存、预占库存、冻结库存、计划库存、库存周转 |
| 供应链 | MOQ、交期、补货周期、安全库存、缺货率、售罄率 |
| 财务 | 毛利、贡献利润、平台费、物流费、现金占用 |
| 客服 | 退货率、差评率、VOC 标签、投诉率 |

### 6.3 system-crosswalk

系统映射必须覆盖：

```text
system-crosswalk/
├─ erp-fields.md
├─ wms-fields.md
├─ amazon-fields.md
├─ walmart-fields.md
├─ tiktok-fields.md
├─ shopify-fields.md
├─ klaviyo-fields.md
└─ zendesk-fields.md
```

每个字段映射文档至少包含：

| 字段 | 含义 |
|---|---|
| business_term | 业务术语 |
| system_name | 系统名称 |
| field_name | 系统字段 |
| data_type | 数据类型 |
| refresh_frequency | 刷新频率 |
| owner | 数据 owner |
| confidence | verified / partial / pending |
| notes | 限制说明 |

### 6.4 business-event-taxonomy

第一阶段定义以下事件：

```text
launch
promotion
demand_spike
stockout
overstock
supplier_delay
listing_suppression
negative_review_spike
ad_budget_change
price_change
platform_policy_change
```

## 7. Agent playbook

### 7.1 Agent 清单

| Agent | 主要调用域 | 输出 |
|---|---|---|
| replenishment-agent | supply-chain, marketing, finance, channel | 补货建议、风险、审批边界 |
| product-research-agent | product, strategy, channel, customer-service | 选品建议、竞品差异、机会点 |
| ad-optimization-agent | marketing, product, finance, channel | 投放诊断、预算调整建议 |
| listing-agent | product, channel, customer-service | 标题、卖点、属性、合规检查 |
| voc-agent | customer-service, product, operations | VOC 归因、产品问题、话术建议 |
| executive-strategy-agent | strategy, finance, marketing, supply-chain | 经营诊断、战略建议、风险提示 |

### 7.2 Agent routing policy 示例

```yaml
agent: replenishment-agent
intent_types:
  - stockout_risk
  - replenishment_decision
  - overstock_clearance
required_kbs:
  - agents/replenishment-agent
  - shared/entity-dictionary
  - shared/metric-dictionary
  - shared/system-crosswalk
  - domains/supply-chain-kb
optional_kbs:
  - domains/marketing-kb
  - domains/finance-kb
  - domains/channel-kb
must_return:
  - answer
  - evidence
  - metric_values_used
  - assumptions
  - manual_review_boundary
blocked_actions:
  - auto_create_purchase_order
  - auto_change_ad_budget
```

### 7.3 Agent 输出格式

所有业务决策型 Agent 输出必须区分：

```text
事实：
- 来自系统、正式指标或已验证文档的事实。

推断：
- 基于事实和规则得到的判断。

建议：
- 可执行建议或下一步检查动作。

不确定项：
- 数据缺失、口径冲突、来源不足、时间滞后。

人工边界：
- 不自动创建采购单，不自动调整预算，不自动修改平台资料。
```

## 8. 供应链样板域

第一阶段建议把 `supply-chain-kb` 作为样板域。

```text
domains/supply-chain-kb/
├─ methodology/
│  ├─ supply-chain-theory.md
│  ├─ inventory-planning-framework.md
│  ├─ safety-stock-model.md
│  └─ demand-forecasting-principles.md
├─ operations/
│  ├─ replenishment-sop.md
│  ├─ procurement-sop.md
│  ├─ warehouse-transfer-sop.md
│  ├─ fba-shipment-sop.md
│  ├─ stockout-response.md
│  └─ overstock-clearance.md
├─ metrics-and-data/
│  ├─ available-inventory.md
│  ├─ in-transit-inventory.md
│  ├─ reserved-inventory.md
│  ├─ frozen-inventory.md
│  ├─ inventory-turnover.md
│  ├─ sell-through-rate.md
│  └─ demand-forecast-accuracy.md
├─ crosswalk/
│  ├─ erp-inventory-fields.md
│  ├─ wms-stock-fields.md
│  ├─ amazon-fba-fields.md
│  ├─ walmart-wfs-fields.md
│  └─ tiktok-shop-fields.md
└─ governance/
   ├─ source-register.md
   ├─ evidence-grade.md
   ├─ version-policy.md
   ├─ permission-policy.md
   └─ quality-gates.md
```

## 9. 商品样板域

第二个样板域建议为 `product-kb`，用于支撑选品、Listing、属性标准化和渠道货架表达。

```text
domains/product-kb/
├─ methodology/
│  ├─ category-research-framework.md
│  ├─ product-lifecycle-model.md
│  ├─ pricing-framework.md
│  └─ listing-quality-principles.md
├─ operations/
│  ├─ new-product-research-sop.md
│  ├─ listing-creation-sop.md
│  ├─ product-attribute-cleanup-sop.md
│  └─ lifecycle-review-sop.md
├─ metrics-and-data/
│  ├─ product-profitability.md
│  ├─ listing-conversion.md
│  ├─ category-rank.md
│  └─ review-rating.md
├─ crosswalk/
│  ├─ sku-asin-msku-mapping.md
│  ├─ amazon-category-fields.md
│  ├─ walmart-category-fields.md
│  └─ tiktok-product-fields.md
└─ governance/
   ├─ source-register.md
   ├─ evidence-grade.md
   ├─ version-policy.md
   └─ quality-gates.md
```

## 10. evidence grade

所有可检索知识必须带证据等级。

| 等级 | 来源 | Agent 用法 |
|---|---|---|
| A | ERP/WMS/API/系统导出/已验证指标 | 可作为事实依据 |
| B | 正式 SOP/审批过的制度/发布过的口径 | 可作为规则依据 |
| C | 会议纪要/复盘/人工经验 | 可作为参考，必须注明限制 |
| D | 未验证草稿/外部资料/推测 | 只能作为候选，不可直接决策 |

## 11. 评估体系

### 11.1 评估不只测检索

每个 Agent 至少测四类问题：

| 类型 | 示例 | 评估重点 |
|---|---|---|
| 事实检索 | “可用库存的定义是什么？” | 是否引用正确指标口径 |
| 诊断推理 | “这个 SKU 是否有断货风险？” | 是否调用正确指标和规则 |
| 跨域综合 | “广告放量是否需要补货？” | 是否跨 marketing/supply-chain/finance |
| 拒答和边界 | “直接帮我创建采购单” | 是否触发人工边界 |

### 11.2 第一阶段最小评估集

| 业务域 | 数量 |
|---|---:|
| supply-chain-kb | 15 |
| product-kb | 10 |
| marketing-kb | 8 |
| finance-kb | 5 |
| channel-kb | 5 |
| shared ontology | 5 |
| refusal / manual boundary | 2 |
| 合计 | 50 |

### 11.3 核心评估指标

| 指标 | 目标 |
|---|---|
| Citation Accuracy | >= 0.90 |
| Correct KB Routing | >= 0.85 |
| Entity Resolution Accuracy | >= 0.90 |
| Metric Definition Accuracy | >= 0.95 |
| Cross-domain Answer Quality | 人工评分 >= 4/5 |
| Manual Boundary Compliance | 100% |

## 12. 技术架构修订口径

### 12.1 状态修订

原 PRD 不应继续标注为“正式发布”。建议状态：

```text
draft · architecture proposal · secondary verification completed · implementation not verified
```

### 12.2 许可证修订

二次核验显示 `opendatalab/MinerU2.5-2509-1.2B` 模型卡 license 为 `agpl-3.0`，与原 PRD 中 Apache 2.0 口径冲突。必须作为 P0 风险进入许可证审查。

### 12.3 LightRAG 检索修订

当前官方 README 支持 `mix` 默认、rerank、embedding 锁定和 PostgreSQL all-in-one 等生产方向。原 PRD 中 “LightRAG 默认 hybrid” 的 M3 表述需要修订为：

> 生产必须显式锁定检索配置，并用本项目评估集验证质量、延迟、成本权衡。

### 12.4 MCP 修订

`lightrag-mcp-server` 的包名、工具数、transport 仍需 P0 验证。P1 不应以 “30+ tools” 作为验收条件，而应先要求最小 readonly tools：

```text
health_check
query
get_doc_status
```

### 12.5 存储修订

P1 优先验证 PostgreSQL all-in-one 或最小后端组合。Milvus、Neo4j、Memgraph 拆分进入 P2 后评估，不作为第一阶段默认生产依赖。

## 13. 第一阶段落地范围

### 13.1 Phase 0：分类和命名冻结

产出：

- 企业业务域 taxonomy。
- 每个业务域 owner。
- shared ontology 最小字段。
- Agent 清单和优先级。

验收：

- 所有知识库目录命名稳定。
- `workspace`、`domain`、`agent`、`evidence_grade` 字段定义完成。

### 13.2 Phase 1：两个样板域

建设：

- `domains/supply-chain-kb`
- `domains/product-kb`
- `shared/entity-dictionary`
- `shared/metric-dictionary`
- `shared/system-crosswalk`
- `governance/source-register`

验收：

- 50 个 eval questions 能跑通。
- Agent 回答能引用来源。
- 跨域问题能调用 shared ontology。

### 13.3 Phase 2：三个高价值 Agent

建设：

- `replenishment-agent`
- `listing-agent`
- `ad-optimization-agent`

验收：

- 每个 Agent 有 routing policy。
- 每个 Agent 有 blocked actions。
- 每个 Agent 有 eval set。

### 13.4 Phase 3：全域扩展

扩展到：

- marketing
- operations
- channel
- customer-service
- finance
- strategy

验收：

- 每个域都有五层结构。
- 每个域都有 source register 和 evidence grade。
- 每个域都有最少 20 个评估问题。

## 14. P1 PRD 验收门槛

P1 不是生产上线，而是可验证闭环。

| Gate | Pass Condition |
|---|---|
| Taxonomy | domains/shared/agents/governance 四层结构确认 |
| Sample Domains | supply-chain-kb 与 product-kb 有五层结构 |
| Shared Ontology | entity、metric、system-crosswalk 最小版完成 |
| Agent Playbook | replenishment-agent 有 routing policy |
| Evidence | 每条样板知识有 evidence grade |
| Evaluation | 50 题 eval set 可执行 |
| Security | workspace 隔离设计完成 |
| Licensing | MinerU/Neo4j/Memgraph 等风险记录完成 |

## 15. 下一步执行建议

建议下一轮执行：

1. 新建 `drafts/analysis/kb-evidence-register.md`。
2. 新建 `drafts/analysis/kb-license-risk-register.md`。
3. 新建 `drafts/analysis/kb-p1-poc-validation-plan.md`。
4. 生成 `enterprise-kb` 目录蓝图草稿。
5. 再决定是否把本 v2.1 draft 回写到主 PRD。

本文件仍是草稿，不代表已完成实现，也不代表生产可用。
