---
title: "Consultant Role KB Full Extraction And Agent Launch Plan"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/consultant-role-kb-prd-addendum-directory-blueprint-20260619.md"
  - "drafts/analysis/consultant-role-kb-small-batch-expansion-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-expanded-regression-eval-report-20260619.md"
  - ".kiro/plan/task_plan.md"
scope: "full extraction, KB construction, agent runtime, and launch plan for consultant-agent"
production_impact: "planning only; production unchanged"
provider_call_boundary: "planning only; no KB provider call in this document"
implementation_status: "roadmap and TODO only; no live KB ingestion"
---

# Consultant Role KB Full Extraction And Agent Launch Plan

## 0. Boundary

This document is the execution plan for moving from the current local PoC to full extraction and online use. It does not itself ingest raw documents into a live KB, call a provider, deploy production services, or approve third-party source rights.

Current hard boundaries remain:

- `production unchanged`
- `no KB provider call`
- no live KB ingestion
- raw `consult/` source files remain local-only
- `license_status=pending_legal_review`

The plan below intentionally includes future gates that will require explicit approval before those boundaries can change.

## 1. Current Baseline

Facts already proven locally:

| area | current state |
|---|---|
| source folder profile | 81 files, about 9407 PDF pages, parser profile completed |
| registered P1 sources | 15 sources |
| role/domain | `consulting-kb`, `consultant-agent`, `consultant-p1` |
| schema | `external_reference` added; typed-card families defined |
| local sample | 33 anchored cards |
| controlled expansion | 150 cards across 15 sources |
| metadata gate | metadata completeness = 1.0 |
| locator gate | unit locator coverage = 1.0 |
| citation gate | source-only citation violations = 0 |
| expanded retrieval | answerable anchored_citation@1 = 0.9167, @5 = 1.0 |
| answer trace | 12/12 deterministic fixture |
| repository | Git initialized and pushed to `zjgulai/kb` |

Inference: the schema, parser route, local embedding/rerank loop, citation anchor contract, and governance artifacts are strong enough to plan full extraction.

Unknown: license clearance, production runtime behavior, provider-backed answer quality, full-library extraction quality, human-approved citation precision, and online operational security are not yet proven.

## 2. Target End State

The desired end state is not just "cards were extracted." It is an end-to-end role KB product:

```text
source governance
  -> full source registration
  -> parser and unit locator extraction
  -> typed-card generation
  -> card QA and human review
  -> embedding/indexing
  -> retrieval/rerank
  -> citation-constrained answer generation
  -> agent policy enforcement
  -> eval and red-team gates
  -> staging deployment
  -> internal pilot
  -> production launch with monitoring and rollback
```

Target user experience:

- user asks a consulting problem question in Chinese;
- `consultant-agent` retrieves registered sources and relevant typed cards;
- answer includes conclusion, evidence, assumptions, uncertainty, confidence, blocked actions, and next human action;
- every substantive claim cites unit-level locator;
- unsafe requests are refused with an internal alternative;
- all sessions are logged for audit and improvement.

## 3. Workstream Map

| workstream | purpose | primary outputs |
|---|---|---|
| W0 Governance | clear source, legal, owner, production boundaries | approved source policy, promotion gates |
| W1 Full Source Register | move from 15 P1 sources to all `consult/` files | full source register, canonical source IDs |
| W2 Parser Pipeline | make parsing repeatable across PDF/PPTX/DOCX/XLSX/CSV/EPUB | parser reports, unit manifests |
| W3 Card Extraction | generate typed cards for full library | full card corpus, QA reports |
| W4 Index And Retrieval | build durable metadata/vector index | index store, retrieval API, rerank policy |
| W5 Agent Runtime | build usable `consultant-agent` | policy engine, answer generator, API/UI |
| W6 Eval And Safety | prove quality and boundaries | eval suites, red-team reports, launch gates |
| W7 Deployment | make staging and production operational | deploy pipeline, auth, logs, monitoring |
| W8 Launch And Ops | pilot, release, operate, improve | pilot report, runbooks, incident process |

## 4. Phase Plan

### Phase 0 - Governance And Launch Decision Baseline

Goal: decide what can be extracted, stored, indexed, pushed, and shown to users.

