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
- Human-label reviewer questionnaire completed: 50 reviewer-facing rows, 48 locator questions, 2 refusal questions; official decision template unchanged and approval_effect_count remains 0.
- Human-label questionnaire intake converter completed: unfilled questionnaire derives temporary candidate JSONL with 50 pending decisions, 0 approved decisions, official_template_write_count 0, provider_call_count 0, and live_kb_write_count 0.
- Human-label candidate promotion preflight completed: current candidate remains blocked with 50 pending decisions, 0 approved decisions, 0 changed rows, 4 blockers, official_template_write_count 0, and approval_effect_count 0.
- Private no-provider retrieval API prototype completed and re-smoked against the 800-record index: localhost/private `/health`, `/retrieve`, and `/eval/label-seed`; smoke failure_count 0, label_seed_match_at_5 1.0, policy_refusal_pass_rate 1.0.
- Draft staging auth/audit contract completed: private ingress/auth/RBAC/audit schema design, JSON schema, and local validator; contract validation failure_count 0 over allowed and denied sample events.
- Local staging auth/audit harness completed: localhost-only wrapper around the private retrieval API with bearer-token hash auth, role-gated protected endpoints, and audit events for allowed, denied, and policy-refusal requests; smoke failure_count 0, audit_schema_failure_count 0, audit_forbidden_leak_count 0.
- Shared staging readiness preflight completed: local preflight and draft runbook exist, but readiness is blocked with 6 blockers after product-owner human-label gate policy and runtime-config integration; no shared staging deployment has occurred.
- Legal/source-owner decision workflow completed: 81 pending source decision rows and 80 selected runtime sources pending; shared staging legal clearance remains false.
- Security/staging-control decision workflow completed: 8 pending security/operations control rows, 0 approved controls, 0 configured external controls, secret_like_value_count 0; shared staging security readiness remains false.
- Manual decision intake preflight completed: current default decision templates are structurally valid. Product-owner Q4:D waives the human-gold label gate for machine-seeded staging evidence only; reviewer-approved human labels remain 0/50 and human-gold metrics are not claimed.
- Manual decision intake smoke completed: default pending templates block, synthetic all-approved fixtures pass, invalid synthetic human decisions fail, provider/live-write counts stay 0, and synthetic fixtures are removed before exit.
- Product-owner decision record completed: Q1-Q7 captured as product intent only, raw `consult/` files remain excluded from GitHub, future Tencent Cloud Lighthouse upload is a separate deployment gate, and provider calls remain disabled.
- Staging runtime config preflight completed: current runtime_config_ready is false with 4 external config blockers: auth token hash, external audit path, rate limit status, and rollback owner. It logs no secret value, private contact detail, source text, provider call, or live KB write.
- Clearance execution pack completed: combined checklist has 88 rows, covering 80 selected legal/source-owner source rows and 8 security/operations controls; current clearance_execution_ready is false.
- Reviewer decision questionnaire completed: 88 reviewer-facing question rows generated from the clearance execution pack, with 80 legal/source-owner questions and 8 security/operations questions; official decision templates were not edited and approval_effect_count remains 0.
- Reviewer questionnaire intake converter completed: unfilled questionnaire derives temporary legal/security candidate JSONL under `tmp/`, validates with failure_count 0, keeps official templates unchanged, and records 0 legal/security approvals.
- Legal/security official decision promotion preflight completed: current candidate files remain blocked with 81 legal pending decisions, 8 security pending decisions, 0 approvals, 0 changed rows, 5 blockers, official_template_write_count 0, and approval_effect_count 0.
- Runtime-config redacted fixture smoke completed: default missing config remains blocked, redacted-ready fixture passes, and secret-like/private-contact fixture remains blocked without leaking raw values; no external configuration was applied.

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
- human-label reviewer questionnaire: questionnaire_row_count 50, locator_question_count 48, refusal_question_count 2, approval_effect_count 0, provider_call_count 0, live_kb_write_count 0
- human-label questionnaire intake: answered_response_count 0, derived_decision_count 50, pending_decision_count 50, approved_decision_count 0, official_template_write_count 0, approval_effect_count 0, provider_call_count 0, live_kb_write_count 0
- human-label candidate promotion preflight: status blocked, candidate_decision_count 50, candidate_pending_count 50, candidate_non_pending_count 0, candidate_approved_count 0, blocker_count 4, official_template_write_count 0, provider_call_count 0, live_kb_write_count 0
- private no-provider retrieval API smoke: record_count 800, label_seed_match_at_1 0.9375, label_seed_match_at_5 1.0, policy_refusal_pass_rate 1.0, workspace forbidden 403, failure_count 0
- staging auth/audit contract validation: event_count 2, allowed_event_count 1, denied_event_count 1, failure_count 0, provider_call_count 0, live_kb_write_count 0, source_text_returned false
- local staging auth/audit harness smoke: record_count 800, allowed HTTP 200, policy refusal HTTP 200, missing-token 401, RBAC denial 403, label_seed_match_at_5 1.0, policy_refusal_pass_rate 1.0, audit events 5, failure_count 0, provider_call_count 0, live_kb_write_count 0
- legal/source-owner decision workflow: source_count 81, selected_source_count 80, pending_review_count 81, selected_approved_internal_staging_count 0, failure_count 0
- security/staging-control decision workflow: control_count 8, pending_review_count 8, approved_control_count 0, configured_external_control_count 0, secret_like_value_count 0, failure_count 0
- manual decision intake preflight: manual_decision_intake_ready false, blocker_count 2, failure_count 0, human_label_gate_waived_for_staging true, reviewer-approved human labels 0/50, legal selected approved 0/80, security approved 0/8
- manual decision intake smoke: ok true, scenario_count 3, default pending blocked, synthetic all-approved ready, invalid synthetic human rejected, no retained synthetic approval evidence
- staging runtime config preflight: runtime_config_ready false, blocker_count 4, secret_value_logged false, private_contact_detail_logged false, provider_call_count 0, live_kb_write_count 0
- shared staging preflight: ready_for_shared_staging false, status blocked, check_count 24, pass_count 18, blocker_count 6, provider_call_count 0, live_kb_write_count 0
- clearance execution pack: checklist rows 88, legal selected pending 80, security pending 8, runtime config blockers 4, provider_call_count 0, live_kb_write_count 0
- reviewer decision questionnaire: questionnaire_row_count 88, legal_question_count 80, security_question_count 8, official_decision_templates_updated false, approval_effect_count 0, provider_call_count 0, live_kb_write_count 0
- reviewer questionnaire intake: answered_response_count 0, legal candidate decisions 81, security candidate decisions 8, legal selected approved 0/80, security approved 0/8, official_template_write_count 0, approval_effect_count 0, provider_call_count 0, live_kb_write_count 0
- legal/security official decision promotion preflight: status blocked, legal pending 81, legal selected approved 0/80, security pending 8, security approved 0/8, changed_row_count 0, blocker_count 5, official_template_write_count 0, provider_call_count 0, live_kb_write_count 0
- runtime-config redacted fixture smoke: scenario_count 3, pass_count 3, default_missing_config blocked, redacted_ready_fixture ready, secret_like_rejected_fixture blocked, redaction_leak_count 0 for all scenarios, provider_call_count 0, live_kb_write_count 0

