---
title: "Enhanced AI Skill 候选组合"
status: "decision_draft_not_installed"
source_dossiers: "01-repository-dossiers.md"
method_atoms: "02-method-atoms.md"
project_target_assumption: "current KB workspace, pending user confirmation"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
live_ingestion_boundary: "no live KB ingestion"
---

# 从方法论到 Skill：候选组合而非“大一统 Fable Skill”

## 先给结论

不建议创建名为 `fable-5`、`enhance-ai` 或“万能增强”的单体 Skill。那会把研究、诊断、委派、执行、审查、UI 和多模型调用混成一个不可测试的超级 prompt。

更适合当前 KB 的做法是：先选择 1–2 个能产生真实项目价值、没有新增 provider/生产副作用的 Skill；通过真实任务验证后，再扩展到多 agent 或多模型能力。以下每一项都是**蓝图**，不是已安装或自动触发的 Skill。

## 候选总表

| 优先级 | Skill 候选 | 主要解决的问题 | 场景 | 现有 KB 契合度 | 风险 / 前置条件 |
|---|---|---|---|---|---|
| P0 | `github-method-intake` | 外部 GitHub 仓库被直接复制，缺来源、许可证、可迁移性判断 | 引入 Skill / agent / prompt / 工具方法时 | 高 | 只读公开研究；不执行安装脚本、不复制长提示词 |
| P0 | `research-evidence-qualification` | 研究报告把作者说法、旧资料、推测混成结论 | 市场、竞品、技术、政策、工具研究 | 高 | 需要来源/日期/证据级别；不替代专家或法务结论 |
| P0 | `delivery-claim-judge` | “已经完成”没有当前可复验依据 | 代码、报告、distillation candidate、部署前工件 | 高 | 只读审计优先；必须能访问规格和产物 |
| P1 | `delegation-ticket-and-write-set` | 多 agent / 多人任务范围漂移、互相覆盖、验收失焦 | 可并行的研发、资料结构化、前端原型 | 高 | 只定义合同，不默认派发外部模型 |
| P1 | `session-checkpoint-recovery` | 长任务从错误的旧计划恢复，或重复已做工作 | 跨会话项目、后台任务、迭代研究 | 高 | 与现有 `.kiro/plan/` / `.codex/` 协同，不能另造影子事实源 |
| P1 | `evidence-first-diagnosis` | 故障/分析只列常见原因，未提出判别测量 | 技术故障、数据异常、业务问题诊断 | 中高 | 不实施修复，除非用户同时授权 |
| P1 | `skill-policy-ablation` | 一条“看起来很强”的 prompt 被直接升格为常驻规则 | 新 Skill / workflow / guardrail 上线前 | 高 | 需要小型真实任务集、对照与停用条件 |
| P2 | `independent-evidence-panel` | 单一方案有盲区，关键冲突未显式处理 | 高价值架构、研究、重大迁移审阅 | 中 | 必须明确允许外发的模型、数据、预算与保留策略 |
| P2 | `reference-to-ui-prototype` | UI 灵感、prompt、代码、demo、授权信息分散 | KB 产品界面/研究报告页面探索 | 中 | 素材、字体、图像、视频、第三方模板须逐项授权 |
| P2 | `ui-experience-audit-to-plan` | 高级设计意见不能转为可执行工程计划 | 已有前端的体验/动效/移动端审计 | 中 | 应仅在 UI 任务触发，实施时查当前官方文档 |

## P0：建议优先落地的三个候选

### 1. `github-method-intake`

**要解决的问题。** 用户给出一批 GitHub 链接时，常见失败方式是：看 README 后直接安装、把“提示词”误认为“能力”、忽略许可、将工具/供应商细节带进项目，最后无法说明为什么某个方法值得迁移。

