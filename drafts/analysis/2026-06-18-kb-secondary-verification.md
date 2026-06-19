---
title: "知识库架构二次核验证据登记"
status: "draft"
created_at: "2026-06-18"
source_document: "KB_Platform_PRD.md"
scope: "docs-only secondary verification"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call; public official source reads only"
---

# 知识库架构二次核验证据登记

## 0. 边界

本文件是二次核验记录，只验证 `KB_Platform_PRD.md` 中关于知识库架构、组件能力、许可证、接口边界和路线图假设的公开证据。不执行部署、不调用生产知识库、不调用模型服务、不修改原始 PRD。

## 1. 核验等级

| 等级 | 含义 |
|---|---|
| confirmed | 官方主源支持，且与 PRD 口径一致或基本一致 |
| partial | 官方主源支持方向，但 PRD 存在过强、过细或需 PoC 的声明 |
| conflict | 官方主源与 PRD 明确冲突 |
| pending | 本轮未能通过官方主源稳定核验 |

## 2. 核验结果总表

| ID | PRD 声明 | 二次核验结论 | 等级 | 建议处理 |
|---|---|---|---|---|
| EV-LR-001 | LightRAG 使用 `mix`、支持 rerank、embedding 不能随意更换 | 官方 README 支持；但 PRD 中“M3 称默认 hybrid”与官方 README 冲突 | partial | 修订 M3，不再说 LightRAG 默认 hybrid |
| EV-LR-002 | LightRAG 可用 PostgreSQL all-in-one，也可选 Milvus/Neo4j/Memgraph | 官方 README 支持方向 | confirmed | P1 优先 PostgreSQL all-in-one，专用存储进入 P2 |
| EV-RA-001 | RAG-Anything 支持 MinerU、Docling、PaddleOCR、content_list 直插 | 官方 README 支持 | confirmed | 保留，但补充各 parser 的边界 |
| EV-RA-002 | RAG-Anything 原生支持完整音视频处理 | 官方 README 只看到 VideoRAG 关联和 content_list 直插，未证实其作为原生音视频主通道 | partial | 音视频写成外部预处理或 VideoRAG spike |
| EV-VR-001 | VideoRAG 支持极长视频、视觉+音频、Video-MME long video 60.2% | 官方仓库 README 支持这些 claim | confirmed | 作为 P2/P3 候选，不直接列为 P1 生产依赖 |
| EV-MU-001 | MinerU2.5-2509-1.2B 许可证 Apache 2.0 | Hugging Face 模型卡显示 license 为 `agpl-3.0` | conflict | P0 修正许可证风险；解析层不得写“无许可证风险” |
| EV-MU-002 | MinerU 2.0 不再使用 `magic-pdf.json` | RAG-Anything README 明确说明 MinerU 2.0 通过命令行参数或函数参数配置 | confirmed | 保留 |
| EV-MV-001 | Milvus 许可证 Apache 2.0 | GitHub API 显示 Apache-2.0 | confirmed | 保留 |
| EV-MV-002 | Milvus 2.6 的 Woodpecker、tiered storage、BM25/JSON 等能力 | Milvus docs 能看到 v2.6 release notes 与相关能力线索；curl 受 403 限制，未能完整本地抓取 | partial | 作为官方宣称能力保留，性能百分比必须标为 vendor benchmark |
| EV-NEO-001 | Neo4j CE 为 GPL v3，社区许可存在商业/SaaS 边界 | Neo4j licensing 页面明确 Community Edition GPL v3，并强调具体许可约束 | confirmed | 保留并提升为 P0/P1 许可证决策 |
| EV-MEM-001 | Memgraph 许可证更清晰 | GitHub API 对 license 返回 NOASSERTION；PRD 的 BSL 1.1 需官方法律页二次确认 | pending | 不再写“许可证更清晰”，改为“需法务确认” |
| EV-PGV-001 | pgvector 是 Postgres 向量检索扩展 | GitHub API 说明为 Postgres vector similarity search，但 license 字段返回 NOASSERTION | partial | 功能方向保留，许可证用 pgvector 官方 LICENSE 再核验 |
| EV-WH-001 | Whisper 为 MIT | GitHub API 显示 MIT | confirmed | 保留 |
| EV-QW-001 | Qwen3-Embedding-0.6B license 为 Apache 2.0 | Hugging Face 页面显示 license `apache-2.0` | confirmed | 保留许可证口径 |
| EV-QW-002 | Qwen3-Embedding 维度、VRAM、MTEB 优势、发布日期 | 页面可见模型卡，但本轮未稳定提取全部数值；PRD 的精确性能 claim 未完成复核 | partial | 精确分数和资源需求标为待 PoC/模型卡复核 |
| EV-QW-003 | Qwen3-Reranker-0.6B license 为 Apache 2.0 | Hugging Face 页面显示 license `apache-2.0` | confirmed | 保留许可证口径 |
| EV-MCP-001 | `lightrag-mcp-server`、30+ tools、uvx 零安装 | PyPI 查询未稳定确认；官方主源证据不足 | pending | P0 降级为 MCP candidate，先验证包名、工具数、transport |

