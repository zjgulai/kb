---
title: "Consultant Role KB Human Label Review Workflow"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-human-gold-locator-labels-report-20260619.md"
  - "agents/consultant-agent/eval-policy.md"
scope: "manual review workflow for consultant-agent locator and policy-refusal labels"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "review queue and decision template generated; no labels approved"
---

# Consultant Role KB Human Label Review Workflow

## 1. Boundary

This workflow turns the machine-generated label seed into an auditable manual
review packet. It does not approve any label by itself.

Current boundary:

- no production deployment;
- no provider call;
- no live KB ingestion;
- no raw source text redistribution;
- source licenses remain `pending_legal_review`;
- labels remain not-human-gold until a reviewer records explicit decisions.

## 2. Artifacts

| artifact | path |
|---|---|
| machine seed | `shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl` |
| review queue CSV | `shared/eval/consultant-agent/human-gold-locator-label-review.queue-20260619.csv` |
| decision schema | `shared/eval/consultant-agent/human-gold-locator-label-review.schema-20260619.json` |
| decision template | `shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl` |
| generator/validator | `tmp/consultant_role_kb_human_label_review_workflow_20260619.py` |
| validation output | `tmp/consultant-role-kb-human-label-review-workflow-validation-20260619.json` |

## 3. Reviewer Decision Options

| decision | meaning | required fields before approval |
|---|---|---|
| `pending` | not reviewed yet | none |
| `approve` | proposed locator or no-source policy is accepted | reviewer, reviewed_at, and locator/policy fields |
| `override` | reviewer supplies a different source/card/locator | reviewer, reviewed_at, override source/card/locator |
| `reject` | proposed label should not become gold | reviewer, reviewed_at, notes |
| `needs_discussion` | human review is blocked on a domain/legal question | reviewer, reviewed_at, notes |

## 4. Review Steps

1. Reviewer opens the queue CSV and decision template.
2. For each row, compare the eval question, proposed source metadata, locator,
   blocked actions, evidence grade, license status, and expected refusal.
3. Update only the decision template or a copy of it. Do not overwrite the seed.
4. Use `approve`, `override`, `reject`, or `needs_discussion`; keep unknown rows
   as `pending`.
5. Re-run the validator before any downstream claim of human-gold precision.
6. A future approved-label export may be generated only from validated reviewer
   decisions, not directly from the machine seed.

## 5. Validation Rules

The validator enforces:

- every seed label has exactly one decision row;
- no duplicate `label_id` or `eval_id`;
- `pending` rows do not pretend to have reviewer approval;
- locator approvals require source ID, card ID, locator, and locator type;
- policy-refusal approvals require `approved_no_source_policy=true`;
- every row keeps `production unchanged`, `no KB provider call`, and
  `no live KB ingestion`;
- no approved human-gold labels are counted until reviewer fields are present.

## 6. Current Validation Result

Current generated workflow state:

- seed_label_count = 50;
- review_queue_count = 50;
- decision_template_count = 50;
- pending_decision_count = 50;
- approved_decision_count = 0;
- locator_candidate_count = 48;
- policy_refusal_count = 2;
- failure_count = 0;
- provider_call_count = 0;
- live_kb_write_count = 0.

## 7. Next Gate

The next gate is manual review by the source owner or delegated reviewer. Until
that happens, retrieval metrics may cite these artifacts as machine-seeded
review candidates, not approved human-gold evidence.
