---
title: "Consultant Role KB Extraction Execution Plan"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "KB_Platform_PRD.md"
  - "drafts/analysis/enterprise-kb-directory-blueprint.md"
  - "drafts/analysis/kb-p1-poc-validation-plan.md"
  - "drafts/analysis/kb-source-register-template.md"
  - "drafts/analysis/kb-p1-eval-set-template.md"
  - "tmp/consult-role-kb-source-profile-20260619.json"
source_root: "consult/"
scope: "senior consultant role knowledge-base extraction planning"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "planning only; no ingestion; no live KB"
---

# Consultant Role KB Extraction Execution Plan

## 0. Boundary

This document is a draft execution plan. It does not ingest documents, call model providers, deploy services, write a production KB, or confirm commercial use rights for the source materials in `consult/`.

The strongest verified state for this pass is:

- PRD read and mapped.
- Existing draft governance templates reviewed.
- `consult/` folder profiled locally in read-only mode.
- Role KB design and P1 plan proposed.

## 1. Facts, Inferences, And Unknowns

### Facts

- `KB_Platform_PRD.md` is `v2.1-draft` and explicitly states `docs-only draft`, `production unchanged`, `no KB provider call`, and `not production ready`.
- Existing project governance artifacts include P1 PoC plan, source register template, eval set template, evidence register, and enterprise directory blueprint.
- `consult/` contains 81 profiled files: 68 PDF, 6 PPTX, 3 XLSX, 2 CSV, 1 DOCX, and 1 EPUB.
- The profiled PDFs report 9407 pages in total.
- After applying an Excel dimension gate, parse errors were cleared for all profiled files.

### Inferences

- `consult/` is best treated as a senior consultant role library, not as one narrow business domain.
- Full-folder ingestion is too broad for P1. A P1 slice should use 12-20 selected sources and a 50-question eval set.
- The role KB should add a `consulting-kb` domain or role overlay, plus a `consultant-agent` playbook, rather than forcing all materials into `strategy-kb`.

### Unknowns

- Whether current source licenses allow internal derivative knowledge cards, eval questions, and agent retrieval.
- Whether the first target role is a broad senior consultant, a diagnostic consultant, a transaction advisor, or a strategy/executive advisor.
- Which source owner should approve this folder for P1 use.
- Whether client-facing outputs are allowed or the first agent must remain internal-draft only.

## 2. Role Definition

Recommended P1 role:

```yaml
agent: consultant-agent
mode: readonly
workspace: consultant-p1
primary_domain: consulting-kb
secondary_domains:
  - strategy-kb
  - finance-kb
  - supply-chain-kb
  - product-kb
required_shared_layers:
  - shared/entity-dictionary
  - shared/metric-dictionary
  - shared/business-event-taxonomy
  - shared/relationship-model
must_return:
  - conclusion
  - evidence
  - assumptions
  - uncertainty
  - confidence
  - blocked_actions
  - next_human_action
blocked_actions:
  - publish_client_deliverable
  - send_client_email
  - submit_rfp
  - commit_budget
  - approve_transaction
  - redistribute_source_text
  - expose_pii
```

Role purpose:

- Select a consulting approach for a business problem.
- Build issue trees, diagnostic plans, interview guides, data request lists, and executive-summary structures.
- Retrieve relevant industry-analysis/KPI references.
- Produce internal draft recommendations with source-backed uncertainty.

Role non-goals:

- No autonomous client communication.
- No final client-ready slide or proposal without human review.
- No copying long passages from copyrighted source files.
- No legal, financial, or transaction approval.

## 3. Proposed KB Architecture

### 3.1 Domain

Add a draft domain candidate:

