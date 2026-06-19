---
title: "Consultant Role KB Extraction Findings"
status: "active"
created_at: "2026-06-19"
scope: "evidence and findings for consult role KB planning"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# Consultant Role KB Extraction Findings

## Project Context

- The project folder now has local `AGENTS.md` and `.codex/context-pack.md`; current behavior follows the project-local instructions plus the active plan files.
- `/Users/pray/project/kb` is a Git repository on `main`, tracking `origin/main`.
- The PRD declares `v2.1-draft`, `docs-only draft`, `production unchanged`, `no KB provider call`, and `not production ready`.
- Existing draft assets include source-register, eval-set, evidence-register, P1 PoC plan, and enterprise directory blueprint under `drafts/analysis/`.

## PRD Requirements Relevant To This Task

- P1 is a readonly proof-of-concept, not production.
- Every source needs `source_id`, `evidence_grade`, `source_uri`, `source_owner`, `version`, `workspace`, `allowed_agents`, and `blocked_actions`.
- P1 validates taxonomy, sample domain structure, shared ontology, agent playbook, evidence grade, eval set, workspace isolation, readonly MCP, and licensing.
- D-grade evidence must not support final conclusions.
- Missing source IDs, unresolved parser license, workspace isolation failure, citation precision failure, agent write attempts, or missing owner confirmation are stop conditions.

## Consult Folder Profile

Read-only source profile was generated at `tmp/consult-role-kb-source-profile-20260619.json`.

Observed inventory:

- Total profiled files: 81.
- File types: 68 PDF, 6 PPTX, 3 XLSX, 2 CSV, 1 DOCX, 1 EPUB.
- PDF pages reported: 9407.
- Parse errors after Excel dimension-gate rerun: 0.
- Candidate category counts: industry-analysis 29, consulting-playbook 26, diagnostic-guide 11, strategy-management 7, reference-data 6, client-development 5, transaction-advisory 4, consultant-delivery-craft 4, unclassified 3.

## Initial Interpretation

The `consult/` folder is not a single homogeneous document set. It is a senior consultant role library spanning:

- Consulting delivery craft: problem solving, executive summaries, PowerPoint, kickoff, proposal.
- Enterprise diagnostics: supply chain, business analytics, customer experience, product management, finance, talent, culture, org design.
- Transaction advisory: commercial due diligence, operational due diligence, post-merger integration, private equity board work.
- Industry-analysis playbooks: SaaS, retail, healthcare, automotive, technology, manufacturing, banking, insurance, pharmaceuticals, and others.
- Reference data: industry KPIs, functional KPIs, acronyms.
- Client development and procurement: RFP, proposal, finding clients.

## P1 Implication

Full-folder ingestion is too broad for P1. A viable P1 should use 12-20 documents focused on one role workflow and produce a 50-question eval set around cited answers, refusal behavior, and blocked actions.

## User Decisions

- P1 role scope: diagnostic and delivery senior consultant.
- Draft domain/agent: `consulting-kb` and `consultant-agent`.
- Source-use boundary: internal local PoC allowed.
- Source owner: 李梁.
- Output boundary: not narrowly limited, but automated send/submit/publish/approval remains blocked.
- Output language: Chinese first, English method/source terms retained.

## Artifacts Created After Decision

- Decision log: `drafts/analysis/consultant-role-kb-decision-log-20260619.md`.
- Source register candidate CSV: `drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv`.
- Eval set skeleton: `drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl`.
- Typed card sample dry run: `tmp/consultant-role-kb-card-samples-20260619.jsonl`.
- Card sample summary: `drafts/analysis/consultant-role-kb-card-sample-summary-20260619.md`.

## Schema Gap

The existing source-register enum did not cleanly represent third-party consulting playbooks, templates, and reference libraries. `external_reference` has now been added to `drafts/analysis/kb-source-register-template.md` and a sample row has been added to `drafts/analysis/kb-source-register.sample.csv`.

## Local Embedding/Indexing PoC

The user approved local embedding/indexing. A no-provider local hash embedding PoC ran against the typed cards:

- Script: `tmp/consultant_role_kb_local_hash_index_poc_20260619.py`
- Local index metadata: `tmp/consultant-role-kb-local-hash-index-20260619.json`
- Retrieval eval result: `tmp/consultant-role-kb-local-retrieval-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-local-embedding-indexing-poc-report-20260619.md`

Results: 33 cards indexed, 50 eval questions run, source_recall@1 = 0.76, source_recall@5 = 0.86. This is plumbing evidence only because the embedding method is deterministic hash embedding, not a real local semantic model.

## Real Local Embedding/Indexing PoC

After user approval, a real local embedding PoC ran with a locally cached model:

