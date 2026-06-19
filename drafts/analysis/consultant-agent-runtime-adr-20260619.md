---
title: "ADR 002 Consultant Agent Runtime Boundary"
status: "accepted"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-extraction-agent-launch-plan-20260619.md"
  - "drafts/analysis/consultant-role-kb-legal-source-owner-review-packet-20260619.md"
  - "drafts/analysis/consultant-role-kb-expanded-regression-eval-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-batch30-regression-eval-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-batch60-regression-eval-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-all-extractable-regression-eval-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-csv-loader-support-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-all-extractable-vector-store-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-human-gold-locator-labels-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-private-retrieval-api-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-staging-auth-audit-design-20260619.md"
  - "drafts/analysis/consultant-role-kb-local-staging-auth-audit-smoke-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-shared-staging-readiness-preflight-20260619.md"
  - "drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md"
  - "drafts/analysis/consultant-role-kb-legal-source-owner-decision-workflow-20260619.md"
  - "drafts/analysis/consultant-role-kb-security-staging-control-workflow-20260619.md"
  - "drafts/analysis/consultant-role-kb-manual-decision-intake-preflight-20260619.md"
scope: "runtime decision for consultant-agent from full extraction to staging"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "accepted runtime boundary; no deployment"
---

# ADR 002 Consultant Agent Runtime Boundary

## 1. Status

Accepted by the project owner on 2026-06-19. This ADR is not a production
approval and does not enable provider calls.

## 2. Context

The local consultant-role KB PoC now has:

- full 81-source draft register;
- full parser unit manifest with 81/81 parse success;
- 150 QA-checked local cards from the first 15 sources;
- 800 QA-checked local cards from 80 non-duplicate extractable sources after CSV loader support;
- durable local vector-store package for the current 800 all-extractable cards;
- pending-review locator label seed for 50 eval items;
- private no-provider local retrieval API prototype;
- localhost-only staging auth/audit harness smoke with failure_count = 0;
- all-extractable answerable anchored_citation@1 = 0.9792 and anchored_citation@5 = 1.0;
- vector plus deterministic rerank answerable source_recall@1 = 0.9583 and @5 = 1.0;
- API smoke label_seed_match_at_5 = 1.0 and policy_refusal_pass_rate = 1.0;
- local staging auth/audit smoke has audit_event_count = 5,
  audit_schema_failure_count = 0, audit_forbidden_leak_count = 0,
  provider_call_count = 0, and live_kb_write_count = 0;
- shared staging readiness preflight is blocked with blocker_count = 7;
- legal/source-owner decision workflow has 81 pending decisions and 0 selected
  sources approved for internal staging;
- security/staging-control decision workflow has 8 pending decisions, 0
  approved controls, 0 configured external controls, and secret_like_value_count
  = 0;
- manual decision intake preflight is structurally green but blocked with 0/50
  human labels, 0/80 selected sources, and 0/8 security controls approved;
- answer-trace fixture pass rate = 1.0.

The unresolved blockers are legal/license review, human approval of locator
labels, persistent derived-card policy, provider policy, staging auth, audit
logging, and production deployment target.

Current extraction exclusion: `SRC-CONSULT-016` is a duplicate EPUB secondary
to the preferred PDF source. `SRC-CONSULT-030` and `SRC-CONSULT-031` now produce
`csv_row` locator cards in the all-extractable local card set.

## 3. Decision

Use the accepted staged runtime path:

1. **Local extraction/runtime now**: local parser, card QA, local BGE embedding,
   deterministic rerank, no provider generation.
2. **Private staging later**: retrieval API plus policy/answer schema behind
   auth, still no provider by default.
3. **Hybrid generation only after approval**: local retrieval and citation
   enforcement, provider generation only if legal/security/product approve
   retrieved-content handling and logging.

## 4. Options Considered

| option | summary | decision |
|---|---|---|
| local-only | safest for full extraction and eval | use now |
| private staging no provider | good for UX, policy, logs, and pilot workflows | next after legal/source-owner review |
| provider-only | fastest answer quality iteration but highest data-governance risk | reject for now |
| local LLM only | preserves data boundary but answer quality and ops are uncertain | keep as fallback research |
| hybrid | best long-term balance if provider policy is approved | target future architecture |

## 5. Runtime Contract

Every `consultant-agent` answer must carry:

- conclusion;
- evidence with source IDs and unit locators;
- assumptions;
- uncertainty;
- confidence;
- blocked actions;
- next human action.

Runtime must enforce:

- no answer without unit-level citation for substantive claims;
- no D-grade evidence for final conclusions;
- no raw source-text redistribution;
- no client-ready publish/send/submit/approval action;
- workspace isolation on `consultant-p1`;
- provider-call logging if provider generation is later enabled.

Private staging, and the current localhost-only staging harness, must
additionally enforce:

- bearer-token validation through external secret storage, with no token stored
  in the repository;
- `X-KB-Agent=consultant-agent`, `X-KB-Workspace=consultant-p1`,
  `X-KB-Reviewer`, and `X-KB-Request-Id`;
- role-based access for `retrieval_reader`, `reviewer`, and `admin`;
- one audit event per allowed or denied retrieval/eval request;
- audit logs with hashed actor/query identifiers and no raw source text.

The localhost-only harness is validation evidence for the auth/audit contract,
not a shared staging deployment.

## 6. Acceptance Gates Before Staging

- legal/source-owner review packet has explicit outcome;
- locator labels have explicit human reviewer decisions before claiming human-gold precision;
- full extraction batch has card QA failure_count = 0;
- answerable anchored_citation@5 >= 0.95;
- answerable anchored_citation@1 target >= 0.90;
- answer-trace pass rate = 1.0;
- blocked-action pass rate = 1.0;
- source-only citation violations = 0;
- audit logs and rollback path are implemented.
- security/staging-control decisions are approved without storing raw secret
  values, bearer tokens, passwords, private keys, or private contact details in
  repository artifacts.
- staging auth/audit contract validation has `failure_count = 0`.
- local staging auth/audit harness smoke has `failure_count = 0` and
  `audit_forbidden_leak_count = 0`.
- manual decision intake preflight must return `manual_decision_intake_ready=true`.
- shared staging readiness preflight must return `ready_for_shared_staging=true`.
- durable vector store and local retrieval API remain aligned with the current all-extractable card set before staging.

## 7. Consequences

Positive:

- preserves source governance while full extraction continues;
- avoids provider data-boundary risk during corpus expansion;
- lets retrieval, citation, QA, and policy mature before UI launch.

Tradeoff:

- no online natural-language generation is approved yet;
- staging UX/deployment work must wait for legal/source-owner, auth, audit, and security gates;
- local BGE/rerank metrics are still proxy evidence, not human gold answer quality.
- raw vector-only retrieval is not sufficient as an acceptance path; deterministic rerank/source-prior logic remains part of the local retrieval contract.

## 8. Current Recommendation

Proceed with local-only full extraction infrastructure, durable local indexing,
human-gold locator labels, the private no-provider retrieval API, local
auth/audit harness, and shared-staging readiness preflight. Do not run shared
staging or enable provider-backed/public online use until legal, security,
product, and source-owner review explicitly approves retrieved-content handling,
external secret storage, append-only audit storage, rate limiting, rollback, and
the readiness preflight returns green.
