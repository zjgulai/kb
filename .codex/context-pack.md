---
title: "KB Project Context Pack"
status: "active"
created_at: "2026-06-19"
scope: "compact Codex self-evolution project context"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB Project Context Pack

This workspace is a draft/local KB platform project. The active role slice is `consulting-kb` plus `consultant-agent` for a 高级咨询顾问诊断与交付 Copilot.

Durable boundaries: `production unchanged`, `no KB provider call`, no live KB ingestion, no client-ready publication, and no raw source redistribution. Raw `consult/` files are local-only because source policy is `evidence_grade=C` and `license_status=pending_legal_review`.

Planning state lives in `.kiro/plan/`. Current key outputs include a full 81-source register, parser unit manifest, 50-question eval set, 150 approved draft cards from the first batch, 300 batch-30 draft cards, 600 batch-60 draft cards, QA/regression reports, answer-trace fixtures, and a draft PRD addendum/directory blueprint under `drafts/analysis/`.

Use bundled Python for PDF/Office parsing. Use Homebrew Python with `sentence_transformers` for local BGE embedding regression.

Project-local decisions on 2026-06-19 approved metadata retention, allowed existing draft cards, approved batch-30 expansion, and accepted ADR 002: local-only now, private staging next, provider/hybrid only after explicit approval.

Batch-60 local expansion passed gate on 2026-06-19. `SRC-CONSULT-030` and `SRC-CONSULT-031` remain registered but were skipped because the current loader produced insufficient extractable units.