- Script: `tmp/consultant_role_kb_real_embedding_poc_20260619.py`
- Model: `BAAI/bge-small-zh-v1.5`
- Snapshot: `7999e1d3359715c523056ef9478215996d62a620`
- License recorded from local README: MIT
- Runtime: Homebrew Python 3.12, CPU, `sentence-transformers`
- Embedding dimension: 512
- Local index metadata: `tmp/consultant-role-kb-bge-small-zh-index-20260619.json`
- Retrieval eval result: `tmp/consultant-role-kb-bge-small-zh-retrieval-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-real-embedding-indexing-poc-report-20260619.md`
- ADR: `drafts/analysis/consultant-role-kb-embedding-adr-001-bge-small-zh-v1.5-20260619.md`

Results: 33 cards indexed, 50 eval questions run, source_recall@1 = 0.66, source_recall@5 = 0.90.

Interpretation:

- Fact: real local embedding/indexing is executable without a provider call and preserves card/source metadata.
- Fact: BGE top5 recall is higher than the hash baseline, while BGE top1 recall is lower than the hash baseline.
- Inference: the registered source is usually present in the first five retrieved cards, but a rerank/source-prior layer is needed before using top1 as an acceptance signal.
- Unknown: answer quality, citation precision, legal clearance, and live KB behavior are not proven by this local PoC.

## Rerank/Source-Prior PoC

The user approved continuing to the next step. A local rerank/source-prior PoC ran on top of the BGE embeddings:

- Script: `tmp/consultant_role_kb_rerank_source_prior_poc_20260619.py`
- Eval output: `tmp/consultant-role-kb-bge-source-prior-rerank-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-rerank-source-prior-poc-report-20260619.md`
- Label-leakage boundary: `allowed_source_ids` were not used during ranking; they were used only after ranking to score recall.

Results:

- BGE-only all-eval source_recall@1 = 0.66; rerank all-eval source_recall@1 = 0.92.
- BGE-only all-eval source_recall@5 = 0.90; rerank all-eval source_recall@5 = 0.96.
- Rerank answerable-eval source_recall@1 = 0.9583.
- Rerank answerable-eval source_recall@5 = 1.0.
- Remaining answerable top1 failures: 2.
- Remaining answerable top5 failures: 0.

Interpretation:

- Fact: deterministic source/card priors improve local source recall in the 33-card sample.
- Inference: source-intent priors materially improved source routing for ambiguous-scoping, client-ready PPT, and high-stakes due-diligence/refusal prompts.
- Unknown: the result may not hold after larger extraction or different source distributions.
- Boundary: still no production readiness, no provider call, no live KB ingestion, and no license clearance.

## Citation Anchor PoC

The user asked to continue the next step. A local citation-anchor PoC was run on the existing 33 typed-card samples:

- Script: `tmp/consultant_role_kb_citation_anchor_poc_20260619.py`
- Anchored card output: `tmp/consultant-role-kb-card-samples-anchored-20260619.jsonl`
- Anchor eval output: `tmp/consultant-role-kb-citation-anchor-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-citation-anchor-poc-report-20260619.md`

Anchor schema:

- PPTX: `slide:{n}`
- PDF: `page:{n}`
- DOCX: `paragraph:{n}`
- XLSX: `sheet:{sheet_name}#row:{n}`

Results:

- card_count = 33.
- citation_precision_ready_count = 33.
- citation_precision_ready_rate = 1.0.
- Modality coverage: 4 PPTX slide cards, 7 PDF page cards, 1 DOCX paragraph card, 21 XLSX sheet-row cards.
- The first run over-matched some acronym cards to the workbook title row; the matching logic was tightened and rerun so acronym cards resolve to concrete term rows.

Interpretation:

- Fact: the current card schema can carry unit-level citation anchors across PPTX, PDF, DOCX, and XLSX sources.
- Fact: every current sample card has a resolved unit-level anchor.
- Inference: the next PRD gate should score anchored retrieval/citation behavior, not just source recall.
- Boundary: this is anchor readiness only; it does not prove answer quality, legal clearance, production readiness, or live KB behavior.

## Anchored Retrieval/Citation Eval

The user asked to continue the next step. A local anchored retrieval/citation eval was run using the anchored card file:

- Script: `tmp/consultant_role_kb_anchored_retrieval_citation_eval_20260619.py`
- Eval output: `tmp/consultant-role-kb-anchored-retrieval-citation-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-anchored-retrieval-citation-eval-report-20260619.md`

Results:

- indexed_card_count = 33.
- eval_count = 50.
- answerable_eval_count = 48.
- all-eval source_recall@1 = 0.92.
- all-eval source_recall@5 = 0.96.
- all-eval anchored_citation@1 = 0.92.
- all-eval anchored_citation@5 = 0.96.
- answerable-eval anchored_citation@1 = 0.9583.
- answerable-eval anchored_citation@5 = 1.0.
- top1_has_unit_anchor = 1.0.
- source_only_citation_violation_count = 0.

Interpretation:

- Fact: retrieved results can carry unit-level locators instead of source-only citations.
- Fact: remaining answerable top1 failures are `CONSULT-EVAL-043` and `CONSULT-EVAL-047`; answerable top5 failures are zero.
- Inference: the next gate should prevent expanded extraction from regressing citation anchors, source routing, or refusal behavior.
- Boundary: the metric is still a proxy over typed-card anchors; there are no human gold locator labels yet, and this does not prove final answer quality or production readiness.

