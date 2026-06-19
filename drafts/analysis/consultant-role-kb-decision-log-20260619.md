---
title: "Consultant Role KB Decision Log"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/consultant-role-kb-extraction-execution-plan-draft-20260619.md"
scope: "decision record for consultant role knowledge-base P1 planning"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# Consultant Role KB Decision Log

## 0. Boundary

This decision log records user-approved P1 planning decisions. It does not ingest documents, call a model provider, create a live KB, or authorize production use.

## 1. User Decisions

| decision_id | decision | user answer | implementation effect |
|---|---|---|---|
| DQ-01 | P1 role scope | 同意收缩为诊断与交付型高级咨询顾问 | First slice is `Consulting Diagnostic And Delivery Copilot`, not full consulting expert. |
| DQ-02 | Domain/agent shape | 同意新增 `consulting-kb` and `consultant-agent` | Treat `consulting-kb` as draft domain candidate. |
| DQ-03 | Source-use boundary | 允许内部本地 PoC card extraction | Candidate sources can become `ready_for_poc` for internal local PoC only. |
| DQ-04 | Source owner | 李梁 | Candidate source owner is `李梁`. |
| DQ-05 | Output boundary | 不限定 | Agent may draft more than diagnostic plans, but automated send/submit/publish/approval remains blocked. |
| DQ-06 | Output language | 中文为主，保留 English method/source terms | Eval questions and card labels use Chinese primary text with English methodology terms retained. |

## 2. Evidence And Risk Interpretation

The approval above is sufficient for an internal local P1 PoC candidate register. It is not evidence of production readiness, formal legal clearance, or unrestricted redistribution rights.

P1 evidence policy:

- `evidence_grade`: `C`
- `owner_review_status`: `owner_reviewed`
- `license_status`: `pending_legal_review`
- `intake_status`: `ready_for_poc`
- `workspace`: `consultant-p1`

## 3. Blocked Actions

These actions remain blocked for P1 even though outputs are not otherwise limited:

- `publish_client_deliverable`
- `send_client_email`
- `submit_rfp`
- `commit_budget`
- `approve_transaction`
- `redistribute_source_text`
- `expose_pii`

## 4. Source Register Schema Decision

The existing `kb-source-register-template.md` did not have a clean enum value for third-party consulting playbooks, diagnostic guides, slide templates, or reference libraries. The user approved adding `external_reference` to the source-register schema.

Implemented on 2026-06-19:

- `drafts/analysis/kb-source-register-template.md` now includes `external_reference`.
- `drafts/analysis/kb-source-register.sample.csv` includes one sample `SRC-CONSULT-001` row.
- The default policy remains `evidence_grade=C`, `license_status=pending_legal_review`, and blocked redistribution/client-final actions.

## 5. Local Embedding/Indexing PoC Decision

The user approved the next local embedding/indexing PoC.

Boundary:

- Local PoC only.
- No KB provider call.
- No production deployment.
- No live KB ingestion.
- Local hash/vector index is allowed as plumbing proof, not as final semantic-quality evidence.

## 6. Local Embedding Model Lock Decision

After the local hash baseline, the user approved continuing to a real local embedding model. The P1 local embedding candidate is locked in draft ADR form:

- ADR: `drafts/analysis/consultant-role-kb-embedding-adr-001-bge-small-zh-v1.5-20260619.md`
- Model: `BAAI/bge-small-zh-v1.5`
- Snapshot: `7999e1d3359715c523056ef9478215996d62a620`
- Dimension: 512
- License recorded from local README: MIT
- Runtime: Homebrew Python 3.12 + `sentence-transformers`

Measured local PoC result:

| method | source_recall@1 | source_recall@5 | interpretation |
|---|---:|---:|---|
| local_hash_embedding | 0.76 | 0.86 | deterministic plumbing baseline |
| `BAAI/bge-small-zh-v1.5` | 0.66 | 0.90 | better top5 source coverage, weaker top1 without rerank/source-prior |

Decision boundary:

- This confirms a runnable local embedding/indexing path.
- This does not confirm production readiness, answer quality, citation precision, legal clearance, or live KB behavior.

## 7. Rerank/Source-Prior PoC Decision

The user approved continuing to the next step after the BGE local embedding PoC. A local rerank/source-prior PoC was implemented and executed.

Artifacts:

- Script: `tmp/consultant_role_kb_rerank_source_prior_poc_20260619.py`
- Eval output: `tmp/consultant-role-kb-bge-source-prior-rerank-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-rerank-source-prior-poc-report-20260619.md`

Method boundary:

- Ranking uses BGE vector score plus source-title/source-note/source-alias keyword overlap, card-type fit, and generic KPI/acronym penalties.
- `allowed_source_ids` are not used during ranking; they are only used after ranking to score eval recall.

Measured local PoC result:

| method | all_eval source_recall@1 | all_eval source_recall@5 | answerable_eval source_recall@1 | answerable_eval source_recall@5 |
|---|---:|---:|---:|---:|
| `BAAI/bge-small-zh-v1.5` | 0.66 | 0.90 | not separately reported | not separately reported |
| BGE + source-prior rerank | 0.92 | 0.96 | 0.9583 | 1.0 |

