---
title: "Enhanced AI 仓库能力档案"
status: "draft_research"
retrieved_at: "2026-09-23"
source_register: "00-source-register.md"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
live_ingestion_boundary: "no live KB ingestion"
---

# 仓库能力档案：从“Fable 标签”到可迁移的方法

## 阅读口径

这些仓库的共同叙事是“让其他模型用出 Fable 5.x 的效果”。本档案不接受这个叙事作为事实结论，而是回答四个更可操作的问题：

1. 仓库实际交付了哪些文件、脚本、Skill、评测或 demo？
2. 其中哪一层是可独立复写的工作机制？
3. 它在当前 KB 项目内能解决什么具体问题？
4. 其模型专用、未经授权、未经复验或有外部副作用的部分为何不能直接迁移？

证据强度从高到低为：可运行/可检查的仓库工件与测试夹具、明确的 Skill/脚本、README 的作者声明、自报 benchmark、仓库名称或第三方转述。所有“模型升阶”“官方系统提示词”“成本优势”等结论均留在作者声明层，除非本项目以后对目标场景独立复验。

## 总体分类

| 集群 | 仓库 | 实际产物 | 本项目应吸收什么 | 不应吸收什么 |
|---|---|---|---|---|
| 可靠交付方法 | FBL-01、FBL-06、FBL-08、FBL-11 | 任务循环、验证规则、状态/Hook、benchmark | 完成定义、失败阈值、冷验证、机制评测 | “提示词可替代模型能力”的宣传与全局 hook |
| 委派与多模型编排 | FBL-02、FBL-07、FBL-10 | agent 定义、路由、派工票据、judge、runner | 写集合、能力/同意路由、独立审查 | 固定厂商模型、绕过项目治理、高权限 runner |
| 行为基线与提示词参考 | FBL-03、FBL-05、FBL-09 | CLAUDE.md/Markdown prompt | 轻核心、模块化、事实/推断分离 | 原文、泄露来源、宿主工具/产品指令 |
| UI / 设计资产体系 | FBL-12、SKL-13 | prompt、demo、build、前端 Skill | 资产证据包、按决策边界拆 Skill、可运行原型 | 未授权素材、异构依赖全量安装、前端规则越界到治理层 |
| 不可核验来源 | FBL-04 | 无 | 无 | 标题、传闻、镜像与任何推测 |

---

## FBL-01 · [Sahir619/fable-method](https://github.com/Sahir619/fable-method)

**定位。** 这是本组中证据链最完整的“可靠交付方法”仓库：四个 Skill、领域适配器、trap fixture、评测结果及方法说明共存。研究快照为 `88b5cf36`，MIT。其作者评测仍是小规模、自建、LLM judge 的 smoke evidence，不是普适性能证明。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 业务/决策层 | 区分问题诊断、计划优先任务和可执行任务；判断答案可否从可访问证据得到 | 先选交付形态，避免把“请分析”误作“直接改动” |
| 编排/治理层 | `classify → define done → evidence → decide → act → verify → report`；复杂任务可并行取证后集中决策 | 每项工作先有可观察的完成定义、证据预算、授权边界和停止条件 |
| 执行/证明层 | 意图冲突检查、最小变更、同类缺陷检索、对完成报告的反向审计 | 把“已完成”视为待证明 claim，而不是执行者口述事实 |

**萃取原子。** 请求形态路由、完成定义、证据与新鲜度门、意图冲突表、授权门、最小改动 + Twin Check、交付 claim judge、领域适配器模板。

**适合迁移。** `research-evidence-qualification`、`delivery-claim-judge`、`domain-adapter-builder` 的方法底座；特别适配当前项目的公开 GitHub 研究和 candidate-only distillation lane。

**禁止直搬。** Fable 品牌和“弱模型胜强模型”的结论、Claude 插件安装方式、作者的专用 agent 名称、未经当前项目验证的评测阈值。即使 MIT 覆盖作者表达，也优先以本项目自己的中文契约重写。

---

## FBL-02 · [DannyMac180/fable-advisor](https://github.com/DannyMac180/fable-advisor)

