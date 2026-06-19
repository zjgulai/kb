---
title: "企业知识库业务分类与 AI Agent 调用架构"
status: "draft"
created_at: "2026-06-18"
source_context:
  - "KB_Platform_PRD.md"
  - "用户截图：cross-border-ecommerce-supply-chain-kb 五层结构"
scope: "business knowledge architecture supplement"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# 企业知识库业务分类与 AI Agent 调用架构

## 0. 目的

当前 `KB_Platform_PRD.md` 主要解决技术底座问题：解析、向量化、图谱、检索、MCP、评估和部署。但对跨境电商企业来说，仅有技术架构不够。真正决定 AI Agent 调用准确性、问题诊断质量和业务可用性的，是企业知识如何被分类、定义、治理、路由和评估。

本补充草稿定义企业知识库的信息架构，目标是让知识库从“资料仓库”升级为“AI 可调用的问题解决系统”。

## 1. 核心判断

### 1.1 用户截图结构的定位

截图中的结构：

```text
cross-border-ecommerce-supply-chain-kb/
├─ methodology/
├─ operations/
├─ metrics-and-data/
├─ crosswalk/
└─ governance/
```

这是一个很好的“单业务域知识库内部结构”，尤其适合供应链域。它不应该直接作为企业知识库顶层分类，而应作为每个业务域内部统一模板。

原因：

- `methodology` 解决原则和模型。
- `operations` 解决流程和 SOP。
- `metrics-and-data` 解决指标、公式、事实表和看板口径。
- `crosswalk` 解决 ERP、WMS、平台字段和业务术语映射。
- `governance` 解决来源、权限、版本、质量和适用范围。

如果每个业务域都采用这个五层结构，AI Agent 在检索时就能稳定判断“该找方法论、操作流程、指标定义、系统映射，还是治理边界”。

### 1.2 当前 PRD 的主要缺口

当前 PRD 缺少三层业务架构：

1. **企业业务域 taxonomy**：营销、商品、供应链、运营、渠道、客服、财务、战略等如何分库。
2. **跨域共享 ontology**：SKU、MSKU、ASIN、店铺、渠道、仓库、供应商、广告活动、指标、事件等如何统一定义。
3. **Agent 调用 playbook**：不同 AI Agent 面对不同问题时，应该先查哪个知识库、用哪些指标、引用什么证据、何时要求人工确认。

没有这三层，技术 RAG 容易退化为“语义搜索”。有这三层，AI Agent 才能稳定地完成“诊断、推理、建议、执行边界判断”。

## 2. 行业案例启发

### 2.1 Amazon：taxonomy + catalog + behavior signals

Amazon AutoKnow 会结合既有产品 taxonomy、用户日志和商品目录来构建 product graph，用于新增产品类型、属性值、纠错和同义词识别。对跨境电商企业的启发是：商品知识库不能只存商品说明，还要结合类目、属性、用户行为和平台反馈。

来源：https://www.amazon.science/blog/building-product-graphs-automatically

### 2.2 Walmart：Retail Graph 连接商品、类目和发现体验

Walmart Retail Graph 关注商品知识图谱对搜索、推荐、类目映射和商品发现的支撑。对跨境电商企业的启发是：商品、渠道、平台类目和属性映射必须作为知识库的一等公民，而不是散落在 Excel 或运营经验里。

来源：https://medium.com/walmartglobaltech/retail-graph-walmarts-product-knowledge-graph-6ef7357963bc

### 2.3 Zalando：ontology 承载业务语义

Zalando 的语义技术实践强调 ontology，用机器可读方式表达材质、风格、用途、场景等业务概念。对跨境电商企业的启发是：`style`、`material`、`fit`、`use_case`、`audience`、`seasonality` 等商品语义应该被结构化，否则 AI 只能靠文本相似度猜。

来源：https://engineering.zalando.com/posts/2018/03/semantic-web-technologies.html

### 2.4 DoorDash：LLM 辅助属性抽取和实体消歧

DoorDash 用 LLM 从非结构化 SKU 数据中抽取品牌、属性并做 duplicate entity 判断，补充 product knowledge graph。对跨境电商企业的启发是：AI 能参与知识建设，但必须有实体字典、属性 schema、置信度和人工审核闭环。

来源：https://careersatdoordash.com/blog/building-doordashs-product-knowledge-graph-with-large-language-models/

## 3. 设计原则

### 3.1 面向 AI Agent 的知识组织原则

1. **按业务问题组织，而不是只按资料来源组织**  
   AI Agent 需要回答“怎么办”，不是只检索“哪里有文件”。

2. **每条知识必须有来源、适用范围和证据等级**  
   同一个 SOP 在不同平台、渠道、国家、仓库、时期可能不适用。

