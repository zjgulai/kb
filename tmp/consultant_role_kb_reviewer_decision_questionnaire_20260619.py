#!/usr/bin/env python3
"""Build reviewer-ready question forms for remaining shared-staging gates.

Boundary: local questionnaire packaging only. This script does not approve
sources, approve security controls, edit formal decision templates, configure
secrets, deploy staging, call a provider, or ingest into a live KB.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LEGAL_QUEUE = ROOT / "shared/governance/consultant-agent/legal-source-owner-review.queue-20260619.csv"
SECURITY_QUEUE = ROOT / "shared/governance/consultant-agent/security-staging-control-review.queue-20260619.csv"
CLEARANCE_CHECKLIST = ROOT / "shared/governance/consultant-agent/clearance-execution-checklist-20260619.csv"

QUESTIONNAIRE = ROOT / "shared/governance/consultant-agent/reviewer-decision-questionnaire-20260619.csv"
OUT_JSON = ROOT / "tmp/consultant-role-kb-reviewer-decision-questionnaire-validation-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-reviewer-decision-questionnaire-20260619.md"

LEGAL_TEMPLATE = "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
SECURITY_TEMPLATE = "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"

LEGAL_CHOICES = [
    "approve_internal_staging_retrieval",
    "approve_local_only",
    "quarantine_source",
    "reject_source",
    "needs_discussion",
    "pending_review",
]
SECURITY_CHOICES = [
    "approved",
    "rejected",
    "needs_discussion",
    "pending_review",
]

COMMON_BOUNDARY = (
    "production unchanged; no KB provider call; no live KB ingestion; "
    "no raw source redistribution; no staging deployment"
)
SECRET_BOUNDARY = (
    "do not store secret values, raw tokens, passwords, private keys, "
    "or private contact details in this repository"
)

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0
APPROVAL_EFFECT_COUNT = 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def pipe_join(values: list[str]) -> str:
    return "|".join(values)


def legal_choice_mapping() -> str:
    mapping = {
        "approve_internal_staging_retrieval": {
            "decision": "approve_internal_staging_retrieval",
            "legal_decision": "approved",
            "source_owner_decision": "approved",
            "license_status_decision": "approved_internal_staging_no_provider",
            "allowed_runtime_scope": "internal_no_provider_staging",
        },
        "approve_local_only": {
            "decision": "approve_local_only",
            "legal_decision": "approved",
            "source_owner_decision": "approved",
            "license_status_decision": "restricted_local_only",
            "allowed_runtime_scope": "local_draft_only",
        },
        "quarantine_source": {
            "decision": "quarantine_source",
            "legal_decision": "needs_discussion",
            "source_owner_decision": "needs_discussion",
            "license_status_decision": "needs_discussion",
            "allowed_runtime_scope": "none",
        },
        "reject_source": {
            "decision": "reject_source",
            "legal_decision": "rejected",
            "source_owner_decision": "rejected",
            "license_status_decision": "rejected",
            "allowed_runtime_scope": "none",
        },
        "needs_discussion": {
            "decision": "needs_discussion",
            "legal_decision": "needs_discussion",
            "source_owner_decision": "needs_discussion",
            "license_status_decision": "needs_discussion",
            "allowed_runtime_scope": "none",
        },
        "pending_review": {
            "decision": "pending_review",
            "legal_decision": "pending_review",
            "source_owner_decision": "pending_review",
            "license_status_decision": "pending_legal_review",
            "allowed_runtime_scope": "none",
        },
    }
    return json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))


def security_choice_mapping() -> str:
    mapping = {
        "approved": {
            "decision": "approved",
            "external_config_status": "configured_externally_or_not_required",
        },
        "rejected": {
            "decision": "rejected",
            "external_config_status": "not_configured",
        },
        "needs_discussion": {
            "decision": "needs_discussion",
            "external_config_status": "not_configured",
        },
        "pending_review": {
            "decision": "pending_review",
            "external_config_status": "not_configured",
        },
    }
    return json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))


def legal_question(row: dict[str, str]) -> dict[str, str]:
    return {
        "lane": "legal_source_owner",
        "questionnaire_item_id": f"Q-LEGAL-{row['source_id']}-20260619",
        "target_id": row["source_id"],
        "target_title": row["source_title"],
        "source_owner": row["source_owner"],
        "control_area": "",
        "question": (
            f"是否允许 {row['source_id']}（{row['source_title']}）进入 "
            "internal no-provider staging retrieval？如不允许，请选择 local-only、"
            "quarantine、reject、needs_discussion 或 pending_review。"
        ),
        "choice_options": pipe_join(LEGAL_CHOICES),
        "default_choice": "pending_review",
        "current_decision": row["current_decision"],
        "required_reviewer": "legal_reviewer_and_source_owner_reviewer",
        "required_evidence": "filled legal/source-owner decision JSONL row; no raw source text",
        "official_template_path": LEGAL_TEMPLATE,
        "official_decision_id": row["review_item_id"],
        "choice_to_template_mapping": legal_choice_mapping(),
        "reviewer_response": "",
        "reviewer_name": "",
        "legal_reviewer": "",
        "source_owner_reviewer": "",
        "security_reviewer": "",
        "ops_reviewer": "",
        "reviewed_at": "",
        "reviewer_notes": "",
        "evidence_uri": "",
        "source_type": row["source_type"],
        "evidence_grade": row["evidence_grade"],
        "workspace": row["workspace"],
        "high_risk_flags": row["high_risk_flags"],
        "blocked_actions": row["blocked_actions"],
        "repository_boundary": COMMON_BOUNDARY,
        "secret_redaction_boundary": SECRET_BOUNDARY,
        "approval_effect": "none_questionnaire_only",
        "validation_command": "python3 tmp/consultant_role_kb_manual_decision_intake_preflight_20260619.py",
    }


def security_question(row: dict[str, str]) -> dict[str, str]:
    return {
        "lane": "security_operations",
        "questionnaire_item_id": f"Q-SECURITY-{row['control_id']}-20260619",
        "target_id": row["control_id"],
        "target_title": row["control_title"],
        "source_owner": "",
        "control_area": row["control_area"],
        "question": (
            f"是否批准 {row['control_id']}（{row['control_title']}）作为 "
            "private no-provider shared staging 前置控制？如尚未具备外部配置证据，"
            "请选择 needs_discussion、rejected 或 pending_review。"
        ),
        "choice_options": pipe_join(SECURITY_CHOICES),
        "default_choice": "pending_review",
        "current_decision": row["current_decision"],
        "required_reviewer": "security_reviewer_and_ops_reviewer",
        "required_evidence": row["required_evidence"],
        "official_template_path": SECURITY_TEMPLATE,
        "official_decision_id": row["review_item_id"],
        "choice_to_template_mapping": security_choice_mapping(),
        "reviewer_response": "",
        "reviewer_name": "",
        "legal_reviewer": "",
        "source_owner_reviewer": "",
        "security_reviewer": "",
        "ops_reviewer": "",
        "reviewed_at": "",
        "reviewer_notes": "",
        "evidence_uri": "",
        "source_type": "",
        "evidence_grade": "",
        "workspace": "",
        "high_risk_flags": "",
        "blocked_actions": row["blocked_actions"],
        "repository_boundary": COMMON_BOUNDARY,
        "secret_redaction_boundary": SECRET_BOUNDARY,
        "approval_effect": "none_questionnaire_only",
        "validation_command": "python3 tmp/consultant_role_kb_manual_decision_intake_preflight_20260619.py",
    }


def write_questionnaire(rows: list[dict[str, str]]) -> None:
    QUESTIONNAIRE.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "lane",
        "questionnaire_item_id",
        "target_id",
        "target_title",
        "source_owner",
        "control_area",
        "question",
        "choice_options",
        "default_choice",
        "current_decision",
        "required_reviewer",
        "required_evidence",
        "official_template_path",
        "official_decision_id",
        "choice_to_template_mapping",
        "reviewer_response",
        "reviewer_name",
        "legal_reviewer",
        "source_owner_reviewer",
        "security_reviewer",
        "ops_reviewer",
        "reviewed_at",
        "reviewer_notes",
        "evidence_uri",
        "source_type",
        "evidence_grade",
        "workspace",
        "high_risk_flags",
        "blocked_actions",
        "repository_boundary",
        "secret_redaction_boundary",
        "approval_effect",
        "validation_command",
    ]
    with QUESTIONNAIRE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(payload: dict[str, object]) -> None:
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Reviewer Decision Questionnaire"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/governance/consultant-agent/clearance-execution-checklist-20260619.csv"
  - "shared/governance/consultant-agent/legal-source-owner-review.queue-20260619.csv"
  - "shared/governance/consultant-agent/security-staging-control-review.queue-20260619.csv"
scope: "questionnaire pack for legal/source-owner and security/operations reviewers"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "questionnaire only; no approvals recorded"
---

# Consultant Role KB Reviewer Decision Questionnaire

## 0. Boundary

This pack turns the clearance checklist into reviewer-friendly questions. It
does not approve any source, approve any security control, edit the official
decision templates, configure secrets, deploy shared staging, call a provider,
or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| questionnaire_ready | {str(payload["questionnaire_ready"]).lower()} |
| questionnaire_row_count | {payload["questionnaire_row_count"]} |
| legal_question_count | {payload["legal_question_count"]} |
| security_question_count | {payload["security_question_count"]} |
| approval_effect_count | {payload["approval_effect_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

## 2. How To Use

1. Use `shared/governance/consultant-agent/reviewer-decision-questionnaire-20260619.csv` as the human-facing question list.
2. Fill reviewer identity fields and `reviewed_at` only after real human review.
3. Copy final reviewer decisions into the official JSONL templates listed in the `official_template_path` column, or first run the local questionnaire-intake converter to create `tmp/` candidate JSONL files.
4. Keep secret values, private keys, raw tokens, passwords, and private contact details outside the repository.
5. Re-run the manual intake and shared-staging preflight after official decision files are filled.

## 3. Choice Mapping

Legal/source-owner choices map to the official legal decision schema:

- `approve_internal_staging_retrieval`: approve internal no-provider staging retrieval only.
- `approve_local_only`: keep source in local draft workflows only.
- `quarantine_source`: remove from staging path until discussion is resolved.
- `reject_source`: reject source for this KB runtime.
- `needs_discussion`: keep blocked pending discussion.
- `pending_review`: no decision yet.

Security/operations choices map to the official security control schema:

- `approved`: control is approved; external config evidence still stays outside Git.
- `rejected`: control is not accepted.
- `needs_discussion`: reviewer needs more information.
- `pending_review`: no decision yet.

## 4. Validation Commands

```bash
python3 tmp/consultant_role_kb_manual_decision_intake_preflight_20260619.py
python3 tmp/consultant_role_kb_shared_staging_readiness_preflight_20260619.py || true
```

Expected current state before real reviewer input: shared staging remains blocked
because official legal/source-owner and security/operations decisions are still
pending.
""",
        encoding="utf-8",
    )