```text
domains/
└─ consulting-kb/
   ├─ methodology/
   │  ├─ frameworks/
   │  ├─ diagnostics/
   │  ├─ due-diligence/
   │  ├─ strategy/
   │  └─ industry-analysis/
   ├─ operations/
   │  ├─ project-kickoff/
   │  ├─ proposal-and-rfp/
   │  ├─ interview-guides/
   │  ├─ workplans/
   │  └─ deliverable-templates/
   ├─ metrics-and-data/
   │  ├─ functional-kpis/
   │  ├─ industry-kpis/
   │  ├─ acronym-library/
   │  └─ data-request-templates/
   ├─ crosswalk/
   │  ├─ industry-to-analysis-map/
   │  ├─ diagnostic-dimension-map/
   │  ├─ role-to-interview-guide-map/
   │  └─ deliverable-section-map/
   └─ governance/
      ├─ source-register/
      ├─ evidence-grade/
      ├─ license-review/
      └─ quality-gates/
```

### 3.2 Shared Ontology Additions

| shared layer | additions for consultant role |
|---|---|
| entity-dictionary | company, business_unit, function, industry, stakeholder_role, project, workstream, hypothesis, issue, diagnostic_dimension, deliverable, KPI, data_request_item |
| metric-dictionary | industry KPI, functional KPI, financial KPI, operational KPI, growth KPI, customer KPI |
| business-event-taxonomy | acquisition, post-merger-integration, transformation, strategic-planning-cycle, go-to-market-launch, operational-diagnostic, vendor-selection, turnaround |
| relationship-model | company-has-industry, project-has-workstream, workstream-uses-framework, diagnostic-dimension-uses-data-request, KPI-belongs-to-function, deliverable-has-section |

## 4. Source Inventory Interpretation

Read-only profile artifact:

`tmp/consult-role-kb-source-profile-20260619.json`

Observed candidate categories:

| category | count | role meaning |
|---|---:|---|
| industry-analysis | 29 | company/industry analysis methods and KPIs |
| consulting-playbook | 26 | repeatable consulting project workflows |
| diagnostic-guide | 11 | data request, interview, checklist, scorecard structures |
| strategy-management | 7 | strategy and management operating methods |
| reference-data | 6 | KPI/acronym/table assets |
| client-development | 5 | RFP, proposal, client acquisition |
| transaction-advisory | 4 | CDD, ODD, PMI, PE board contexts |
| consultant-delivery-craft | 4 | problem solving, slides, executive summaries |
| unclassified | 3 | requires manual classification |

## 5. Recommended P1 Slice

Recommendation: start with "Consulting Diagnostic And Delivery Copilot", not the full library.

Reason:

- It exercises every PRD-required layer: methodology, operations, metrics/data, crosswalk, governance, agent playbook, eval.
- It is broad enough to prove role-based KB extraction.
- It is narrow enough to review manually.
- It avoids prematurely ingesting 9407 PDF pages.

### 5.1 P1 Candidate Sources

| source_id | source | target layer | intended use | initial evidence grade | license status | intake status |
|---|---|---|---|---|---|---|
| SRC-CONSULT-001 | `McKinsey Approach to Problem Solving from Umbrex.pptx` | methodology/frameworks | problem definition and issue-structuring method cards | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-002 | `Consulting Frameworks Toolkit from Umbrex.pptx` | methodology/frameworks | framework catalog and selection map | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-003 | `Project Kickoff Toolkit from Umbrex.pptx` | operations/project-kickoff | kickoff workflow and scope/deliverable templates | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-004 | `Executive Summary Slides from Umbrex.pptx` | operations/deliverable-templates | executive-summary structure | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-005 | `Proposal-template-for-a-consulting-project.docx` | operations/proposal-and-rfp | proposal structure and required sections | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-006 | `RFP Playbook.pdf` | operations/proposal-and-rfp | RFP process and vendor-selection playbook | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-007 | `Supply Chain Diagnostic Guide.pdf` | methodology/diagnostics | diagnostic data request/interview/scorecard structure | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-008 | `Umbrex Business Analytics Diagnostic Guide.pdf` | methodology/diagnostics | analytics diagnostic dimensions | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-009 | `Umbrex Customer Experience Diagnostic Guide Firs.pdf` | methodology/diagnostics | CX diagnostic structure | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-010 | `Commercial Due Diligence Playbook 2024.pdf` | methodology/due-diligence | CDD workstream and diligence question map | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-011 | `Operational Due Diligence Playbook.pdf` | methodology/due-diligence | ODD workstream and operational risk map | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-012 | `Post merger integration playbook.pdf` | methodology/due-diligence | PMI planning and workstream map | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-013 | `The Umbrex Library of Functional Key Performance.xlsx` | metrics-and-data/functional-kpis | functional KPI dictionary seed | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-014 | `Umbrex Library of Industry-specific KPIs.xlsx` | metrics-and-data/industry-kpis | industry KPI dictionary seed | C | pending_legal_review | registered_candidate |
| SRC-CONSULT-015 | `The Umbrex Library of Industry Acronyms - First .xlsx` | crosswalk/terminology | industry acronym and terminology crosswalk | C | pending_legal_review | registered_candidate |

