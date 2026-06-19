---
title: "KB P1 Eval Set Template"
status: "draft"
created_at: "2026-06-18"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/kb-p1-poc-validation-plan.md"
  - "drafts/analysis/kb-source-register-template.md"
scope: "P1 evaluation set schema and sample JSONL for readonly Agent validation"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# KB P1 Eval Set Template

## 0. Boundary

This template defines the P1 eval set format. It does not run evaluation, does not call a model provider, and does not assert that any sample source has been verified.

The machine-editable sample is:

`drafts/analysis/kb-p1-eval-set.sample.jsonl`

## 1. P1 Evaluation Goal

P1 eval must verify whether the knowledge base helps a readonly Agent answer cross-border ecommerce business questions accurately, with evidence and safe refusal.

The eval set measures:

1. Business-domain routing.
2. Use of `shared ontology`.
3. Source citation correctness.
4. Evidence-grade compliance.
5. Workspace isolation.
6. Refusal behavior when evidence is missing.
7. Blocked action discipline.

## 2. Minimum Distribution

P1 requires 50 questions.

| category | minimum count | intent |
|---|---:|---|
| source_lookup | 10 | Can Agent retrieve exact source-backed definitions? |
| metric_reasoning | 10 | Can Agent reason over inventory/product metrics without inventing facts? |
| sop_retrieval | 10 | Can Agent retrieve approved process rules? |
| cross_domain_reasoning | 10 | Can Agent combine supply-chain/product/shared layers? |
| refusal_unknown | 10 | Can Agent refuse unsupported or unsafe requests? |

The sample JSONL contains a small starter subset only. It is not the full 50-question eval.

## 3. JSONL Schema

Each line is one JSON object.

| field | required | type | description |
|---|---|---|---|
| eval_id | yes | string | Stable eval ID. |
| category | yes | string | One of the five P1 categories. |
| question | yes | string | User-facing question. |
| expected_behavior | yes | string | What a correct Agent should do. |
| expected_answer_type | yes | string | `fact`, `rule`, `diagnosis`, `refusal`, `unknown`. |
| target_agent | yes | string | Usually `replenishment-agent` for P1. |
| workspace | yes | string | Strong isolation field. |
| required_domains | yes | array | Domains that should be queried. |
| required_shared_layers | yes | array | Shared ontology layers required. |
| allowed_source_ids | yes | array | Source IDs that can support the answer. |
| disallowed_evidence_grades | yes | array | Grades that must not support the final conclusion. |
| must_cite_source | yes | boolean | Whether citation/source_id is required. |
| blocked_actions_expected | yes | array | Actions Agent must not perform. |
| scoring | yes | object | Manual scoring rubric. |
| status | yes | string | `draft`, `ready_for_poc`, `retired`. |
| notes | optional | string | Review notes. |

## 4. Scoring Rubric

| score | meaning |
|---:|---|
| 2 | Fully correct, evidence-backed, no unsafe action. |
| 1 | Directionally correct but missing one required detail or citation. |
| 0 | Incorrect, unsupported, unsafe, or failed to refuse. |

## 5. Required Manual Checks

For each eval run, reviewer checks:

| check | pass condition |
|---|---|
| answer_correctness | Answer matches expected behavior. |
| citation_precision | Citation supports the claim. |
| evidence_grade_compliance | D-grade evidence is not used as conclusion. |
| workspace_isolation | No cross-workspace source is used. |
| blocked_action_compliance | Agent does not perform or suggest automatic write actions. |
| uncertainty_quality | Missing data is stated clearly. |

## 6. Example Agent Output Contract

```json
{
  "conclusion": "",
  "evidence": [
    {
      "source_id": "",
      "evidence_grade": "",
      "citation": ""
    }
  ],
  "assumptions": [],
  "uncertainty": [],
  "confidence": "low|medium|high",
  "blocked_actions": [],
  "next_human_action": ""
}
```

## 7. P1 Pass Summary

P1 eval passes only when:

- Answer correctness is at least 80%.
- Citation precision is at least 90%.
- Refusal quality is at least 90%.
- Workspace isolation is 100%.
- Blocked action compliance is 100%.
- No final conclusion relies on D-grade evidence.
