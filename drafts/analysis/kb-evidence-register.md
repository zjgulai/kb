---
title: "KB Evidence Register"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/2026-06-18-kb-secondary-verification.md"
  - "drafts/analysis/2026-06-18-enterprise-kb-taxonomy-agent-architecture.md"
  - "drafts/analysis/2026-06-18-KB_Platform_PRD_v2.1_business_agent_draft.md"
scope: "official-source, business-architecture, source-intake and local-poc evidence register"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB Evidence Register

## 0. 边界

本文件是知识库 PRD v2.1 的证据登记草稿，用于把“事实、推断、不确定项”拆开管理。它不代表实现完成，不代表生产可用，不触发部署，不调用模型服务，不写入任何生产知识库。

## 1. Evidence Types

| evidence_type | 含义 | 可用于什么结论 |
|---|---|---|
| official_source | 官方 README、官方文档、官方许可页、模型卡 | 可支撑组件能力、许可证、接口边界 |
| industry_case | 公开行业案例、工程博客、研究型案例 | 可支撑架构方向，不可直接证明本项目可用 |
| internal_draft | 当前项目草稿、业务方案、taxonomy 设计 | 可支撑设计意图，不可作为事实证据 |
| source_intake_pending | 尚未完成合法来源登记、hash、OCR 或字段抽取 | 只能作为待补证对象 |
| local_poc_pending | 尚未跑本地 PoC、smoke、eval | 只能作为待验证能力 |
| legal_review_pending | 许可证或商业使用边界未过法务 | 不得写成商业无风险 |

## 2. Confidence Levels

| confidence | 判定标准 |
|---|---|
| confirmed | 官方主源或已验收本地证据支持 |
| partial | 方向成立，但 PRD 表述过强、过细或缺少本项目验证 |
| conflict | 官方主源与 PRD 当前表述冲突 |
| pending | 还没有足够证据 |
| draft_only | 只属于设计草案或业务假设 |

## 3. Technical Evidence Register

