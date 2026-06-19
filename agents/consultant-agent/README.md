---
title: "Consultant Agent"
status: "draft"
created_at: "2026-06-19"
scope: "draft role-agent profile"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# Consultant Agent

`consultant-agent` is the draft role agent for the 高级咨询顾问诊断与交付 Copilot.

Allowed draft outputs:

- issue tree and problem definition support
- diagnostic plan outlines
- data request and interview guide outlines
- executive summary and proposal structure outlines
- KPI and terminology lookup summaries

Blocked actions include publishing client deliverables, sending client email, submitting RFPs, approving transactions, committing budget, exposing PII, and redistributing source text.

Local runtime prototype:

- `agents/consultant-agent/runtime/local_retrieval_api.py`
- endpoints: `GET /health`, `POST /retrieve`, `POST /eval/label-seed`
- boundary: localhost/private only, no provider call, no live KB ingestion, no raw source text response, no staging deployment

Private staging prerequisites:

- auth/audit design: `drafts/analysis/consultant-role-kb-staging-auth-audit-design-20260619.md`
- audit event schema: `shared/audit/consultant-agent/staging-audit-event.schema-20260619.json`
- local contract validator: `tmp/consultant_role_kb_staging_auth_audit_contract_20260619.py`
- staging must fail closed on missing token, reviewer, request ID, agent, or workspace
- audit events must keep actor/query hashes, result refs, source governance fields, and no raw source text
