---
title: "知识库 PRD 完善实施计划 V2"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/2026-06-18-kb-architecture-audit.md"
  - "drafts/analysis/2026-06-18-kb-secondary-verification.md"
scope: "docs-only remediation plan"
production_impact: "production unchanged"
provider_call_boundary: "no production write; no KB provider call"
---

# 知识库 PRD 完善实施计划 V2

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `KB_Platform_PRD.md` 修订为可执行、可审计、可 PoC 验证的知识库平台实施基线。

**Architecture:** 先把文档治理、证据登记、许可证风险和核心契约收敛，再定义 P1 最小文本/PDF 闭环，最后把图片、音频、视频、MCP 扩展和多智能体高级能力拆成后续验证包。所有未验证能力以 `candidate` 或 `pending_verification` 标注。

**Tech Stack:** Markdown, JSON Schema, OpenAPI, LightRAG, RAG-Anything, PostgreSQL/pgvector, MCP, Prometheus/Grafana, evaluation JSONL.

---

## File Structure

**Modify**

- `/Users/pray/project/kb/KB_Platform_PRD.md`  
  主 PRD。修订状态、证据登记、许可证表、术语、schema、MCP、路线图。

**Create**

- `/Users/pray/project/kb/drafts/analysis/kb-evidence-register.md`  
  证据登记表。只记录官方来源、本地 PoC、法务确认和待验证项。

- `/Users/pray/project/kb/drafts/analysis/kb-p1-poc-validation-plan.md`  
  P1 最小闭环 PoC 计划。覆盖文本/PDF 入库、查询、引用、workspace 隔离、最小评估集。

- `/Users/pray/project/kb/drafts/analysis/kb-license-risk-register.md`  
  许可证风险登记。重点覆盖 MinerU AGPL、Neo4j GPL、Memgraph 待确认、模型许可证。

**Do Not Touch**

- 不创建生产 `.env`。
- 不创建正式 Docker Compose。
- 不写入长期记忆。
- 不部署任何服务。

## Task 1: 状态和证据治理

**Files:**
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:4`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:36-47`
- Create: `/Users/pray/project/kb/drafts/analysis/kb-evidence-register.md`

- [ ] **Step 1: 备份主 PRD**

Run:

```bash
mkdir -p /Users/pray/.Codex/file-history
cp /Users/pray/project/kb/KB_Platform_PRD.md \
  /Users/pray/.Codex/file-history/$(date +%Y%m%d-%H%M%S)-KB_Platform_PRD-before-v2-remediation.md
```

Expected: backup file exists under `/Users/pray/.Codex/file-history/`.

- [ ] **Step 2: 修订文档状态**

Change:

```markdown
> **文档版本**：v2.0 · **发布日期**：2026-06-17 · **状态**：已交叉审计 · 正式发布
```

To:

```markdown
> **文档版本**：v2.0-draft · **发布日期**：2026-06-17 · **状态**：draft · architecture proposal · secondary verification completed · implementation not verified
```

Also update table row:

```markdown
| 状态 | draft · architecture proposal · secondary verification completed · implementation not verified |
```

- [ ] **Step 3: 新增证据登记表**

Create `/Users/pray/project/kb/drafts/analysis/kb-evidence-register.md` with:

```markdown
---
title: "KB Evidence Register"
status: "draft"
created_at: "2026-06-18"
source_document: "KB_Platform_PRD.md"
scope: "official-source and local-poc evidence register"
production_impact: "production unchanged"
---

# KB Evidence Register

| evidence_id | claim | source_url | source_type | verified_at | confidence | notes |
|---|---|---|---|---|---|---|
| EV-LR-001 | LightRAG default query mode is mix and embedding model changes require re-embedding | https://github.com/HKUDS/LightRAG | official_readme | 2026-06-18 | confirmed | PRD M3 must be revised because current README says default mode is mix. |
| EV-RA-001 | RAG-Anything supports MinerU parser and direct content list insertion | https://github.com/HKUDS/RAG-Anything | official_readme | 2026-06-18 | confirmed | Audio/video should remain external integration or candidate flow. |
| EV-MU-001 | MinerU2.5-2509-1.2B model card license is AGPL-3.0 | https://huggingface.co/opendatalab/MinerU2.5-2509-1.2B | model_card | 2026-06-18 | conflict | PRD currently says Apache 2.0. Requires legal review. |
| EV-NEO-001 | Neo4j Community Edition is GPL v3 | https://neo4j.com/licensing/ | license | 2026-06-18 | confirmed | SaaS/distribution must be reviewed. |
| EV-MCP-001 | lightrag-mcp-server package name/tool count/transport | pending | package_registry | 2026-06-18 | pending | Must be verified before P1 MCP acceptance. |
```

- [ ] **Step 4: 校验状态词**

Run:

```bash
rg -n "正式发布|生产就绪|已完成" /Users/pray/project/kb/KB_Platform_PRD.md
```

Expected: any remaining hits are inside “历史口径/待修订口径” sections, not authoritative metadata.

## Task 2: 许可证风险修订

