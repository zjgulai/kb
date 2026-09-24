---
title: "Enhanced AI 方法论研究包"
status: "draft_research"
created_at: "2026-09-23"
scope: "对用户提供的 Fable 5.1 / Skill GitHub 仓库进行能力萃取、可迁移性评估、Skill 组合设计，并给出 Magpie-Horch 的外置迁移方案"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
live_ingestion_boundary: "no live KB ingestion"
---

# Enhanced AI 方法论研究包

## 本包回答什么

这不是把某个模型的系统提示词整体搬进项目的安装包，而是把 13 个公开仓库中可验证、可复用的工作方法拆成：

1. 仓库本身实际提供了什么；
2. 哪些机制可以抽象为跨模型的能力原子；
3. 它们分别适合解决什么场景与问题；
4. 在当前 KB 项目中应放在输入蒸馏、工作流编排、交付校验或 Skill 目录的哪一层；
5. 哪些内容不能直接迁移，包括来源不明的系统提示词、平台私有工具指令和未经验证的能力宣称。

## 阅读顺序

| 文件 | 用途 |
|---|---|
| [00-source-register.md](00-source-register.md) | 13 个来源的可追溯清单、快照引用与访问状态 |
| [01-repository-dossiers.md](01-repository-dossiers.md) | 每个仓库的分层能力、方法论与迁移限制 |
| [02-method-atoms.md](02-method-atoms.md) | 跨仓库去重后的能力原子、输入—机制—输出关系 |
| [03-skill-portfolio.md](03-skill-portfolio.md) | 可构建的 Skill 候选、解决的问题、优先级与非目标 |
| [04-migration-workshop.md](04-migration-workshop.md) | 迁移到当前 KB 项目的建议路线与待你确认的决策 |
| [05-magpie-horch-adaptation.md](05-magpie-horch-adaptation.md) | 面向 Magpie-Horch 的外置 Skill 架构、已安装的第一版与后续验证路线 |

## 研究边界

- 仅使用公开 GitHub 仓库、公开页面和本地项目既有设计作为研究证据。
- 不复制外部仓库的长文本、完整系统提示词、私有工具协议或任何疑似泄露内容；这里保存的是短摘要、结构化事实、方法原子和来源链接。
- “Fable 5.1”是这些社区仓库使用的名称，不被当作官方能力或性能保证。所有效果宣称只按仓库自身的证据等级记录。
- 当前项目仍保持 `production unchanged`、`no KB provider call`、`no live KB ingestion`。本研究包不修改现有 KB 运行时、索引、生产环境或 provider 配置。
- 前四份文档中的 KB 候选仍只保留为研究与迁移设计；Magpie-Horch 已按后续明确目标安装四个**用户级外置 Skill**。它们不注册为 KB 或 Magpie-Horch 的项目运行时 Skill，不写入项目配置、预设、源码或 provider。

## 初步结论

最值得迁移的不是“更长的系统提示词”，而是四类可检验的机制：任务分类与完成定义、证据/授权门、分工与可恢复交接、以及独立验证与反虚假完成。它们既可补强 KB 的 `distillation_job → QA → manual promotion` 链条，也可通过外置 Skill 提升 Magpie-Horch 的开发质量，而无需把第三方模型专用提示词写入任何项目核心运行时。

来源快照与完整判断见后续文档。所有分析均为本地研究成果；推送后仍不等同于生产启用。