**定位。** 小型 Markdown agent / orchestration Skill 组合，研究快照 `92973f68`，MIT。它更像一个“架构者—实施者—独立 reviewer”的任务票据模板，而不是已验证的编排平台；未发现可独立复跑的 CI 或效果评测。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 业务/决策层 | 主代理保留需求澄清、接口、取舍、风险和验收 | 把“判断”与边界清楚的“执行”分开，责任不随派工转移 |
| 编排/路由层 | routine / complex / review 通道；按规格是否足以决定结果与失败历史路由 | 以不确定性、风险、可逆性和验收可得性路由，而不是只按文件数或模型名 |
| 执行/证明层 | 六段式委托、diff 回读、验证重跑、空 diff 拒绝、最终 clean-context review | task ticket + independent evidence gate |

**萃取原子。** `Objective / Files / Interfaces / Constraints / Verification / Reasoning` 委托合同；模型/通道透明；失败升级；空产物拒绝；独立 reviewer 的 `ship / fix-first / rethink` 三值结论。

**适合迁移。** `delegation-spec-contract`、`task-lane-router`、`delegated-delivery-verifier`。这些应成为本项目多 agent 工作的可选工作流，而不是覆盖现有 `AGENTS.md` 的全局 prompt。

**禁止直搬。** 特定 CLI、模型 slug、认证与 token 假设；任何要求子代理忽略项目编排规则的前导语；`--skip-git-repo-check` 类参数。它们可能越过当前 main branch、脏工作区保护和不主动 commit 的明确规范。

---

## FBL-03 · [TheColliny/FableClaudeMDForOpus](https://github.com/TheColliny/FableClaudeMDForOpus)

**定位。** 面向 Claude Code 的 Guardrails Kit：小型 `CLAUDE.md` 核心、按需 guardrail 文档、迁移说明和状态管理建议。研究快照 `e96027da`；未找到许可证，GitHub API license 为 null，因此只能归纳思想，不能复制文本、脚本或模板。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 业务/状态层 | TASK 块、范围、验收、约束、`STATE.md` 恢复点 | 用真实状态账本而非聊天记忆恢复长任务 |
| 编排/控制层 | 在“将要编辑、测试失败、要宣布完成”等事件按需加载规则 | 轻核心 + 事件触发 playbook，避免长提示词常驻失焦 |
| 执行/证明层 | 先读再改、窄基线、失败账本、验证回显 | 本轮真实工具输出决定 VERIFIED / UNVERIFIED，而不是乐观措辞 |

**萃取原子。** 事件触发守卫、任务块与基线、失败账本、验证回显、跨会话 checkpoint、代码陷阱局部检查表。

**适合迁移。** `session-checkpoint-recovery`、`task-scope-and-baseline`、`verification-evidence-echo`、`failure-ledger-and-escalation`。它们能加强现有 `.kiro/plan/`、`.codex/session-thread.md` 的使用，而不是另建一个未经治理的会话存储。

**禁止直搬。** 整份 `CLAUDE.md`、固定 marker、迁移脚本及自动 commit 建议；它们既无许可，也与本项目现有工作区与提交规则可能冲突。

---

## FBL-04 · [asgeirtj/system_prompts_leak](https://github.com/asgeirtj/system_prompts_leak)

**核验结论：排除。** 2026-09-23 对原 URL 的 GitHub 页面、REST/API 和 Git 远端访问均未取得内容，网页返回 HTTP 404。404 不能区分删除、改名、私有或链接错误；因此没有默认分支、提交、许可证、文件树或方法论证据。

不从标题推断“各厂商系统提示词”真实性，不寻找不明镜像或缓存，也不把任何提示词泄露内容纳入本项目。若未来有作者恢复 URL、明确 commit SHA 或合法授权副本，应作为新来源重新走 source/license review。

---

## FBL-05 · [KinetiNode/claude-fable-5-system-prompt-clean](https://github.com/KinetiNode/claude-fable-5-system-prompt-clean)

**定位。** 纯 Markdown 的跨模型行为基线（`core / balanced / complete` 三档），研究快照 `c2624b5f`，MIT。它没有 runtime、工具调用、测试或编排器；真正的价值是“将厂商实现细节与通用行为原则分开”。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 业务/交互层 | 识别目标、必要澄清、诚实处理不确定性、清晰表达 | 事实、推断、假设与观点分层表达 |
| 推理/编排层 | 正确性与诚实优先，复杂任务考虑权衡与失败模式 | 最小必要澄清与交付前覆盖度检查 |
| 交付层 | 遵守项目惯例、避免虚构与无谓元评论 | 用短行为基线统一跨模型的报告质量 |

**萃取原子。** 优先级栈、认识论标注、最小必要澄清、交付前自检、分级上下文预算。