TODO:

- [ ] Confirm whether `consult/` raw sources may be used beyond local PoC.
- [ ] Confirm whether cards derived from third-party sources may be stored in a persistent KB.
- [ ] Confirm whether cards may be committed to Git, stored in private object storage, or only stored locally.
- [ ] Assign reviewers: source owner, legal/license reviewer, product owner, technical owner, security owner.
- [ ] Define evidence-grade upgrade policy from `C` to higher grades.
- [ ] Decide whether online use is internal-only pilot or broader production.
- [ ] Decide model runtime: provider model, local model, or hybrid.

Acceptance criteria:

- legal/license policy documented;
- raw-source redistribution policy documented;
- owner review workflow documented;
- production approval path documented.

Stop condition:

- legal/license cannot approve persistent derived cards or retrieval use.

### Phase 1 - Full Source Register

Goal: every file in `consult/` has a canonical source record before extraction.

TODO:

- [ ] Promote current 15-source candidate register into a full 81-source draft register.
- [ ] Assign `SRC-CONSULT-###` IDs for every source.
- [ ] Record source type, file path, hash, file size, parser route, owner, evidence grade, license status, workspace, allowed agents, and blocked actions.
- [ ] Detect duplicate sources, near-duplicate PDF/EPUB pairs, and superseded versions.
- [ ] Split the full library into extraction batches: methods, diagnostics, delivery, transaction advisory, industry analysis, reference data, client development.
- [ ] Mark high-risk sources: legal/financial/investment advice, PII risk, client-ready templates, source redistribution risk.
- [ ] Produce full source register report.

Acceptance criteria:

- 100% of files have source IDs;
- 100% have hash and parser route;
- 100% have license status;
- no extraction starts from unregistered source.

### Phase 2 - Parser Productionization

Goal: make parsing repeatable and measurable, not ad hoc.

TODO:

- [ ] Create a unified parser CLI for PDF, PPTX, DOCX, XLSX, CSV, and EPUB.
- [ ] Output a unit manifest for each source: `page`, `slide`, `paragraph`, `sheet_row`, or `section`.
- [ ] Record parse coverage, empty-unit rate, image-only pages/slides, table extraction status, warnings, and errors.
- [ ] Implement worksheet dimension reset for Excel.
- [ ] Implement PDF warning capture for pointer/layout issues.
- [ ] Implement table-of-contents and heading detection where possible.
- [ ] Add parser regression fixtures for representative files.
- [ ] Store parser outputs as local artifacts first; decide later whether to persist them in repo or object storage.

Acceptance criteria:

- parse success rate = 100% or explicit blocked-source list;
- unit locator coverage >= 0.98 for extractable files;
- parse error report generated for every batch.

### Phase 3 - Full Typed-Card Extraction

Goal: extract the full library into typed, source-anchored cards.

TODO:

- [ ] Extend current 150-card logic into batch extraction.
- [ ] Define target card count per source by source type and density.
- [ ] Generate cards by card family:
  - [ ] `consult_method_card`
  - [ ] `diagnostic_dimension_card`
  - [ ] `deliverable_template_card`
  - [ ] `consulting_kpi_card`
  - [ ] `terminology_crosswalk_card`
  - [ ] `industry_analysis_card`
  - [ ] `client_development_card`
  - [ ] `transaction_advisory_card`
- [ ] Add deduplication across repeated templates and industry playbooks.
- [ ] Add card quality checks: required fields, source ID, evidence grade, license status, blocked actions, locator, no long source text.
- [ ] Add high-risk flags for legal/financial/investment/client-ready/PII-sensitive cards.
- [ ] Build human-review queues by card family and risk level.
- [ ] Produce batch-level card QA reports.

Acceptance criteria:

- metadata completeness = 1.0;
- unit locator coverage = 1.0 for included cards;
- long text reproduction violations = 0;
- source-only citation violations = 0;
- all high-risk cards are routed to human review.

### Phase 4 - Knowledge Store And Index

Goal: move from local JSONL artifacts to a durable KB storage/index layer.

Recommended architecture:

```text
object storage / local source vault
  -> parser unit manifests
  -> card registry
  -> metadata DB
  -> vector index
  -> retrieval/rerank service
```

