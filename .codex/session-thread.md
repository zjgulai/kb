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
- All-extractable expansion completed: 80 selected non-duplicate sources, 800 local draft cards, QA failure_count 0, answerable anchored_citation@1 0.9792, answerable anchored_citation@5 1.0, answer-trace 12/12.
- CSV loader support completed for `SRC-CONSULT-030` and `SRC-CONSULT-031`: 20 `csv_row` locator cards added; `SRC-CONSULT-016` is the only skipped source because it is a duplicate secondary EPUB.
- Durable local vector store rebuilt after CSV support: 800 records, 800 embedding rows, 512 dimensions, local `BAAI/bge-small-zh-v1.5`, row-aligned metadata in `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/`.
- Vector-store smoke: raw vector answerable source_recall@1 0.5833 and @5 0.75; vector plus deterministic rerank answerable source_recall@1 0.9583 and @5 1.0; fixture answerable reranked @5 1.0.
- Human-gold locator label seed completed: 50 pending-review labels, 48 locator candidates, 2 policy-only refusal labels, QA failure_count 0; no labels are human-approved yet.
- Human label review workflow completed: 50-item review queue, 50-item decision template, validation failure_count 0; all decisions remain pending and approved_decision_count is 0.
- Private no-provider retrieval API prototype completed and re-smoked against the 800-record index: localhost/private `/health`, `/retrieve`, and `/eval/label-seed`; smoke failure_count 0, label_seed_match_at_5 1.0, policy_refusal_pass_rate 1.0.
- Draft staging auth/audit contract completed: private ingress/auth/RBAC/audit schema design, JSON schema, and local validator; contract validation failure_count 0 over allowed and denied sample events.
- Local staging auth/audit harness completed: localhost-only wrapper around the private retrieval API with bearer-token hash auth, role-gated protected endpoints, and audit events for allowed, denied, and policy-refusal requests; smoke failure_count 0, audit_schema_failure_count 0, audit_forbidden_leak_count 0.

## Active Next Work

Full extraction readiness sprint is now in progress.

Evidence:

- branch: `main`
- remote: `https://github.com/zjgulai/kb.git`
- full source register: 81/81 sources registered
- parser manifest: 81/81 parse success, 0 parse errors, 23310 structural units
- card QA: 800 all-extractable cards, failure_count 0, locator_manifest_coverage 1.0
- all-extractable retrieval regression: answerable anchored_citation@1 0.9792, @5 1.0
- answer trace: 12/12
- durable local vector store: 800 records, 800 embedding rows, local BGE 512-dim embeddings from the current 800-card all-extractable set
- vector-store smoke: answerable reranked source_recall@1 0.9583, @5 1.0; raw vector-only @5 0.75 is diagnostic, not acceptance path
- human-gold locator label seed: 50 labels, 48 locator candidates, 2 no-source refusal labels, all `pending_human_review`, QA failure_count 0
- human label review workflow: review_queue_count 50, decision_template_count 50, pending_decision_count 50, approved_decision_count 0, failure_count 0
- private no-provider retrieval API smoke: record_count 800, label_seed_match_at_1 0.9375, label_seed_match_at_5 1.0, policy_refusal_pass_rate 1.0, workspace forbidden 403, failure_count 0
- staging auth/audit contract validation: event_count 2, allowed_event_count 1, denied_event_count 1, failure_count 0, provider_call_count 0, live_kb_write_count 0, source_text_returned false
- local staging auth/audit harness smoke: record_count 800, allowed HTTP 200, policy refusal HTTP 200, missing-token 401, RBAC denial 403, label_seed_match_at_5 1.0, policy_refusal_pass_rate 1.0, audit events 5, failure_count 0, provider_call_count 0, live_kb_write_count 0

Raw `consult/` source files remain excluded by `.gitignore`; only `consult/README.md` is tracked.

Next blockers:

- legal/source-owner review packet requires human decisions;
- human-gold locator labels now have a review queue/template but still require manual reviewer decisions before they can be treated as approved gold labels;
- persistent derived-card storage policy is pending;
- runtime ADR 002 is accepted for local-only now, private staging next, provider/hybrid only after explicit approval;
- private no-provider retrieval API and staging auth/audit harness are local prototypes only; no staging deployment has occurred;
- no provider call, live KB ingestion, staging deployment, or production launch has occurred.
- next local build choices: actual human-review decisions for locator labels, security-approved staging implementation, or PRD addendum promotion after human/legal review.
