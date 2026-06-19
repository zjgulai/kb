---
title: "Consultant Role KB Manual Decision Intake Preflight"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
  - "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
  - "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"
scope: "aggregate validation before manual decisions can affect shared-staging readiness"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local preflight only; no manual approval recorded"
---

# Consultant Role KB Manual Decision Intake Preflight

## 0. Boundary

This preflight validates decision files for the human label, legal/source-owner,
and security/staging-control gates. It does not create approvals, configure
secrets, deploy shared staging, call a provider, or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| manual_decision_intake_ready | false |
| status | blocked |
| blocker_count | 3 |
| failure_count | 0 |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Decision Files

| gate | file |
|---|---|
| human labels | `shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl` |
| legal/source-owner | `shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl` |
| security/staging controls | `shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl` |

## 3. Gate Summary

| gate | ready | current count |
|---|---:|---:|
| human_label_decisions | false | 0/50 approved |
| legal_source_owner_clearance | false | 0/80 selected sources approved |
| security_staging_controls | false | 0/8 controls approved |

## 4. Interpretation

Fact: the current default decision files are structurally valid and have
`failure_count = 0`.

Fact: all three manual decision gates remain blocked because they still contain
pending decisions rather than approved human/legal/security outcomes.

Boundary: this is only an intake preflight. Approval decisions must be made by
the appropriate human reviewers and must not include raw secret values,
passwords, private keys, or private contact details in repository artifacts.
