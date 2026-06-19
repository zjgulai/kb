---
title: "多模态知识库架构深度审计报告"
status: "draft"
created_at: "2026-06-18"
source_document: "KB_Platform_PRD.md"
scope: "docs-only architecture audit"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call; external public source reads only"
---

# 多模态知识库架构深度审计报告

## 0. 边界声明

本报告是 `docs-only / draft audit`。本次工作只审计当前项目文档，不改生产配置、不部署服务、不调用知识库生产接口、不执行模型 provider live send。已执行的外部动作仅为读取公开官方来源，用于验证 PRD 中的技术声明。

当前项目根目录只发现一个主文档：`KB_Platform_PRD.md`。未发现项目级 `AGENTS.md`、`.codex/context-pack.md`、Git 仓库历史、ADR 文件、评估结果、部署脚本或源码实现。因此，本文所有“已落地/已验证/生产就绪”判断都只针对文档可信度，不代表系统已实现。

## 1. 审计结论摘要

### 1.1 总体判断

当前 PRD 的架构方向基本成立：它把“训练知识库”定义为离线 indexing pipeline，而不是模型训练；并覆盖解析、分块、实体关系抽取、向量化、图谱与向量混合检索、MCP 调用、多租户治理、评估和运维。这是合理的知识库平台边界。

主要风险不在“少写了章节”，而在“过早写成确定态”。文档中大量声明使用了 `已交叉审计`、`正式发布`、`生产就绪`、`官方支持`、`满足` 等强结论，但项目内缺少 evidence register、ADR、接口验证、最小可运行闭环、许可证审查记录和评估基线。

### 1.2 最高优先级问题

| 等级 | 问题 | 影响 | 证据位置 |
|---|---|---|---|
| P0 | 文档状态过强，缺少本地审计证据 | 误导实施团队把 draft 当 production baseline | `KB_Platform_PRD.md:4`, `KB_Platform_PRD.md:411-423` |
| P0 | `tenant_id` / `namespace` / `workspace` 模型混用 | 多租户隔离和权限测试无法收敛 | `KB_Platform_PRD.md:1328-1346`, `KB_Platform_PRD.md:2217-2245`, `KB_Platform_PRD.md:4618-4681` |
| P0 | 图谱唯一约束与 namespace 隔离冲突 | 跨租户实体合并或误删风险 | `KB_Platform_PRD.md:1655-1703` |
| P0 | 部署示例疑似不可直接运行 | P0 验收命令可能在环境搭建阶段失败 | `KB_Platform_PRD.md:3647-3797` |
| P1 | `content_list` 正文与附录 schema 不一致 | 多模态入库接口无法稳定测试 | `KB_Platform_PRD.md:1313-1324`, `KB_Platform_PRD.md:4618-4681` |
| P1 | 评估集设计过早使用 PRD 自身内容作为答案来源 | Recall/KPI 可能验证的是文档记忆，不是业务知识库质量 | `KB_Platform_PRD.md:4164-4194` |
| P1 | 技术选型表把若干待集成组件写成无条件生产就绪 | 容易低估 PoC 和集成成本 | `KB_Platform_PRD.md:147-164` |

## 2. 证据等级

本报告使用以下证据等级：

| 等级 | 含义 |
|---|---|
| F0 | 当前项目本地文档内事实 |
| F1 | 官方主源公开文档或官方仓库可核验事实 |
| F2 | 基于 F0/F1 的架构推断 |
| U | 未验证或当前证据不足 |

## 3. 外部主源核验摘要