Implementation decision needed:

- metadata DB: SQLite for local MVP, PostgreSQL for production;
- vector index: local FAISS/LanceDB for MVP, pgvector or managed vector DB for production;
- source vault: local-only for now; private object storage only after license review.

TODO:

- [ ] Define card table schema.
- [ ] Define source register table schema.
- [ ] Define citation anchor table schema.
- [ ] Define eval result table schema.
- [ ] Implement local index build command.
- [ ] Implement index versioning and rollback.
- [ ] Implement re-index on changed source hash.
- [ ] Implement retrieval API returning cards plus unit anchors.
- [ ] Persist model ID, snapshot, embedding dimension, and build timestamp.

Acceptance criteria:

- index can be rebuilt from registered cards;
- every retrieval result includes source metadata and unit locator;
- index version can be rolled back;
- no unregistered source enters index.

### Phase 5 - Agent Runtime

Goal: build a usable `consultant-agent`, not only retrieval scripts.

TODO:

- [ ] Define agent contract: input, context, retrieval call, answer schema, refusal schema.
- [ ] Build policy layer for blocked actions.
- [ ] Build citation enforcement: no final answer without unit locator.
- [ ] Build evidence-grade enforcement: D-grade cannot support final conclusions.
- [ ] Build workspace isolation checks.
- [ ] Add answer template:
  - [ ] conclusion
  - [ ] evidence
  - [ ] assumptions
  - [ ] uncertainty
  - [ ] confidence
  - [ ] blocked actions
  - [ ] next human action
- [ ] Decide runtime model and provider approval.
- [ ] Add provider-call logging and cost controls if provider model is approved.
- [ ] Add local fallback mode if provider is unavailable.

Acceptance criteria:

- safe answer traces pass in automated tests;
- blocked actions are refused;
- no source-only citation in final answer;
- provider calls are logged and bounded if enabled.

### Phase 6 - Eval, Red Team, And Launch Quality Gates

Goal: expand eval beyond the current 50-question local set.

TODO:

- [ ] Expand eval set from 50 to at least 300 questions.
- [ ] Cover every source family and card type.
- [ ] Add multi-hop consulting questions.
- [ ] Add refusal and unsafe-action prompts.
- [ ] Add citation precision gold labels for a human-reviewed subset.
- [ ] Add answer-quality rubric: usefulness, correctness, uncertainty, source fit, citation precision, boundary compliance.
- [ ] Add regression tests for the four current rank-1 misses.
- [ ] Add adversarial prompts: client-ready PPT, legal/financial/investment advice, PII, source redistribution, cross-workspace leakage.
- [ ] Add load and latency tests for online use.

Launch thresholds:

- answerable anchored_citation@5 >= 0.95;
- answerable anchored_citation@1 target >= 0.90, improve toward >= 0.95;
- answer-trace pass rate = 1.0;
- blocked-action pass rate = 1.0;
- source-only citation violations = 0;
- workspace leakage = 0;
- high-risk card human-review completion = 1.0.

### Phase 7 - Staging Deployment

Goal: put the agent behind a controlled internal staging environment.

TODO:

- [ ] Choose deployment target.
- [ ] Add config separation: local, staging, production.
- [ ] Add auth and role access.
- [ ] Add audit logs.
- [ ] Add request/response trace logs with source IDs and citations.
- [ ] Add health endpoint.
- [ ] Add admin endpoint for source/card/index status.
- [ ] Add rollback for index version and agent prompt/policy version.
- [ ] Run staging smoke tests.
- [ ] Run staging E2E tests with representative user workflows.

Acceptance criteria:

- staging health check passes;
- staging retrieval and answer generation pass eval subset;
- audit logs capture source IDs and blocked actions;
- rollback tested.

### Phase 8 - Internal Pilot

Goal: validate real use with a small consulting workflow group.

TODO:

- [ ] Define pilot users and allowed use cases.
- [ ] Train users on draft/internal-only limits.
- [ ] Add feedback capture.
- [ ] Review failed answers weekly.
- [ ] Review top retrieved sources and citation quality.
- [ ] Update eval set from real pilot failures.
- [ ] Run source owner review on high-usage cards.

