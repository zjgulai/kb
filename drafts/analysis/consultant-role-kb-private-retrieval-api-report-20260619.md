---
title: "Consultant Role KB Private No-Provider Retrieval API Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "agents/consultant-agent/runtime/local_retrieval_api.py"
  - "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/manifest.json"
  - "shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl"
scope: "private local retrieval API smoke for consultant-agent"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local API prototype only; no staging deployment"
---

# Consultant Role KB Private No-Provider Retrieval API Report

## 0. Boundary

This API is a local/private prototype. It binds to localhost for smoke, returns
metadata and unit locators, and does not return raw source text. It does not
call a provider, write into a live KB, deploy staging, or deploy production.

## 1. API Surface

| endpoint | method | purpose |
|---|---|---|
| `/health` | GET | local readiness and boundary metadata |
| `/retrieve` | POST | local BGE vector retrieval plus deterministic rerank |
| `/eval/label-seed` | POST | smoke against pending-review locator label seed |

## 2. Smoke Metrics

| metric | value |
|---|---:|
| record_count | 800 |
| eval001_top1_source | `SRC-CONSULT-001` |
| eval016_target_in_top5 | true |
| eval046_status | `policy_refusal` |
| forbidden_status | 403 |
| label_seed_match_at_1 | 0.9375 |
| label_seed_match_at_5 | 1.0 |
| policy_refusal_pass_rate | 1.0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |
| failure_count | 0 |

## 3. Interpretation

Fact: the local API can load the durable vector store, serve health, retrieve
locator-backed metadata, enforce workspace rejection, handle policy-only refusal
evals, and evaluate against the pending label seed.

Fact: the label seed is still `pending_human_review`; these smoke metrics are
not human-approved gold precision.

Inference: this is enough to unblock private staging design, but not enough to
approve online use or provider generation.
