#!/usr/bin/env python3
"""Generate and validate legal/source-owner decision workflow.

Boundary: local governance artifact only. This does not approve legal use,
deploy staging, call a provider, or ingest into a live KB.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
SELECTION = ROOT / "drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv"
SCHEMA_PATH = ROOT / "shared/governance/consultant-agent/legal-source-owner-decision.schema-20260619.json"
QUEUE_PATH = ROOT / "shared/governance/consultant-agent/legal-source-owner-review.queue-20260619.csv"
TEMPLATE_PATH = ROOT / "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
VALIDATION_PATH = ROOT / "tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json"
REPORT_PATH = ROOT / "drafts/analysis/consultant-role-kb-legal-source-owner-decision-workflow-20260619.md"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def blocked_actions(row: dict[str, str]) -> list[str]:
    return [item for item in row["blocked_actions"].split(";") if item]


def source_trace(row: dict[str, str]) -> dict[str, str]:
    return {
        "source_type": row["source_type"],
        "source_uri": row["source_uri"],
        "hash_sha256": row["hash_sha256"],
        "evidence_grade": row["evidence_grade"],
        "workspace": row["workspace"],
        "source_suffix": row["source_suffix"],
        "duplicate_policy": row["duplicate_policy"],
        "high_risk_flags": row["high_risk_flags"],
    }


def queue_row(row: dict[str, str], selected_ids: set[str]) -> dict[str, str]:
    return {
        "review_item_id": f"LEGAL-{row['source_id']}-20260619",
        "source_id": row["source_id"],
        "source_title": row["source_title"],
        "source_owner": row["source_owner"],
        "included_in_all_extractable": str(row["source_id"] in selected_ids).lower(),
        "current_license_status": row["license_status"],
        "current_owner_review_status": row["owner_review_status"],
        "evidence_grade": row["evidence_grade"],
        "workspace": row["workspace"],
        "source_type": row["source_type"],
        "source_suffix": row["source_suffix"],
        "duplicate_policy": row["duplicate_policy"],
        "high_risk_flags": row["high_risk_flags"],
        "blocked_actions": "|".join(blocked_actions(row)),
        "hash_sha256": row["hash_sha256"],
        "review_action_options": (
            "approve_internal_staging_retrieval|approve_local_only|"
            "quarantine_source|reject_source|needs_discussion|pending_review"
        ),
        "review_instruction": (
            "Confirm legal and source-owner status for internal no-provider staging. "
            "Do not approve raw source redistribution, provider generation, live KB writes, "
            "or client-ready publication through this decision file."
        ),
        "current_decision": "pending_review",
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
    }


def decision_template(row: dict[str, str], selected_ids: set[str]) -> dict[str, Any]:
    return {
        "decision_id": f"LEGAL-{row['source_id']}-20260619",
        "source_id": row["source_id"],
        "source_title": row["source_title"],
        "source_owner": row["source_owner"],
        "decision": "pending_review",
        "legal_reviewer": None,
        "source_owner_reviewer": None,
        "reviewed_at": None,
        "review_notes": None,
        "legal_decision": "pending_review",
        "source_owner_decision": "pending_review",
        "license_status_decision": "pending_legal_review",
        "allowed_runtime_scope": "none",
        "permitted_actions": [],
        "blocked_actions": blocked_actions(row),
        "conditions": [],
        "included_in_all_extractable": row["source_id"] in selected_ids,
        "source_trace": source_trace(row),
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "legal and source-owner review required before shared staging",
    }


def write_queue(rows: list[dict[str, str]], selected_ids: set[str]) -> None:
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(queue_row(rows[0], selected_ids).keys())
    with QUEUE_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(queue_row(row, selected_ids))


def write_template(rows: list[dict[str, str]], selected_ids: set[str]) -> list[dict[str, Any]]:
    decisions = [decision_template(row, selected_ids) for row in rows]
    TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE_PATH.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in decisions) + "\n",
        encoding="utf-8",
    )
    return decisions


def type_matches(value: Any, expected: Any) -> bool:
    if isinstance(expected, list):
        return any(type_matches(value, item) for item in expected)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported schema type: {expected}")


def validate_value(name: str, value: Any, schema: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if "type" in schema and not type_matches(value, schema["type"]):
        return [f"{name}: expected type {schema['type']}"]
    if "const" in schema and value != schema["const"]:
        failures.append(f"{name}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        failures.append(f"{name}: expected one of {schema['enum']!r}")
    if "uniqueItems" in schema and isinstance(value, list) and len(value) != len(set(value)):
        failures.append(f"{name}: duplicate array items")
    if "minItems" in schema and isinstance(value, list) and len(value) < schema["minItems"]:
        failures.append(f"{name}: below minItems")
    if isinstance(value, str):
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            failures.append(f"{name}: above maxLength")
        if "pattern" in schema and not re.match(schema["pattern"], value):
            failures.append(f"{name}: pattern mismatch")
    if isinstance(value, dict):
        failures.extend(validate_object(name, value, schema))
    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            failures.extend(validate_value(f"{name}[{index}]", item, schema["items"]))
    return failures


def validate_object(name: str, value: Any, schema: dict[str, Any]) -> list[str]:
    if not isinstance(value, dict):
        return [f"{name}: expected object"]
    failures: list[str] = []
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    for field in sorted(required.difference(value)):
        failures.append(f"{name}: missing required field {field}")
    if schema.get("additionalProperties") is False:
        for field in sorted(set(value).difference(properties)):
            failures.append(f"{name}: unexpected field {field}")
    for field, item in value.items():
        if field in properties:
            failures.extend(validate_value(f"{name}.{field}", item, properties[field]))
    return failures


def validate_decision_logic(row: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    decision = row["decision"]
    if decision == "pending_review":
        if row["legal_reviewer"] or row["source_owner_reviewer"] or row["reviewed_at"]:
            failures.append("pending_review must not include reviewer or reviewed_at")
        if row["allowed_runtime_scope"] != "none":
            failures.append("pending_review must keep allowed_runtime_scope=none")
        if row["permitted_actions"]:
            failures.append("pending_review must not include permitted_actions")
        return failures

    if not row["legal_reviewer"] or not row["source_owner_reviewer"] or not row["reviewed_at"]:
        failures.append("non-pending decision requires legal/source owner reviewers and reviewed_at")
    if decision in {"quarantine_source", "reject_source", "needs_discussion"} and not row["review_notes"]:
        failures.append(f"{decision} requires review_notes")
    if decision == "approve_internal_staging_retrieval":
        if not row["included_in_all_extractable"]:
            failures.append("internal staging approval is only valid for selected all-extractable sources")
        if row["legal_decision"] != "approved" or row["source_owner_decision"] != "approved":
            failures.append("internal staging approval requires both legal and source-owner approval")
        if row["license_status_decision"] != "approved_internal_staging_no_provider":
            failures.append("internal staging approval requires approved_internal_staging_no_provider")
        if row["allowed_runtime_scope"] != "internal_no_provider_staging":
            failures.append("internal staging approval requires internal_no_provider_staging scope")
        if "internal_no_provider_retrieval" not in row["permitted_actions"]:
            failures.append("internal staging approval must permit internal_no_provider_retrieval")
    if decision == "approve_local_only":
        if row["allowed_runtime_scope"] != "local_draft_only":
            failures.append("approve_local_only requires local_draft_only scope")
        if row["license_status_decision"] not in {"approved_internal_use", "restricted_local_only"}:
            failures.append("approve_local_only requires internal-use or restricted-local license decision")
    return failures


def validate_workflow(
    register_rows: list[dict[str, str]],
    selected_ids: set[str],
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    failures: list[dict[str, Any]] = []
    register_ids = [row["source_id"] for row in register_rows]
    decision_ids = [row["source_id"] for row in decisions]
    if len(register_ids) != len(set(register_ids)):
        failures.append({"scope": "register", "failure": "duplicate source_id"})
    if len(decision_ids) != len(set(decision_ids)):
        failures.append({"scope": "decision", "failure": "duplicate decision source_id"})
    if set(register_ids) != set(decision_ids):
        failures.append({"scope": "decision", "failure": "decision source_id set does not match register"})

    selected_approvals = 0
    for row in decisions:
        row_failures = validate_object("decision", row, schema)
        row_failures.extend(validate_decision_logic(row))
        if row["source_id"] in selected_ids and row["decision"] == "approve_internal_staging_retrieval":
            selected_approvals += 1
        if row_failures:
            failures.append({"source_id": row.get("source_id"), "failures": row_failures})

    decision_counts = Counter(row["decision"] for row in decisions)
    selected_decisions = [row for row in decisions if row["source_id"] in selected_ids]
    selected_pending = sum(1 for row in selected_decisions if row["decision"] == "pending_review")
    ready = selected_approvals == len(selected_ids) and not failures
    failure_count = 0
    for item in failures:
        failure_count += len(item.get("failures", [item.get("failure")]))
    return {
        "ok": not failures,
        "shared_staging_legal_clearance_ready": ready,
        "schema": str(SCHEMA_PATH.relative_to(ROOT)),
        "queue": str(QUEUE_PATH.relative_to(ROOT)),
        "decision_template": str(TEMPLATE_PATH.relative_to(ROOT)),
        "source_count": len(register_rows),
        "decision_count": len(decisions),
        "selected_source_count": len(selected_ids),
        "selected_approved_internal_staging_count": selected_approvals,
        "selected_pending_review_count": selected_pending,
        "pending_review_count": decision_counts["pending_review"],
        "approve_internal_staging_retrieval_count": decision_counts["approve_internal_staging_retrieval"],
        "approve_local_only_count": decision_counts["approve_local_only"],
        "quarantine_source_count": decision_counts["quarantine_source"],
        "reject_source_count": decision_counts["reject_source"],
        "needs_discussion_count": decision_counts["needs_discussion"],
        "failure_count": failure_count,
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "legal and source-owner review required before shared staging",
        "failures": failures,
    }


def write_report(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(
        f"""---