Grade rationale:

- These are local third-party reference materials. They can be useful for P1 design and internal local PoC, but should remain C-grade until source-use permission, internal owner approval, and license boundaries are confirmed.
- If the user confirms an internal-use-only policy and assigns a source owner, sources can move from `registered_candidate` to `ready_for_poc`, while still not becoming production facts.

## 6. Extraction Schema

Do not chunk these sources only as raw paragraphs. Convert them into typed knowledge cards.

### 6.1 Method Card

```yaml
card_type: consult_method_card
method_id: ""
method_name: ""
problem_type: ""
when_to_use: []
required_inputs: []
steps: []
outputs: []
failure_modes: []
source_id: ""
evidence_grade: ""
allowed_agents: ["consultant-agent"]
blocked_actions: []
```

### 6.2 Diagnostic Card

```yaml
card_type: diagnostic_dimension_card
dimension_id: ""
diagnostic_name: ""
dimension_name: ""
data_requests: []
interview_roles: []
interview_question_themes: []
scorecard_criteria: []
red_flags: []
source_id: ""
evidence_grade: ""
```

### 6.3 Deliverable Template Card

```yaml
card_type: deliverable_template_card
deliverable_id: ""
deliverable_type: ""
purpose: ""
sections: []
required_inputs: []
reviewer_roles: []
quality_checks: []
source_id: ""
evidence_grade: ""
```

### 6.4 KPI Card

```yaml
card_type: consulting_kpi_card
kpi_id: ""
kpi_name: ""
function_or_industry: ""
definition: ""
interpretation: ""
typical_questions: []
source_id: ""
evidence_grade: ""
```

### 6.5 Industry Analysis Card

```yaml
card_type: industry_analysis_card
industry: ""
analysis_name: ""
business_question: ""
required_data: []
calculation_or_method: ""
interpretation: ""
related_kpis: []
source_id: ""
evidence_grade: ""
```

## 7. Parser And Chunking Plan

| source type | parser route | chunking/card strategy | quality gate |
|---|---|---|---|
| PDF playbooks | pypdf/pdfplumber first; render sampled pages if layout matters | chapter/section cards, not arbitrary fixed-size chunks | page coverage, table-of-contents alignment, citation page retained |
| PPTX toolkits | zip XML extraction or office parser | slide-level cards and template-section cards | slide count, title extraction, image-only slide detection |
| XLSX KPI libraries | openpyxl with worksheet dimension reset | row-level KPI cards, sheet-level metadata | dimension reset, header detection, sampled row count |
| DOCX proposal | python-docx | section-level deliverable template cards | paragraph count, placeholder detection |
| EPUB/PDF duplicate | choose one canonical source | avoid duplicate ingestion | hash/version and content overlap check |

## 8. PRD Gate Mapping