**适合迁移。** 一个很短的 `evidence-aware-response-baseline`，仅规定本项目回答如何标示事实、推断、限制和验证状态。它不应替代已有系统/开发者/项目规则。

**禁止直搬。** 所谓上游提示词的措辞和真实性叙事；“跨模型兼容”不等于跨模型评测；与当前宿主不相符的 tool/MCP/产品行为。

---

## FBL-06 · [mrtooher/fable-mode](https://github.com/mrtooher/fable-mode)

**定位。** 面向复杂交付的 Claude Skill/agent 组合，含 stage map、worker 分工、double check、benchmark。研究快照 `a368f94a`；没有 LICENSE，不能复制其 Skill、hook 或文本。其自报 benchmark 的价值在于披露“高能力模型正确性增益可能为零、但审计轨迹增加成本”的边界。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 任务治理层 | 阶段地图；每阶段一个可验证产物；重规划预算 | `阶段 → 工件 → 可失败验证` 三元组 |
| 角色层 | 编排者、推理 worker、机械 worker、冷 verifier 分工；禁止 worker 嵌套派工 | 有边界的最小并行与责任隔离 |
| 验收层 | 冷审者只看规格与产物；PASS / FAIL / UNVERIFIABLE | 防确认偏误的交付前 claim/requirement checklist |

**萃取原子。** Stage Map First、委托合同、可失败验证、冷验证隔离、三值结论、综合缝隙检查、先证实再报警、范围/重规划预算。

**适合迁移。** 面向多文件、跨来源、长周期或高风险任务的 `staged-delivery-orchestrator` 与 `cold-artifact-verifier`。在本项目中可直接映射到 distillation job 的阶段与 QA，不需安装 Claude 插件。

**禁止直搬。** Claude 模型阶梯、Task schema、“无 Write/Edit 就安全”的误解（Bash 仍可能写文件）、全局安装脚本。多阶段与双检会增加成本，不能强加给琐碎任务。

---

## FBL-07 · [duolahypercho/fusion-fable](https://github.com/duolahypercho/fusion-fable)

**定位。** 独立 panel → judge 综合的多模型 Skill，研究快照 `a07a62e0`，MIT。它的可复用方法是隔离式多视角与证据化综合，不是“融合后等同 Fable”的市场主张。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 决策层 | 对高不确定、高代价错误的议题收集独立解决方案 | 以分歧、盲区和证据强度帮助人类决策，不以多数票替代事实 |
| 编排层 | panelist 接收同一原始任务且互不看答案；judge 独立综合 | independent fan-out + judge separation，降低早期锚定 |
| 执行/审计层 | 研究按共识/冲突/部分覆盖/独特洞见/盲区综合；代码候选先分别运行再合并 | 运行证据优先于文字平均；外部模型失败必须透明降级 |

**萃取原子。** 独立 fan-out、judge 分离、五类综合结构、证据权重、降级透明、候选先运行后 graft、计划与执行分离。

**适合迁移。** 仅作为需要人类决策的 `independent-evidence-panel` 或 `convergent-plan-review`。适合架构选择、重大迁移、关键市场判断或多个可运行候选的对比。

**禁止直搬。** 脚本会复制工作区并用高权限方式调用 Codex/Gemini 等工具，且将原问题与多模型回答落盘；不得运行。多供应商外发须先有敏感性分级、明确可外发 provider、预算、保留期和用户授权。

---

## FBL-08 · [fivetaku/fablize](https://github.com/fivetaku/fablize)

**定位。** Claude plugin / hook 集合，研究快照 `e221f32b`，MIT。它把可程序化纪律放入目标状态、根因调查、运行态观察和 stop gate；同时明确提出应测量机制自身是否造成副作用。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 任务闭环层 | 多故事目标状态、checkpoint、最终验证故事 | 完成是带证据的状态转换，不是文本声称 |
| 调查/验证层 | 复现→至少三个竞争假设→证伪→因果链→前后验证；UI/图表/脚本要真实运行观察 | 根因优先与运行态验收 |
| Hook 控制层 | quick/normal/deep 分类、变更/验证记录、无验证的结束提醒 | 最小匹配路由与“验证缺失”显式化 |

**萃取原子。** 最终验收故事、复现优先、竞争假设、根因链、运行态观察、完成声明绑定工具证据、机制 ON/OFF 测量、时间/会话上限。

