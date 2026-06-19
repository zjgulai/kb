---
title: "知识库架构审计后完善计划"
status: "draft"
created_at: "2026-06-18"
source_document: "KB_Platform_PRD.md"
scope: "docs-only remediation and validation plan"
production_impact: "production unchanged"
provider_call_boundary: "no production write; no KB provider call"
---

# 知识库架构审计后完善计划

## 0. 目标

把当前 `KB_Platform_PRD.md` 从“结构完整但证据不足的方案文档”推进为“可验证实施基线”。本计划只覆盖文档修订、证据补齐和 PoC 验证设计，不直接部署生产系统。

## 1. 执行原则

- `docs-only`：先只改草稿和正式 PRD 文档，不改生产配置。
- `draft`：未跑通 PoC 前，不使用“已完成”“生产就绪”“正式发布”。
- `read-only verification`：外部组件先读官方来源、模型卡、release notes、许可证，不做 provider live send。
- `evidence first`：每条关键技术声明必须有 evidence ID 或明确标记为 `pending_verification`。
- `smallest working loop`：先完成 PDF/文本知识库闭环，再扩图片、音频、视频和多智能体高级能力。

## 2. 阶段 0：文档治理收敛

目标：让 PRD 的状态、证据、术语和边界不误导实施。

### Step 0.1 状态降级

修改 `KB_Platform_PRD.md` 顶部元信息：

- 从 `已交叉审计 · 正式发布`
- 改为 `draft · architecture proposal · partially externally verified`

验收：

- 文档顶部、1.1 元信息、结尾版权说明中的状态一致。
- 未验证组件不出现 `生产就绪` 这类强结论。

### Step 0.2 新增证据登记表

新增 `drafts/analysis/kb-evidence-register.md` 或在 PRD 第三章前加入 evidence register。

字段：

| 字段 | 说明 |
|---|---|
| evidence_id | 例如 `EV-LR-001` |
| claim | 被支持的技术声明 |
| source_url | 官方来源 URL |
| source_type | official_readme / release_note / model_card / license / local_poc |
| verified_at | 验证日期 |
| confidence | confirmed / partial / pending / contradicted |
| notes | 限制和待验证事项 |

验收：

- LightRAG、RAG-Anything、MinerU、VideoRAG、Milvus、pgvector、Neo4j、Memgraph、Qwen、BGE、MCP Server 均有记录。
- Milvus 2.6、Qwen3 具体指标、MCP 30+ tools 等当前证据不足项标为 `pending`。

### Step 0.3 统一术语

确定唯一隔离主语：

- 推荐：外部 API 使用 `workspace`
- 文档语义可说明 `namespace` 是业务别名
- `tenant_id` 只作为组织/租户元数据，不参与底层权限主键

验收：

- OpenAPI、content_list、JWT claims、数据库 schema、图谱 schema 均使用同一主键字段。
- 术语表明确：`workspace` 为强隔离过滤字段，`namespace` 为 UI/业务别名，`tenant_id` 为审计元数据。

## 3. 阶段 1：核心契约修订

目标：消除未来实现时最容易造成安全事故和接口漂移的问题。

### Step 1.1 修订 content_list schema

建议契约：

```json
{
  "type": "text",
  "text": "转写内容或正文",
  "page_idx": 0,
  "metadata": {
    "workspace": "legal_docs",
    "tenant_id": "team_alpha",
    "source_uri": "s3://kb-bucket/docs/contract_001.pdf",
    "source_type": "pdf",
    "modality": "document",
    "created_at": "2026-06-18T00:00:00Z"
  }
}
```

规则：

- `type` 表达索引载体：`text`、`image`、`table`、`equation`。
- `metadata.modality` 表达来源模态：`document`、`image`、`audio`、`video`、`agent_memory`。
- 音频转写使用 `type=text, modality=audio`。
- 视频帧描述使用 `type=text` 或 `type=image`，但必须明确是否保存帧图像。

验收：

- 正文示例和附录 JSON Schema 完全一致。
- 每种模态至少有 1 条合法样例。

### Step 1.2 修订图谱唯一约束

将全局唯一实体名改为 workspace 级唯一。

建议：

```cypher
CREATE CONSTRAINT entity_workspace_name_type_unique IF NOT EXISTS
FOR (e:Entity)
REQUIRE (e.workspace, e.normalized_name, e.entity_type) IS UNIQUE;
```

验收：

- 同名实体在不同 workspace 可共存。
- 跨 workspace merge 默认禁止。
- 删除、更新、查询的 Cypher 示例全部带 workspace 条件。

### Step 1.3 修订 MCP 权限模型

JWT claims 统一为：

```json
{
  "sub": "agent_retrieval_001",
  "role": "agent:retrieval",
  "workspaces": ["legal_docs"],
  "scopes": ["kb:query"],
  "exp": 1781712000,
  "aud": "kb-mcp-server"
}
```

工具权限：

| 工具组 | scope | 阶段 |
|---|---|---|
| query tools | `kb:query` | P1 |
| document insert/update | `kb:write` | P2 |
| delete/admin | `kb:admin` | P3 |

验收：

