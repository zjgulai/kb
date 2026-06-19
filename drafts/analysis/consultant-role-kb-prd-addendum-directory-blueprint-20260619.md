---
title: "Consultant Role KB PRD Addendum And Directory Blueprint"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/consultant-role-kb-extraction-execution-plan-draft-20260619.md"
  - "drafts/analysis/consultant-role-kb-small-batch-expansion-gate-20260619.md"
  - "drafts/analysis/consultant-role-kb-small-batch-expansion-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-expanded-regression-eval-report-20260619.md"
  - "drafts/analysis/consultant-role-kb-expanded-answer-trace-fixture-report-20260619.md"
scope: "draft PRD addendum and directory blueprint for consultant-agent role KB"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "draft addendum only; no PRD source edit; no live KB ingestion"
---

# Consultant Role KB PRD Addendum And Directory Blueprint

## 0. Boundary

This is a draft addendum candidate for `KB_Platform_PRD.md`. It does not modify the PRD source file, ingest documents into a live KB, call a provider, deploy production code, or approve license/legal use.

The addendum should remain draft until source owner review, legal/license review, and a human PRD review are complete.

## 1. Addendum Summary

Add a role-based P1 slice:

```yaml
domain: consulting-kb
agent: consultant-agent
workspace: consultant-p1
role_name: 高级咨询顾问诊断与交付 Copilot
source_type_extension:
  - external_reference
evidence_policy:
  default_grade: C
  default_license_status: pending_legal_review
  final_answer_from_D_grade: blocked
runtime_boundary:
  production_impact: production unchanged
  provider_call_boundary: no KB provider call
  live_ingestion: blocked
```

## 2. Evidence From Local A Gate

Facts from the controlled local expansion:

| check | result |
|---|---:|
| expanded cards | 150 |
| registered P1 sources | 15 |
| cards per source | 10 |
| metadata completeness | 1.0 |
| unit locator coverage | 1.0 |
| source-only citation violations | 0 |
| long text violations | 0 |
| provider calls | 0 |
| live KB writes | 0 |
| answerable anchored_citation@1 | 0.9167 |
| answerable anchored_citation@5 | 1.0 |
| answer-trace fixture | 12/12 |

Inference: the role-KB schema is ready for PRD-level draft review as a P1 local pattern.

Unknown: production behavior, human-approved citation precision, and legal/license clearance remain unproven.

## 3. PRD Delta Proposal

### 3.1 Taxonomy Delta

Add a draft domain candidate under the PRD taxonomy:

```text
domains/consulting-kb
```

Purpose:

- represent consulting methods, diagnostics, deliverable templates, KPI references, and terminology crosswalks as typed knowledge cards;
- support role-based retrieval for `consultant-agent`;
- keep evidence, license, and blocked-action policy attached to every card.

### 3.2 Source Register Delta

Keep the source-register schema extension:

```yaml
source_type:
  - internal_doc
  - database_export
  - web_capture
  - external_reference
```

Policy for `external_reference`:

- default `evidence_grade=C`;
- default `license_status=pending_legal_review`;
- must include `source_owner`, `workspace`, `allowed_agents`, and `blocked_actions`;
- cannot support final client-facing claims without human review;
- cannot redistribute long source text.

### 3.3 Card Schema Delta

Add these card families:

| card_type | purpose |
|---|---|
| `consult_method_card` | consulting methods, problem definition, frameworks, diligence workstreams |
| `diagnostic_dimension_card` | diagnostic dimensions, data requests, interviews, scorecards |
| `deliverable_template_card` | kickoff, proposal, RFP, executive summary, delivery workflow |
| `consulting_kpi_card` | functional and industry KPI references |
| `terminology_crosswalk_card` | acronym and terminology mappings |

Required fields:

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
source_anchors:
  - locator_type: ""
    locator: ""
    anchor_label: ""
```

### 3.4 Citation Delta

Final answers from this role must cite unit-level locators, not only source IDs.

Allowed locators:

- `slide:{n}`
- `page:{n}`
- `paragraph:{n}`
- `sheet:{sheet_name}#row:{n}`

Blocked citation patterns:

- source-only citation for final answer;
- long source text reproduction;
- citation to unregistered source;
- citation across workspace boundary.

### 3.5 Agent Boundary Delta

`consultant-agent` may generate:

- internal issue trees;
- diagnostic plans;
- interview guide outlines;
- data request outlines;
- executive summary outlines;
- proposal/RFP structure notes;
- KPI/reference lookup summaries.

`consultant-agent` must not:

- publish a client deliverable;
- send a client email;
- submit an RFP;
- approve a transaction;
- commit budget;
- expose PII;
- redistribute source text;
- provide final legal, financial, or investment advice.

## 4. Directory Blueprint

Recommended draft project structure:

```text
kb/
├─ KB_Platform_PRD.md
├─ AGENTS.md
├─ .codex/
│  ├─ context-pack.md
│  └─ session-thread.md
├─ .kiro/
│  └─ plan/
│     ├─ task_plan.md
│     ├─ findings.md
│     └─ progress.md
├─ consult/
│  └─ original local source files
├─ domains/
│  └─ consulting-kb/
│     ├─ README.md
│     ├─ methodology/
│     ├─ operations/
│     ├─ metrics-and-data/
│     ├─ crosswalk/
│     └─ governance/
├─ agents/
│  └─ consultant-agent/
│     ├─ README.md
│     ├─ playbook.md
│     └─ eval-policy.md
├─ shared/
│  ├─ entity-dictionary/
│  ├─ metric-dictionary/
│  ├─ business-event-taxonomy/
│  └─ relationship-model/
├─ drafts/
│  └─ analysis/
├─ tmp/
└─ archive/
```

## 5. Promotion Gates

Do not promote this addendum into the PRD until all gates pass:

| gate | required evidence |
|---|---|
| source owner | 李梁 reviews source register and role scope |
| legal/license | `external_reference` use policy approved or restricted |
| card schema | 150-card expansion keeps metadata completeness = 1.0 |
| citation | unit locator coverage = 1.0 and source-only violations = 0 |
| retrieval | answerable anchored_citation@5 >= 0.95 |
| answer trace | fixture pass rate = 1.0 |
| security | no workspace leakage, no write tool, no live KB ingestion |
| production | explicit production approval remains absent |

## 6. Current Recommendation

Proceed with project initialization and Git tracking for the draft/local knowledge-base platform artifacts, while keeping `consult/` source files governed by repository policy before pushing.

Recommended repository policy:

- track PRD, `.kiro/plan`, `.codex/`, draft reports, schemas, eval sets, and scripts;
- track local PoC metadata and summarized JSON outputs only if size and licensing are acceptable;
- do not expose secrets;
- do not claim production readiness;
- decide explicitly whether raw `consult/` source files should be committed, because they are third-party reference materials with `pending_legal_review`.