| 主题 | 审计判断 | 证据等级 | 来源 |
|---|---|---|---|
| LightRAG embedding 模型必须在索引前确定 | PRD 的风险判断基本成立 | F1 | https://github.com/HKUDS/LightRAG |
| LightRAG 默认 query mode 为 `mix`，且支持 Reranker | PRD 中把 `hybrid` 写成默认需要修订 | F1 | https://github.com/HKUDS/LightRAG |
| LightRAG 生产存储后端可选 PostgreSQL / Milvus / Neo4j / Memgraph 等 | 大方向成立，但具体版本与 schema 仍需 PoC 验证 | F1/F2 | https://github.com/HKUDS/LightRAG |
| RAG-Anything 支持 MinerU、Docling、PaddleOCR 和直接 content_list 注入 | 大方向成立 | F1 | https://github.com/HKUDS/RAG-Anything |
| RAG-Anything 对音视频作为原生管道能力 | 当前证据不足，应写为外部集成路径 | F2/U | https://github.com/HKUDS/RAG-Anything |
| VideoRAG 支持长视频、多模态检索、Video-MME long video 60.2% | PRD 可作为研究级长视频补强候选，但需本项目集成验证 | F1/F2 | https://github.com/HKUDS/VideoRAG |
| Neo4j Community Edition 为 GPL v3 | PRD 许可证风险成立 | F1 | https://neo4j.com/licensing/ |
| Milvus 2.6 hot/cold tiering、Woodpecker WAL 等具体声明 | 本次未抓到稳定官方 release evidence，应降级为待核验 | U | https://milvus.io/docs/ |
| Qwen3 embedding/reranker 具体维度、发布日期、VRAM、分数优势 | 本机网络抓取模型卡超时，应降级为待核验 | U | https://huggingface.co/Qwen |

## 4. 分层架构审计

### 4.1 文档状态与治理

事实：PRD 顶部声明 `已交叉审计 · 正式发布`，并在第三章写明交叉审计方法和审计员为“架构团队”。当前项目中没有对应审计记录、证据登记、审计人员签名、ADR 文件或 Git 历史。

推断：该文档目前应被视为“结构完整的方案草案”，而不是可直接作为实施基线的正式发布文档。

建议：

- 将文档状态改为 `draft / architecture proposal / externally partially verified`。
- 新增 `evidence_register`，逐条记录组件声明、来源、验证日期、验证人、验证结果、待验证项。
- 把“正式发布”前置条件写成 checklist：ADR 已签署、PoC 已通过、许可证已审查、评估集已建立、P0 smoke 已跑通。

### 4.2 总体架构边界

事实：PRD 的核心 pipeline 是 `原始数据 -> 解析 -> 分块 -> 实体/关系抽取 -> 向量化 -> 图谱/索引存储`，这一点在 `KB_Platform_PRD.md:63-77` 定义清楚。

判断：该边界合理。但架构图同时引入 RAG-Anything、LightRAG、VideoRAG、Whisper、MinerU、Milvus、Neo4j、Memgraph、MCP、A2A、collective memory，已经超过单个 16 周计划的低风险实施范围。

建议：

- 将 P0/P1 收敛为“文本/PDF 知识库闭环”：MinerU or Docling、LightRAG、PostgreSQL、MCP readonly query、评估集。
- 将图片、音频、视频、A2A、collective memory 统一降级为 P2/P3 扩展，不作为第一版生产上线门槛。
- 把“RAG-Anything + LightRAG + VideoRAG”写成集成链路，而不是单个已验证产品。

### 4.3 摄取与解析层

事实：PRD 对格式路由器、MinerU、图像 VLM、Whisper、短视频抽帧和长视频 VideoRAG 路由都有设计。

风险：

- `get_video_duration()` 对 ffprobe 失败返回 `0.0`，会把异常长视频误判为短视频。
- 短视频处理把视频文件直接传给 `process_audio(video_path, metadata)`，但音频处理函数语义是音频文件，应补 ffmpeg 音轨抽取步骤。
- VLM 图像描述要求 `img_public_url`，但生产私有部署和数据主权要求 `无数据外发`，二者需要明确“公网 URL”是否只是内网可访问对象地址。
- SVG 进入图片通道，但 OCR/VLM 对 SVG 的实际处理路径不清楚。

建议：