| PRD gate | consultant role adaptation | P1 pass condition |
|---|---|---|
| Taxonomy | confirm `consulting-kb` domain or role overlay | domain decision logged |
| Sample domains | fill five-layer `consulting-kb` draft | methodology/operations/metrics/crosswalk/governance all present |
| Shared ontology | add consultant entities, KPIs, events, relations | 30-50 entity terms and 20-30 KPI/relationship terms seeded |
| Source register | register 12-20 P1 sources | all have source_id/hash/source_uri/evidence/license status |
| Evidence | keep C-grade unless owner/license approval upgrades | no D-grade supports final answer |
| Evaluation | build 50-question consultant-agent eval set | eval JSONL ready for local run |
| Security | workspace isolation | all entries use `consultant-p1` workspace |
| MCP | readonly query/doc_status/health only | no write tools in P1 |
| Licensing | third-party source-use boundary | pending/legal/restricted status explicit |

## 9. Eval Set Design

P1 should contain 50 questions.

| category | count | example intent |
|---|---:|---|
| source_lookup | 10 | retrieve which playbook supports a method, diagnostic area, or deliverable structure |
| methodology_selection | 10 | choose a framework or diagnostic route for a business problem |
| diagnostic_planning | 10 | create a data request/interview/scorecard plan for a functional diagnostic |
| deliverable_workflow | 10 | structure a proposal, kickoff, RFP response, or executive-summary draft |
| refusal_unknown | 10 | refuse unsupported final claims, client-ready output, long text reproduction, or write/send actions |

Minimum scoring checks:

- Answer correctness >= 80%.
- Citation precision >= 90%.
- Refusal quality >= 90%.
- Workspace isolation 100%.
- Blocked action compliance 100%.

## 10. Execution Phases

### Phase A - Decision Lock

Output:

- Decision log for role boundary, P1 slice, license/use boundary, source owner, and output boundary.

Stop if:

- No source-use boundary is approved.
- The role scope remains broader than one P1 slice.

### Phase B - Source Register Draft

Output:

- `drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv`
- hash, source_uri, evidence_grade, owner_review_status, workspace, license_status, blocked_actions.

Stop if:

- A source lacks hash/source_uri.
- license status must be treated as restricted and the user does not approve local internal PoC.

### Phase C - Typed Extraction Dry Run

Output:

- `tmp/consultant-role-kb-card-samples-20260619.jsonl`
- 30-50 sample cards across method, diagnostic, deliverable, KPI, and industry-analysis card types.

Stop if:

- Parser cannot preserve citation location.
- Generated cards reproduce excessive copyrighted text instead of structured summaries.

### Phase D - Shared Ontology Seed

Output:

- entity dictionary seed.
- KPI dictionary seed.
- relationship model seed.
- diagnostic dimension taxonomy.

Stop if:

- ontology terms cannot be mapped back to source IDs.

### Phase E - Eval Set Draft

Output:

- `drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl`
- reviewer checklist.

Stop if:

- eval questions cannot be answered with registered sources.

### Phase F - Local PoC, Only If Authorized

Output:

- ingestion/chunk manifest.
- retrieval benchmark.
- readonly agent trace samples.
- workspace isolation test report.

Boundary:

- Requires explicit approval for any provider/model call or live KB service.

### Phase G - PRD Feedback

Output:

- draft PRD addendum or PRD patch proposal for role-based KB support.

Boundary:

- Do not rewrite `KB_Platform_PRD.md` until user approves the decisions and draft artifacts.

## 11. Decision Questionnaire

Use these as the first user interview round.