| 项目 | 设计内容 |
|---|---|
| 触发 | “分析这些仓库”“提炼方法论”“把开源技能迁移进项目”“比较 agent/Skill 仓库” |
| 不触发 | 单个依赖的常规安装、用户已明确要求直接执行并已完成代码审计的内部包 |
| 输入 | URL 清单、目标项目/业务场景、是否只读、是否可 clone、资料敏感性说明 |
| 方法原子 | A02 请求路由、A04 证据门、A05 许可/授权、A13 claim judge、A15 Skill 评测设计 |
| 输出 | source register、版本快照、仓库 dossier、能力层次、可复用原子、不可迁移边界、候选 Skill 卡和决策问题 |
| 通过口径 | 每个来源有可访问状态与短引用定位；作者自报与实证分离；无效 URL 记录为不可核验；不复制长提示词/不执行脚本 |
| 权限边界 | 禁止安装、执行 repo script、写入全局 config、发布、provider 调用和 live KB ingestion，除非用户另行明确授权 |

**为何先做。** 这正是本次任务的可复用版：能把未来同类资源收敛为可审计的项目知识，而不是积累一堆难以追溯的链接。

### 2. `research-evidence-qualification`

**要解决的问题。** 市场/技术/业务研究常将“网页说了什么”“模型推断了什么”“下一步建议什么”混在一起，尤其容易在时效、数字、引用和授权上越界。

| 项目 | 设计内容 |
|---|---|
| 触发 | 深度研究、竞品分析、技术选型、政策/价格/产品现状核验、可对外使用的洞察草案 |
| 不触发 | 纯创意脑暴、明确标为虚构的文案、无需外部事实的代码重构 |
| 输入 | 研究问题、目标地区/时间范围、可访问来源、已知局限、所需交付形式 |
| 方法原子 | A01、A02、A03、A04、A05、A13 |
| 输出 | evidence map、事实/推断/建议分层、来源时效表、未验证问题、结论和可复查定位 |
| 通过口径 | 高影响事实能定位来源与日期；不同证据等级不可混用；无来源或旧来源被显式标记；最终报告不复述受版权保护的长文 |
| 权限边界 | 不自动抓取私有站点、不调用外部付费搜索/模型、不对外发布；专业医疗/法律/投资结论需转人工或专业审查 |

**为何适配当前 KB。** 项目已有 source register、evidence grade、license status、candidate-only ingestion 与 review gate；这个 Skill 把它们前移到研究阶段，使“外部输入”从一开始就可进入受控的 distillation job。

### 3. `delivery-claim-judge`

**要解决的问题。** 工作完成报告可能把“计划已写”“文件已创建”“历史测试曾通过”表述为“功能/研究/部署已完成”。这在当前项目的 candidate → promotion 边界最容易产生误判。

| 项目 | 设计内容 |
|---|---|
| 触发 | “帮我验收”“深度检查”“审查这个交付”“已经完成了吗”“准备 promotion / 发布 / 交接” |
| 不触发 | 用户只要创意建议、尚未提供规格或产物、简单问答 |
| 输入 | 原始目标、验收条件、变更/候选工件、当前命令输出或访问证据、已知限制 |
| 方法原子 | A03、A05、A10、A12、A13 |
| 输出 | claim ledger；每条结论为 `VERIFIED`、`VERIFIED_WITH_CAVEATS`、`REFUTED` 或 `UNVERIFIABLE`；最小修复/下一步 |
| 通过口径 | 结论只基于当前读取的规格、diff、运行输出或访问观察；计划、局部检查、历史绿灯和生产证据严格分开 |
| 权限边界 | 默认只读；任何修复、运行成本高的测试、部署、push、promotion、数据写入均需对应授权 |

**为何先做。** 它不依赖额外 provider，能复用当前 QA、preflight、E2E 和报告工件，且直接防止“草案/候选被过度宣称”的高风险问题。

## P1：在 P0 已有真实样本后再实现

### `delegation-ticket-and-write-set`

