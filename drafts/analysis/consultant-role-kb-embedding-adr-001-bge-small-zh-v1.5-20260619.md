---
title: "ADR-001 Consultant Role KB Local Embedding Model"
status: "draft"
created_at: "2026-06-19"
scope: "embedding model lock for consultant role KB P1 local PoC"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# ADR-001 Consultant Role KB Local Embedding Model

## Decision

Use `BAAI/bge-small-zh-v1.5` as the P1 local embedding candidate for the consultant-role KB PoC.

## Locked Parameters

| field | value |
|---|---|
| model_id | `BAAI/bge-small-zh-v1.5` |
| model_snapshot | `7999e1d3359715c523056ef9478215996d62a620` |
| embedding_dimension | 512 |
| license | `MIT` based on local model README |
| runtime | Homebrew Python 3.12 + sentence-transformers |
| query_instruction | `为这个句子生成表示以用于检索相关文章：` |
| passage_instruction | none |

## Rationale

- The role KB output is Chinese-first with retained English methodology terms.
- The model is already cached locally and can run without a provider call.
- The measured output dimension is 512 and therefore can be locked before durable indexing.
- The local README marks the model/license line as MIT.

## Constraints

- This is a P1 local PoC lock, not production model selection.
- Any future model replacement requires full re-embedding and eval rerun.
- License remains recorded from local README and should still be included in broader legal review.