## Answer-Trace Fixture

The user asked to continue the next step. A deterministic local answer-trace fixture was run over 12 representative eval questions:

- Script: `tmp/consultant_role_kb_answer_trace_fixture_20260619.py`
- Trace output: `tmp/consultant-role-kb-answer-trace-fixture-20260619.jsonl`
- Eval output: `tmp/consultant-role-kb-answer-trace-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-answer-trace-fixture-report-20260619.md`

Results:

- trace_count = 12.
- trace_pass_count = 12.
- trace_pass_rate = 1.0.
- source_selection_pass_rate = 1.0.
- locator_citation_pass_rate = 1.0.
- boundary_checks_pass_rate = 1.0.
- blocked_action_pass_rate = 1.0.
- refusal_pass_rate = 1.0.
- long_text_reproduction_pass_rate = 1.0.
- workspace_isolation_pass_rate = 1.0.

Failures:

- None in the 12-question representative fixture after the source-intent prior rerun.

Interpretation:

- Fact: generated answer text can cite selected unit locators and preserve evidence/license/refusal/workspace boundaries.
- Fact: the previous answer-trace source-selection failures were cleared by source-intent routing.
- Inference: the next bottleneck is controlled expansion: new cards must preserve source metadata, unit locators, blocked actions, and regression coverage.
- Boundary: this is deterministic local fixture evidence, not provider-backed answer quality or production readiness.

## Small-Batch Expansion Gate

The next draft artifact was created at `drafts/analysis/consultant-role-kb-small-batch-expansion-gate-20260619.md`.

Key gate decisions:

- Recommended first expansion is a capped 120-180 card local batch across the 15 registered P1 sources, not the full `consult/` folder.
- Every expanded card must preserve `source_id`, `source_type=external_reference` where applicable, `evidence_grade=C`, `license_status=pending_legal_review`, `workspace=consultant-p1`, allowed agents, blocked actions, and a unit locator.
- Expansion is blocked on missing source IDs, missing unit locators, workspace leakage, provider calls, live KB writes, long source-text reproduction, or unauthorized license/evidence upgrades.
- Regression gates require metadata completeness = 1.0, unit locator coverage = 1.0, source-only citation violations = 0, answer-trace pass rate = 1.0, and answerable anchored_citation@5 >= 0.95.
- Boundary: this is a draft/local gate only; no expanded extraction has been run yet.

## Controlled Local Expansion

The controlled local expansion was executed after the user chose A before B.

Artifacts:

- Script: `tmp/consultant_role_kb_small_batch_expansion_20260619.py`
- Expanded cards: `tmp/consultant-role-kb-expanded-cards-20260619.jsonl`
- Gate eval: `tmp/consultant-role-kb-expanded-card-gate-eval-20260619.json`
- Expansion report: `drafts/analysis/consultant-role-kb-small-batch-expansion-report-20260619.md`
- Regression script: `tmp/consultant_role_kb_expanded_regression_eval_20260619.py`
- Retrieval/citation eval: `tmp/consultant-role-kb-expanded-anchored-retrieval-citation-eval-20260619.json`
- Retrieval/citation report: `drafts/analysis/consultant-role-kb-expanded-regression-eval-report-20260619.md`
- Answer trace eval: `tmp/consultant-role-kb-expanded-answer-trace-eval-20260619.json`
- Answer trace report: `drafts/analysis/consultant-role-kb-expanded-answer-trace-fixture-report-20260619.md`

Results:

- card_count = 150, with 10 cards per registered P1 source.
- metadata_completeness = 1.0.
- unit_locator_coverage = 1.0.
- source_only_citation_violation_count = 0.
- long_text_violation_count = 0.
- provider_call_count = 0.
- live_kb_write_count = 0.
- answerable anchored_citation@1 = 0.9167.
- answerable anchored_citation@5 = 1.0.
- expanded answer-trace pass rate = 1.0.

Interpreter note:

- PDF/Office parsing requires the Codex bundled Python runtime in this environment.
- Local embedding regression requires the Homebrew Python runtime with `sentence_transformers`.

Boundary:

- This is still local draft evidence only; no provider call, no live KB ingestion, no production deployment, and no legal/license clearance.

## PRD Addendum And Directory Blueprint

The draft addendum was created at `drafts/analysis/consultant-role-kb-prd-addendum-directory-blueprint-20260619.md`.

It proposes:

- `consulting-kb` as a draft role/domain;
- `consultant-agent` as the P1 role agent;
- `external_reference` source policy;
- unit-level citation locators;
- blocked action boundaries;
- a draft directory blueprint including `.codex/`, `.kiro/plan/`, `domains/`, `agents/`, `shared/`, `drafts/`, `tmp/`, and `archive/`.

Boundary:

- The source PRD file was not modified.
- This is a draft addendum candidate, not a production-ready PRD update.