**Files:**
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:147-164`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:600-615`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:4417-4431`
- Create: `/Users/pray/project/kb/drafts/analysis/kb-license-risk-register.md`

- [ ] **Step 1: 修订 MinerU 许可证**

Change MinerU row from:

```markdown
| 解析 | **MinerU 2.5**（MinerU2.5-2509-1.2B） | 2.5 VLM，2026 SOTA | Apache 2.0 | claimed-ready | ... |
```

To:

```markdown
| 解析 | **MinerU 2.5**（MinerU2.5-2509-1.2B） | 2.5 VLM，待本地 PoC | AGPL-3.0 model card; legal review required | candidate | ... |
```

- [ ] **Step 2: 修订许可证扫描表**

Replace MinerU license row with:

```markdown
| MinerU2.5-2509-1.2B | AGPL-3.0（Hugging Face model card）| 待法务确认 | 待法务确认 | 高 | 不得在商业/SaaS 场景直接写“无风险”；评估 Docling/PaddleOCR/云 OCR 替代 |
```

- [ ] **Step 3: 增加风险 R-016**

Add to risk matrix:

```markdown
| R-016 | MinerU2.5 模型许可证与 PRD 声明冲突 | 高 | 高 | Critical | P0 法务审查 + 替代解析器评估 + 部署边界说明 | 架构师/法务 |
```

- [ ] **Step 4: 创建许可证风险登记**

Create `/Users/pray/project/kb/drafts/analysis/kb-license-risk-register.md` with rows:

```markdown
---
title: "KB License Risk Register"
status: "draft"
created_at: "2026-06-18"
scope: "license review candidates"
production_impact: "production unchanged"
---

# KB License Risk Register

| component | PRD license | verified license/status | risk | required action |
|---|---|---|---|---|
| MinerU2.5-2509-1.2B | Apache 2.0 | AGPL-3.0 model card | High | Legal review before any production or SaaS usage. |
| Neo4j CE | GPL 3.0 | GPL v3 official licensing page | Medium/High | Do not use as SaaS default without legal review. |
| Memgraph | BSL 1.1 | pending | Unknown | Verify official legal terms. |
| Qwen3-Embedding-0.6B | Apache 2.0 | apache-2.0 model card | Low | Keep model card link in evidence register. |
| Qwen3-Reranker-0.6B | Apache 2.0 | apache-2.0 model card | Low | Keep model card link in evidence register. |
```

## Task 3: 术语和隔离契约修订

**Files:**
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:1326-1347`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:2217-2245`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:2882-2944`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:4937`

- [ ] **Step 1: 固定术语**

Set:

```markdown
| workspace | 强隔离字段，所有查询、写入、删除、评估必须携带 |
| namespace | 业务显示别名，可映射到 workspace，但不能替代访问控制 |
| tenant_id | 组织/租户审计元数据，不作为唯一隔离条件 |
```

- [ ] **Step 2: 修订 metadata 示例**

Use this canonical metadata:

```json
{
  "workspace": "legal_docs",
  "tenant_id": "team_alpha",
  "namespace_label": "Legal Docs",
  "source_uri": "s3://kb-bucket/docs/contract_001.pdf",
  "source_type": "pdf",
  "modality": "document",
  "version": "1.0",
  "created_at": "2026-06-17T10:00:00Z",
  "updated_at": "2026-06-17T10:00:00Z",
  "acl": ["agent:retrieval"],
  "language": "zh"
}
```

- [ ] **Step 3: 修订 JWT claims**

Replace JWT example with:

```json
{
  "sub": "agent_retrieval_001",
  "role": "agent:retrieval",
  "workspaces": ["legal_docs"],
  "scopes": ["kb:query"],
  "aud": "kb-mcp-server",
  "exp": 1781712000
}
```

- [ ] **Step 4: 修订 ACL 校验规则**

Document this rule:

```python
if requested_workspace not in payload["workspaces"] and "*" not in payload["workspaces"]:
    return False
if required_scope not in payload["scopes"]:
    return False
```

Expected: no role name mismatch between matrix and code sample.

## Task 4: content_list 和图谱 schema 修订

**Files:**
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:1309-1347`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:1648-1704`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:4618-4692`

- [ ] **Step 1: 修订 content_list 类型规则**

Document:

```markdown
`type` 表达索引载体，只允许 `text`、`image`、`table`、`equation`。
`metadata.modality` 表达来源模态，只允许 `document`、`image`、`audio`、`video`、`agent_memory`。
音频转写使用 `type=text, metadata.modality=audio`。
视频帧描述使用 `type=text, metadata.modality=video`；若保留帧图像，再附 `frame_image_uri`。
```

- [ ] **Step 2: 修订 JSON Schema required 字段**

Set required:

```json
"required": ["type", "page_idx", "metadata"]
```

Inside metadata:

```json
"required": ["workspace", "source_uri", "source_type", "modality"]
```

- [ ] **Step 3: 修订图谱唯一约束**

Replace global entity name constraint with:

```cypher
CREATE CONSTRAINT entity_workspace_name_type_unique IF NOT EXISTS
FOR (e:Entity)
REQUIRE (e.workspace, e.normalized_name, e.entity_type) IS UNIQUE;
```

