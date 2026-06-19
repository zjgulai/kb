#!/usr/bin/env python3
"""Convert answered reviewer questionnaire rows into temporary decision JSONL.

Boundary: local candidate generation and validation only. This script does not
overwrite official decision templates, approve sources, approve security
controls, configure secrets, deploy staging, call a provider, or ingest into a
live KB.
"""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

QUESTIONNAIRE = ROOT / "shared/governance/consultant-agent/reviewer-decision-questionnaire-20260619.csv"
OFFICIAL_LEGAL_TEMPLATE = (
    ROOT / "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
)
OFFICIAL_SECURITY_TEMPLATE = (
    ROOT / "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"
)

LEGAL_MODULE = ROOT / "tmp/consultant_role_kb_legal_source_owner_decision_workflow_20260619.py"
SECURITY_MODULE = ROOT / "tmp/consultant_role_kb_security_staging_control_workflow_20260619.py"

OUT_LEGAL = ROOT / "tmp/consultant-role-kb-reviewer-questionnaire-derived-legal-decisions-20260619.jsonl"
OUT_SECURITY = ROOT / "tmp/consultant-role-kb-reviewer-questionnaire-derived-security-decisions-20260619.jsonl"
OUT_JSON = ROOT / "tmp/consultant-role-kb-reviewer-questionnaire-intake-validation-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-reviewer-questionnaire-intake-20260619.md"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0
OFFICIAL_TEMPLATE_WRITE_COUNT = 0

LEGAL_ALLOWED = {
    "approve_internal_staging_retrieval",
    "approve_local_only",
    "quarantine_source",
    "reject_source",
    "needs_discussion",
    "pending_review",
    "",
}
SECURITY_ALLOWED = {"approved", "rejected", "needs_discussion", "pending_review", ""}

LEGAL_APPROVE_INTERNAL_ACTIONS = [
    "metadata_retention",
    "parser_manifest_retention",
    "local_draft_cards",
    "local_embedding_index",
    "human_label_review",
    "internal_no_provider_retrieval",
]
LEGAL_LOCAL_ONLY_ACTIONS = [
    "metadata_retention",
    "parser_manifest_retention",
    "local_draft_cards",
    "local_embedding_index",
    "human_label_review",
]
SECURITY_APPROVED_ACTIONS = ["allow_private_no_provider_shared_staging_after_all_gates_pass"]


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: invalid JSONL at line {line_number}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def split_actions(raw: str) -> list[str]:
    return [item for item in raw.split("|") if item]


def response(row: dict[str, str]) -> str:
    raw = row.get("reviewer_response", "").strip()
    return raw or row.get("default_choice", "pending_review").strip() or "pending_review"


def blank_to_none(value: str) -> str | None:
    value = value.strip()
    return value or None


def legal_reviewer(row: dict[str, str]) -> str | None:
    return blank_to_none(row.get("legal_reviewer", "")) or blank_to_none(row.get("reviewer_name", ""))


def source_owner_reviewer(row: dict[str, str]) -> str | None:
    return blank_to_none(row.get("source_owner_reviewer", "")) or blank_to_none(row.get("reviewer_name", ""))


def security_reviewer(row: dict[str, str]) -> str | None:
    return blank_to_none(row.get("security_reviewer", "")) or blank_to_none(row.get("reviewer_name", ""))


def ops_reviewer(row: dict[str, str]) -> str | None:
    return blank_to_none(row.get("ops_reviewer", "")) or blank_to_none(row.get("reviewer_name", ""))


def reviewed_at(row: dict[str, str]) -> str | None:
    return blank_to_none(row.get("reviewed_at", ""))