- 权限矩阵、代码样例和 OpenAPI security schema 使用同一 scope 名称。
- `agent:domain_{ns}` 与 `agent:domain` 的命名冲突消失。

### Step 1.4 修订删除与版本策略

需要明确：

- `DEPRECATED` 是否参与默认检索。
- `ARCHIVED` 是否保留向量索引。
- `DELETED` 是否立即从向量库和图谱清除。
- `PURGED` 的对象存储、日志和审计记录如何处理。

验收：

- 每个状态都有 `query_visible`、`index_retained`、`storage_retained`、`recoverable` 四个字段。
- 查询默认排除 `DEPRECATED`、`ARCHIVED`、`DELETED`，除非显式开启历史查询。

## 4. 阶段 2：最小 PoC 验证计划

目标：验证核心路线是否可运行，不碰音视频和复杂多智能体。

### Step 2.1 P0 基础环境 smoke

范围：

- PostgreSQL 或 LightRAG 推荐最小存储后端
- LightRAG Server
- Embedding 服务
- Rerank 服务可选
- MCP readonly query server

验收：

- `/health` 返回 200。
- 插入 1 条文本，查询返回带 source 引用。
- embedding model hash 写入本地锁定记录。

### Step 2.2 PDF/文本入库闭环

范围：

- 10 个 PDF 或 Markdown 测试文档
- 解析输出 `content_list`
- 入库
- 查询
- 引用返回

验收：

- 解析成功率 >= 90%。
- 每个 chunk 带 `workspace`、`source_uri`、`chunk_idx`。
- 查询不会跨 workspace 返回结果。

### Step 2.3 最小评估集

先建 30-50 题，不直接跳到 200-500 题。

配额：

| 类型 | 数量 |
|---|---|
| 单文档事实型 | 20 |
| 跨文档比较型 | 10 |
| 不可回答问题 | 5 |
| 引用准确抽检 | 5 |

验收：

- `Recall@5` 可自动计算。
- 引用准确率支持人工抽检。
- 不可回答问题能触发“根据现有知识库暂无相关信息”。

### Step 2.4 namespace 隔离红线测试

构造两个 workspace：

- `tenant_a_private`
- `tenant_b_private`

测试：

- A 的 token 查询 B 的文档必须 401/403 或空结果。
- 缺失 workspace 的请求必须拒绝。
- 伪造 metadata_filter 不能绕过 workspace。

验收：

- 0 跨 tenant 数据泄露。
- 所有失败请求有审计日志。

## 5. 阶段 3：多模态扩展验证

目标：在文本闭环通过后逐步扩展。

### Step 3.1 图片

范围：

- 10 张图片或 PDF 内嵌图片
- OCR + VLM 描述
- 图片引用或媒体访问 URL

验收：

- 图片描述可检索。
- 引用能定位原图或页面。
- 私有部署下不生成公网裸露 URL。

### Step 3.2 音频

范围：

- 5 段短音频
- Whisper/faster-whisper 转写
- 时间戳索引

验收：

- 查询结果返回 start_time/end_time。
- 音频转写以 `type=text, modality=audio` 入库。

### Step 3.3 视频 spike

分两条路径验证：

- 短视频：ffmpeg 抽音轨 + 抽帧 + VLM 描述。
- 长视频：VideoRAG 作为独立候选，不直接写入生产主路径。

验收：

- 只要求技术 spike 报告，不把 VideoRAG 标为生产依赖。
- 如果 VideoRAG 输出格式无法稳定转 `content_list`，保持 P3 后续候选。

## 6. 阶段 4：生产化前置门槛

进入生产试点前必须满足：

| 门槛 | 要求 |
|---|---|
| Evidence register | P0/P1 组件全部 confirmed 或 partial with mitigation |
| ADR | Embedding、storage、retrieval、MCP、license 均有 ADR |
| Security | namespace 隔离红线测试通过 |
| Evaluation | 最小评估集可重复运行，结果有 baseline |
| Deletion | update/delete/deprecated 语义验证通过 |
| Observability | query latency、ingestion status、parse error、cross namespace access 指标可见 |
| Rollback | 有从原始文件重建索引的恢复说明 |

## 7. 推荐修订顺序

1. 先修状态、证据、术语。
2. 再修 content_list、图谱 schema、MCP 权限。
3. 然后修部署示例，将不可运行片段标为 pseudo-code 或换成 verified compose。
4. 最后重排路线图，把 P1 收敛为文本/PDF 闭环。

## 8. 不建议现在做的事

- 不建议立即按当前 Docker Compose 启动生产环境。
- 不建议把 VideoRAG、A2A、collective memory 放进第一版生产门槛。
- 不建议在没有 evidence register 的情况下继续使用“正式发布”状态。
- 不建议把 Neo4j CE 作为 SaaS 场景默认图存储。
- 不建议在没有评估集前调参比较模型好坏。

## 9. 下一次确认点

建议下一次人工确认的问题只有一个：

是否允许我把当前审计结果回写到 `KB_Platform_PRD.md`，将其从“正式发布口径”修订为“draft 可验证实施基线”？

如果确认，下一轮应先备份原文件，再做窄范围 PRD 修订，不改任何运行时代码。