## Full Extraction And Agent Launch Plan

The roadmap document was created at `drafts/analysis/consultant-role-kb-full-extraction-agent-launch-plan-20260619.md`.

It defines the path from the current local PoC to online use:

- W0 governance and legal/source-owner review;
- W1 full 81-source register;
- W2 parser productionization and unit manifests;
- W3 full typed-card extraction;
- W4 durable knowledge store and vector index;
- W5 `consultant-agent` runtime;
- W6 eval, red-team, citation, and safety gates;
- W7 staging deployment;
- W8 internal pilot;
- W9 production launch and operations.

Key blockers:

- legal/license decision for third-party `consult/` sources;
- persistent storage policy for derived cards;
- model/provider policy for online agent;
- production architecture and deployment target;
- human source-owner review.

Immediate next sprint:

- full 81-source register;
- parser unit-manifest CLI;
- card QA validator;
- rerank tuning for `CONSULT-EVAL-014`, `CONSULT-EVAL-017`, `CONSULT-EVAL-038`, and `CONSULT-EVAL-047`;
- legal/source-owner review packet;
- runtime decision for local, private staging, provider, or hybrid deployment.

## Full Extraction Readiness Sprint

Artifacts created:

- Full source register: `drafts/analysis/consultant-role-kb-full-source-register-20260619.csv`.
- Full source register report: `drafts/analysis/consultant-role-kb-full-source-register-report-20260619.md`.
- Parser unit-manifest CLI: `tmp/consultant_role_kb_parser_unit_manifest_20260619.py`.
- Parser unit manifest: `tmp/consultant-role-kb-parser-unit-manifest-20260619.jsonl`.
- Parser manifest report: `drafts/analysis/consultant-role-kb-parser-unit-manifest-report-20260619.md`.
- Card QA validator: `tmp/consultant_role_kb_card_qa_validator_20260619.py`.
- Card QA report: `drafts/analysis/consultant-role-kb-card-qa-validation-report-20260619.md`.
- Legal/source-owner review packet: `drafts/analysis/consultant-role-kb-legal-source-owner-review-packet-20260619.md`.
- Runtime ADR: `drafts/analysis/consultant-agent-runtime-adr-20260619.md`.
- Sprint execution report: `drafts/analysis/consultant-role-kb-next-sprint-execution-report-20260619.md`.

Evidence:

- Full register covers 81/81 profiled sources.
- Intake split: 15 `ready_for_poc`, 66 `registered`.
- All 81 sources remain `license_status=pending_legal_review`.
- Parser manifest covers 81/81 sources with parse_error_count = 0.
- Parser unit count = 23310, including 9407 PDF pages, 572 PPTX slides, 12112 XLSX sheet rows, 1178 CSV rows, 36 DOCX paragraphs, and 5 EPUB sections.
- Card QA over 150 expanded cards has failure_count = 0 and locator_manifest_coverage = 1.0.
- Rerank tuning cleared the four expanded answerable rank-1 misses; current expanded answerable anchored_citation@1 = 1.0 and @5 = 1.0.
- Answer-trace fixture remains 12/12.

Remaining blockers:

- Legal/source-owner approval is not complete.
- Persistent storage policy for derived cards remains pending.
- No full 81-source typed-card extraction has started.
- No durable vector store, retrieval API, staging service, provider generation, or production deployment has been built.

Boundary:

- `production unchanged`.
- `no KB provider call`.
- `no live KB ingestion`.
- Raw `consult/` files remain local-only.

## Batch-30 Local Expansion And Approval Capture

The project owner approved four local gates on 2026-06-19:

- `approve_local_metadata` for full source register and structural parser manifests.
- Existing 150 draft derived cards may remain persisted as local/draft eval artifacts before legal review.
- The next extraction batch may expand to 30 sources.
- ADR 002 runtime boundary is accepted: local-only now, private staging next, provider/hybrid only after explicit approval.

Artifacts created:

- Approval record: `drafts/analysis/consultant-role-kb-approval-decision-record-20260619.md`.
- Batch-30 source selection: `drafts/analysis/consultant-role-kb-batch30-source-selection-20260619.csv`.
- Batch-30 expansion script: `tmp/consultant_role_kb_batch30_expansion_20260619.py`.
- Batch-30 cards: `tmp/consultant-role-kb-batch30-cards-20260619.jsonl`.
- Batch-30 gate eval: `tmp/consultant-role-kb-batch30-card-gate-eval-20260619.json`.
- Batch-30 card QA report: `drafts/analysis/consultant-role-kb-batch30-card-qa-validation-report-20260619.md`.
- Batch-30 regression script: `tmp/consultant_role_kb_batch30_regression_eval_20260619.py`.
- Batch-30 retrieval/citation report: `drafts/analysis/consultant-role-kb-batch30-regression-eval-report-20260619.md`.
- Batch-30 answer-trace report: `drafts/analysis/consultant-role-kb-batch30-answer-trace-fixture-report-20260619.md`.

