---
title: "Consultant Role KB Reviewer Questionnaire Intake"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/governance/consultant-agent/reviewer-decision-questionnaire-20260619.csv"
  - "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
  - "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"
scope: "local conversion and validation of answered reviewer questionnaire rows"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "candidate JSONL only; official templates unchanged"
---

# Consultant Role KB Reviewer Questionnaire Intake

## 0. Boundary

This intake converts answered questionnaire rows into temporary candidate
decision JSONL files under `tmp/`. It does not overwrite official decision
templates, approve sources, approve security controls, configure secrets,
deploy shared staging, call a provider, or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| ok | true |
| status | valid_candidate |
| questionnaire_row_count | 88 |
| answered_response_count | 0 |
| response_failure_count | 0 |
| official_template_write_count | 0 |
| legal_selected_approved_internal_staging_count | 0 |
| security_approved_control_count | 0 |
| approval_effect_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Candidate Outputs

- Legal/source-owner candidate JSONL: `tmp/consultant-role-kb-reviewer-questionnaire-derived-legal-decisions-20260619.jsonl`
- Security/operations candidate JSONL: `tmp/consultant-role-kb-reviewer-questionnaire-derived-security-decisions-20260619.jsonl`
- Validation JSON: `tmp/consultant-role-kb-reviewer-questionnaire-intake-validation-20260619.json`

## 3. Interpretation

Fact: with the current unfilled questionnaire, all derived decisions remain
pending and no official decision template is updated.

Fact: this converter is now ready for a filled questionnaire. Non-pending legal
answers require `legal_reviewer`, `source_owner_reviewer`, and `reviewed_at`.
Non-pending security answers require `security_reviewer`, `ops_reviewer`,
`reviewed_at`, and `evidence_uri`.

Boundary: candidate JSONL files under `tmp/` are not approval evidence until a
human reviewer accepts them and the official decision files are filled or
supplied to the manual intake preflight through external paths.