def main() -> None:
    legal_rows = read_csv(LEGAL_QUEUE)
    security_rows = read_csv(SECURITY_QUEUE)
    checklist_rows = read_csv(CLEARANCE_CHECKLIST)

    selected_legal_ids = {
        row["item_id"] for row in checklist_rows if row["lane"] == "legal_source_owner"
    }
    legal_questions = [
        legal_question(row)
        for row in legal_rows
        if row["source_id"] in selected_legal_ids and row["included_in_all_extractable"] == "true"
    ]
    security_questions = [security_question(row) for row in security_rows]
    questions = legal_questions + security_questions
    write_questionnaire(questions)

    payload = {
        "ok": True,
        "questionnaire_ready": len(questions) == 88
        and len(legal_questions) == 80
        and len(security_questions) == 8,
        "questionnaire": str(QUESTIONNAIRE.relative_to(ROOT)),
        "questionnaire_row_count": len(questions),
        "legal_question_count": len(legal_questions),
        "security_question_count": len(security_questions),
        "legal_choice_options": LEGAL_CHOICES,
        "security_choice_options": SECURITY_CHOICES,
        "official_decision_templates_updated": False,
        "approval_effect_count": APPROVAL_EFFECT_COUNT,
        "source_text_included": False,
        "raw_secret_included": False,
        "private_contact_detail_included": False,
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "questionnaire only; official reviewer decision files remain required",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()