3. **共享实体和指标必须统一**  
   如果 `SKU`、`MSKU`、`ASIN`、`可用库存`、`在途库存`、`ACOS` 在不同知识库里口径不同，Agent 会产生稳定性错误。

4. **业务域知识和 Agent playbook 分离**  
   业务知识回答“事实和规则是什么”；Agent playbook 定义“面对问题如何调用知识”。

5. **分类必须服务评估集**  
   每个业务域、每类问题都要能设计 eval question，否则无法证明知识库提升了准确率。

## 4. 方案 A：业务域分库 + 每域五层结构

### 4.1 结构

```text
enterprise-kb/
├─ marketing-kb/
├─ product-kb/
├─ supply-chain-kb/
├─ operations-kb/
├─ channel-kb/
├─ customer-service-kb/
├─ finance-kb/
├─ strategy-kb/
├─ data-and-metrics-kb/
└─ governance-kb/
```

每个业务域内部统一采用五层结构：

```text
domain-kb/
├─ methodology/
├─ operations/
├─ metrics-and-data/
├─ crosswalk/
└─ governance/
```

### 4.2 业务域定义

| 业务域 | 主要问题 | 典型知识 |
|---|---|---|
| marketing-kb | 投放、内容、活动、增长 | 广告策略、活动复盘、投放 SOP、素材方法论、预算规则 |
| product-kb | 选品、定价、生命周期、Listing | 商品属性、竞品分析、类目规则、Listing 优化、生命周期策略 |
| supply-chain-kb | 预测、备货、补货、库存、物流 | 供应链理论、补货 SOP、库存指标、ERP/WMS 字段映射 |
| operations-kb | 订单、履约、异常、平台运营 | 店铺 SOP、平台规则、异常处理、账号健康 |
| channel-kb | Amazon、Walmart、TikTok、Shopify 等渠道 | 平台政策、类目规则、流量机制、履约方式 |
| customer-service-kb | 售后、评价、VOC、工单 | 客诉分类、话术、VOC 标签、Zendesk/评论映射 |
| finance-kb | 毛利、费用、现金流、预算 | 利润模型、费用口径、现金流规则、预算控制 |
| strategy-kb | 品类、市场、竞品、组织战略 | 市场研究、品类战略、年度规划、竞品情报 |
| data-and-metrics-kb | 指标口径、数仓、事实表、维表 | 指标字典、公式、BI 看板、数据血缘 |
| governance-kb | 证据、权限、版本、质量 | source register、权限矩阵、质量门禁、审计 SOP |

### 4.3 优点

- 组织接受度高，容易指定业务 owner。
- 与企业部门和数据权限天然匹配。
- 适合从供应链、商品、营销等重点域逐步建设。
- 每个业务域可以独立评估知识质量。

### 4.4 缺点

- 跨域问题容易被单域检索截断。
- Agent 需要额外路由逻辑判断该查哪些域。
- 如果 shared ontology 不建设，跨域实体和指标会逐渐漂移。

### 4.5 适用阶段

适合第一阶段落地。建议先选：

- `supply-chain-kb`
- `product-kb`
- `data-and-metrics-kb`
- `governance-kb`

## 5. 方案 B：任务型知识库 + Agent 调用优先

### 5.1 结构

```text
agent-task-kb/
├─ replenishment-decision-kb/
├─ listing-optimization-kb/
├─ ad-diagnosis-kb/
├─ product-research-kb/
├─ channel-operations-kb/
├─ voc-and-review-kb/
├─ profit-diagnosis-kb/
└─ strategy-research-kb/
```

每个任务库内部结构：

```text
task-kb/
├─ problem-types/
├─ diagnosis-playbooks/
├─ decision-rules/
├─ metrics-contracts/
├─ data-crosswalk/
├─ evidence-cases/
└─ guardrails/
```

### 5.2 示例：补货决策知识库

```text
replenishment-decision-kb/
├─ problem-types/
│  ├─ stockout-risk.md
│  ├─ overstock-risk.md
│  ├─ demand-spike.md
│  └─ supplier-delay.md
├─ diagnosis-playbooks/
│  ├─ replenishment-diagnosis-flow.md
│  └─ inventory-aging-diagnosis-flow.md
├─ decision-rules/
│  ├─ reorder-point-policy.md
│  ├─ safety-stock-policy.md
│  └─ clearance-trigger-policy.md
├─ metrics-contracts/
│  ├─ available-inventory.md
│  ├─ in-transit-inventory.md
│  └─ reserved-and-frozen-inventory.md
├─ data-crosswalk/
│  ├─ erp-inventory-fields.md
│  ├─ wms-stock-fields.md
│  └─ amazon-fba-fields.md
├─ evidence-cases/
│  ├─ 2026-q1-stockout-postmortem.md
│  └─ 2026-q2-overstock-clearance-case.md
└─ guardrails/
   ├─ manual-approval-boundary.md
   └─ no-auto-po-policy.md
```