- 路由器应返回 `UNKNOWN` 或 `NEEDS_REVIEW`，不能在媒体探测失败时默认短视频。
- 音视频管道增加独立 `media_probe` 和 `audio_extract` 步骤。
- `public_url` 改名为 `media_access_url`，并标注是否可外网访问。
- 对 PDF、Office、HTML、EPUB 的解析器优先级做最小基线，不在 P1 同时承诺全部格式。

### 4.4 content_list 与 metadata 契约

事实：正文允许 `type` 为自定义字符串，但附录 JSON Schema 将 `type` 限定为固定 enum。正文音频示例使用 `"type": "text"`，附录又定义 `audio_transcript` 和 `video_frame`。

风险：该不一致会导致 parser、validator、indexer、retriever 各自实现不同假设，后续集成测试难以定位问题。

建议采用双字段模型：

```json
{
  "type": "text",
  "modality": "audio",
  "metadata": {
    "media_kind": "audio_transcript",
    "start_time": 0.0,
    "end_time": 12.4
  }
}
```

其中 `type` 只表达索引载体类型：`text`、`image`、`table`、`equation`。`modality` 表达来源模态：`document`、`image`、`audio`、`video`、`agent_memory`。这样可以避免“音频转写本质是文本，但来源是音频”的二义性。

### 4.5 知识构建与图谱层

事实：PRD 定义了 Entity、Relation、Chunk，并声明 LightRAG merge 策略按实体名称 union。

高风险冲突：Neo4j schema 写了 `CREATE CONSTRAINT entity_name_unique ... e.name IS UNIQUE`，但多租户部分又要求跨 namespace 不合并。这两个约束不能同时成立。若 `Entity.name` 全局唯一，则不同 tenant 的同名实体会冲突；若允许多租户隔离，则唯一键至少应是 `(workspace, normalized_name, entity_type)`。

建议：

- 统一主键为 `entity_id = hash(workspace + normalized_name + entity_type)`。
- 图谱所有节点和边都必须携带 `workspace`，且查询层和数据库层双重过滤。
- 软删和重插必须定义“旧实体引用是否仍参与检索”。当前 `DEPRECATED` 保留索引但标记过期，可能导致检索混入旧版本答案。
- 删除逻辑里 `cleanup_orphan_entities(namespace=namespace)` 使用了未定义变量，是代码样例缺陷。

### 4.6 存储层

事实：PRD 采用起步期 PostgreSQL + pgvector + AGE，规模期 Milvus + Neo4j/Memgraph 的分层策略。

判断：作为方向合理，但需要拆成两个可验证决策：

- P1 起步方案：是否真的需要 Apache AGE，还是先使用 LightRAG 支持的 PostgreSQL all-in-one 存储。
- P2 规模方案：Milvus 和 Neo4j 拆分后的同步、备份、恢复、重建路径。

风险：

- 规模阈值 `800 万 / 1000 万向量` 没有本项目 benchmark 支撑。
- Neo4j CE 许可证风险已经识别，但“默认 Neo4j CE”与潜在 SaaS 场景冲突。
- Memgraph BSL 条款也需要法务/商业使用审查，不能简单写成许可证更清晰。

建议：

- P1 只承诺 PostgreSQL all-in-one 或最小后端组合，避免一开始同时部署 PostgreSQL、AGE、Neo4j、Milvus。
- 迁移阈值改成“性能触发 + 数据规模触发 + 运维能力触发”的组合，而不是固定向量数。
- 对许可证敏感场景默认使用 PostgreSQL/可替代图存储，Neo4j/Memgraph 均列为需审查。

### 4.7 检索服务层

事实：LightRAG 官方 README 显示 `mix` 是默认 query mode，并说明 rerank 可改善质量但会增加 1-2 秒延迟。

问题：PRD 的 M3 写“LightRAG 默认配置为 hybrid，未开启 rerank”，该声明与当前官方 README 不一致。M3 的方向“生产要做 rerank/混合检索/评估”仍然正确，但理由需要修订为“显式锁定检索配置并验证延迟质量权衡”，而不是“修正 LightRAG 默认缺陷”。

