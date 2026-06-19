---
title: "Consultant Role KB Approval Decision Record"
status: "active"
created_at: "2026-06-19"
scope: "project-local approval record for consultant-agent KB extraction gates"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local draft approvals recorded; legal review pending"
---

# Consultant Role KB Approval Decision Record

## 1. Decisions

| item | user decision | recorded meaning |
|---|---|---|
| 1 | 批准 | `approve_local_metadata`: full source register and structural parser manifests may remain committed because they do not contain raw source text. |
| 2 | 允许 | Existing 150 draft derived cards may remain persisted as local/draft eval artifacts before legal review is complete. |
| 3 | 扩展 | Continue extraction by expanding the local batch to 30 sources, with source metadata, unit locators, blocked actions, and QA gates preserved. |
| 4 | 接受 | Accept ADR 002: local-only runtime now, private staging next, provider/hybrid only after explicit approval. |

## 2. Boundary

These decisions are project-local workflow approvals. They do not approve raw
source redistribution, do not clear `license_status=pending_legal_review`, do
not authorize live KB ingestion, do not authorize provider calls, and do not
approve production launch.

## 3. Evidence After Execution

| artifact | fact |
|---|---|
| `drafts/analysis/consultant-role-kb-batch30-source-selection-20260619.csv` | 30 selected sources |
| `tmp/consultant-role-kb-batch30-cards-20260619.jsonl` | 300 local draft cards |
| `tmp/consultant-role-kb-batch30-card-qa-validation-20260619.json` | QA `failure_count=0` |
| `tmp/consultant-role-kb-batch30-anchored-retrieval-citation-eval-20260619.json` | answerable anchored_citation@1 `0.9792`, @5 `1.0`, source-only citation violations `0` |
| `tmp/consultant-role-kb-batch30-answer-trace-eval-20260619.json` | answer trace `12/12`, trace pass rate `1.0` |
| `drafts/analysis/consultant-role-kb-batch60-source-selection-20260619.csv` | 60 selected extractable sources |
| `tmp/consultant-role-kb-batch60-cards-20260619.jsonl` | 600 local draft cards |
| `tmp/consultant-role-kb-batch60-card-qa-validation-20260619.json` | QA `failure_count=0` |
| `tmp/consultant-role-kb-batch60-anchored-retrieval-citation-eval-20260619.json` | answerable anchored_citation@1 `0.9792`, @5 `1.0`, source-only citation violations `0` |
| `tmp/consultant-role-kb-batch60-answer-trace-eval-20260619.json` | answer trace `12/12`, trace pass rate `1.0` |
| `drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv` | 80 selected non-duplicate extractable sources |
| `tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl` | 800 local draft cards |
| `tmp/consultant-role-kb-all-extractable-card-qa-validation-20260619.json` | QA `failure_count=0` |
| `tmp/consultant-role-kb-all-extractable-anchored-retrieval-citation-eval-20260619.json` | answerable anchored_citation@1 `0.9792`, @5 `1.0`, source-only citation violations `0` |
| `tmp/consultant-role-kb-all-extractable-answer-trace-eval-20260619.json` | answer trace `12/12`, trace pass rate `1.0` |
| `drafts/analysis/consultant-role-kb-csv-loader-support-report-20260619.md` | `SRC-CONSULT-030` and `SRC-CONSULT-031` now have `csv_row` locator cards in the all-extractable set |
| `shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/manifest.json` | durable local vector store with 800 records, 800 embedding rows, 80 sources, 512-dim local BGE embeddings |
| `tmp/consultant-role-kb-all-extractable-vector-store-smoke-20260619.json` | vector plus deterministic rerank answerable source_recall@1 `0.9583`, @5 `1.0`; raw vector-only @5 `0.75`; provider calls `0`; live KB writes `0` |
| `shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl` | 50 pending-review label seeds; 48 locator candidates; 2 policy-only refusal labels; no human-approved labels yet |
| `tmp/consultant-role-kb-human-gold-locator-labels-qa-20260619.json` | label QA `failure_count=0`, locator coverage `1.0`, provider calls `0`, live KB writes `0` |
| `shared/eval/consultant-agent/human-gold-locator-label-review.queue-20260619.csv` | human review queue with 50 review items |
| `shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl` | decision template with 50 pending decisions and 0 approvals |
| `tmp/consultant-role-kb-human-label-review-workflow-validation-20260619.json` | workflow validation `failure_count=0`, approved decisions `0`, provider calls `0`, live KB writes `0` |
| `agents/consultant-agent/runtime/local_retrieval_api.py` | private localhost no-provider retrieval API prototype with `/health`, `/retrieve`, and `/eval/label-seed` |
| `tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json` | API smoke `record_count=800`, `failure_count=0`, label_seed_match_at_5 `1.0`, policy_refusal_pass_rate `1.0`, provider calls `0`, live KB writes `0` |
| `drafts/analysis/consultant-role-kb-staging-auth-audit-design-20260619.md` | private-staging auth/audit contract drafted; no staging deployment |
| `shared/audit/consultant-agent/staging-audit-event.schema-20260619.json` | audit event schema for allowed/denied retrieval events |
| `tmp/consultant-role-kb-staging-auth-audit-contract-validation-20260619.json` | local contract validation `failure_count=0`, provider calls `0`, live KB writes `0`, source text returned `false` |
| `agents/consultant-agent/runtime/staging_auth_audit.py` | localhost-only staging auth/audit harness; not a staging deployment |
| `tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json` | local harness smoke `record_count=800`, missing-token `401`, RBAC denial `403`, audit events `5`, `failure_count=0`, provider calls `0`, live KB writes `0` |
| `tmp/consultant-role-kb-local-staging-audit-events-20260619.jsonl` | audit events store hashed actor/query identifiers and source/card/locator refs only; no raw token/header/question/source leakage detected by smoke |
| `tmp/consultant-role-kb-shared-staging-readiness-preflight-20260619.json` | shared staging readiness preflight is `blocked`, `ready_for_shared_staging=false`, `pass_count=13`, `blocker_count=6`, provider calls `0`, live KB writes `0` |
| `drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md` | draft runbook for future approved shared staging; not an approval or deployment |

## 3.1 Batch-60 Selection Note

`SRC-CONSULT-030` and `SRC-CONSULT-031` were skipped during batch-60 because
the current extraction path produced fewer than 10 extractable units for each.
They remain registered sources, but are not counted as completed typed-card
extractions.

## 3.2 All-Extractable Selection Note

The all-extractable batch now selects 80 non-duplicate sources after CSV loader
support. `SRC-CONSULT-016` remains skipped as the duplicate EPUB secondary to
the preferred PDF source. `SRC-CONSULT-030` and `SRC-CONSULT-031` now produce
`csv_row` locator cards and are included in the 800-card all-extractable set.
The durable local vector store and local retrieval API smoke now cover the
current 800-card all-extractable set, including the CSV cards.

## 4. Next Decision Candidates

- Whether and when a human reviewer should approve, override, reject, or mark pending locator labels as needing discussion.
- Whether to run actual human review over locator labels.
- Whether to record legal/source-owner clearance.
- Whether to configure security-approved shared staging deployment, external secret storage, append-only audit storage, rate limiting, rollback owner, and private ingress for the no-provider API.
