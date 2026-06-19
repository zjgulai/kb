---
title: "KB Project Session Thread"
status: "active"
created_at: "2026-06-19"
scope: "active task state for consultant role KB project"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB Project Session Thread

## Current State

- A completed: controlled local expansion generated 150 cards across 15 registered P1 sources.
- Expanded gate passed: metadata completeness 1.0, unit locator coverage 1.0, source-only citation violations 0, long text violations 0.
- Expanded regression passed gate after latest rerank tuning: answerable anchored_citation@1 0.9792, answerable anchored_citation@5 1.0, answer-trace 12/12.
- B completed: draft PRD addendum and directory blueprint created.
- Project-local decisions captured: approve local metadata, allow existing draft cards, expand to batch-30, and accept ADR 002 runtime boundary.
- Batch-30 expansion completed: 30 sources, 300 local draft cards, QA failure_count 0, answerable anchored_citation@1 0.9792, answerable anchored_citation@5 1.0, answer-trace 12/12.
- Batch-60 expansion completed: 60 extractable sources, 600 local draft cards, QA failure_count 0, answerable anchored_citation@1 0.9792, answerable anchored_citation@5 1.0, answer-trace 12/12.
- Batch-60 skipped `SRC-CONSULT-030` and `SRC-CONSULT-031` because the current loader produced insufficient extractable units.
- All-extractable expansion completed: 78 selected sources, 780 local draft cards, QA failure_count 0, answerable anchored_citation@1 0.9792, answerable anchored_citation@5 1.0, answer-trace 12/12.
- All-extractable skipped `SRC-CONSULT-016` as duplicate secondary EPUB and `SRC-CONSULT-030`/`031` as insufficient-unit CSV sources.
- Durable local vector store completed: 780 records, 780 embedding rows, 512 dimensions, local `BAAI/bge-small-zh-v1.5`, row-aligned metadata in `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/`.
- Vector-store smoke: raw vector answerable source_recall@1 0.5833 and @5 0.75; vector plus deterministic rerank answerable source_recall@1 0.9583 and @5 1.0; fixture answerable reranked @5 1.0.
- Human-gold locator label seed completed: 50 pending-review labels, 48 locator candidates, 2 policy-only refusal labels, QA failure_count 0; no labels are human-approved yet.
- Private no-provider retrieval API prototype completed: localhost/private `/health`, `/retrieve`, and `/eval/label-seed`; smoke failure_count 0, label_seed_match_at_5 1.0, policy_refusal_pass_rate 1.0.

## Active Next Work

Full extraction readiness sprint is now in progress.

Evidence:

- branch: `main`
- remote: `https://github.com/zjgulai/kb.git`
- full source register: 81/81 sources registered
- parser manifest: 81/81 parse success, 0 parse errors, 23310 structural units
- card QA: 780 all-extractable cards, failure_count 0, locator_manifest_coverage 1.0
- all-extractable retrieval regression: answerable anchored_citation@1 0.9792, @5 1.0
- answer trace: 12/12
- durable local vector store: 780 records, 780 embedding rows, local BGE 512-dim embeddings
- vector-store smoke: answerable reranked source_recall@1 0.9583, @5 1.0; raw vector-only @5 0.75 is diagnostic, not acceptance path
- human-gold locator label seed: 50 labels, 48 locator candidates, 2 no-source refusal labels, all `pending_human_review`, QA failure_count 0
- private no-provider retrieval API smoke: record_count 780, label_seed_match_at_1 0.9375, label_seed_match_at_5 1.0, policy_refusal_pass_rate 1.0, workspace forbidden 403, failure_count 0

Raw `consult/` source files remain excluded by `.gitignore`; only `consult/README.md` is tracked.

Next blockers:

- legal/source-owner review packet requires human decisions;
- human-gold locator labels require manual reviewer decisions before they can be treated as approved gold labels;
- persistent derived-card storage policy is pending;
- runtime ADR 002 is accepted for local-only now, private staging next, provider/hybrid only after explicit approval;
- private no-provider retrieval API is local prototype only; no staging deployment has occurred;
- no provider call, live KB ingestion, staging deployment, or production launch has occurred.
- next local build choices: human-review workflow for locator labels, staging auth/audit design, CSV loader support, or PRD addendum promotion after human/legal review.
