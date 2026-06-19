---
title: "KB License Risk Register"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/2026-06-18-kb-secondary-verification.md"
  - "drafts/analysis/kb-evidence-register.md"
scope: "license review candidates for KB PRD v2.1"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
legal_status: "not legal advice; pending human legal review"
---

# KB License Risk Register

## 0. 边界

本文件是许可证风险登记草稿，不是法律意见，不代表法务确认完成。任何 `AGPL`、`GPL`、`BSL`、模型卡许可证、商业 SaaS 分发边界，在进入生产或商业闭源交付前都需要人工法务审查。

## 1. Risk Levels

| level | 含义 | PRD 处理方式 |
|---|---|---|
| Critical | 与 PRD 当前表述冲突，且可能影响商业部署或分发 | 必须修订 PRD；P0 法务/替代方案 |
| High | 许可证可能限制 SaaS、商业闭源、网络服务或模型分发 | 不得作为 P1 默认生产依赖 |
| Medium | 开源许可可用方向明确，但仍需确认组合使用边界 | 可作为候选，需保留链接和 owner |
| Low | 官方许可证相对宽松，仍需保留来源 | 可进入 PoC，但不等同于生产合规完成 |
| Unknown | 未找到稳定官方法律来源 | 保持 pending，不得写成无风险 |

## 2. Component Risk Register

| risk_id | component | PRD license/status | verified license/status | risk_level | fact/inference/uncertainty | required_action | P1 decision |
|---|---|---|---|---|---|---|---|
| LIC-001 | MinerU2.5-2509-1.2B | Apache 2.0 / claimed-ready | Hugging Face model card shows `agpl-3.0` | Critical | Fact: model card conflicts with PRD. Uncertainty: project code/license split and deployment obligations need legal review. | 修订 PRD 许可证表；新增 R-016；评估 Docling/PaddleOCR/云 OCR/内部隔离部署 | 不得作为无风险默认生产依赖 |
| LIC-002 | Neo4j Community Edition | GPL 3.0 | Official licensing page says Community Edition is GPL v3 | High | Fact: GPL v3 confirmed. Uncertainty: SaaS/内部服务/分发边界需法务解释。 | P1 不默认依赖 Neo4j；如用图存储，先选最小后端或商业许可评估 | P2 后再评估 |
| LIC-003 | Memgraph | BSL 1.1 / license clearer | GitHub API license returned NOASSERTION in二次核验 | Unknown | Fact: 本轮未确认。Uncertainty: 官方 legal terms 和商业限制未核验。 | 查官方 legal/license 页面；必要时法务确认 | P1 不纳入默认依赖 |
| LIC-004 | pgvector | Open-source extension | Function direction confirmed; license field still needs LICENSE file verification | Medium | Fact: Postgres vector extension direction成立。Uncertainty: license metadata需直接核验。 | 读取官方 LICENSE；记录版本和 commit | 可作为 P1 候选，需补证 |
| LIC-005 | Milvus | Apache 2.0 | GitHub API shows Apache-2.0 | Low/Medium | Fact: license confirmed. Uncertainty: 运维成本和性能 claim 需 benchmark。 | P2 大规模向量拆分验证；P1 不默认引入复杂后端 | P2 candidate |
| LIC-006 | Qwen3-Embedding-0.6B | Apache 2.0 | Model card shows `apache-2.0` | Low | Fact: license direction confirmed. Uncertainty: 精确维度、VRAM、效果需本地 PoC。 | 保留模型卡链接；P1 eval 验证效果/延迟 | P1 candidate |
| LIC-007 | Qwen3-Reranker-0.6B | Apache 2.0 | Model card shows `apache-2.0` | Low | Fact: license direction confirmed. Uncertainty: 延迟和排序收益需 eval。 | 保留模型卡链接；P1 对比 rerank on/off | P1 candidate |
| LIC-008 | OpenAI Whisper | MIT | GitHub API shows MIT | Low | Fact: license confirmed. Uncertainty: 音频转写合规还涉及数据隐私。 | P2 音频 spike 再纳入；P1 不默认处理音频 | P2 candidate |
| LIC-009 | RAG-Anything | Open-source candidate | Official source supports parser/content_list direction | Medium | Fact: 能力方向成立。Uncertainty: 其依赖链中 MinerU/Docling/OCR 的许可证需逐项拆开。 | 不把框架许可等同于全链路许可；依赖级 SBOM | P1 text/PDF candidate |
| LIC-010 | LightRAG | Open-source candidate | Official source supports architecture direction | Medium | Fact: 框架能力方向成立。Uncertainty: 存储后端和模型依赖会改变合规边界。 | P1 使用最小依赖组合；记录依赖版本 | P1 candidate |
| LIC-011 | VideoRAG | Open-source candidate | Official source supports long-video direction | Medium | Fact: 技术方向成立。Uncertainty: 视频数据、模型依赖、算力和许可证链未评估。 | P2/P3 spike 前做 SBOM 和数据权限审查 | P2/P3 only |

## 3. Required PRD Corrections

| correction_id | section | current issue | required wording |
|---|---|---|---|
| COR-LIC-001 | 技术选型表 | MinerU2.5 写为 Apache 2.0 / claimed-ready | `AGPL-3.0 model card; legal review required; candidate` |
| COR-LIC-002 | 许可证扫描 | MinerU 写成无明显风险 | `高风险；不得在商业/SaaS 场景直接写无风险` |
| COR-LIC-003 | 风险矩阵 | 缺少 MinerU 许可证冲突风险 | 新增 `R-016 MinerU2.5 模型许可证与 PRD 声明冲突` |
| COR-LIC-004 | 存储选型 | Neo4j/Memgraph/Milvus 同时作为近似默认选项 | P1 收敛到最小后端；图/向量专用后端进入 P2 |
| COR-LIC-005 | MCP 依赖 | 包名和工具数未证实 | 降级为 `MCP wrapper candidate`，P1 只验 readonly 最小工具 |

## 4. Legal Review Packet

进入人工法务审查前，应准备：

| packet_item | description | owner |
|---|---|---|
| SBOM | P1 实际依赖列表、版本、license、source URL、commit/tag | 架构 owner |
| deployment_mode | 内部使用、SaaS、客户私有化、模型再分发、API 服务边界 | 产品/架构 owner |
| data_policy | 输入文件、客户数据、平台数据、PII、跨境传输边界 | 数据治理 owner |
| license_questions | AGPL/GPL/BSL 是否触发网络服务、分发、代码披露或商业许可要求 | 法务 |
| alternatives | Docling、PaddleOCR、云 OCR、商业 Neo4j、Postgres-only 等替代方案 | 架构 owner |

## 5. Blocked Actions

在 `legal_review_pending` 解除前，不允许把以下句子写入主 PRD 的权威结论：

- `MinerU2.5 商业使用无风险`
- `Neo4j CE 可直接作为 SaaS 默认图数据库`
- `Memgraph 许可证更清晰，因此优先用于生产`
- `全链路开源许可证已经确认`
- `P1 可以直接进入生产`

允许的安全表述：

- `candidate`
- `pending legal review`
- `production unchanged`
- `implementation not verified`
- `requires SBOM and human legal review before production`
