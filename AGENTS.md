---
title: "KB Project Agent Instructions"
status: "active"
created_at: "2026-06-19"
scope: "local instructions for Codex agents working in this KB workspace"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB Project Agent Instructions

- Default language is Chinese; preserve English method names, paths, code identifiers, and source terminology.
- Before work, read `.kiro/plan/task_plan.md`, `.kiro/plan/progress.md`, and `.codex/context-pack.md` when present.
- Treat this workspace as draft/local unless the user explicitly approves a production transition.
- Keep these boundaries separate: `production unchanged`, `no KB provider call`, `no live KB ingestion`, `read-only`, `draft`, and `manual review`.
- Do not commit or push raw `consult/` source files while their license status is `pending_legal_review`.
- Keep source traceability through `source_id`, `source_type`, `source_uri`, `evidence_grade`, `license_status`, `workspace`, `allowed_agents`, and `blocked_actions`.
- Do not reproduce long source text in cards, reports, or answers.
- Use `.codex/context-pack.md` for compact durable project context and `.codex/session-thread.md` for active task state.
- Write self-evolution candidate lessons only after failure, user correction, or test failure; do not promote long-term memory without explicit approval.