Acceptance criteria:

- pilot completion report;
- known failure classes documented;
- no severe policy violation;
- product owner approves production-readiness review.

### Phase 9 - Production Launch

Goal: make the agent available under approved production boundaries.

TODO:

- [ ] Get production approval from product, legal, security, and source owner.
- [ ] Confirm source policy and user terms.
- [ ] Enable production environment.
- [ ] Enable monitoring and alerting.
- [ ] Set incident response and rollback owners.
- [ ] Publish usage policy inside the app.
- [ ] Run production read-only smoke.
- [ ] Run authorized live-side-effect tests only if such features are explicitly enabled.

Acceptance criteria:

- production go-live checklist signed;
- live health checks pass;
- first pilot production sessions logged and reviewed;
- rollback path validated.

## 5. Master TODO List

### P0 Blockers

- [ ] Legal/license decision for third-party `consult/` sources.
- [ ] Source owner review workflow with 李梁.
- [ ] Decide raw-source storage policy.
- [ ] Decide model/provider policy for online agent.
- [ ] Decide production target architecture.

### P1 Engineering

- [ ] Full 81-source register.
- [ ] Unified parser CLI.
- [ ] Full unit manifest generation.
- [ ] Full typed-card batch extraction.
- [ ] Card QA validator.
- [ ] Full index build command.
- [ ] Retrieval/rerank service.
- [ ] Agent answer policy engine.
- [ ] Citation enforcement.
- [ ] Eval runner.

### P1 Product / UX

- [ ] Define top user workflows.
- [ ] Define answer UX.
- [ ] Define refusal UX.
- [ ] Define source/citation display.
- [ ] Define feedback capture.

### P1 Security / Governance

- [ ] Workspace isolation.
- [ ] Access control.
- [ ] Audit logging.
- [ ] PII handling.
- [ ] Blocked action enforcement.
- [ ] Data retention policy.

### P1 QA

- [ ] 300-question eval set.
- [ ] Human gold citation subset.
- [ ] Regression for rank-1 misses.
- [ ] Red-team unsafe prompt set.
- [ ] Load/latency tests.
- [ ] Staging E2E suite.

### P2 Launch

- [ ] Internal pilot.
- [ ] Pilot failure review.
- [ ] Production readiness review.
- [ ] Production smoke.
- [ ] Runbook and rollback drill.
- [ ] Monitoring dashboard.

## 6. Immediate Next Sprint

Recommended next sprint is not production. It should remove the current P0 blockers and prepare full extraction.

Sprint goal: make full extraction legally and technically executable.

TODO:

1. Create `consultant-role-kb-full-source-register-20260619.csv` covering all 81 files.
2. Build a parser unit-manifest CLI that emits one manifest per source.
3. Build a card QA validator that can run before indexing.
4. Tune rerank rules for current four answerable rank-1 misses:
   - `CONSULT-EVAL-014`
   - `CONSULT-EVAL-017`
   - `CONSULT-EVAL-038`
   - `CONSULT-EVAL-047`
5. Draft legal/source-owner review packet for all `external_reference` materials.
6. Decide technical runtime for full KB:
   - local-only PoC,
   - private staging,
   - production with provider model,
   - production with local model.

## 7. Decision Questions

These decisions should be answered before full extraction starts:

1. Can derived typed cards from `consult/` be stored persistently, or must they remain local-only until legal review?
2. Should full extraction include all 81 files immediately, or run by batches: registered 15 -> 30 -> 60 -> 81?
3. Should online agent use a provider model, a local model, or both?
4. What is the first launch target: internal pilot only, selected users, or production workspace?
5. Should the PRD addendum be merged into `KB_Platform_PRD.md` before or after full extraction?

## 8. Current Recommendation

Recommended sequence:

1. Do not start production work yet.
2. Complete legal/source-owner review path.
3. Expand source register from 15 to all 81 files.
4. Build parser manifest and full-card extraction pipeline.
5. Run full extraction in batches, not as a single unreviewed ingest.
6. Build durable index and agent runtime only after batch extraction gates stay green.
7. Launch first as an internal staging pilot, not broad production.

This path keeps momentum while preserving source governance, citation precision, and safety boundaries.