### 5.3 优点

- 最贴近 AI Agent 的问题解决过程。
- 检索路径清晰：问题类型 -> 诊断 playbook -> 指标 -> 数据映射 -> 决策规则 -> guardrail。
- 适合做高价值 Agent，例如补货 Agent、广告诊断 Agent、Listing Agent。

### 5.4 缺点

- 前期建模难度更高。
- 需要先梳理高频业务问题。
- 任务型知识库会引用多个业务域，如果没有源域知识库，容易重复。

### 5.5 适用阶段

适合第二阶段，在业务域知识库已有基础后，为高频任务建立 Agent playbook。

## 6. 方案 C：推荐方案，业务域分库 + 共享 ontology + Agent playbook

### 6.1 总体结构

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

### 6.2 为什么推荐方案 C

方案 C 把三件事分开：

- `domains/` 管理业务知识本体。
- `shared/` 管理跨域共同语言。
- `agents/` 管理 AI 如何调用知识解决问题。

这样既保留业务部门可维护性，又能支持跨域推理。

### 6.3 Agent 调用示例

用户问题：

```text
TikTok 广告最近放量，这个 SKU 是否需要补货？
```

推荐调用路径：

```text
1. agents/replenishment-agent/
   识别问题类型：demand_spike_replenishment

2. shared/entity-dictionary/
   解析 SKU、MSKU、ASIN、店铺、渠道、仓库、供应商

3. shared/metric-dictionary/
   读取可用库存、在途库存、预占库存、冻结库存、日均销量、预测销量、毛利

4. domains/marketing-kb/
   检索广告放量原因、投放计划、活动周期、预算变化

5. domains/supply-chain-kb/
   检索补货规则、交期、MOQ、安全库存、库存周转

6. domains/finance-kb/
   检索毛利、现金流、资金占用、清仓风险

7. governance/evidence-grade/
   判断证据等级和是否需要人工审批

8. 输出
   给出补货建议、关键证据、风险、需人工确认事项
```

## 7. 企业知识库全景分类

### 7.1 domains 层

| Domain | 子库 | 说明 |
|---|---|---|
| marketing-kb | ads, content, campaign, influencer, crm | 增长和获客 |
| product-kb | category, attribute, pricing, lifecycle, listing | 商品和货架表达 |
| supply-chain-kb | planning, procurement, inventory, warehouse, logistics | 供应、库存、履约 |
| operations-kb | account-health, order, fulfillment, platform-policy | 店铺和平台运营 |
| channel-kb | amazon, walmart, tiktok, shopify, temu, shein | 渠道差异规则 |
| customer-service-kb | ticket, review, return, complaint, voc | 客户声音和售后 |
| finance-kb | gross-margin, fee, cashflow, budget, settlement | 财务口径和约束 |
| strategy-kb | market, competitor, category-strategy, annual-plan | 战略研究和规划 |

### 7.2 shared 层

```text
shared/
├─ entity-dictionary/
│  ├─ product-identity.md        # SPU/SKU/MSKU/ASIN/FNSKU/Listing
│  ├─ channel-identity.md        # 店铺、站点、平台、渠道
│  ├─ supply-identity.md         # 供应商、仓库、物流商、采购单
│  └─ customer-identity.md       # 客户、会员、工单、评论、标签
├─ metric-dictionary/
│  ├─ sales-metrics.md
│  ├─ ad-metrics.md
│  ├─ inventory-metrics.md
│  ├─ finance-metrics.md
│  └─ service-metrics.md
├─ system-crosswalk/
│  ├─ erp-fields.md
│  ├─ wms-fields.md
│  ├─ amazon-fields.md
│  ├─ tiktok-fields.md
│  ├─ shopify-fields.md
│  ├─ klaviyo-fields.md
│  └─ zendesk-fields.md
├─ business-event-taxonomy/
│  ├─ launch.md
│  ├─ promotion.md
│  ├─ stockout.md
│  ├─ overstock.md
│  ├─ listing-suppression.md
│  └─ negative-review-spike.md
└─ relationship-model/
   ├─ product-channel-inventory.md
   ├─ ad-sales-inventory.md
   ├─ voc-product-quality.md
   └─ price-margin-cashflow.md
```

### 7.3 agents 层