**适合迁移。** `resumable-goal-and-evidence-gate`、`root-cause-investigation`、`rendered-artifact-observation`、`skill-policy-ablation`。它们应写入项目认可的计划/报告与测试契约，而不是采用全局 hook。

**禁止直搬。** 全局 `CLAUDE.md` 注入、`~/.fablize` ledger、英文/韩文启发式分类、非空 `verify-evidence` 字段即代表验证的假设。Hook 的 fail-open 与正则识别不能取代权限、测试或发布审批。

---

## FBL-09 · [moely-ai/claude-fable-5-prompt](https://github.com/moely-ai/claude-fable-5-prompt)

**定位。** 一个“原始 / 泛化英文 / 泛化中文”提示词参考库，研究快照 `dd7cd6df`，无 LICENSE。README 自称原始提示词属于 Anthropic；所谓原始文件来源和完整性均未由官方或签名链证明。因此它只能支持原则研究，不能作为可部署资产。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 行为与边界层 | 语气、澄清、拒绝、风险话题表达 | 把通用行为与厂商产品信息拆开 |
| 信息与工具层 | 时效事实、用户 URL、文件/代码交付的触发条件 | 时效性触发器与用户给定资料优先 |
| 输出治理层 | 格式、引用、版权、产物媒介选择 | 复杂内容才增加结构，独立产物应落为可审计文件 |

**萃取原子。** 供应商层/行为层分离、策略模块化、时效性触发、交付媒介选择、格式服务于理解。

**适合迁移。** 作为 `agent-behavior-baseline` 和 `evidence-aware-research-response` 的反面校验材料：只重写经验证的最小行为模块。

**禁止直搬。** 所谓原始系统提示词、任何模型/价格/API/连接器断言、绝对策略文本。无许可且来源不明的原文不可复制、再发布或嵌入商业运行时。

---

## FBL-10 · [olsenbrands/fable-foreman](https://github.com/olsenbrands/fable-foreman)

**定位。** MIT 的多 agent 编码交付框架，研究快照 `fbfb0324`。含一个主 Skill、5 个 agent、委派/路由/验证文档、脚本与测试 fixture；本研究没有执行它的测试。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 任务层 | 先定义质量门槛和观察式完成条件 | 质量阈值优先于成本优化；达不到应 `NEEDS USER` |
| 编排层 | 先探测运行时能力；能力席位而非固定模型；7 段票据、WRITE SET、账本和有限恢复 | 并发前先声明写集合；能力/同意状态是运行时事实 |
| 验收层 | deterministic check、独立 reviewer、lead 读原始需求/diff/行为后最终接受 | 审查 PASS 是证据，最终验收仍属于负责者 |

**萃取原子。** 能力探测、质量/成本路由、`TASK / EXPECTED OUTCOME / CONTEXT / CONSTRAINTS / MUST DO / MUST NOT / OUTPUT FORMAT / WRITE SET` 票据、写集合、三套状态词汇、证据分级、有限恢复、停放并继续。

**适合迁移。** `delivery-ticket-and-write-set`、`evidence-based-acceptance`、`capability-and-consent-routing`。这三个能够为本项目多 agent 工作提供准确的 ownership 和批准门。

**禁止直搬。** Worktree/WIP commit、用户级 CLI 安装、具体 provider 价格/模型矩阵/transport。它们与当前项目 main branch、禁止 worktree、不主动 commit 的规则冲突。

---

## FBL-11 · [itsinseong/value-for-fable](https://github.com/itsinseong/value-for-fable)

**定位。** AGPL-3.0 的 plugin、output style、hook 与 benchmark 组合，研究快照 `afbfff6e`。它的有价值部分不是“某模型接近 Fable”的声称，而是公开记录了消融失败、样本小和判题偏差等实验边界。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 质量策略层 | 结论先行、证据可见、诊断关注全部线索 | 能力上限与行为表现分离，主假设必须解释关键线索 |
| 会话编排层 | 触发式模式、2-pass reviewer、必要时升级模型 | 窄范围 reviewer 与高风险任务的可见升级 |
| 执行/漂移层 | 先读后改、并行独立工具调用、完成前验证、长会话提醒 | 最便宜判别测量、置信度校准、可逆性决定行动/暂停 |

**萃取原子。** 线索覆盖优先、低成本判别测量、验证绑定完成、置信度校准、可逆性门、窄范围两轮审查、反压缩经验、对新策略的对照实验与停用条件。