Evidence:

- Batch-30 selected source count = 30.
- Batch-30 local draft card count = 300.
- Expansion gate: metadata_completeness = 1.0, unit_locator_coverage = 1.0, source_only_citation_violation_count = 0, long_text_violation_count = 0, provider_call_count = 0, live_kb_write_count = 0.
- Card QA: registered_source_coverage = 1.0, locator_manifest_coverage = 1.0, blocked_actions_complete_rate = 1.0, high_risk_review_routed_rate = 1.0, failure_count = 0.
- Retrieval/citation regression: answerable anchored_citation@1 = 0.9792, answerable anchored_citation@5 = 1.0, source_only_citation_violation_count = 0, gate_threshold_pass = true.
- Answer-trace fixture: trace_pass_count = 12/12, trace_pass_rate = 1.0.
- Remaining answerable top1 failure: `CONSULT-EVAL-016`; expected `SRC-CONSULT-011`, retrieved top1 `SRC-CONSULT-010`, and expected source appears at top2. This is not a current gate blocker because answerable anchored_citation@5 = 1.0.

Remaining blockers:

- Legal/source-owner review has not cleared raw source redistribution or online use.
- Full 81-source typed-card extraction has not started.
- No durable local vector store, retrieval API, private staging service, provider generation, or production launch has been built.
- Human-gold locator labels are still missing; current retrieval metrics are local proxy evidence.

## Batch-60 Local Expansion

The next local extraction batch expanded from batch-30 to batch-60.

Artifacts created:

- Batch-60 source selection: `drafts/analysis/consultant-role-kb-batch60-source-selection-20260619.csv`.
- Batch-60 expansion script: `tmp/consultant_role_kb_batch60_expansion_20260619.py`.
- Batch-60 cards: `tmp/consultant-role-kb-batch60-cards-20260619.jsonl`.
- Batch-60 gate eval: `tmp/consultant-role-kb-batch60-card-gate-eval-20260619.json`.
- Batch-60 expansion report: `drafts/analysis/consultant-role-kb-batch60-expansion-report-20260619.md`.
- Batch-60 card QA report: `drafts/analysis/consultant-role-kb-batch60-card-qa-validation-report-20260619.md`.
- Batch-60 regression script: `tmp/consultant_role_kb_batch60_regression_eval_20260619.py`.
- Batch-60 retrieval/citation report: `drafts/analysis/consultant-role-kb-batch60-regression-eval-report-20260619.md`.
- Batch-60 answer-trace report: `drafts/analysis/consultant-role-kb-batch60-answer-trace-fixture-report-20260619.md`.

Evidence:

- Batch-60 selected source count = 60 extractable sources.
- Batch-60 local draft card count = 600.
- Expansion gate: metadata_completeness = 1.0, unit_locator_coverage = 1.0, source_only_citation_violation_count = 0, long_text_violation_count = 0, provider_call_count = 0, live_kb_write_count = 0.
- Card QA: registered_source_coverage = 1.0, locator_manifest_coverage = 1.0, blocked_actions_complete_rate = 1.0, high_risk_review_routed_rate = 1.0, failure_count = 0.
- Retrieval/citation regression: answerable anchored_citation@1 = 0.9792, answerable anchored_citation@5 = 1.0, source_only_citation_violation_count = 0, gate_threshold_pass = true.
- Answer-trace fixture: trace_pass_count = 12/12, trace_pass_rate = 1.0.
- Remaining answerable top1 failure: `CONSULT-EVAL-016`; expected source appears at top2, so this is not a current gate blocker.

Skipped sources:

- `SRC-CONSULT-030` and `SRC-CONSULT-031` produced 0 extractable units under the current loader and remain registered but not typed-card extracted.

Boundary:

- `production unchanged`.
- `no KB provider call`.
- `no live KB ingestion`.
- Raw `consult/` files remain local-only.
- Legal/source-owner review is still pending.

## All-Extractable Local Expansion

The next local extraction step expanded from batch-60 to all currently
extractable non-duplicate sources. A later CSV-loader support pass added
`SRC-CONSULT-030` and `SRC-CONSULT-031` through `csv_row` locators, so this
section reflects the superseding 800-card state.

Artifacts created:

- Source selection: `drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv`.
- Expansion script: `tmp/consultant_role_kb_all_extractable_expansion_20260619.py`.
- Cards: `tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl`.
- Gate eval: `tmp/consultant-role-kb-all-extractable-card-gate-eval-20260619.json`.
- Expansion report: `drafts/analysis/consultant-role-kb-all-extractable-expansion-report-20260619.md`.
- Card QA report: `drafts/analysis/consultant-role-kb-all-extractable-card-qa-validation-report-20260619.md`.
- Regression script: `tmp/consultant_role_kb_all_extractable_regression_eval_20260619.py`.
- Retrieval/citation report: `drafts/analysis/consultant-role-kb-all-extractable-regression-eval-report-20260619.md`.
- Answer-trace report: `drafts/analysis/consultant-role-kb-all-extractable-answer-trace-fixture-report-20260619.md`.
- CSV loader support report: `drafts/analysis/consultant-role-kb-csv-loader-support-report-20260619.md`.

