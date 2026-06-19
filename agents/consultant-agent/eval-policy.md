---
title: "Consultant Agent Eval Policy"
status: "draft"
created_at: "2026-06-19"
scope: "local eval policy for consultant-agent"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# Consultant Agent Eval Policy

Required local gates:

- source register metadata completeness
- unit locator coverage
- retrieval source recall
- anchored citation recall
- answer-trace boundary checks
- blocked-action compliance
- refusal quality
- pending-review locator label coverage
- human approval state for gold labels

Current eval set: `drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl`.

Current locator label seed:

- `shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl`
- status: `pending_human_review`
- use boundary: can support local no-provider retrieval API tests, but cannot be cited as approved human-gold precision until reviewer decisions are recorded.

Current local API smoke:

- `tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json`
- required: `failure_count=0`, `label_seed_match_at_5=1.0`, `policy_refusal_pass_rate=1.0`, `provider_call_count=0`, `live_kb_write_count=0`

Current staging auth/audit contract validation:

- schema: `shared/audit/consultant-agent/staging-audit-event.schema-20260619.json`
- validator: `tmp/consultant_role_kb_staging_auth_audit_contract_20260619.py`
- output: `tmp/consultant-role-kb-staging-auth-audit-contract-validation-20260619.json`
- required: `failure_count=0`, `provider_call_count=0`, `live_kb_write_count=0`, `source_text_returned=false`
- boundary: design and local contract validation only; no staging deployment