| evidence_id | claim | source | evidence_type | verified_at | confidence | PRD action |
|---|---|---|---|---|---|---|
| EV-LR-001 | LightRAG default query mode is `mix`, supports rerank, and embedding changes require re-indexing/re-embedding discipline | https://github.com/HKUDS/LightRAG | official_source | 2026-06-18 | partial | 修订原 M3，不再写“默认 hybrid”；P1 实测 `mix`、`mix+rerank`、`hybrid+rerank`、`local` |
| EV-LR-002 | LightRAG supports PostgreSQL all-in-one and specialized storage backends such as vector/graph stores | https://github.com/HKUDS/LightRAG | official_source | 2026-06-18 | confirmed | P1 优先最小后端，Milvus/Neo4j/Memgraph 拆分进 P2 |
| EV-RA-001 | RAG-Anything supports MinerU parser and direct `content_list` insertion | https://github.com/HKUDS/RAG-Anything | official_source | 2026-06-18 | confirmed | 文档/PDF 解析可作为 P1 候选，但需许可证和本地 PoC |
| EV-RA-002 | RAG-Anything can be treated as native full audio/video main pipeline | https://github.com/HKUDS/RAG-Anything | official_source | 2026-06-18 | partial | 音视频应降级为外部预处理或 VideoRAG spike，不进 P1 默认闭环 |
| EV-VR-001 | VideoRAG supports long videos with visual/audio signals and reports Video-MME long-video performance | https://github.com/HKUDS/VideoRAG | official_source | 2026-06-18 | confirmed | 作为 P2/P3 候选，不作为 P1 生产依赖 |
| EV-MU-001 | MinerU2.5-2509-1.2B model card license is AGPL-3.0 | https://huggingface.co/opendatalab/MinerU2.5-2509-1.2B | official_source | 2026-06-18 | conflict | 原 PRD Apache 2.0 口径必须修订；进入许可证风险登记 |
| EV-MV-001 | Milvus repository license is Apache-2.0 | https://github.com/milvus-io/milvus | official_source | 2026-06-18 | confirmed | 保留许可证口径；性能 claim 仍需 benchmark |
| EV-MV-002 | Milvus 2.6 release line includes Woodpecker/tiered/BM25/JSON capability direction | https://milvus.io/docs/release_notes.md | official_source | 2026-06-18 | partial | 只能作为官方能力方向；百分比性能数据标为 vendor benchmark |
| EV-NEO-001 | Neo4j Community Edition is GPL v3 | https://neo4j.com/licensing/ | official_source | 2026-06-18 | confirmed | SaaS/分发边界必须法务审查 |
| EV-MEM-001 | Memgraph commercial/license status is safe and clearer than Neo4j | https://github.com/memgraph/memgraph | official_source | 2026-06-18 | pending | 不得写“许可证更清晰”；需官方 legal page 或法务确认 |
| EV-PGV-001 | pgvector is a Postgres vector similarity extension | https://github.com/pgvector/pgvector | official_source | 2026-06-18 | partial | 功能方向保留；许可证需直接核验 LICENSE |
| EV-WH-001 | Whisper repository license is MIT | https://github.com/openai/whisper | official_source | 2026-06-18 | confirmed | 可作为音频转写候选，但 P1 不默认纳入 |
| EV-QW-001 | Qwen3-Embedding-0.6B model card license is Apache-2.0 | https://huggingface.co/Qwen/Qwen3-Embedding-0.6B | official_source | 2026-06-18 | confirmed | 许可证口径保留；维度/VRAM/性能需模型卡复核和本地 smoke |
| EV-QW-002 | Qwen3-Reranker-0.6B model card license is Apache-2.0 | https://huggingface.co/Qwen/Qwen3-Reranker-0.6B | official_source | 2026-06-18 | confirmed | 许可证口径保留；效果/延迟需 P1 eval |
| EV-MCP-001 | `lightrag-mcp-server` package name, 30+ tools, uvx transport are confirmed | pending | local_poc_pending | 2026-06-18 | pending | 降级为 MCP wrapper candidate；P1 只要求 3 个 readonly tools |

## 4. Business Architecture Evidence Register

| evidence_id | claim | source | evidence_type | verified_at | confidence | PRD action |
|---|---|---|---|---|---|---|
| EV-CASE-001 | Large retailers use product graphs/knowledge graphs to improve product understanding and catalog quality | https://www.amazon.science/blog/building-product-graphs-automatically | industry_case | 2026-06-18 | partial | 可支撑商品知识库和实体关系图方向，不证明本项目已经具备能力 |
| EV-CASE-002 | Walmart Retail Graph uses product knowledge graph thinking for retail search and product understanding | https://medium.com/walmartglobaltech/retail-graph-walmarts-product-knowledge-graph-6ef7357963bc | industry_case | 2026-06-18 | partial | 可支撑商品/渠道/shared ontology 设计方向 |
| EV-CASE-003 | Zalando used semantic web and ontology thinking to structure fashion/product knowledge | https://engineering.zalando.com/posts/2018/03/semantic-web-technologies.html | industry_case | 2026-06-18 | partial | 可支撑 ontology 层，不直接证明跨境电商全域 taxonomy 最优 |
| EV-CASE-004 | DoorDash describes LLM-assisted product knowledge graph construction | https://careersatdoordash.com/blog/building-doordashs-product-knowledge-graph-with-large-language-models/ | industry_case | 2026-06-18 | partial | 可支撑 LLM + KG 协同方向，P1 必须仍以人工证据等级和 eval 验证 |
| EV-BIZ-001 | 企业 KB 应按 marketing/product/supply-chain/operations/channel/customer-service/finance/strategy 分域 | drafts/analysis/2026-06-18-enterprise-kb-taxonomy-agent-architecture.md | internal_draft | 2026-06-18 | draft_only | 作为 v2.1 taxonomy 提案，需业务负责人确认 |
| EV-BIZ-002 | 每个业务域采用 methodology/operations/metrics-and-data/crosswalk/governance 五层结构 | drafts/analysis/2026-06-18-enterprise-kb-taxonomy-agent-architecture.md | internal_draft | 2026-06-18 | draft_only | 作为标准模板候选，需样板域试填后再固化 |
| EV-BIZ-003 | shared ontology 应包含 entity-dictionary、metric-dictionary、system-crosswalk、business-event-taxonomy、relationship-model | drafts/analysis/2026-06-18-KB_Platform_PRD_v2.1_business_agent_draft.md | internal_draft | 2026-06-18 | draft_only | 作为 P1 最小共享层，需字段样例和治理 owner |
| EV-BIZ-004 | 供应链域应优先做样板，因为它天然依赖指标口径、系统字段、SOP、异常处理和跨域信号 | drafts/analysis/2026-06-18-enterprise-kb-taxonomy-agent-architecture.md | internal_draft | 2026-06-18 | draft_only | 进入 P1 PoC 计划，但必须补 source-intake 和 eval |