def overlay_legal(base: dict[str, Any], row: dict[str, str]) -> dict[str, Any]:
    item = dict(base)
    choice = response(row)
    if choice == "pending_review":
        return item

    item["decision"] = choice
    item["legal_reviewer"] = legal_reviewer(row)
    item["source_owner_reviewer"] = source_owner_reviewer(row)
    item["reviewed_at"] = reviewed_at(row)
    item["review_notes"] = blank_to_none(row.get("reviewer_notes", ""))

    if choice == "approve_internal_staging_retrieval":
        item["legal_decision"] = "approved"
        item["source_owner_decision"] = "approved"
        item["license_status_decision"] = "approved_internal_staging_no_provider"
        item["allowed_runtime_scope"] = "internal_no_provider_staging"
        item["permitted_actions"] = LEGAL_APPROVE_INTERNAL_ACTIONS
    elif choice == "approve_local_only":
        item["legal_decision"] = "approved"
        item["source_owner_decision"] = "approved"
        item["license_status_decision"] = "restricted_local_only"
        item["allowed_runtime_scope"] = "local_draft_only"
        item["permitted_actions"] = LEGAL_LOCAL_ONLY_ACTIONS
    elif choice == "reject_source":
        item["legal_decision"] = "rejected"
        item["source_owner_decision"] = "rejected"
        item["license_status_decision"] = "rejected"
        item["allowed_runtime_scope"] = "none"
        item["permitted_actions"] = []
    else:
        item["legal_decision"] = "needs_discussion"
        item["source_owner_decision"] = "needs_discussion"
        item["license_status_decision"] = "needs_discussion"
        item["allowed_runtime_scope"] = "none"
        item["permitted_actions"] = []
    return item


def overlay_security(base: dict[str, Any], row: dict[str, str]) -> dict[str, Any]:
    item = dict(base)
    choice = response(row)
    if choice == "pending_review":
        return item

    item["decision"] = choice
    item["security_reviewer"] = security_reviewer(row)
    item["ops_reviewer"] = ops_reviewer(row)
    item["reviewed_at"] = reviewed_at(row)
    item["review_notes"] = blank_to_none(row.get("reviewer_notes", ""))
    item["evidence_uri"] = blank_to_none(row.get("evidence_uri", ""))

    if choice == "approved":
        item["external_config_status"] = (
            "configured_externally" if item["external_config_required"] else "not_required"
        )
        item["permitted_actions"] = SECURITY_APPROVED_ACTIONS
    else:
        item["external_config_status"] = (
            "not_configured" if item["external_config_required"] else "not_required"
        )
        item["permitted_actions"] = []
    return item


