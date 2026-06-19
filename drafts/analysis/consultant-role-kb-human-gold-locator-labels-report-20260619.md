---
title: "Consultant Role KB Human-Gold Locator Label Seed Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "tmp/consultant-role-kb-all-extractable-anchored-retrieval-citation-eval-20260619.json"
  - "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/records.jsonl"
scope: "pending-review locator label seed set for consultant-agent retrieval evaluation"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local draft labels only; manual review required"
---

# Consultant Role KB Human-Gold Locator Label Seed Report

## 0. Boundary

This artifact is a machine-generated seed for human review. It is not an
approved human-gold set until a reviewer fills the `human_review` fields and
changes label decisions explicitly.

It does not call a provider, write into a live KB, deploy production code,
approve source licensing, or redistribute raw source text.

## 1. Outputs

| artifact | path |
|---|---|
| label seed | `shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl` |
| QA result | `tmp/consultant-role-kb-human-gold-locator-labels-qa-20260619.json` |
| generator | `tmp/consultant_role_kb_human_gold_locator_labels_20260619.py` |

## 2. Metrics

| metric | value |
|---|---:|
| label_count | 50 |
| locator_gold_candidate | 48 |
| refusal_policy_no_source | 2 |
| locator_coverage_rate_for_48_citable_evals | 1.0 |
| rank_not_top1_count | 1 |
| pending_human_review | 50 |
| failure_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 3. Interpretation

Fact: all 50 eval items now have a structured label seed. The 48 citable evals
have source-and-locator candidates; the 2 no-source refusal evals have explicit
policy-only expectations.

Fact: every label remains `pending_human_review`; this file must not be treated
as approved human-gold evidence.

Inference: this label seed is sufficient to unblock a no-provider retrieval API
contract and future reviewer workflow, but not enough to claim human-approved
locator precision.

Unknown: final human judgment may override source, card, or locator selections.
