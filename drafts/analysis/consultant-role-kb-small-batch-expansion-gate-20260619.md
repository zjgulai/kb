---
title: "Consultant Role KB Small-Batch Expansion Gate"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/consultant-role-kb-extraction-execution-plan-draft-20260619.md"
  - "drafts/analysis/consultant-role-kb-decision-log-20260619.md"
  - "tmp/consultant-role-kb-anchored-retrieval-citation-eval-20260619.json"
  - "tmp/consultant-role-kb-answer-trace-eval-20260619.json"
scope: "gate for expanding consultant role KB cards beyond the 33-card local sample"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "draft gate only; no expanded extraction; no live KB ingestion"
---

# Consultant Role KB Small-Batch Expansion Gate

## 0. Boundary

This gate defines when the consultant-role KB may expand from the current 33 anchored typed-card samples to a larger local extraction batch.

It does not extract additional source content, ingest into a live KB, call a provider, deploy a service, or approve client-facing use. Source policy remains `evidence_grade=C`, `license_status=pending_legal_review`, and `production unchanged`.

## 1. Current Local Evidence

The current local PoC has these verified properties:

| check | current result |
|---|---:|
| typed cards | 33 |
| unit anchor coverage | 33/33 |
| all-eval anchored_citation@1 | 0.92 |
| all-eval anchored_citation@5 | 0.96 |
| answerable-eval anchored_citation@1 | 0.9583 |
| answerable-eval anchored_citation@5 | 1.0 |
| source-only citation violations | 0 |
| answer-trace pass rate | 12/12 |
| provider calls | 0 |
| live KB ingestion | 0 |

Fact: the 33-card sample can carry source metadata, unit locators, and deterministic governance boundary language.

Inference: the next useful test is a controlled local expansion, not production deployment.

Unknown: these metrics may drop when the card count and source distribution expand.

## 2. Expansion Shape

Recommended first expansion: a capped, source-balanced batch of 120-180 typed cards across the 15 registered P1 candidate sources.

| source group | included sources | target card families |
|---|---|---|
| consulting method | `SRC-CONSULT-001`, `SRC-CONSULT-002` | `consult_method_card`, framework-selection cards |
| delivery workflow | `SRC-CONSULT-003` to `SRC-CONSULT-006` | kickoff, proposal, RFP, executive-summary cards |
| diagnostic guides | `SRC-CONSULT-007` to `SRC-CONSULT-009` | diagnostic dimension, data request, interview guide cards |
| transaction advisory | `SRC-CONSULT-010` to `SRC-CONSULT-012` | CDD, ODD, PMI workstream and refusal-boundary cards |
| reference data | `SRC-CONSULT-013` to `SRC-CONSULT-015` | KPI and acronym cards with strict row-level anchors |

Do not expand the full `consult/` folder yet. Keep expansion inside the registered P1 sources until the PRD addendum, license review, and owner review gates are settled.

## 3. Required Card Contract

Every expanded card must include:

```yaml
card_id: ""
card_type: ""
workspace: "consultant-p1"
domain: "consulting-kb"
source_id: ""
source_type: "external_reference"
source_owner: "李梁"
source_uri: ""
source_version: ""
evidence_grade: "C"
license_status: "pending_legal_review"
allowed_agents:
  - "consultant-agent"
blocked_actions: []
citation_anchor:
  locator_type: ""
  locator: ""
  anchor_confidence: ""
  anchor_label: ""
```

The `citation_anchor.locator` must be one of:

- `slide:{n}`
- `page:{n}`
- `paragraph:{n}`
- `sheet:{sheet_name}#row:{n}`

## 4. Extraction Rules

- Extract structured knowledge cards, not long source passages.
- Keep labels and summaries short enough to support retrieval and human review.
- Preserve English method/source terms where they are method names or file terminology.
- Keep Chinese as the primary generated card language.
- Do not create final legal, financial, investment, or client-ready advice cards.
- Do not allow cards without `source_id`, `evidence_grade`, `license_status`, `workspace`, and unit locator.
- Treat all third-party P1 sources as `external_reference` unless a future source-register review proves a more specific type.

## 5. Blocking Gates

Expansion is blocked if any of these occur:

| gate | stop condition |
|---|---|
| source register | any expanded card lacks a registered `source_id` |
| license | any source is upgraded beyond `pending_legal_review` without explicit approval |
| evidence | any `D`-grade source supports a conclusion or answer |
| locator | any extracted card lacks a unit locator |
| workspace | any card leaves `consultant-p1` or enables a write tool |
| blocked actions | any card omits applicable client-send, publish, approval, budget, PII, or redistribution blocks |
| copyright | any card reproduces long source text rather than structured metadata |
| provider | any provider call is required for extraction, embedding, or answer generation |
| live KB | any ingestion target is a live or production KB |

## 6. Regression Gate

After expansion, rerun these local checks:

| check | blocking threshold |
|---|---:|
| metadata completeness | 1.0 |
| unit locator coverage | 1.0 |
| source-only citation violations | 0 |
| answer-trace fixture pass rate | 1.0 |
| answerable anchored_citation@5 | >= 0.95 |
| no-provider-call check | 0 provider calls |
| live-ingestion check | 0 live KB writes |

Review thresholds:

- If answerable anchored_citation@1 drops below 0.90, do not expand further until failures are classified.
- If any category-level source_recall@1 drops below 0.80, add category-specific evals before proceeding.
- If `refusal_unknown` regressions increase, tune refusal/source-intent routing before adding more cards.

## 7. Human Review Gate

Before any PRD addendum or live KB planning, a human owner should review:

- all transaction advisory cards from `SRC-CONSULT-010` to `SRC-CONSULT-012`;
- all cards whose blocked actions include `approve_transaction`, `commit_budget`, `publish_client_deliverable`, or `send_client_email`;
- a stratified sample of at least 20 cards across method, delivery, diagnostic, and reference-data families;
- every card with low or medium anchor confidence.

## 8. Next Decisions

Recommended defaults:

| decision | recommended default | reason |
|---|---|---|
| expansion size | 120-180 cards | large enough to stress retrieval, small enough for manual review |
| source scope | only 15 P1 registered sources | keeps source governance auditable |
| PRD addendum timing | after expansion regression gate | avoids promoting a schema before it survives a larger batch |
| human reviewer | 李梁 plus one consulting-domain reviewer if available | source owner plus subject review reduces overfitting risk |

Unresolved user decision: whether to run the controlled local expansion batch next, or first draft the PRD addendum/directory blueprint from the current 33-card evidence.