Evidence:

- Selected source count = 80.
- Local draft card count = 800.
- Expansion gate: metadata_completeness = 1.0, unit_locator_coverage = 1.0, source_only_citation_violation_count = 0, long_text_violation_count = 0, provider_call_count = 0, live_kb_write_count = 0.
- Card QA: registered_source_coverage = 1.0, locator_manifest_coverage = 1.0, blocked_actions_complete_rate = 1.0, high_risk_review_routed_rate = 1.0, failure_count = 0.
- Retrieval/citation regression: answerable anchored_citation@1 = 0.9792, answerable anchored_citation@5 = 1.0, source_only_citation_violation_count = 0, gate_threshold_pass = true.
- Answer-trace fixture: trace_pass_count = 12/12, trace_pass_rate = 1.0.
- Remaining answerable top1 failure: `CONSULT-EVAL-016`; expected source appears at top2, so this is not a current gate blocker.
- CSV source coverage: `SRC-CONSULT-030` has 941 CSV units and 10 cards; `SRC-CONSULT-031` has 237 CSV units and 10 cards.

Skipped sources:

- `SRC-CONSULT-016`: duplicate EPUB secondary to the preferred PDF source.

Interpretation:

- Fact: under the current local parser/loader stack, all 80 non-duplicate registered sources have typed-card extraction coverage.
- Inference: extraction and durable local indexing now cover the current 800-card set; the next engineering bottleneck is human-gold evaluation labels or security-approved private staging.
- Boundary: this remains local draft evidence only; no legal clearance, provider call, live ingestion, staging deployment, or production launch has occurred.

## Durable Local Vector Store

The all-extractable cards were packaged into a durable local vector-store index.

Artifacts created:

- Build script: `tmp/consultant_role_kb_all_extractable_vector_store_20260619.py`.
- Index manifest: `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/manifest.json`.
- Index records: `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/records.jsonl`.
- Embedding matrix: `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/embeddings.float32.npy`.
- Checksums: `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/checksums.json`.
- Smoke output: `tmp/consultant-role-kb-all-extractable-vector-store-smoke-20260619.json`.
- Report: `drafts/analysis/consultant-role-kb-all-extractable-vector-store-report-20260619.md`.

Evidence:

- Indexed records = 800.
- Embedding rows = 800.
- Embedding dimension = 512.
- Source count = 80.
- Model = local cached `BAAI/bge-small-zh-v1.5`, snapshot `7999e1d3359715c523056ef9478215996d62a620`, recorded license MIT.
- Raw vector-only answerable source_recall@1 = 0.5833 and @5 = 0.75.
- Vector plus deterministic rerank answerable source_recall@1 = 0.9583 and @5 = 1.0.
- Fixture answerable reranked source_recall@5 = 1.0.
- top1_unit_anchor_rate = 1.0.
- provider_call_count = 0.
- live_kb_write_count = 0.

Interpretation:

- Fact: the all-extractable draft card set now has a reusable local vector-store package with row-aligned metadata, routing text, normalized embeddings, and checksums.
- Inference: raw vector-only retrieval is insufficient as the acceptance path; local agent retrieval should use vector search plus deterministic rerank/source-prior behavior.
- Boundary: this is still local draft infrastructure only; no legal clearance, provider call, live KB ingestion, staging deployment, or production launch has occurred.

## Human-Gold Locator Label Seed

The 50-question eval set now has a pending-review locator label seed.

Artifacts created:

- Generator: `tmp/consultant_role_kb_human_gold_locator_labels_20260619.py`.
- Label seed: `shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl`.
- QA output: `tmp/consultant-role-kb-human-gold-locator-labels-qa-20260619.json`.
- Report: `drafts/analysis/consultant-role-kb-human-gold-locator-labels-report-20260619.md`.

Evidence:

- label_count = 50.
- locator_gold_candidate = 48.
- refusal_policy_no_source = 2.
- label_status_counts.pending_human_review = 50.
- locator_coverage_rate_for_48_citable_evals = 1.0.
- rank_not_top1_count = 1, for `CONSULT-EVAL-016`.
- failure_count = 0.
- provider_call_count = 0.
- live_kb_write_count = 0.

Interpretation:

- Fact: every eval item now has a structured label seed that can drive reviewer workflow and retrieval API tests.
- Fact: no label is approved human-gold yet; all labels are explicitly `pending_human_review`.
- Inference: this unblocks private no-provider retrieval API contract work, but not a claim of human-approved locator precision.
- Boundary: local draft labels only; no legal clearance, provider call, live KB ingestion, staging deployment, or production launch has occurred.

## Private No-Provider Retrieval API Prototype

The local retrieval API slice was implemented for `consultant-agent`.

Artifacts created:

- API module: `agents/consultant-agent/runtime/local_retrieval_api.py`.
- Smoke script: `tmp/consultant_role_kb_private_retrieval_api_smoke_20260619.py`.
- Smoke output: `tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json`.
- Report: `drafts/analysis/consultant-role-kb-private-retrieval-api-report-20260619.md`.

API surface:

- `GET /health`
- `POST /retrieve`
- `POST /eval/label-seed`

Evidence:

- record_count = 800.
- eval001_top1_source = `SRC-CONSULT-001`.
- eval016 target source/locator appears in top5.
- workspace-forbidden smoke returned HTTP 403.
- label_seed_match_at_1 = 0.9375.
- label_seed_match_at_5 = 1.0.
- policy_refusal_pass_rate = 1.0.
- failure_count = 0.
- provider_call_count = 0.
- live_kb_write_count = 0.

Implementation note:

- The first smoke failed because the API used a vector topN prefilter before deterministic rerank, which diverged from the accepted full-record rerank evaluation path.
- The API now reranks all 800 local records, preserving the accepted evaluation path.
- Workspace-forbidden policy labels are counted as no-retrieval policy compliance when the eval is explicitly testing workspace isolation.

Boundary:

- This is a local/private API prototype only.
- It is not a staging deployment, production deployment, provider-backed agent, live KB ingestion, or legal/source-owner approval.

## Staging Auth/Audit Contract

The private no-provider retrieval API now has a draft staging auth/audit
contract, but it has not been deployed to staging.

Artifacts:

- Design: `drafts/analysis/consultant-role-kb-staging-auth-audit-design-20260619.md`
- Schema: `shared/audit/consultant-agent/staging-audit-event.schema-20260619.json`
- Validator: `tmp/consultant_role_kb_staging_auth_audit_contract_20260619.py`
- Sample events: `tmp/consultant-role-kb-staging-auth-audit-sample-events-20260619.jsonl`
- Validation output: `tmp/consultant-role-kb-staging-auth-audit-contract-validation-20260619.json`

Required staging request headers:

- `Authorization`
- `X-KB-Agent=consultant-agent`
- `X-KB-Workspace=consultant-p1`
- `X-KB-Reviewer`
- `X-KB-Request-Id`

Audit validation result:

- event_count = 2.
- allowed_event_count = 1.
- denied_event_count = 1.
- failure_count = 0.
- provider_call_count = 0.
- live_kb_write_count = 0.
- source_text_returned = false.

Interpretation:

- Fact: the draft schema can validate allowed and denied retrieval audit events.
- Fact: the local validator checks hashed actor/query identifiers and forbids
  raw question/source text leakage in the sample events.
- Inference: the next implementation step can add auth/audit middleware around
  the local API without changing retrieval semantics.
- Boundary: legal/source-owner approval, secret storage, private ingress,
  append-only audit storage, rate limiting, and rollback remain unimplemented.

## Local Staging Auth/Audit Harness

The local staging auth/audit harness was implemented around the existing
`LocalRetrievalService`. It remains localhost-only validation and is separate
from any shared staging deployment.

Artifacts:

- Harness module: `agents/consultant-agent/runtime/staging_auth_audit.py`
- Smoke script: `tmp/consultant_role_kb_local_staging_auth_audit_smoke_20260619.py`
- Smoke output: `tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json`
- Audit events: `tmp/consultant-role-kb-local-staging-audit-events-20260619.jsonl`
- Report: `drafts/analysis/consultant-role-kb-local-staging-auth-audit-smoke-report-20260619.md`

Implemented controls:

- Bearer auth validates against a runtime-provided SHA-256 token hash; the
  token itself is not persisted.
- Protected endpoints require `X-KB-Agent`, `X-KB-Workspace`, `X-KB-Reviewer`,
  `X-KB-Request-Id`, and `X-KB-Role`.
- RBAC allows `retrieval_reader` on `/retrieve`, and `reviewer`/`admin` on
  `/retrieve` plus `/eval/label-seed`.
- Every allowed, denied, and policy-refusal protected request emits one audit
  event.
- Audit events store hashed actor/query identifiers plus source/card/locator
  refs only; they do not store raw questions, raw source text, bearer headers,
  or bearer tokens.

Smoke result:

- record_count = 800.
- allowed_http_status = 200.
- policy_refusal_http_status = 200.
- missing_token_status = 401.
- rbac_denied_status = 403.
- label_seed_match_at_5 = 1.0.
- policy_refusal_pass_rate = 1.0.
- audit_event_count = 5.
- allowed_event_count = 2.
- denied_event_count = 2.
- policy_refusal_event_count = 1.
- audit_schema_failure_count = 0.
- audit_forbidden_leak_count = 0.
- provider_call_count = 0.
- live_kb_write_count = 0.
- failure_count = 0.

Implementation notes:

- The first smoke failed because audit result reference collection assumed
  `/eval/label-seed` response rows had retrieval result fields; it now skips
  non-retrieval rows for `result_refs`.
