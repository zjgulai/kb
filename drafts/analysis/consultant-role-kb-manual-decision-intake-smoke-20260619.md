---
title: "Consultant Role KB Manual Decision Intake Smoke"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant_role_kb_manual_decision_intake_preflight_20260619.py"
  - "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
  - "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
  - "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"
scope: "synthetic smoke for manual decision intake validation behavior"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "synthetic local smoke only; no approval recorded"
---

# Consultant Role KB Manual Decision Intake Smoke

## 0. Boundary

This smoke creates temporary synthetic decision fixtures during execution and
removes them before exit. These fixtures are not manual approvals, do not
configure secrets, do not deploy shared staging, do not call a provider, and do
not ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| ok | true |
| scenario_count | 3 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Scenarios

| scenario | ready | blocker_count | validation_failure_count | human_approved | security_approved |
|---|---:|---:|---:|---:|---:|
| `default_pending_templates` | false | 3 | 0 | 0 | 0 |
| `synthetic_all_approved` | true | 0 | 0 | 50 | 8 |
| `synthetic_invalid_human_missing_reviewer` | false | 1 | 1 | 50 | 8 |

## 3. Interpretation

Fact: the current default pending templates remain blocked.

Fact: a fully synthetic approved fixture can pass the intake readiness logic,
which proves the manual decision bridge can become green after valid reviewer
decisions are supplied.

Fact: an invalid synthetic human decision with missing reviewer is rejected by
the validator before it can clear readiness.

Boundary: the synthetic approved fixture is test data only and must not be used
as legal, source-owner, security, or human-gold evidence.