Decision boundary:

- This is enough to keep rerank/source-prior in the P1 local design.
- This is not enough to claim production answer quality; citation anchors and answer-trace checks remain required before any expansion.

## 8. Citation Anchor PoC Decision

The user approved continuing to the citation-anchor step. A local anchor PoC was implemented and executed for the current 33 typed-card samples.

Artifacts:

- Script: `tmp/consultant_role_kb_citation_anchor_poc_20260619.py`
- Anchored cards: `tmp/consultant-role-kb-card-samples-anchored-20260619.jsonl`
- Eval output: `tmp/consultant-role-kb-citation-anchor-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-citation-anchor-poc-report-20260619.md`

Measured local PoC result:

| metric | value |
|---|---:|
| card_count | 33 |
| citation_precision_ready_count | 33 |
| citation_precision_ready_rate | 1.0 |
| pptx slide cards | 4 |
| pdf page cards | 7 |
| docx paragraph cards | 1 |
| xlsx sheet-row cards | 21 |

Decision boundary:

- This confirms the card schema can carry unit-level source anchors.
- This is not final citation precision for answers; the next check must run anchored retrieval/citation eval using the anchored card file.
- This does not authorize extraction expansion, production ingestion, provider calls, or live KB behavior.

## 9. Anchored Retrieval/Citation Eval Decision

The user approved continuing to anchored retrieval/citation eval. The eval was implemented and executed using the anchored card samples.

Artifacts:

- Script: `tmp/consultant_role_kb_anchored_retrieval_citation_eval_20260619.py`
- Eval output: `tmp/consultant-role-kb-anchored-retrieval-citation-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-anchored-retrieval-citation-eval-report-20260619.md`

Measured local PoC result:

| metric | value |
|---|---:|
| indexed_card_count | 33 |
| eval_count | 50 |
| answerable_eval_count | 48 |
| all_eval source_recall@1 | 0.92 |
| all_eval source_recall@5 | 0.96 |
| all_eval anchored_citation@1 | 0.92 |
| all_eval anchored_citation@5 | 0.96 |
| answerable_eval anchored_citation@1 | 0.9583 |
| answerable_eval anchored_citation@5 | 1.0 |
| source_only_citation_violation_count | 0 |

Decision boundary:

- This confirms retrieval outputs can carry unit-level locators.
- Remaining top1 failures are source-selection failures, not missing-anchor failures.
- This is still proxy citation scoring over typed-card anchors, not human-approved final answer citation precision.
- Next gate: create a small answer-trace fixture that checks answer text cites selected locators and preserves evidence/license/refusal boundaries.

## 10. Answer-Trace Fixture Decision

The user approved continuing to answer-trace validation. A deterministic local fixture was implemented and executed over 12 representative eval questions.

Artifacts:

- Script: `tmp/consultant_role_kb_answer_trace_fixture_20260619.py`
- Trace output: `tmp/consultant-role-kb-answer-trace-fixture-20260619.jsonl`
- Eval output: `tmp/consultant-role-kb-answer-trace-eval-20260619.json`
- Report: `drafts/analysis/consultant-role-kb-answer-trace-fixture-report-20260619.md`

Measured local fixture result:

| metric | value |
|---|---:|
| trace_count | 12 |
| trace_pass_count | 12 |
| trace_pass_rate | 1.0 |
| source_selection_pass_rate | 1.0 |
| locator_citation_pass_rate | 1.0 |
| boundary_checks_pass_rate | 1.0 |
| blocked_action_pass_rate | 1.0 |
| refusal_pass_rate | 1.0 |
| long_text_reproduction_pass_rate | 1.0 |
| workspace_isolation_pass_rate | 1.0 |

Failed traces:

- None after the source-intent prior rerun.

Decision boundary:

- This confirms answer text can carry selected unit locators and governance boundary language.
- The previous answer-trace source-selection blocker has been cleared for the 12-question representative fixture.
- Remaining retrieval risk is limited to two answerable rank-1 misses in the 50-question anchored retrieval/citation eval; answerable rank-5 remains 1.0.
- This does not authorize extraction expansion, provider calls, live KB ingestion, or production use.

## 11. Small-Batch Expansion Gate Decision

The next approved-safe direction is a draft/local small-batch expansion gate, not production ingestion.

Artifact:

- `drafts/analysis/consultant-role-kb-small-batch-expansion-gate-20260619.md`

Required gate before expanding beyond the current 33 sample cards:

- every expanded card keeps `source_id`, `source_type` including `external_reference` where applicable, evidence grade, license status, workspace, allowed agents, and blocked actions;
- every expanded card carries a unit locator (`slide`, `page`, `paragraph`, or `sheet_row`);
- the 50-question retrieval/citation eval reruns after expansion;
- the 12-question answer-trace fixture reruns after expansion;
- any new source-selection regression is treated as a blocker before PRD addendum or live KB work.

Boundary remains unchanged: `production unchanged`, `no KB provider call`, no live KB ingestion, and no formal legal clearance.