| id | question | recommended answer | why it matters |
|---|---|---|---|
| DQ-01 | Is `高级咨询顾问` a broad role, or should P1 narrow it to "diagnostic and delivery consultant"? | Narrow to diagnostic and delivery consultant for P1. | Keeps the first eval measurable. |
| DQ-02 | Should `consulting-kb` be a new domain or a role overlay on `strategy-kb`? | Create `consulting-kb` as a draft domain, with cross-links to existing business domains. | Consultant knowledge contains methods, workflows, and templates that do not fit only strategy. |
| DQ-03 | Can the Umbrex/local consulting documents be used for internal local PoC card extraction? | Approve internal local PoC only; block redistribution and client-ready publishing. | Source license/copyright boundary affects extraction depth. |
| DQ-04 | Who is the source owner for this folder in P1? | Assign `current_thread_user` or a named internal owner for P1 only. | Source register cannot reach `ready_for_poc` without owner. |
| DQ-05 | What should the first agent output? | Internal diagnostic plan, interview guide, data request, and executive-summary outline. | Avoids unsafe client-facing automation. |
| DQ-06 | Which P1 source group is highest value? | Recommended: problem solving + diagnostics + delivery templates + KPI libraries. | Covers the full PRD gate set with limited sources. |
| DQ-07 | Should outputs be Chinese, English, or bilingual? | Chinese output with English method/source terms retained. | Affects chunk labels, eval questions, and agent response contract. |
| DQ-08 | Are long source excerpts allowed in derived artifacts? | No; use structured summaries and short source references only. | Prevents copyright and retrieval leakage risk. |
| DQ-09 | Do we allow the agent to draft proposals/RFP responses? | Draft outline only; no send/submit/publish. | Keeps blocked actions explicit. |
| DQ-10 | What counts as P1 success? | 50-question eval ready, 12-20 sources registered, 30-50 sample cards generated, no provider call unless separately approved. | Defines acceptance before implementation. |

## 12. Decision Outcomes

User decisions recorded on 2026-06-19:

| decision_id | outcome |
|---|---|
| DQ-01 | P1 scope narrowed to diagnostic and delivery senior consultant. |
| DQ-02 | `consulting-kb` draft domain and `consultant-agent` approved. |
| DQ-03 | Internal local PoC card extraction from `consult/` approved. |
| DQ-04 | Source owner set to `李梁`. |
| DQ-05 | Output is not narrowly limited, but automated send/submit/publish/approval remains blocked by governance. |
| DQ-06 | Chinese-first output with English method/source terms retained. |

Artifacts created after the decision:

- `drafts/analysis/consultant-role-kb-decision-log-20260619.md`
- `drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv`
- `drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl`
- `tmp/consultant-role-kb-card-samples-20260619.jsonl`
- `drafts/analysis/consultant-role-kb-card-sample-summary-20260619.md`

## 13. Implemented Local PoC Step

User-approved P1 local PoC work completed after the decision round:

| artifact | status | path |
|---|---|---|
| `external_reference` source-register schema extension | draft implemented | `drafts/analysis/kb-source-register-template.md` |
| source-register sample row | draft implemented | `drafts/analysis/kb-source-register.sample.csv` |
| typed-card sample set | local artifact | `tmp/consultant-role-kb-card-samples-20260619.jsonl` |
| hash embedding/index baseline | local PoC executed | `drafts/analysis/consultant-role-kb-local-embedding-indexing-poc-report-20260619.md` |
| BGE real local embedding/index PoC | local PoC executed | `drafts/analysis/consultant-role-kb-real-embedding-indexing-poc-report-20260619.md` |
| embedding model ADR | draft created | `drafts/analysis/consultant-role-kb-embedding-adr-001-bge-small-zh-v1.5-20260619.md` |
| BGE source-prior rerank PoC | local PoC executed | `drafts/analysis/consultant-role-kb-rerank-source-prior-poc-report-20260619.md` |
| citation anchor PoC | local PoC executed | `drafts/analysis/consultant-role-kb-citation-anchor-poc-report-20260619.md` |
| anchored retrieval/citation eval | local PoC executed | `drafts/analysis/consultant-role-kb-anchored-retrieval-citation-eval-report-20260619.md` |
| answer-trace fixture | local fixture executed | `drafts/analysis/consultant-role-kb-answer-trace-fixture-report-20260619.md` |
| small-batch expansion gate | draft created | `drafts/analysis/consultant-role-kb-small-batch-expansion-gate-20260619.md` |

