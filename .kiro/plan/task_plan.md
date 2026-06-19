---
title: "Consultant Role KB Extraction Plan"
status: "active"
created_at: "2026-06-19"
scope: "role-based knowledge-base extraction plan for consult source folder"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# Consultant Role KB Extraction Plan

## Goal

Use `KB_Platform_PRD.md` and the local `consult/` source folder to design a role-based knowledge-base extraction plan for a senior management consultant role, while keeping the work in draft/read-only planning mode until source governance and implementation gates are approved.

## Boundaries

- No production deployment.
- No provider call.
- No document ingestion into a live KB.
- No long-term memory update.
- No copyrighted source material is reproduced into final artifacts beyond short metadata/snippet inspection for local analysis.

## Phases

| phase | status | objective | expected artifact |
|---|---|---|---|
| P0 | complete | Read PRD, project rules, existing KB drafts, and consult folder inventory | Findings and source profile |
| P1 | complete | Define role taxonomy, source-selection gates, and P1 PoC slice for `consultant-agent` | Draft execution plan |
| P2 | complete | Create source register/eval set candidates after user answers decision questions | Draft CSV/JSONL or Markdown |
| P3 | complete | Run parser/chunk/eval local PoC if authorized, including local hash baseline, real local embedding candidate, and rerank/source-prior check | Local PoC reports and embedding ADR |
| P4 | complete | Add citation anchors, run controlled expansion, and prepare PRD deltas/directory blueprint after review | Anchored card samples, expanded regression, and PRD addendum draft |
| P5 | complete | Initialize project structure, Git repository, and remote push | `.codex/` context, repository metadata, GitHub push |
| P6 | in_progress | Move from role-KB PoC toward full extraction, agent runtime, staging, and launch | Full extraction and agent launch sprint artifacts |

## Current Decisions Needed

Resolved on 2026-06-19:

1. `approve_local_metadata` is approved for full source register and structural parser manifests.
2. Existing 150 draft derived cards may remain persisted before legal review as local/draft artifacts.
3. Batch extraction is approved to expand to 30 sources.
4. Runtime ADR is accepted: local-only now, private staging next, provider/hybrid only after approval.

Still open:

1. Whether to later promote the PRD addendum into `KB_Platform_PRD.md` after human/legal review.
2. Whether raw `consult/` third-party source files can ever be committed after legal/license review.
3. Whether next expansion should move to the remaining extractable sources or first add human-gold eval locator labels.
4. Whether to build a durable local vector store/index before private staging.
5. Whether to implement a private no-provider retrieval API as the next agent runtime slice.
