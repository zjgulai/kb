---
title: "Consultant Role KB Legal And Source Owner Review Packet"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-full-source-register-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-parser-unit-manifest-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-card-qa-validation-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-batch30-card-qa-validation-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-batch60-card-qa-validation-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-all-extractable-card-qa-validation-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-csv-loader-support-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-all-extractable-vector-store-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-human-gold-locator-labels-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-human-label-review-workflow-20260619.md"
  - "drafts/analysis/consultant-role-kb-private-retrieval-api-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-staging-auth-audit-design-20260619.md"
  - "drafts/analysis/consultant-role-kb-local-staging-auth-audit-smoke-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-shared-staging-readiness-preflight-20260619.md"
  - "drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md"
  - "drafts/analysis/consultant-role-kb-legal-source-owner-decision-workflow-20260619.md"
scope: "human review packet for full consultant-agent source and derived-card governance"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "project-local gates approved for metadata retention and batch-30 draft expansion; legal review still pending; no live KB ingestion"
---

# Consultant Role KB Legal And Source Owner Review Packet

## 0. Boundary

This packet is for human review. It does not approve legal use, upgrade
evidence grade, persist new cards into a live KB, call a provider, or deploy
`consultant-agent`.

Current source policy remains:

- raw `consult/` files are local-only;
- all 81 sources have `license_status=pending_legal_review`;
- source type is `external_reference`;
- evidence grade remains `C`;
- blocked actions include `redistribute_source_text`, `publish_client_deliverable`, `send_client_email`, `submit_rfp`, `commit_budget`, `approve_transaction`, and `expose_pii`.

## 0.1 Project Decisions Captured

The project owner approved the following local/draft gates on 2026-06-19:

| decision | project outcome | boundary |
|---|---|---|
| `approve_local_metadata` | approved | full source register and structural parser manifests may remain in the repo because they do not contain raw source text |
| existing 150 draft derived cards | allowed | existing draft cards may remain persisted for local eval before legal review; this is not approval for client-ready publication |
| next extraction batch | expand to 30 sources | batch expansion remains local/draft and must keep source metadata, unit locators, blocked actions, and no long source-text reproduction |
| runtime ADR | accepted | local-only now, private staging next, provider/hybrid only after explicit legal/security/product approval |

These project decisions do not clear `license_status=pending_legal_review`, do
not authorize raw source redistribution, and do not authorize online
provider-backed `consultant-agent` use.

## 1. Review Scope

| item | current fact |
|---|---:|
| full registered sources | 81 |
| ready_for_poc seed sources | 15 |
| registered pending-review sources | 66 |
| license_status pending_legal_review | 81 |
| sources with high-risk flags | 75 |
| duplicate groups | 1 |
| parser manifest parse errors | 0 |
| structural parser units | 23310 |
| local expanded cards already QA-checked | 150 |
| card QA failure_count | 0 |
| batch-30 local cards already QA-checked | 300 |
| batch-30 card QA failure_count | 0 |
| batch-30 answerable anchored_citation@1 | 0.9792 |
| batch-30 answerable anchored_citation@5 | 1.0 |
| batch-30 answer trace pass rate | 1.0 |
| batch-60 local cards already QA-checked | 600 |
| batch-60 card QA failure_count | 0 |
| batch-60 answerable anchored_citation@1 | 0.9792 |
| batch-60 answerable anchored_citation@5 | 1.0 |
| batch-60 answer trace pass rate | 1.0 |
| batch-60 skipped sources | SRC-CONSULT-030; SRC-CONSULT-031 |
| all-extractable local cards already QA-checked | 800 |
| all-extractable selected sources | 80 |
| all-extractable card QA failure_count | 0 |
| all-extractable answerable anchored_citation@1 | 0.9792 |
| all-extractable answerable anchored_citation@5 | 1.0 |
| all-extractable answer trace pass rate | 1.0 |
| all-extractable skipped sources | SRC-CONSULT-016 |
| CSV loader support | SRC-CONSULT-030 and SRC-CONSULT-031 selected with csv_row locators |
| durable local vector-store records | 800 |
| durable local vector-store embedding rows | 800 |
| durable local vector-store answerable reranked source_recall@5 | 1.0 |
| durable local vector-store provider calls | 0 |
| durable local vector-store live KB writes | 0 |
| pending-review locator label seeds | 50 |
| pending-review locator candidates | 48 |
| approved human-gold locator labels | 0 |
| human label review queue items | 50 |
| human label review approved decisions | 0 |
| human label review workflow failure_count | 0 |
| private no-provider retrieval API smoke record_count | 800 |
| private no-provider retrieval API smoke failure_count | 0 |
| private no-provider retrieval API label_seed_match_at_5 | 1.0 |
| private no-provider retrieval API live KB writes | 0 |
| staging auth/audit contract validation failure_count | 0 |
| local staging auth/audit harness smoke failure_count | 0 |
| local staging auth/audit harness audit events | 5 |
| local staging auth/audit harness audit forbidden leaks | 0 |
| shared staging readiness preflight status | blocked |
| shared staging readiness preflight blockers | 6 |
| legal/source-owner decision rows | 81 |
| legal/source-owner selected approved internal staging rows | 0 |

## 2. High-Risk Review Buckets

| bucket | source count |
|---|---:|
| source_redistribution_restricted | 66 |
| transaction_or_investment_context | 5 |
| client_facing_context | 6 |
| tabular_data_review | 2 |
| classification_review | 3 |
| none | 6 |

Human interpretation:

- `source_redistribution_restricted` means the KB can use locator-backed
  metadata for local PoC, but must not reproduce or redistribute long source
  text without legal approval.
- `transaction_or_investment_context` sources must not support final investment,
  transaction, budget, or approval decisions.
