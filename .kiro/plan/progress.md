---
title: "Consultant Role KB Extraction Progress"
status: "active"
created_at: "2026-06-19"
scope: "progress log for consult role KB planning"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# Consultant Role KB Extraction Progress

## 2026-06-19

- Read user-provided AGENTS instructions from chat.
- Checked for local `AGENTS.md` and `.codex/context-pack.md`; none found.
- Read `planning-with-files` skill instructions.
- Read PDF skill instructions because the source folder is PDF-heavy.
- Loaded bundled workspace dependencies for PDF/Office parsing.
- Read key PRD sections, especially P1 roadmap, taxonomy, evidence governance, eval, and stop conditions.
- Read existing draft templates and registers in `drafts/analysis/`.
- Profiled `consult/` folder in read-only mode and generated `tmp/consult-role-kb-source-profile-20260619.json`.
- Reran Excel profiling after worksheet dimension metadata errors and cleared parse errors.
- Created this `.kiro/plan/` planning workspace.
- Created `drafts/analysis/consultant-role-kb-extraction-execution-plan-draft-20260619.md`.
- Recorded user decisions in `drafts/analysis/consultant-role-kb-decision-log-20260619.md`.
- Created `drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv` with 15 P1-ready candidate sources.
- Created `drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl` with 50 eval questions across five categories.
- Generated deterministic typed-card samples in `tmp/consultant-role-kb-card-samples-20260619.jsonl`.
- Created `drafts/analysis/consultant-role-kb-card-sample-summary-20260619.md`.
- Fixed the typed-card sample by filtering an accidental acronym workbook header row; current sample count is 33 cards.
- User approved adding `external_reference` to source-register schema and approved the next local embedding/indexing PoC.
- Updated `drafts/analysis/kb-source-register-template.md` and `drafts/analysis/kb-source-register.sample.csv` to include `external_reference`.
- Created and ran `tmp/consultant_role_kb_local_hash_index_poc_20260619.py`.
- Generated `tmp/consultant-role-kb-local-hash-index-20260619.json`, `tmp/consultant-role-kb-local-retrieval-eval-20260619.json`, and `drafts/analysis/consultant-role-kb-local-embedding-indexing-poc-report-20260619.md`.
- Local hash embedding PoC indexed 33 cards and ran 50 eval questions with source_recall@1 = 0.76 and source_recall@5 = 0.86.
- User approved continuing to the real local embedding model step.
- Created and ran `tmp/consultant_role_kb_real_embedding_poc_20260619.py` with cached `BAAI/bge-small-zh-v1.5`.
- Generated `tmp/consultant-role-kb-bge-small-zh-index-20260619.json`, `tmp/consultant-role-kb-bge-small-zh-retrieval-eval-20260619.json`, `drafts/analysis/consultant-role-kb-real-embedding-indexing-poc-report-20260619.md`, and `drafts/analysis/consultant-role-kb-embedding-adr-001-bge-small-zh-v1.5-20260619.md`.
- Real local BGE embedding PoC indexed 33 cards and ran 50 eval questions with source_recall@1 = 0.66 and source_recall@5 = 0.90.
- Current interpretation: BGE improves top5 source coverage over hash baseline but needs rerank/source-prior work before top1 retrieval can be used as a stronger acceptance signal.
- User asked to continue the next step; implemented a local rerank/source-prior PoC without using eval `allowed_source_ids` during ranking.
- Created and ran `tmp/consultant_role_kb_rerank_source_prior_poc_20260619.py`.
- Generated `tmp/consultant-role-kb-bge-source-prior-rerank-eval-20260619.json` and `drafts/analysis/consultant-role-kb-rerank-source-prior-poc-report-20260619.md`.
- Rerank/source-prior all-eval source_recall@1 = 0.86 and source_recall@5 = 0.96; answerable-eval source_recall@1 = 0.8958 and source_recall@5 = 1.0.
- Current next gate: add page/slide/sheet anchors to typed cards and score citation precision before expanding extraction beyond 33 sample cards.
- User asked to continue the next step; implemented a local citation-anchor PoC for the current 33 cards.
- Created and ran `tmp/consultant_role_kb_citation_anchor_poc_20260619.py` with bundled Python parser dependencies.
- Generated `tmp/consultant-role-kb-card-samples-anchored-20260619.jsonl`, `tmp/consultant-role-kb-citation-anchor-eval-20260619.json`, and `drafts/analysis/consultant-role-kb-citation-anchor-poc-report-20260619.md`.
- Citation anchor readiness: 33/33 cards resolved to unit-level anchors; modality coverage is 4 PPTX slide cards, 7 PDF page cards, 1 DOCX paragraph card, and 21 XLSX sheet-row cards.
- Fixed an initial acronym-anchor over-broad match so acronym cards resolve to concrete term rows rather than workbook title rows.
- Current next gate: run anchored retrieval/citation eval with the anchored cards; do not expand extraction based only on source recall or anchor readiness.
- User asked to continue the next step; implemented anchored retrieval/citation eval using `tmp/consultant-role-kb-card-samples-anchored-20260619.jsonl`.
- Created and ran `tmp/consultant_role_kb_anchored_retrieval_citation_eval_20260619.py`.
- Generated `tmp/consultant-role-kb-anchored-retrieval-citation-eval-20260619.json` and `drafts/analysis/consultant-role-kb-anchored-retrieval-citation-eval-report-20260619.md`.
- Anchored eval all-eval source_recall@1 = 0.86, source_recall@5 = 0.96, anchored_citation@1 = 0.86, anchored_citation@5 = 0.96.
- Anchored eval answerable-eval anchored_citation@1 = 0.8958 and anchored_citation@5 = 1.0; source_only_citation_violation_count = 0.
- Current next gate: create a small answer-trace fixture to verify generated answers cite selected unit locators and preserve evidence/license/refusal boundaries.
- User asked to continue the next step; implemented a deterministic local answer-trace fixture over 12 representative eval questions.
- Created and ran `tmp/consultant_role_kb_answer_trace_fixture_20260619.py`.
- Generated `tmp/consultant-role-kb-answer-trace-fixture-20260619.jsonl`, `tmp/consultant-role-kb-answer-trace-eval-20260619.json`, and `drafts/analysis/consultant-role-kb-answer-trace-fixture-report-20260619.md`.
- Answer-trace results: trace_pass_count = 9/12, trace_pass_rate = 0.75, source_selection_pass_rate = 0.75, locator_citation_pass_rate = 1.0, boundary_checks_pass_rate = 1.0, blocked_action_pass_rate = 1.0, refusal_pass_rate = 1.0.
- Failed traces: `CONSULT-EVAL-018`, `CONSULT-EVAL-040`, and `CONSULT-EVAL-050`; all fail only `source_selection_pass`.
- Previous next gate: tune source-selection/rerank behavior for those three failure modes before expanding extraction.
- User asked to continue the next step; tuned source-intent priors for ambiguous problem definition, client-ready PPT/executive summary, and high-stakes due-diligence/refusal prompts.
- Reran `tmp/consultant_role_kb_rerank_source_prior_poc_20260619.py`.
- Updated rerank/source-prior result: all-eval source_recall@1 = 0.92 and source_recall@5 = 0.96; answerable-eval source_recall@1 = 0.9583 and source_recall@5 = 1.0.
- Reran `tmp/consultant_role_kb_anchored_retrieval_citation_eval_20260619.py`.
- Updated anchored eval result: all-eval anchored_citation@1 = 0.92 and anchored_citation@5 = 0.96; answerable-eval anchored_citation@1 = 0.9583 and anchored_citation@5 = 1.0; source_only_citation_violation_count = 0.
- Reran `tmp/consultant_role_kb_answer_trace_fixture_20260619.py`.
- Updated answer-trace result: trace_pass_count = 12/12, trace_pass_rate = 1.0, source_selection_pass_rate = 1.0, locator_citation_pass_rate = 1.0, boundary_checks_pass_rate = 1.0, blocked_action_pass_rate = 1.0, refusal_pass_rate = 1.0.
- Updated `drafts/analysis/consultant-role-kb-extraction-execution-plan-draft-20260619.md`, `drafts/analysis/consultant-role-kb-decision-log-20260619.md`, and `.kiro/plan/findings.md` with the new local evidence.
- Created `drafts/analysis/consultant-role-kb-small-batch-expansion-gate-20260619.md`.
- Updated the execution plan, decision log, and findings to reference the small-batch expansion gate.
- Current next gate: decide whether to run the controlled local expansion batch or draft the PRD addendum/directory blueprint first; no production KB, no provider call, and no live ingestion.
- User instructed to execute A then B, then initialize the project with Codex self-evolution project structure, Git, and remote push.
- Created `tmp/consultant_role_kb_small_batch_expansion_20260619.py`.
- First attempted expansion with Homebrew Python failed because that runtime lacked `openpyxl`; switched to the Codex bundled Python runtime for PDF/Office parsing.
- Ran controlled local expansion and generated 150 cards at `tmp/consultant-role-kb-expanded-cards-20260619.jsonl`.
- Expansion gate result: metadata_completeness = 1.0, unit_locator_coverage = 1.0, source_only_citation_violation_count = 0, long_text_violation_count = 0, provider_call_count = 0, live_kb_write_count = 0.
- Created `tmp/consultant_role_kb_expanded_regression_eval_20260619.py`.
- Ran expanded retrieval/citation regression with local `BAAI/bge-small-zh-v1.5`; answerable anchored_citation@1 = 0.9167, answerable anchored_citation@5 = 1.0, source_only_citation_violation_count = 0, gate_threshold_pass = true.
- Ran expanded answer-trace fixture; trace_pass_count = 12/12 and trace_pass_rate = 1.0.
- Created `drafts/analysis/consultant-role-kb-prd-addendum-directory-blueprint-20260619.md`.
- Current next gate: initialize `.codex/` project context and Git repository while preserving draft/local boundaries and source licensing cautions.
- Created Codex self-evolution project structure: `.codex/context-pack.md`, `.codex/session-thread.md`, project `AGENTS.md`, root `README.md`, `domains/`, `agents/`, `shared/`, and `archive/`.
- Added `.gitignore` that excludes raw `consult/` source files and `.DS_Store`, while keeping `consult/README.md`.
- Wrote one self-evolution candidate lesson to `~/.codex/evolution/inbox/candidates.jsonl` after the Python runtime mismatch failure; no long-term memory promotion was performed.
- Initialized Git repository on branch `main`.
- Verified `git ls-remote https://github.com/zjgulai/kb.git` returned empty output before push.
- Created root commit `9cb0309` with 99 files; raw `consult/` source files were not staged.
- Added remote `origin=https://github.com/zjgulai/kb.git`.
- Pushed `main` to `origin`; Git reported `[new branch] main -> main` and set local branch to track `origin/main`.
- Current boundary after push: repository contains draft/local governance docs, scripts, eval artifacts, and metadata; raw third-party source files remain local-only.