Raw `consult/` source files remain excluded by `.gitignore`; only `consult/README.md` is tracked.

Next blockers:

- legal/source-owner review packet requires human decisions;
- human-gold locator labels now have a review queue/template but still require manual reviewer decisions before they can be treated as approved gold labels;
- human-label questionnaire and intake converter can produce temporary candidate decisions, but the official human-label decision file still requires real reviewer input before human-gold metrics can be claimed;
- human-label candidate promotion preflight now exists, but current candidate is a no-op pending set; a later official update still requires fully reviewed candidate decisions and explicit acceptance authorization;
- persistent derived-card storage policy is pending;
- runtime ADR 002 is accepted for local-only now, private staging next, provider/hybrid only after explicit approval;
- private no-provider retrieval API and staging auth/audit harness are local prototypes only; no staging deployment has occurred;
- shared staging readiness is blocked by legal/source-owner clearance over the 80 selected sources, security/operations control approval, external token hash, external audit path, rate limit configuration, and rollback owner; human-gold metrics still require separate reviewer-approved labels before they can be claimed;
- the reviewer decision questionnaire can guide human review, but the official legal/source-owner and security/operations JSONL decision files still require real reviewer input;
- the questionnaire intake converter can create candidate JSONL files, but candidate files under `tmp/` are not approval evidence until accepted into official decision files or supplied to manual intake through reviewed external paths;
- the legal/security official decision promotion preflight now exists, but current candidates are no-op pending sets; a later official update still requires reviewed candidate decisions and explicit acceptance authorization;
- redacted runtime fixtures prove validation mechanics only; they are not external configuration, security approval, or staging deployment evidence;
- no provider call, live KB ingestion, staging deployment, or production launch has occurred.
- next local build choices: human-label review decisions, official accepted-decision promotion workflow, shared-staging deployment gate after approvals, or PRD addendum promotion after human/legal review.
