---
title: "Enhanced AI 来源登记册"
status: "research_snapshot"
retrieved_at: "2026-09-23"
source_mode: "public GitHub/web research"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
live_ingestion_boundary: "no live KB ingestion"
---

# 来源登记册

## 取证规则

每条“仓库能力”都必须能回到公开 URL、当前提交快照和实际文件结构。README 是作者声明；可执行代码、Skill 文件、评测夹具和明确的许可证是更强证据。未能打开、无法克隆或没有可验证实现的来源，不据此构建可执行能力。

本次提交快照通过 `git ls-remote <repo> HEAD` 于 2026-09-23 取得。它只定位研究时的公开版本，不代表项目对仓库代码、模型输出或其中转述的上游系统提示词拥有再授权权利。

| ID | 仓库 | 方法类别 | 研究快照（HEAD） | 证据 / 许可证状态 |
|---|---|---|---|---|
| FBL-01 | [Sahir619/fable-method](https://github.com/Sahir619/fable-method) | 工作方法、循环、验证、领域适配器 | `88b5cf36b10ee3679e08ee0f0181b9774d481508` | 一手 Skill、评测和夹具；MIT；性能宣称仍属自报评测 |
| FBL-02 | [DannyMac180/fable-advisor](https://github.com/DannyMac180/fable-advisor) | 多模型策略与任务编排 | `92973f684fe2c66166eebdb8fe8b5a187fc8c312` | 一手 Markdown agents / Skill；MIT；无独立评测/CI 证据 |
| FBL-03 | [TheColliny/FableClaudeMDForOpus](https://github.com/TheColliny/FableClaudeMDForOpus) | 质量行为指令的 Claude MD 适配 | `e96027da98f233458c53847e340a807e678b98f5` | Guardrails 文档可读；无 LICENSE / GitHub license=null；仅可独立归纳原则 |
| FBL-04 | [asgeirtj/system_prompts_leak](https://github.com/asgeirtj/system_prompts_leak) | 系统提示词集合（用户描述） | — | 2026-09-23 GitHub HTTP 404；不尝试绕过访问或从非授权镜像恢复 |
| FBL-05 | [KinetiNode/claude-fable-5-system-prompt-clean](https://github.com/KinetiNode/claude-fable-5-system-prompt-clean) | 跨模型行为原则的精简适配 | `c2624b5fa0f3e5d03ded01a8d6f66e6f661f016b` | 纯 Markdown 行为基线；MIT；没有跨模型评测 |
| FBL-06 | [mrtooher/fable-mode](https://github.com/mrtooher/fable-mode) | 阶段化执行、委派、双重检查 | `a368f94a36e38c9b42648cc9b4a2a28347d165ea` | Skill、agents、benchmark 可读；无 LICENSE / license=null；不可复制文本或 hook |
| FBL-07 | [duolahypercho/fusion-fable](https://github.com/duolahypercho/fusion-fable) | 双模型草拟—审阅—融合 | `a07a62e0cdd75b5b67289411d2c0d648ccf24316` | Skill、judge rubric、脚本可读；MIT；脚本有高权限与多供应商外发风险 |
| FBL-08 | [fivetaku/fablize](https://github.com/fivetaku/fablize) | 程序化完成、证据、验证 | `e221f32b16f7b0ef39393ba47c37cb8345ffe749` | Skill、hook、状态脚本、测量协议可读；MIT；hook 不能代替权限控制 |
| FBL-09 | [moely-ai/claude-fable-5-prompt](https://github.com/moely-ai/claude-fable-5-prompt) | 原始/泛化/中文提示词参考 | `dd7cd6df98d12d85ff785c8bbf36a70f12019091` | 无 LICENSE；原始提示词的来源/授权不可核验，仅可研究抽象原则 |
| FBL-10 | [olsenbrands/fable-foreman](https://github.com/olsenbrands/fable-foreman) | 多 Agent 编排、派工、独立验证 | `fbfb03247a2d74f72f830daf8bfe00dbd952aaed` | Skill、5 个 agent、验证/路由文档与脚本 fixture；MIT；未在本项目执行测试 |
| FBL-11 | [itsinseong/value-for-fable](https://github.com/itsinseong/value-for-fable) | 成本—质量分层运营 | `afbfff6e63fb48b133be68fb8ddff254df01dbaf` | Plugin、hook、benchmark 可读；AGPL-3.0；不复制或嵌入闭源运行时 |
| FBL-12 | [pulkitxm/claude-directory](https://github.com/pulkitxm/claude-directory) | AI 辅助界面/前端资产目录 | `f3d7e12f34bf7d90130dce3ec3b26cf69c29794e` | Prompt—源码—demo—构建目录；MIT，但内含第三方视觉/媒体需逐项权利核验 |
| SKL-13 | [emilkowalski/skills](https://github.com/emilkowalski/skills) | 设计/工程实践 Skill 集 | `85e8e2363b713506e1d5b6e07a0eb2da66be1bc3` | 13 个边界明确的 SKILL.md；MIT；前端建议实施时需重新查官方文档 |

## 许可与来源处理原则

1. 所见到的仓库许可证只适用于该仓库作者能授权的部分，不自动覆盖其中声称来自第三方/平台的系统提示词。
2. 本研究不 vendoring、不执行第三方安装脚本、不写入任何模型系统提示词，也不把外部内容写入现有 live KB。
3. 若之后选择实现某个 Skill，只复写经本项目验证后确有必要的行为契约；不复制外部表达、品牌名、模型特定工具调用或长段提示词。
4. FBL-04 在取得作者恢复链接、具体 commit SHA 或用户提供的合法本地副本前，保持 `unverified / excluded`，而非用猜测补齐。