- [ ] **Step 4: 修复删除示例未定义变量**

Change:

```python
await rag.cleanup_orphan_entities(namespace=namespace)
```

To:

```python
await rag.cleanup_orphan_entities(workspace=workspace)
```

Expected: update/delete examples all carry explicit `workspace`.

## Task 5: 检索策略和 KPI 修订

**Files:**
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:541-572`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:2266-2299`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:4164-4194`

- [ ] **Step 1: 修订 M3 问题描述**

Replace:

```markdown
LightRAG 默认配置：查询模式为 `hybrid`...
```

With:

```markdown
当前 LightRAG 官方 README 将 `mix` 描述为默认查询模式，并支持 Rerank。生产风险不在于默认值本身，而在于没有显式锁定检索配置、没有用本项目评估集验证质量/延迟/成本权衡。
```

- [ ] **Step 2: 添加检索配置矩阵**

Add:

```markdown
| profile | query_mode | rerank | target |
|---|---|---|---|
| baseline_fast | local | false | 低延迟事实查询 |
| balanced | mix | false | 默认候选 |
| quality | mix | true | 高价值复杂查询 |
| graph_heavy | hybrid | true | 多跳和实体密集查询 |
```

- [ ] **Step 3: 调整 KPI**

Add metrics:

```markdown
| Citation Accuracy | >= 0.90 | 人工抽样 + source chunk 校验 |
| Unanswerable Detection | >= 0.85 | 不可回答评估集 |
| P99 by profile | profile-specific | Locust + trace |
| Rerank Added Latency | measured | query trace |
```

## Task 6: MCP 接入降级和 P1 验收重写

**Files:**
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:2733-2881`
- Modify: `/Users/pray/project/kb/KB_Platform_PRD.md:4543-4548`

- [ ] **Step 1: 降级 MCP Server 口径**

Replace deterministic dependency language:

```markdown
推荐实现：lightrag-mcp-server
```

With:

```markdown
候选实现：LightRAG MCP wrapper。包名、transport、工具数量必须在 P0 package verification 中确认。
```

- [ ] **Step 2: 重写 P1 MCP 验收**

Replace:

```markdown
- [ ] MCP 工具列表返回 ≥ 22 个工具
```

With:

```markdown
- [ ] P1 readonly MCP 工具可用：health_check、query、get_doc_status
- [ ] 每个 MCP 调用都强制校验 workspace 和 scope
- [ ] 智能体不能直连 LightRAG Server 的网络策略有设计记录
```

## Task 7: P1 PoC 计划文件

**Files:**
- Create: `/Users/pray/project/kb/drafts/analysis/kb-p1-poc-validation-plan.md`

- [ ] **Step 1: 创建 PoC 计划**

Write:

```markdown
---
title: "KB P1 PoC Validation Plan"
status: "draft"
created_at: "2026-06-18"
scope: "text and PDF knowledge base closed-loop validation"
production_impact: "production unchanged"
---

# KB P1 PoC Validation Plan

## Scope

P1 validates only text/PDF ingestion, indexing, retrieval, citation, minimal evaluation, and workspace isolation.

## Dataset

- 10 Markdown/PDF files
- 2 workspaces: `tenant_a_private`, `tenant_b_private`
- 30-50 evaluation questions

## Gates

| gate | pass condition |
|---|---|
| ingestion | >= 90% documents DONE |
| retrieval | Recall@5 baseline recorded |
| citation | >= 90% sampled citations point to source chunks |
| isolation | 0 cross-workspace result leakage |
| unanswerable | unavailable knowledge returns explicit no-answer |
```

- [ ] **Step 2: Add stop/go rule**

Add:

```markdown
P1 cannot proceed to image/audio/video until workspace isolation, citation accuracy, and minimal evaluation are passing.
```

## Task 8: Self-Review

**Files:**
- All modified and created files above.

- [ ] **Step 1: Boundary scan**

Run:

```bash
rg -n "正式发布|生产就绪|已完成|无风险|无前置条件" /Users/pray/project/kb/KB_Platform_PRD.md /Users/pray/project/kb/drafts/analysis
```

Expected: all hits are either removed or explicitly marked as old PRD wording.

- [ ] **Step 2: Schema term scan**

Run:

```bash
rg -n "tenant_id|namespace|workspace" /Users/pray/project/kb/KB_Platform_PRD.md
```

Expected: `workspace` is the strong isolation field; `namespace` and `tenant_id` are not used as primary access-control fields.

- [ ] **Step 3: Evidence scan**

Run:

```bash
rg -n "pending|conflict|confirmed|partial" /Users/pray/project/kb/drafts/analysis/kb-evidence-register.md
```

Expected: every critical component has an evidence status.

- [ ] **Step 4: PRD line-count sanity**

Run:

```bash
wc -l /Users/pray/project/kb/KB_Platform_PRD.md /Users/pray/project/kb/drafts/analysis/*.md
```

Expected: files exist; no accidental truncation.

## Execution Handoff

This plan is ready for docs-only execution. Recommended next step is to apply Task 1 through Task 3 first, then stop for review before touching schema, MCP, and roadmap sections.