**适合迁移。** `evidence-first-diagnosis`、`verified-delivery-reporting`、`scoped-two-pass-review`、`prompt-policy-ablation`。对于当前 KB，最直接的是在候选输出进入人工 promotion 前设计小型 on/off eval。

**禁止直搬。** AGPL 的 prompt、hook、benchmark 实现或网络服务衍生物；模型控制语义、会话 transcript 路径和常驻 output style。任何复写应独立完成并先作许可证/法务评估。

---

## FBL-12 · [pulkitxm/claude-directory](https://github.com/pulkitxm/claude-directory)

**定位。** MIT 的前端实验和展示目录，研究快照 `f3d7e12f`。核心不是 agent 编排，而是将设计生成意图、源代码、demo、构建与静态展示连为可检索的资产单元。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 设计资产层 | Hero、landing、shader、component、portfolio 等可浏览实验 | 按用户/设计场景归档，而不是按技术文件堆放 |
| 实验编排层 | `prompt.md + 源码 + package manifest + demo + poster` | Prompt—实现—演示的三元证据包 |
| 交付展示层 | 自动发现项目、构建 Pages、校验入口与静态 assets | 构建后交付检查；研究/审计资料与公开展示分离 |

**萃取原子。** 项目级隔离、可检索实验目录、从可运行 demo 反推交付条件、production 展示与 `.reference/.audit` 分离。

**适合迁移。** `reference-to-ui-prototype`、`ui-experiment-catalog`、`static-preview-integrity-check`。它们可用于未来 KB 产品界面探索，而不影响当前知识处理链路。

**禁止直搬。** 整库或全量依赖安装、第三方视觉/视频/字体/商标、pixel-faithful clone 资产、Pages 脚本作为业务应用发布链路。MIT 不自动覆盖子项目使用的第三方素材。

---

## SKL-13 · [emilkowalski/skills](https://github.com/emilkowalski/skills)

**定位。** MIT 的 13 个设计工程 Skill，研究快照 `85e8e236`。它提供的更高价值是 Skill 架构范式：每个 Skill 对应一种决策类型，实施、审查、全仓审计、发散原型、依赖选择严格分开。

| 分层 | 实际能力 | 可迁移的机制 |
|---|---|---|
| 专业知识层 | 动效、性能、无障碍、移动体验、组件和依赖选择 | 将“品味”拆为可讨论的目标、约束和质量门 |
| 工作流层 | animate / review / improve / prototype 等职责分开 | 一 Skill 一类决策，避免万能 Skill 越权 |
| 执行层 | recipe、文件证据、Before/After/Why、plan 模板与验证要求 | 审查发现应能成为低成本执行者的可执行计划 |

**萃取原子。** 决策顺序先于参数、频率决定体验预算、性能/无障碍入场门、可执行审查发现、不动也是有效结果、侦察→并行只读审计→回读引用、真正有差异的原型发散、依赖按任务/现状决策。

**适合迁移。** `ui-craft-review`、`ui-experience-audit-to-plan`、`prototype-divergence-lab`、`mobile-web-finish-check`、`dependency-decision-record`。最重要的迁移价值是其**边界设计**，而不是特定 CSS、Swift 或库清单。

**禁止直搬。** 把前端/动效规则扩张到知识治理、后端或业务决策；过期的框架参数和库建议；未被当前项目采用的专用依赖 Skill。真正落地时必须按当前技术栈与官方文档复核。

---

## 结论：可迁移的不是“Fable”，而是六个可验证问题

1. **这个请求应该被诊断、计划还是执行？** — FBL-01。
2. **完成到底由什么可观察证据定义？** — FBL-01 / 03 / 06 / 08 / 11。
3. **任务能否安全委派，谁能改哪里，何时需要用户？** — FBL-02 / 06 / 10。
4. **单一答案不可靠时，是否值得引入独立视角，且是否允许外发？** — FBL-07。
5. **如何把研究、原型和设计资产保存为可追溯、可复用的证据包？** — FBL-12 / SKL-13。
6. **新增规则本身是否真的改善了目标任务，还是只是增加仪式和 token？** — FBL-08 / FBL-11。

下一步不应“安装 12 个仓库”，而应从这些问题中挑选本项目眼下最需要的 1–2 个，并以清晰的输入、输出、验证和停止条件制作自己的 Skill。候选组合见 [03-skill-portfolio.md](03-skill-portfolio.md)。