- The second smoke failed because the allowed `/eval/label-seed` audit event
  had no `retrieval_mode`; it now defaults allowed non-retrieval events to
  `local_bge_vector_plus_deterministic_rerank`.

Boundary:

- Local validation only.
- No provider call.
- No live KB ingestion.
- No staging deployment.
- No human label approvals.
- No legal/source-owner clearance.

## Human Label Review Workflow

The pending locator label seed now has a local manual-review workflow. The
workflow creates a reviewer-facing queue and a separate decision template, but
it does not approve any labels.

Artifacts:

- Workflow design: `drafts/analysis/consultant-role-kb-human-label-review-workflow-20260619.md`
- Queue CSV: `shared/eval/consultant-agent/human-gold-locator-label-review.queue-20260619.csv`
- Decision template: `shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl`
- Decision schema: `shared/eval/consultant-agent/human-gold-locator-label-review.schema-20260619.json`
- Generator/validator: `tmp/consultant_role_kb_human_label_review_workflow_20260619.py`
- Validation output: `tmp/consultant-role-kb-human-label-review-workflow-validation-20260619.json`

Validation result:

- seed_label_count = 50.
- review_queue_count = 50.
- decision_template_count = 50.
- locator_candidate_count = 48.
- policy_refusal_count = 2.
- pending_decision_count = 50.
- approved_decision_count = 0.
- failure_count = 0.
- provider_call_count = 0.
- live_kb_write_count = 0.

Interpretation:

- Fact: every machine-seeded label has exactly one review queue row and one
  pending decision row.
- Fact: the template has 0 approved decisions and cannot be cited as
  human-gold evidence yet.
- Inference: this unblocks a human reviewer pass without mutating the machine
  seed file.
- Boundary: actual reviewer decisions, legal/license clearance, staging
  implementation, provider calls, and live KB ingestion remain unperformed.

## Shared Staging Readiness Preflight

A local shared-staging readiness preflight and draft runbook were created after
the localhost auth/audit harness. This advances the staging lane without
claiming staging deployment or approval.

Artifacts:

- Preflight script: `tmp/consultant_role_kb_shared_staging_readiness_preflight_20260619.py`
- Preflight output: `tmp/consultant-role-kb-shared-staging-readiness-preflight-20260619.json`
- Preflight report: `drafts/analysis/consultant-role-kb-shared-staging-readiness-preflight-20260619.md`
- Runbook: `drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md`

Preflight result:

- ready_for_shared_staging = false.
- status = blocked.
- check_count = 19.
- pass_count = 13.
- blocker_count = 6.
- provider_call_count = 0.
- live_kb_write_count = 0.

Passing checks include local API smoke, 800-record alignment, policy-refusal
path, local auth/audit harness smoke, missing-token 401 behavior, RBAC 403
behavior, audit contract validation, audit leak check, no-provider boundary,
no-live-write boundary, human label workflow generation, raw `consult/` Git
exclusion, and rollback runbook existence.

Current blockers:

- `human_labels_approved`: approved decision count remains 0.
- `legal_source_owner_clearance`: legal/source-owner clearance remains pending.
- `external_auth_token_hash_configured`: `KB_STAGING_AUTH_TOKEN_SHA256` is not configured.
- `external_audit_path_configured`: `KB_STAGING_AUDIT_PATH` is not configured.
- `rate_limit_configured`: ingress or middleware rate limiting is not recorded.
- `rollback_owner_recorded`: rollback owner is not recorded.

Boundary:

- Local readiness check only.
- Draft runbook only.
- No shared staging deployment.
- No provider call.
- No live KB ingestion.
- No human label approval.
- No legal/source-owner clearance.

## Legal Source-Owner Decision Workflow

A structured legal/source-owner decision workflow now exists for the registered
consultant-agent corpus. It converts the legal review packet into source-level
decision intake without recording any approvals.

Artifacts:

- Schema: `shared/governance/consultant-agent/legal-source-owner-decision.schema-20260619.json`
- Queue: `shared/governance/consultant-agent/legal-source-owner-review.queue-20260619.csv`
- Decision template: `shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl`
- Generator/validator: `tmp/consultant_role_kb_legal_source_owner_decision_workflow_20260619.py`
- Validation output: `tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-legal-source-owner-decision-workflow-20260619.md`

Validation result:

- source_count = 81.
- selected_source_count = 80.
- decision_count = 81.
- pending_review_count = 81.
- selected_approved_internal_staging_count = 0.
- selected_pending_review_count = 80.
- shared_staging_legal_clearance_ready = false.
- failure_count = 0.
- provider_call_count = 0.
- live_kb_write_count = 0.

Interpretation:

- Fact: every registered source has one pending legal/source-owner decision row.
- Fact: all 80 selected runtime sources still need explicit legal and
  source-owner approval before shared staging can clear the legal gate.
- Fact: the shared-staging preflight now reads this structured validation file
  instead of inferring clearance from prose.
- Boundary: no source approval was recorded, no license status was upgraded,
  and no shared staging deployment occurred.