title: "Consultant Role KB Legal Source Owner Decision Workflow"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv"
  - "shared/governance/consultant-agent/legal-source-owner-decision.schema-20260619.json"
scope: "structured legal and source-owner decision intake for consultant-agent corpus"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "decision workflow only; no legal approval recorded"
---

# Consultant Role KB Legal Source Owner Decision Workflow

## 0. Boundary

This workflow creates a review queue, pending decision template, and validation
summary. It does not approve source use, upgrade license status, deploy shared
staging, call a provider, or ingest into a live KB.

## 1. Validation Summary

| metric | value |
|---|---:|
| source_count | {summary["source_count"]} |
| selected_source_count | {summary["selected_source_count"]} |
| decision_count | {summary["decision_count"]} |
| pending_review_count | {summary["pending_review_count"]} |
| selected_approved_internal_staging_count | {summary["selected_approved_internal_staging_count"]} |
| selected_pending_review_count | {summary["selected_pending_review_count"]} |
| shared_staging_legal_clearance_ready | {str(summary["shared_staging_legal_clearance_ready"]).lower()} |
| failure_count | {summary["failure_count"]} |
| provider_call_count | {summary["provider_call_count"]} |
| live_kb_write_count | {summary["live_kb_write_count"]} |

## 2. Artifacts

- Schema: `shared/governance/consultant-agent/legal-source-owner-decision.schema-20260619.json`
- Queue: `shared/governance/consultant-agent/legal-source-owner-review.queue-20260619.csv`
- Decision template: `shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl`
- Validation: `tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json`

## 3. Interpretation

Fact: every registered source has one pending legal/source-owner decision row.

Fact: the current selected 80-source all-extractable runtime corpus has zero
approved internal-staging decisions.

Boundary: shared staging remains blocked until selected sources receive explicit
legal and source-owner approval for `internal_no_provider_staging`.
""",
        encoding="utf-8",
    )


def main() -> None:
    register_rows = read_csv(REGISTER)
    selection_rows = read_csv(SELECTION)
    selected_ids = {row["source_id"] for row in selection_rows if row["selection_status"] == "selected"}
    write_queue(register_rows, selected_ids)
    decisions = write_template(register_rows, selected_ids)
    summary = validate_workflow(register_rows, selected_ids, decisions)
    VALIDATION_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not summary["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