把多 agent 任务写成明确的职责与路径合同，重点是先定义写集合再并行。输出为 ticket、owner、文件/数据范围、接口、验收、依赖和 `blocked / parked / ready` 状态。它只描述协作，不负责自动调用任何特定模型。

### `session-checkpoint-recovery`

统一记录 `goal / authoritative current state / completed evidence / current blocker / next safe action / pending user decision`，并且恢复时先读实际状态与现有计划，而不是照搬旧日志。应扩展现有 `.kiro/plan/` 和 `.codex/session-thread.md`，而非创建无法同步的第二套账本。

### `evidence-first-diagnosis`

要求先复现或收集症状，再给至少两个竞争假设和一个最低成本的判别测量。输出是结论强度、假设覆盖的线索、下一步测量和授权范围；除非用户请求修复，否则停在诊断层。

### `skill-policy-ablation`

在规则变成常驻 Skill 前，用少量真实但脱敏任务做 A/B：无此 Skill vs 有此 Skill，记录质量、返工、token/时间、用户再纠正、失败验证率。若收益不清晰或成本高，应缩小触发范围或下线，而不是累积更多 prompt。

## P2：条件性能力，不是下一步默认项

### `independent-evidence-panel`

采用“独立答案、独立 judge、证据权重、冲突报告”的流程，只处理信息性建议或可运行候选的比较。启动前必须记录：

- 可发送给哪些模型/服务；
- 输入是否含客户数据、代码、密钥、个人信息或受限来源；
- 调用预算、允许轮数、答案保留期与审计可见范围；
- 人类最终裁决者；
- provider 不可用时的降级结论。

在当前 `no KB provider call` 边界下，该候选仅保留设计，不实施。

### `reference-to-ui-prototype` 与 `ui-experience-audit-to-plan`

前者将设计 brief、已授权参考、生成 prompt、隔离原型、截图/录屏、构建检查和授权状态收进一个可搜索资产包；后者只读审计现有 UI，产生按影响/成本排序、带文件定位与验收项的实施计划。两者属于未来 KB 产品体验工作，不应掺入知识抽取/权限治理核心。

## 每个候选 Skill 的最小“定义完成”契约

在用户决定真正建哪一个之后，Skill 目录不应先堆模板。每个 Skill 至少应具有下面的可验证定义：

| 维度 | 最小要求 |
|---|---|
| 名称与触发 | 名称描述解决的问题；说明何时自动/显式触发，何时禁止触发 |
| 行为边界 | 只列会改变决策的非显然规则；不重述宿主安全和项目规则 |
| 输入和输出 | 输入必须可获得；输出必须可审计、可由用户理解 |
| 资源 | 只加入能复用的 schema、checklist、脚本或 reference；不复制外部仓库长文 |
| 授权 | 外部写入、provider 调用、发布、安装、删除、全局配置变更的阻断点明确 |
| 验证 | 至少有一个成功样本、一个失败/边界样本；若无自动测试，也要有具体观察式检查 |
| 维护 | 版本、来源、许可处理、已知无效场景和可删除条件 |

## 推荐的选择顺序

如果“新项目”指的就是当前 KB，建议采用下面的顺序，而不是同时建十个 Skill：

1. 先把 **`github-method-intake`** 作为外部方法资产入库前的只读 Skill；本次 `enhance_ai` 已经提供了第一个真实样本。
2. 再把 **`delivery-claim-judge`** 放到现有 distillation job 的 candidate/pre-promotion review；用一个现有本地 job 验证它能抓到哪些过度结论。
3. 若研究类输入增多，再落地 **`research-evidence-qualification`**，让技术、市场与业务研究共享同一证据/时效边界。
4. 只有协作任务持续出现写冲突、范围漂移或恢复困难时，才引入 delegation / checkpoint 系列。
5. 多模型 panel、UI 资产生产线均在数据、授权、预算和场景明确后再启动。

迁移路线与待确认决策见 [04-migration-workshop.md](04-migration-workshop.md)。