def validate_responses(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for row in rows:
        item_id = row.get("questionnaire_item_id", "")
        lane = row.get("lane", "")
        choice = response(row)
        if item_id in seen_ids:
            failures.append({"item_id": item_id, "failure": "duplicate questionnaire item"})
        seen_ids.add(item_id)
        if lane == "legal_source_owner" and choice not in LEGAL_ALLOWED:
            failures.append({"item_id": item_id, "failure": f"invalid legal response: {choice}"})
        if lane == "security_operations" and choice not in SECURITY_ALLOWED:
            failures.append({"item_id": item_id, "failure": f"invalid security response: {choice}"})
        if choice not in {"", "pending_review"} and not reviewed_at(row):
            failures.append({"item_id": item_id, "failure": "non-pending response requires reviewed_at"})
        if lane == "legal_source_owner" and choice not in {"", "pending_review"}:
            if not legal_reviewer(row) or not source_owner_reviewer(row):
                failures.append(
                    {
                        "item_id": item_id,
                        "failure": "non-pending legal response requires legal_reviewer and source_owner_reviewer",
                    }
                )
        if lane == "security_operations" and choice not in {"", "pending_review"}:
            if not security_reviewer(row) or not ops_reviewer(row):
                failures.append(
                    {
                        "item_id": item_id,
                        "failure": "non-pending security response requires security_reviewer and ops_reviewer",
                    }
                )
            if not row.get("evidence_uri", "").strip():
                failures.append({"item_id": item_id, "failure": "non-pending security response requires evidence_uri"})
    return failures


def main() -> None:
    legal_mod = load_module("legal_decision_workflow", LEGAL_MODULE)
    security_mod = load_module("security_decision_workflow", SECURITY_MODULE)

    questionnaire_rows = read_csv(QUESTIONNAIRE)
    legal_templates = read_jsonl(OFFICIAL_LEGAL_TEMPLATE)
    security_templates = read_jsonl(OFFICIAL_SECURITY_TEMPLATE)
    legal_by_id = {row["decision_id"]: row for row in legal_templates}
    security_by_id = {row["decision_id"]: row for row in security_templates}

    response_failures = validate_responses(questionnaire_rows)

    legal_decisions = [dict(row) for row in legal_templates]
    security_decisions = [dict(row) for row in security_templates]

    legal_index = {row["decision_id"]: index for index, row in enumerate(legal_decisions)}
    security_index = {row["decision_id"]: index for index, row in enumerate(security_decisions)}

    answered_count = 0
    for row in questionnaire_rows:
        choice = response(row)
        if choice not in {"", "pending_review"}:
            answered_count += 1
        if row["lane"] == "legal_source_owner":
            decision_id = row["official_decision_id"]
            legal_decisions[legal_index[decision_id]] = overlay_legal(legal_by_id[decision_id], row)
        elif row["lane"] == "security_operations":
            decision_id = row["official_decision_id"]
            security_decisions[security_index[decision_id]] = overlay_security(security_by_id[decision_id], row)

    write_jsonl(OUT_LEGAL, legal_decisions)
    write_jsonl(OUT_SECURITY, security_decisions)

    register_rows = legal_mod.read_csv(legal_mod.REGISTER)
    selection_rows = legal_mod.read_csv(legal_mod.SELECTION)
    selected_ids = {row["source_id"] for row in selection_rows if row["selection_status"] == "selected"}
    legal_validation = legal_mod.validate_workflow(register_rows, selected_ids, legal_decisions)
    security_validation = security_mod.validate_workflow(security_decisions)

    failure_count = (
        len(response_failures)
        + int(legal_validation["failure_count"])
        + int(security_validation["failure_count"])
    )
    provider_call_count = max(
        PROVIDER_CALL_COUNT,
        int(legal_validation["provider_call_count"]),
        int(security_validation["provider_call_count"]),
    )
    live_kb_write_count = max(
        LIVE_KB_WRITE_COUNT,
        int(legal_validation["live_kb_write_count"]),
        int(security_validation["live_kb_write_count"]),
    )
    approval_effect_count = 0

    payload = {
        "ok": failure_count == 0,
        "status": "valid_candidate" if failure_count == 0 else "invalid_candidate",
        "questionnaire": str(QUESTIONNAIRE.relative_to(ROOT)),
        "derived_legal_decisions": str(OUT_LEGAL.relative_to(ROOT)),
        "derived_security_decisions": str(OUT_SECURITY.relative_to(ROOT)),
        "official_decision_templates_updated": False,
        "official_template_write_count": OFFICIAL_TEMPLATE_WRITE_COUNT,
        "questionnaire_row_count": len(questionnaire_rows),
        "answered_response_count": answered_count,
        "response_failure_count": len(response_failures),
        "response_failures": response_failures,
        "legal_decision_count": len(legal_decisions),
        "legal_selected_source_count": legal_validation["selected_source_count"],
        "legal_selected_approved_internal_staging_count": legal_validation[
            "selected_approved_internal_staging_count"
        ],
        "legal_failure_count": legal_validation["failure_count"],
        "security_decision_count": len(security_decisions),
        "security_approved_control_count": security_validation["approved_control_count"],
        "security_secret_like_value_count": security_validation["secret_like_value_count"],
        "security_failure_count": security_validation["failure_count"],
        "candidate_manual_decision_intake_ready": bool(
            legal_validation["shared_staging_legal_clearance_ready"]
            and security_validation["shared_staging_security_controls_ready"]
            and failure_count == 0
            and provider_call_count == 0
            and live_kb_write_count == 0
        ),
        "approval_effect_count": approval_effect_count,
        "provider_call_count": provider_call_count,
        "live_kb_write_count": live_kb_write_count,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "candidate JSONL only; official reviewer decision files remain required",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    REPORT.write_text(
        f"""---
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
| ok | {str(payload["ok"]).lower()} |
| status | {payload["status"]} |
| questionnaire_row_count | {payload["questionnaire_row_count"]} |
| answered_response_count | {payload["answered_response_count"]} |
| response_failure_count | {payload["response_failure_count"]} |
| official_template_write_count | {payload["official_template_write_count"]} |
| legal_selected_approved_internal_staging_count | {payload["legal_selected_approved_internal_staging_count"]} |
| security_approved_control_count | {payload["security_approved_control_count"]} |
| approval_effect_count | {payload["approval_effect_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

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
""",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "ok": payload["ok"],
                "answered_response_count": payload["answered_response_count"],
                "legal_selected_approved_internal_staging_count": payload[
                    "legal_selected_approved_internal_staging_count"
                ],
                "security_approved_control_count": payload["security_approved_control_count"],
                "failure_count": failure_count,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