建议：

- 将检索默认策略写成可测配置矩阵：`mix+rerank`、`mix no rerank`、`hybrid+rerank`、`local`。
- KPI 不应只写 Recall@5，还要写 P50/P95/P99、rerank cost、citation accuracy。
- 对高频低延迟查询保留降级策略，避免把 `mix+rerank` 作为所有请求的硬默认。

### 4.8 MCP 与多智能体接口

事实：PRD 明确“所有智能体通过 MCP Server 访问知识库，禁止直连 LightRAG Server REST API”。

判断：这个安全方向正确，但需要更强边界：

- “禁止直连”不能只写在文档中，需要网络层 ACL 或服务网格策略。
- MCP 工具清单写 30+，P1 验收写工具列表返回不少于 22，但附录只列了少量接口样例，数量口径不一致。
- 权限矩阵中 `agent:domain_{ns}`，代码校验却检查 `role in ["agent:domain", ...]`，命名不一致。

建议：

- 把 MCP 工具分为 P1 readonly query、P2 ingestion、P3 admin 三批。
- JWT claims 规范化为 `sub`, `role`, `workspaces`, `scopes`, `exp`, `aud`。
- 每个工具必须声明 scope，例如 `kb:query`, `kb:insert`, `kb:delete`, `kb:admin`。

### 4.9 评估与可观测性

事实：PRD 明确“没有评估集就无法量化 KPI”，这是正确方向。

问题：评估集示例问题使用 PRD 自身知识，例如 “LightRAG 的增量更新相比 GraphRAG 节省多少成本”。这适合验证演示知识库，不适合作为业务知识库质量基线。

建议：

- 评估集分两套：`platform_demo_eval` 与 `business_domain_eval`。
- P1 最小评估集可从 30-50 题开始，先验证评估管道；200-500 题作为 P1 完成门槛可能过重。
- 对开放题不要只用 F1/EM，应加入引用支持率、不可回答识别率、答案事实性人工抽样。

### 4.10 路线图与工期

事实：PRD 规划 16 周完成基础设施、PDF、评估、多模态、多租户、collective memory、A2A、压测和上线。

推断：如果团队已有基础平台和 GPU 环境，16 周可能可做出内测版；若从零开始，当前范围偏大，尤其 P2/P3 的多模态和多智能体生产化同时推进会放大集成风险。

建议：

- 将第一个里程碑改为“P1 可验证闭环”，而不是“正式生产可用”。
- 将 collective memory 和 A2A 从核心上线范围移到后续增强。
- 每阶段都必须有 stop/go gate：未通过评估集、隔离测试或 smoke，不进入下一阶段。

## 5. 需要立即修订的文档口径

| 原口径 | 建议口径 |
|---|---|
| 已交叉审计 · 正式发布 | draft · architecture proposal · partially externally verified |
| 生产就绪 | candidate / verified by official docs / requires PoC |
| HC-01/02/03 满足 | design satisfies in principle; implementation verification pending |
| 所有智能体通过 MCP | target contract: agents must use MCP; network enforcement pending |
| Neo4j 默认 | graph backend candidate; license and deployment mode pending |
| Milvus 2.6 新特性确定 | pending official release-note verification |
| mix+rerank 无条件默认 | default candidate; latency/quality benchmark required |

## 6. 推荐的下一步

1. 先做文档治理修订：状态降级、证据登记、术语统一、schema 统一。
2. 再做 P1 PoC：PDF/文本入库、查询、引用、评估、namespace 隔离。
3. P1 通过后再引入图片；音频/视频进入独立技术 spike。
4. 多租户和删除/更新语义必须在任何生产试点前完成红线测试。

本报告不建议当前 PRD 直接进入开发执行。建议先按配套计划文件推进为“可验证实施基线”。