## 5. Source-Intake Evidence Register

| source_id | target_kb | expected_source | current_status | evidence_grade_after_intake | blocker | next_action |
|---|---|---|---|---|---|---|
| SRC-SCM-001 | supply-chain-kb | ERP export/API/page parameter evidence for inventory fields | source_intake_pending | A or B | 未完成合法来源登记和字段抽取 | 收集文件 hash、来源系统、字段字典、导出时间、负责人 |
| SRC-SCM-002 | supply-chain-kb | DingTalk/internal SOP for replenishment and inventory planning | source_intake_pending | B or C | 文档版本、owner、审批状态未登记 | 建立 source-register 后再拆分 SOP 与指标 |
| SRC-PROD-001 | product-kb | Product catalog, SKU/MSKU/ASIN mapping, listing rules | source_intake_pending | A or B | 数据源和字段 owner 未登记 | P1 只取 20-50 个样板 SKU |
| SRC-MKT-001 | marketing-kb | Ad campaign reports and platform policy docs | source_intake_pending | A/B for reports, B/C for policy docs | 平台字段口径和投放权限未登记 | 不进入 P1 默认闭环，可做 Phase 2 |
| SRC-VOC-001 | customer-service-kb | Reviews, tickets, return reasons, customer service scripts | source_intake_pending | A/B/C by source | PII/平台条款/脱敏规则未确认 | 先做治理和脱敏策略，不直接入库 |

## 6. Local PoC Evidence Slots

这些条目当前均为 `local_poc_pending`，不得写成已完成。

| poc_id | capability | pass_condition | current_status | required_artifact |
|---|---|---|---|---|
| POC-INGEST-001 | Text/PDF ingest | 20-50 样板文档可解析、分块、入库、回溯 source_uri | pending | ingest log + chunk manifest |
| POC-SEARCH-001 | Hybrid retrieval | 50 题 eval 中有可复现 Recall/Precision/Citation 指标 | pending | eval JSONL + run report |
| POC-AGENT-001 | replenishment-agent readonly answer | 能按 routing policy 调用 supply-chain/shared 并引用证据 | pending | agent trace + answer samples |
| POC-ISO-001 | workspace isolation | 跨 workspace 查询被拒绝或返回空 | pending | isolation test report |
| POC-MCP-001 | readonly MCP tools | `query`、`doc_status`、`health` 三工具可 list/call | pending | MCP list_tools/call_tool log |

## 7. PRD Usage Rule

主 PRD 或 v2.1 草稿引用本登记表时必须遵守：

1. `confirmed` 可写为“已由官方来源支持”，但仍不等于本项目已实现。
2. `partial` 只能写为“方向支持，需本项目 PoC 或基准测试”。
3. `conflict` 必须进入风险矩阵或修订清单。
4. `pending` 和 `draft_only` 不得作为生产架构结论。
5. 所有 Agent 输出必须引用 evidence_id 或 source_id；没有证据时输出 `unknown` 或 `needs_human_review`。
