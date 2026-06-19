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

Planning state lives in `.kiro/plan/`. Current key outputs include a full 81-source register, parser unit manifest, 50-question eval set, 780 all-extractable draft cards from 78 sources, QA/regression reports, answer-trace fixtures, a durable local vector-store package, and a draft PRD addendum/directory blueprint under `drafts/analysis/`.

Use bundled Python for PDF/Office parsing. Use Homebrew Python with `sentence_transformers` for local BGE embedding regression.

Project-local decisions on 2026-06-19 approved metadata retention, allowed existing draft cards, approved batch-30 expansion, and accepted ADR 002: local-only now, private staging next, provider/hybrid only after explicit approval.

All-extractable local expansion passed gate on 2026-06-19. `SRC-CONSULT-016` is skipped as duplicate EPUB; `SRC-CONSULT-030` and `SRC-CONSULT-031` remain registered but were skipped because the current loader produced insufficient extractable units.

Durable local index package: `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/`. It stores 780 row-aligned records and 512-dimension local BGE embeddings. Raw vector-only recall is a diagnostic lower bound; accepted local retrieval path is vector search plus deterministic rerank, with answerable reranked source_recall@1 = 0.9583 and @5 = 1.0 in the current smoke.