## 3. 关键修正项

### 3.1 MinerU 许可证冲突应升为 P0

PRD 当前在技术选型表和许可证扫描中把 MinerU 2.5 写为 Apache 2.0 且无许可证风险。二次核验发现 Hugging Face 模型卡的 `opendatalab/MinerU2.5-2509-1.2B` license 为 `agpl-3.0`。这不是一般“待验证项”，而是与 PRD 明确冲突。

建议修订：

- 技术选型表中 MinerU 2.5 的许可证改为 `AGPL-3.0 model card; project/license split requires legal review`。
- 许可证扫描中新增 `R-016 MinerU AGPL model license risk`。
- 解析层 P0 前置检查必须包含 MinerU 模型许可证和部署方式审查。
- 如商业闭源/SaaS 分发受限，需评估替代解析路径：Docling、PaddleOCR、云厂商 OCR、或仅在内部非分发环境使用。

### 3.2 LightRAG M3 表述需要修订

官方 README 显示 LightRAG 当前默认 query mode 是 `mix`，并且支持 rerank。PRD 的 M3 将问题描述为“LightRAG 默认 hybrid，未开启 Rerank”不再准确。

建议修订：

- M3 标题从“必须默认混合检索+跨编码器重排”改为“必须显式锁定检索配置并基准测试质量/延迟权衡”。
- 保留 `mix + rerank` 作为推荐候选，但不能写成无条件适用于所有查询。
- 在 P1 PoC 中实测 `mix`、`mix+rerank`、`hybrid+rerank`、`local` 的 Recall、P99、成本。

### 3.3 MCP Server 需要从确定依赖降级为验证对象

PRD 把 `lightrag-mcp-server` 写成已确定组件，并写有 `30+ 工具` 与 `uvx` 部署命令。本轮 PyPI/API 查询没有稳定确认该包和工具数。该项会直接影响多智能体接口。

建议修订：

- P0 任务新增 `MCP package verification`。
- 在验证前，文档只写 `MCP wrapper candidate`，不写具体包名为唯一方案。
- 工具数验收从 `>=22` 改为“P1 必须有 3 个 readonly tools：query、doc_status、health”。

### 3.4 存储策略需要收敛

LightRAG 官方 README 支持生产中使用 PostgreSQL all-in-one，也支持专用向量/图存储组合。PRD 同时引入 PostgreSQL、pgvector、AGE、Neo4j、Milvus、Memgraph，范围偏大。

建议修订：

- P1：只验证 PostgreSQL all-in-one 或最小后端组合。
- P2：再验证 Milvus/Neo4j/Memgraph 拆分。
- 迁移阈值不使用固定 800 万/1000 万向量，改为基于本项目 benchmark 的触发条件。

## 4. 当前证据缺口

| 缺口 | 影响 | 补证方式 |
|---|---|---|
| MinerU 项目代码许可证与模型许可证是否一致 | 解析层商业使用风险 | 读取 GitHub LICENSE、Hugging Face model card、必要时人工法务确认 |
| Milvus 2.6 具体能力和性能百分比 | 存储规模期规划准确性 | 官方 release notes + 本项目 benchmark |
| Qwen3 embedding/reranker 维度、VRAM、MTEB 分数 | Embedding ADR 准确性 | Hugging Face model card + 本地推理 smoke |
| lightrag-mcp-server 包名、工具数、transport | MCP 接入可行性 | PyPI/GitHub official package + 本地 `list_tools` smoke |
| Memgraph 商业使用条款 | SaaS/分发合规 | 官方 license/legal 页面 + 法务确认 |
| pgvector license 字段 | 开源合规表准确性 | GitHub LICENSE 文件直接核验 |

## 5. 二次核验后的状态建议

当前 PRD 不应继续标注为 `正式发布`。建议状态改为：

`draft · architecture proposal · secondary verification completed · implementation not verified`

其中：

- `secondary verification completed` 只表示公开证据二次核验完成。
- `implementation not verified` 表示尚无本地 PoC、smoke、评估集或生产验证。

## 6. 使用过的主源

- LightRAG official repository: https://github.com/HKUDS/LightRAG
- RAG-Anything official repository: https://github.com/HKUDS/RAG-Anything
- VideoRAG official repository: https://github.com/HKUDS/VideoRAG
- MinerU2.5 Hugging Face model card: https://huggingface.co/opendatalab/MinerU2.5-2509-1.2B
- Qwen3 Embedding model card: https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Qwen3 Reranker model card: https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
- Milvus release notes: https://milvus.io/docs/release_notes.md
- Milvus GitHub repository: https://github.com/milvus-io/milvus
- Neo4j licensing: https://neo4j.com/licensing/
- OpenAI Whisper repository: https://github.com/openai/whisper
- pgvector repository: https://github.com/pgvector/pgvector
- Memgraph repository: https://github.com/memgraph/memgraph
