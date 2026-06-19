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

Planning state lives in `.kiro/plan/`. Current key outputs include a full 81-source register, parser unit manifest, 50-question eval set, 800 all-extractable draft cards from 80 non-duplicate sources, QA/regression reports, answer-trace fixtures, a durable local vector-store package for the 800-card set, a pending-review human-gold locator label seed, a private no-provider retrieval API prototype, and a draft PRD addendum/directory blueprint under `drafts/analysis/`.

Use bundled Python for PDF/Office parsing. Use Homebrew Python with `sentence_transformers` for local BGE embedding regression.

Project-local decisions on 2026-06-19 approved metadata retention, allowed existing draft cards, approved batch-30 expansion, and accepted ADR 002: local-only now, private staging next, provider/hybrid only after explicit approval.

All-extractable local expansion passed gate on 2026-06-19. CSV row support was added for `SRC-CONSULT-030` and `SRC-CONSULT-031`, so the current all-extractable local card set covers 80 non-duplicate sources and 800 cards with `csv_row` locators. `SRC-CONSULT-016` is the only skipped source because it is a duplicate EPUB secondary to the preferred PDF source.

Durable local index package: `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/`. It stores 800 row-aligned records and 512-dimension local BGE embeddings from the current all-extractable set. Raw vector-only recall is a diagnostic lower bound; accepted local retrieval path is vector search plus deterministic rerank, with answerable reranked source_recall@1 = 0.9583 and @5 = 1.0 in the current smoke.

Human-gold locator label seed: `shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl`. It has 50 labels, 48 locator candidates, 2 policy-only refusal labels, QA failure_count 0, and all labels remain `pending_human_review`.

Human label review workflow: `shared/eval/consultant-agent/human-gold-locator-label-review.queue-20260619.csv`, `shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl`, and schema `shared/eval/consultant-agent/human-gold-locator-label-review.schema-20260619.json`. Workflow validation has failure_count 0, pending_decision_count 50, approved_decision_count 0, provider_call_count 0, and live_kb_write_count 0.

Private no-provider retrieval API prototype: `agents/consultant-agent/runtime/local_retrieval_api.py`. It exposes `/health`, `/retrieve`, and `/eval/label-seed` for localhost/private use. Current smoke loads 800 records and has failure_count 0, label_seed_match_at_5 = 1.0, policy_refusal_pass_rate = 1.0, provider_call_count = 0, and live_kb_write_count = 0.

Draft staging auth/audit contract: `drafts/analysis/consultant-role-kb-staging-auth-audit-design-20260619.md` plus schema `shared/audit/consultant-agent/staging-audit-event.schema-20260619.json`. Local validator output at `tmp/consultant-role-kb-staging-auth-audit-contract-validation-20260619.json` has 2 sample events, failure_count 0, provider_call_count 0, live_kb_write_count 0, and source_text_returned false. This is design/local validation only; no staging deployment has occurred.