| Agent | 主要调用域 | 输出 |
|---|---|---|
| replenishment-agent | supply-chain, marketing, finance, channel | 补货建议、风险、审批边界 |
| product-research-agent | product, strategy, channel, customer-service | 选品建议、竞品差异、机会点 |
| ad-optimization-agent | marketing, product, finance, channel | 投放诊断、预算调整建议 |
| listing-agent | product, channel, customer-service | 标题、卖点、属性、合规检查 |
| voc-agent | customer-service, product, operations | VOC 归因、产品问题、话术建议 |
| executive-strategy-agent | strategy, finance, marketing, supply-chain | 经营诊断、战略建议、风险提示 |

## 8. 每个业务域的标准内部模板

每个 `domain-kb` 建议采用以下模板。

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

## 9. 供应链域样板

建议优先把供应链域作为第一个样板，因为它天然依赖指标口径、系统字段、SOP、异常处理和跨域信号。

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

## 10. AI Agent 准确率设计

### 10.1 检索路由必须显式化

每个 Agent 需要有 routing policy：

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

### 10.2 答案必须区分事实、推断和建议

Agent 输出格式建议：

```text
事实：
- 当前可用库存、在途库存、预占库存、日均销量、广告变化。

推断：
- 按当前销量和在途周期，预计 X 天后缺货。

建议：
- 建议补货 X 件，或先人工确认供应商交期。

不确定项：
- 某渠道库存未同步，某指标来源未验证。

人工边界：
- 不自动创建采购单，不自动调整广告预算。
```

### 10.3 每个知识块必须有 evidence grade

建议等级：

| 等级 | 含义 | Agent 用法 |
|---|---|---|
| A | 系统导出/API/已验证指标 | 可作为事实依据 |
| B | 正式 SOP/审批过的制度 | 可作为规则依据 |
| C | 会议纪要/人工经验/复盘 | 可作为参考，但需注明 |
| D | 未验证草稿/外部资料 | 只能作为候选，不可直接决策 |

## 11. 评估体系

### 11.1 评估集不应只测检索

每个 Agent 至少测四类问题：

| 类型 | 示例 | 评估重点 |
|---|---|---|
| 事实检索 | “可用库存的定义是什么？” | 是否引用正确指标口径 |
| 诊断推理 | “这个 SKU 是否有断货风险？” | 是否调用正确指标和规则 |
| 跨域综合 | “广告放量是否需要补货？” | 是否跨 marketing/supply-chain/finance |
| 拒答和边界 | “直接帮我创建采购单” | 是否触发 manual review |

### 11.2 第一阶段最小评估集

建议第一阶段不要追求 200-500 题，先做 50 题：

| 业务域 | 数量 |
|---|---:|
| supply-chain-kb | 15 |
| product-kb | 10 |
| marketing-kb | 8 |
| finance-kb | 5 |
| channel-kb | 5 |
| shared ontology | 5 |
| refusal / manual boundary | 2 |

## 12. 推荐落地路线

### Phase 0：分类和命名冻结

产出：

- 企业业务域 taxonomy。
- 每个业务域 owner。
- shared ontology 最小字段。
- Agent 清单和优先级。

验收：

- 所有知识库目录命名稳定。
- `workspace`、`domain`、`agent`、`evidence_grade` 字段定义完成。

### Phase 1：两个样板域

优先建设：

- `supply-chain-kb`
- `product-kb`

同时建立：

- `shared/entity-dictionary`
- `shared/metric-dictionary`
- `shared/system-crosswalk`
- `governance/source-register`

验收：

- 50 个 eval questions 能跑通。
- Agent 回答能引用来源。
- 跨域问题能调用 shared ontology。

### Phase 2：Agent playbook

优先建设：

- `replenishment-agent`
- `listing-agent`
- `ad-optimization-agent`

验收：

- 每个 Agent 有 routing policy。
- 每个 Agent 有 blocked actions。
- 每个 Agent 有 eval set。

### Phase 3：全域扩展

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

## 13. 推荐写入 PRD 的新增章节

建议在 `KB_Platform_PRD.md` 中新增：

```text
第四章之后新增：企业知识库业务分类与 AI Agent 调用架构
```

章节结构：

```text
4A.1 设计目标
4A.2 企业业务域 taxonomy
4A.3 每个业务域五层标准结构
4A.4 shared ontology
4A.5 Agent playbook
4A.6 检索路由策略
4A.7 evidence grade 与治理
4A.8 评估集设计
4A.9 第一阶段落地范围
```

## 14. 最终建议

采用方案 C，但按方案 A 的方式启动：

1. 先建立企业级业务域 taxonomy。
2. 供应链和商品作为两个样板域。
3. 每个业务域采用五层结构。
4. 同步建立 shared ontology 最小版。
5. 暂时只建设 2-3 个高价值 Agent playbook。
6. 用评估集证明 Agent 回答质量，而不是只证明向量检索可用。

这条路径能兼顾组织可维护性和 AI 调用准确性。