Measured retrieval results:

| method | indexed cards | eval questions | source_recall@1 | source_recall@5 |
|---|---:|---:|---:|---:|
| local hash embedding | 33 | 50 | 0.76 | 0.86 |
| `BAAI/bge-small-zh-v1.5` | 33 | 50 | 0.66 | 0.90 |
| BGE + source-prior rerank | 33 | 50 | 0.92 | 0.96 |

Answerable-only rerank result:

| method | answerable questions | source_recall@1 | source_recall@5 |
|---|---:|---:|---:|
| BGE + source-prior rerank | 48 | 0.9583 | 1.0 |

Citation anchor readiness:

| metric | value |
|---|---:|
| anchored cards | 33 |
| citation_precision_ready_count | 33 |
| citation_precision_ready_rate | 1.0 |
| PPTX slide anchors | 4 |
| PDF page anchors | 7 |
| DOCX paragraph anchors | 1 |
| XLSX sheet-row anchors | 21 |

Anchored retrieval/citation eval:

| metric | value |
|---|---:|
| eval_count | 50 |
| answerable_eval_count | 48 |
| all_eval source_recall@1 | 0.92 |
| all_eval source_recall@5 | 0.96 |
| all_eval anchored_citation@1 | 0.92 |
| all_eval anchored_citation@5 | 0.96 |
| answerable_eval anchored_citation@1 | 0.9583 |
| answerable_eval anchored_citation@5 | 1.0 |
| source_only_citation_violation_count | 0 |

Answer-trace fixture:

| metric | value |
|---|---:|
| trace_count | 12 |
| trace_pass_count | 12 |
| trace_pass_rate | 1.0 |
| source_selection_pass_rate | 1.0 |
| locator_citation_pass_rate | 1.0 |
| boundary_checks_pass_rate | 1.0 |
| blocked_action_pass_rate | 1.0 |
| refusal_pass_rate | 1.0 |

Interpretation:

- The real local embedding path is runnable with no provider call.
- `BAAI/bge-small-zh-v1.5` improves top5 source coverage but currently underperforms the hash baseline at top1.
- Rerank/source-prior improves top1 and top5 source recall without using eval labels during ranking.
- Source-intent priors fixed the previous answer-trace source-selection failures for ambiguous scoping, client-ready PPT, and high-stakes due-diligence/refusal prompts.
- The current 33 sample cards now carry unit-level citation anchors.
- Anchored retrieval/citation eval confirms retrieved results can carry unit-level locators and avoid source-only citations.
- Remaining answerable top1 failures are limited to `CONSULT-EVAL-043` and `CONSULT-EVAL-047`; answerable top5 failures are zero.
- Answer-trace fixture confirms citation formatting and governance boundary language are viable in deterministic local output.
- Answer-trace fixture has no remaining failed traces in the 12-question representative set.
- Before extraction expansion, define a small-batch expansion gate so new cards must retain source register metadata, unit locators, blocked actions, and eval coverage.

## 14. Recommended Next Step

Recommended P4 preparation, still draft/local only:

1. Decide whether the next local action is controlled expansion (recommended cap: 120-180 cards across the 15 registered P1 sources) or a PRD addendum/directory blueprint first.
2. If expansion is chosen, use `drafts/analysis/consultant-role-kb-small-batch-expansion-gate-20260619.md` as the blocking checklist.
3. Rerun the 50-question eval, anchored retrieval/citation eval, and 12-question answer-trace fixture after expansion.
4. Keep source policy unchanged: `evidence_grade=C`, `license_status=pending_legal_review`, `production unchanged`, and `no KB provider call`.
