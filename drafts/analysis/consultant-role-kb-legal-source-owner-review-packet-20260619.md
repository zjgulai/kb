---
title: "Consultant Role KB Legal And Source Owner Review Packet"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-full-source-register-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-parser-unit-manifest-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-card-qa-validation-report-20260619.md"
scope: "human review packet for full consultant-agent source and derived-card governance"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "manual review packet only; no live KB ingestion"
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
| Can full source register metadata be committed? | Yes, because it stores metadata, hashes, parser route, and governance flags, not source text. | source owner |
| Can parser unit manifests be committed? | Yes for structural locator manifests that do not store source text. | source owner/legal |
| Can derived typed cards be stored persistently before legal review? | Keep existing PoC cards as draft; do not expand persistent card storage beyond approved batches until legal/source-owner review. | legal/source owner |
| Can local vector indexes be built from draft cards? | Yes for local PoC only; no live KB or external service. | technical owner/source owner |
| Can `consultant-agent` answer users online from this corpus? | Not yet; staging requires legal/source-owner/security approval. | product/legal/security |
| Can a provider model see retrieved card content? | Not before provider policy and data-use approval. | legal/security/product |

## 4. Review Checklist

- [ ] Confirm whether `external_reference` materials can support internal role-KB extraction.
- [ ] Confirm whether short derived cards are acceptable before full license clearance.
- [ ] Confirm whether structural locator manifests are acceptable to persist.
- [ ] Confirm whether local-only embedding/indexing is acceptable.
- [ ] Confirm whether internal staging can use the 15-source P1 card set.
- [ ] Confirm whether full extraction should run in batches: 15 -> 30 -> 60 -> 81.
- [ ] Confirm whether any source must be quarantined before batch extraction.
- [ ] Confirm whether duplicate EPUB/PDF pairs should prefer PDF anchors.
- [ ] Confirm whether `consultant-agent` may call a provider model in staging.
- [ ] Confirm retention policy for prompts, retrieved card IDs, and answer traces.

## 5. Proposed Gate Outcomes

| outcome | meaning |
|---|---|
| approve_local_metadata | Full source register and parser manifests may stay in repo. |
| approve_local_cards_batch_15 | Existing 150-card P1 batch may remain draft/local and support local eval. |
| approve_batch_expansion_30 | Next extraction batch may expand to 30 registered sources. |
| approve_staging_no_provider | Internal staging may run retrieval/QA without provider generation. |
| approve_provider_staging | Provider generation may be enabled with logging and cost controls. |
| quarantine_source | Specific source cannot be extracted or indexed. |
| block_persistent_cards | Derived cards must remain local-only or be removed from persistent storage. |

## 6. Current Recommendation

Approve `approve_local_metadata` first. Then review `approve_local_cards_batch_15`
and `approve_batch_expansion_30` separately.

Do not approve online provider-backed `consultant-agent` until legal/source-owner
and security review explicitly permits retrieved KB content to leave the local
environment.