- `client_facing_context` sources must not send, submit, publish, or mark
  client-ready outputs without human approval.

## 3. Requested Decisions

| decision | recommended answer | reviewer |
|---|---|---|
| Can raw `consult/` files be committed or redistributed? | No, keep local-only unless legal explicitly approves. | legal/source owner |
| Can full source register metadata be committed? | Approved at project-local gate because it stores metadata, hashes, parser route, and governance flags, not source text. | project owner; legal/source owner still pending |
| Can parser unit manifests be committed? | Approved at project-local gate for structural locator manifests that do not store source text. | project owner; legal/source owner still pending |
| Can derived typed cards be stored persistently before legal review? | Existing 150 draft cards, batch-30, batch-60, and 800 all-extractable draft cards are allowed as local eval artifacts. | project owner; legal/source owner still pending |
| Can local vector indexes be built from draft cards? | Yes for local PoC only; no live KB or external service. | technical owner/source owner |
| Can pending locator label seeds be reviewed into approved gold labels? | Yes, but reviewer decisions must be explicit and recorded before using them as human-gold evidence. | source owner/domain reviewer |
| Is the review workflow ready for reviewer input? | Yes as a local/draft queue and decision template; no labels are approved until a reviewer fills decisions and validation passes. | source owner/domain reviewer |
| Can a private no-provider retrieval API be prototyped locally? | Completed locally; staging still requires auth, audit, security, and source-owner/legal gates. | technical owner/security |
| Can staging auth/audit be designed before deployment? | Design, local contract validation, and localhost-only harness smoke are acceptable as draft/local artifacts; shared staging still requires security/legal approval. | technical owner/security |
| Is shared staging ready now? | No. Preflight is blocked by human label, legal/source-owner, external secret, external audit path, rate limit, and rollback-owner gates. | product/legal/security |
| Is there a structured legal/source-owner decision intake? | Yes. The decision template is generated, but every source remains `pending_review`; no approval is recorded. | legal/source owner |
| Can `consultant-agent` answer users online from this corpus? | Not yet; staging requires legal/source-owner/security approval. | product/legal/security |
| Can a provider model see retrieved card content? | Not before provider policy and data-use approval. | legal/security/product |

## 4. Review Checklist

- [ ] Confirm whether `external_reference` materials can support internal role-KB extraction.
- [x] Project-local: confirm whether short derived cards are acceptable before full license clearance.
- [x] Project-local: confirm whether structural locator manifests are acceptable to persist.
- [x] Project-local: confirm whether local-only embedding/indexing is acceptable.
- [ ] Confirm whether internal staging can use the 15-source P1 card set.
- [x] Project-local: confirm whether full extraction should run in batches: 15 -> 30 -> 60 -> 81.
- [x] Add CSV loader support for `SRC-CONSULT-030` and `SRC-CONSULT-031` as `csv_row` locator cards.
- [ ] Confirm whether any source must be quarantined before batch extraction.
- [ ] Confirm whether duplicate EPUB/PDF pairs should prefer PDF anchors.
- [x] Generate review queue and decision template for pending locator label seeds.
- [ ] Review and approve, override, reject, or mark pending locator label seeds as needing discussion.
- [x] Draft staging auth, audit log, and deployment topology contract before running the local API as a shared service.
- [x] Implement and smoke-test localhost-only staging auth/audit harness without shared staging deployment.
- [x] Generate shared-staging readiness preflight and draft runbook.
- [x] Generate structured legal/source-owner decision queue and template.
- [ ] Review and approve, restrict, quarantine, reject, or mark pending every selected source needed for shared staging.
- [ ] Confirm and implement staging auth, audit log, and deployment topology before running the local API as a shared service.
- [ ] Confirm whether `consultant-agent` may call a provider model in staging.
- [ ] Confirm retention policy for prompts, retrieved card IDs, and answer traces.

## 5. Proposed Gate Outcomes

| outcome | meaning |
|---|---|
| approve_local_metadata | Full source register and parser manifests may stay in repo. |
| approve_local_cards_batch_15 | Existing 150-card P1 batch may remain draft/local and support local eval. |
| approve_batch_expansion_30 | Next extraction batch may expand to 30 registered sources. |
| approve_batch_expansion_60 | Next extraction batch may expand to 60 extractable registered sources. |
| approve_all_extractable_expansion | Expand to all currently extractable non-duplicate registered sources. |
| approve_staging_no_provider | Internal staging may run retrieval/QA without provider generation. |
| approve_provider_staging | Provider generation may be enabled with logging and cost controls. |
| quarantine_source | Specific source cannot be extracted or indexed. |
| block_persistent_cards | Derived cards must remain local-only or be removed from persistent storage. |

## 6. Current Recommendation

The project-local gates `approve_local_metadata`, existing draft-card
retention, `approve_batch_expansion_30`, `approve_batch_expansion_60`,
`approve_all_extractable_expansion`, durable local vector-store packaging, and
pending locator label seeding, locator label review workflow generation,
runtime ADR acceptance, draft staging auth/audit contract design,
localhost-only auth/audit harness smoke, and shared-staging readiness preflight
are now
recorded. CSV loader support now covers the two previously insufficient-unit
registered CSV sources in the 800-card all-extractable set, and the durable
vector store plus local retrieval API smoke have been rebuilt against that
800-card set. Legal/source-owner decision intake now exists, but all 81 source
decisions remain `pending_review`, and the 80 selected runtime sources have 0
approved internal-staging decisions. Shared staging readiness is currently
blocked with 6 blockers. The next local step should move to actual human review
of locator labels or recording legal/security decisions needed to clear the
preflight.

Do not approve online provider-backed `consultant-agent` until legal/source-owner
and security review explicitly permits retrieved KB content to leave the local
environment.
