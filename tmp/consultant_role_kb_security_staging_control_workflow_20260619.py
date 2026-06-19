#!/usr/bin/env python3
"""Generate and validate shared-staging security control decisions.

Boundary: local governance artifact only. This does not configure secrets,
approve shared staging, deploy a service, call a provider, or ingest into a live
KB.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "shared/governance/consultant-agent/security-staging-control-decision.schema-20260619.json"
QUEUE_PATH = ROOT / "shared/governance/consultant-agent/security-staging-control-review.queue-20260619.csv"
TEMPLATE_PATH = ROOT / "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"
VALIDATION_PATH = ROOT / "tmp/consultant-role-kb-security-staging-control-validation-20260619.json"
REPORT_PATH = ROOT / "drafts/analysis/consultant-role-kb-security-staging-control-workflow-20260619.md"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0

CONTROL_ROWS = [
    {
        "control_id": "SEC-STG-001",
        "control_title": "Private ingress and network boundary approved",
        "control_area": "network_boundary",
        "external_config_required": True,
        "required_evidence": "approved VPN, internal reverse proxy, or localhost tunnel boundary; no public anonymous endpoint",
        "blocked_actions": [
            "public_anonymous_endpoint",
            "shared_staging_without_private_ingress_approval",
        ],
        "conditions": [
            "bind remains localhost unless private ingress is approved",
            "public internet exposure requires separate approval",
        ],
    },
    {
        "control_id": "SEC-STG-002",
        "control_title": "External secret storage approved",
        "control_area": "secret_storage",
        "external_config_required": True,
        "required_evidence": "external secret store or local operator secret file outside the repository",
        "blocked_actions": [
            "commit_raw_secret_values",
            "commit_private_keys_or_passwords",
        ],
        "conditions": [
            "repository stores only redacted status and hash evidence",
            "raw credential material remains outside Git",
        ],
    },
    {
        "control_id": "SEC-STG-003",
        "control_title": "Bearer-token hash configured outside Git",
        "control_area": "auth",
        "external_config_required": True,
        "required_evidence": "KB_STAGING_AUTH_TOKEN_SHA256 configured in approved external runtime environment",
        "blocked_actions": [
            "commit_raw_bearer_token",
            "run_shared_staging_without_token_hash",
        ],
        "conditions": [
            "preflight sees token hash as configured without logging the value",
            "token rotation path is documented before pilot access",
        ],
    },
    {
        "control_id": "SEC-STG-004",
        "control_title": "Append-only audit path configured outside repository",
        "control_area": "audit_storage",
        "external_config_required": True,
        "required_evidence": "KB_STAGING_AUDIT_PATH points outside the repository with writable parent",
        "blocked_actions": [
            "write_shared_staging_audit_logs_inside_repo",
            "run_shared_staging_without_audit_path",
        ],
        "conditions": [
            "audit JSONL path resolves outside /Users/pray/project/kb",
            "audit events must not contain raw source text or raw credential material",
        ],
    },
    {
        "control_id": "SEC-STG-005",
        "control_title": "Audit retention and access policy approved",
        "control_area": "audit_retention",
        "external_config_required": False,
        "required_evidence": "retention period, access scope, and incident preservation rule recorded",
        "blocked_actions": [
            "delete_audit_logs_as_rollback",
            "share_audit_logs_without_access_review",
        ],
        "conditions": [
            "rollback preserves audit logs",
            "audit access is limited to approved reviewers and operators",
        ],
    },
    {
        "control_id": "SEC-STG-006",
        "control_title": "Rate limiting configured at private ingress or middleware",
        "control_area": "rate_limit",
        "external_config_required": True,
        "required_evidence": "KB_STAGING_RATE_LIMIT_CONFIGURED asserted after operator config",
        "blocked_actions": [
            "run_shared_staging_without_rate_limit",
            "load_test_shared_staging_without_approval",
        ],
        "conditions": [
            "rate limit is enforced before external reviewer access",
            "load or abuse tests require separate approval",
        ],
    },
    {
        "control_id": "SEC-STG-007",
        "control_title": "Rollback owner and stop procedure recorded",
        "control_area": "rollback",
        "external_config_required": True,
        "required_evidence": "KB_STAGING_ROLLBACK_OWNER recorded externally and runbook stop procedure accepted",
        "blocked_actions": [
            "run_shared_staging_without_rollback_owner",
            "delete_audit_logs_during_rollback",
        ],
        "conditions": [
            "rollback disables ingress before stopping the service",
            "private contact details are not stored in repository artifacts",
        ],
    },
    {
        "control_id": "SEC-STG-008",
        "control_title": "Operator roster and RBAC scope approved",
        "control_area": "rbac",
        "external_config_required": False,
        "required_evidence": "approved reviewer/operator roles for retrieval_reader, reviewer, and admin scopes",
        "blocked_actions": [
            "grant_admin_without_review",
            "bypass_role_gated_endpoints",
        ],
        "conditions": [
            "shared pilot users receive least-privilege roles",
            "role changes are recorded before access is granted",
        ],
    },
]


def queue_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "review_item_id": f"{row['control_id']}-20260619",
        "control_id": row["control_id"],
        "control_title": row["control_title"],
        "control_area": row["control_area"],
        "external_config_required": str(row["external_config_required"]).lower(),
        "required_evidence": row["required_evidence"],
        "blocked_actions": "|".join(row["blocked_actions"]),
        "conditions": "|".join(row["conditions"]),
        "review_action_options": "approved|rejected|needs_discussion|pending_review",
        "current_decision": "pending_review",
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
    }


def decision_template(row: dict[str, Any]) -> dict[str, Any]:
    external_status = "not_configured" if row["external_config_required"] else "not_required"
    return {
        "decision_id": f"{row['control_id']}-20260619",
        "control_id": row["control_id"],
        "control_title": row["control_title"],
        "control_area": row["control_area"],
        "decision": "pending_review",
        "security_reviewer": None,
        "ops_reviewer": None,
        "reviewed_at": None,
        "review_notes": None,
        "evidence_uri": None,
        "external_config_required": row["external_config_required"],
        "external_config_status": external_status,
        "permitted_actions": [],
        "blocked_actions": row["blocked_actions"],
        "conditions": row["conditions"],
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "security and operations approval required before shared staging",
        "secret_redaction_boundary": "do not store secret values, raw tokens, passwords, private keys, or private contact details in this repository",
    }


def write_queue(rows: list[dict[str, Any]]) -> None:
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(queue_row(rows[0]).keys())
    with QUEUE_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(queue_row(row))


def write_template(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions = [decision_template(row) for row in rows]
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
        if "minLength" in schema and len(value) < schema["minLength"]:
            failures.append(f"{name}: below minLength")
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
        if row["security_reviewer"] or row["ops_reviewer"] or row["reviewed_at"] or row["evidence_uri"]:
            failures.append("pending_review must not include reviewers, reviewed_at, or evidence_uri")
        if row["permitted_actions"]:
            failures.append("pending_review must not include permitted_actions")
        if row["external_config_required"] and row["external_config_status"] != "not_configured":
            failures.append("pending required external config must remain not_configured")
        if not row["external_config_required"] and row["external_config_status"] != "not_required":
            failures.append("pending non-external control must remain not_required")
        return failures

    if not row["security_reviewer"] or not row["ops_reviewer"] or not row["reviewed_at"]:
        failures.append("non-pending decision requires security/ops reviewers and reviewed_at")
    if not row["review_notes"] or not row["evidence_uri"]:
        failures.append("non-pending decision requires review_notes and evidence_uri")
    if decision == "approved":
        if row["external_config_required"] and row["external_config_status"] != "configured_externally":
            failures.append("approved external control requires configured_externally")
        if not row["permitted_actions"]:
            failures.append("approved control requires at least one permitted action")
    if decision in {"rejected", "needs_discussion"} and row["permitted_actions"]:
        failures.append(f"{decision} must not include permitted_actions")
    return failures


def contains_secret_like_value(value: Any) -> bool:
    if isinstance(value, dict):
        return any(contains_secret_like_value(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_secret_like_value(item) for item in value)
    if not isinstance(value, str):
        return False
    if len(value) < 24:
        return False
    if re.search(r"(-----BEGIN|AKIA|sk-[A-Za-z0-9]|xox[baprs]-)", value):
        return True
    if re.fullmatch(r"[A-Za-z0-9+/=]{40,}", value) and re.search(r"\d", value):
        return True
    return False


def validate_workflow(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    failures: list[dict[str, Any]] = []
    control_ids = [row["control_id"] for row in decisions]
    if len(control_ids) != len(set(control_ids)):
        failures.append({"scope": "decision", "failure": "duplicate control_id"})
    if set(control_ids) != {row["control_id"] for row in CONTROL_ROWS}:
        failures.append({"scope": "decision", "failure": "control_id set does not match required control set"})

    approved_count = 0
    configured_external_count = 0
    secret_value_count = 0
    for row in decisions:
        row_failures = validate_object("decision", row, schema)
        row_failures.extend(validate_decision_logic(row))
        if row["decision"] == "approved":
            approved_count += 1
        if row["external_config_status"] == "configured_externally":
            configured_external_count += 1
        if contains_secret_like_value(row):
            secret_value_count += 1
        if row_failures:
            failures.append({"control_id": row.get("control_id"), "failures": row_failures})

    decision_counts = Counter(row["decision"] for row in decisions)
    required_external_controls = sum(1 for row in decisions if row["external_config_required"])
    ready = approved_count == len(CONTROL_ROWS) and not failures
    failure_count = 0
    for item in failures:
        failure_count += len(item.get("failures", [item.get("failure")]))
    return {
        "ok": not failures,
        "shared_staging_security_controls_ready": ready,
        "schema": str(SCHEMA_PATH.relative_to(ROOT)),
        "queue": str(QUEUE_PATH.relative_to(ROOT)),
        "decision_template": str(TEMPLATE_PATH.relative_to(ROOT)),
        "control_count": len(CONTROL_ROWS),
        "decision_count": len(decisions),
        "required_external_control_count": required_external_controls,
        "pending_review_count": decision_counts["pending_review"],
        "approved_control_count": approved_count,
        "configured_external_control_count": configured_external_count,
        "rejected_count": decision_counts["rejected"],
        "needs_discussion_count": decision_counts["needs_discussion"],
        "secret_like_value_count": secret_value_count,
        "failure_count": failure_count,
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "failures": failures,
    }


def write_report(validation: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        f"""---
title: "Consultant Role KB Security Staging Control Workflow"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md"
  - "drafts/analysis/consultant-role-kb-shared-staging-readiness-preflight-20260619.md"
  - "shared/governance/consultant-agent/security-staging-control-decision.schema-20260619.json"
scope: "structured security and operations decision intake for consultant-agent shared staging"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "decision workflow only; no security approval or shared staging deployment"
---

# Consultant Role KB Security Staging Control Workflow

## 0. Boundary

This workflow creates a review queue, pending decision template, and validation
summary for shared-staging security controls. It does not configure secrets,
approve staging, deploy shared staging, call a provider, or ingest into a live
KB.

## 1. Validation Summary

| metric | value |
|---|---:|
| control_count | {validation["control_count"]} |
| decision_count | {validation["decision_count"]} |
| required_external_control_count | {validation["required_external_control_count"]} |
| pending_review_count | {validation["pending_review_count"]} |
| approved_control_count | {validation["approved_control_count"]} |
| configured_external_control_count | {validation["configured_external_control_count"]} |
| shared_staging_security_controls_ready | {str(validation["shared_staging_security_controls_ready"]).lower()} |
| secret_like_value_count | {validation["secret_like_value_count"]} |
| failure_count | {validation["failure_count"]} |
| provider_call_count | {validation["provider_call_count"]} |
| live_kb_write_count | {validation["live_kb_write_count"]} |

## 2. Artifacts

- Schema: `shared/governance/consultant-agent/security-staging-control-decision.schema-20260619.json`
- Queue: `shared/governance/consultant-agent/security-staging-control-review.queue-20260619.csv`
- Decision template: `shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl`
- Validation: `tmp/consultant-role-kb-security-staging-control-validation-20260619.json`

## 3. Required Control Areas

| control | area | pending evidence |
|---|---|---|
| `SEC-STG-001` | network_boundary | private ingress and network boundary approval |
| `SEC-STG-002` | secret_storage | external secret storage approval |
| `SEC-STG-003` | auth | bearer-token hash configured outside Git |
| `SEC-STG-004` | audit_storage | append-only audit path outside repository |
| `SEC-STG-005` | audit_retention | audit retention and access policy |
| `SEC-STG-006` | rate_limit | private ingress or middleware rate limit |
| `SEC-STG-007` | rollback | rollback owner and stop procedure |
| `SEC-STG-008` | rbac | operator roster and RBAC scope |

## 4. Interpretation

Fact: all required security controls now have pending decision rows and the
template validates with `failure_count = 0`.

Fact: no control has been approved, no external configuration has been
recorded, and shared-staging security readiness remains false.

Boundary: the decision template must not contain raw secret values, bearer
tokens, passwords, private keys, or private contact details.
""",
        encoding="utf-8",
    )


def main() -> None:
    write_queue(CONTROL_ROWS)
    decisions = write_template(CONTROL_ROWS)
    validation = validate_workflow(decisions)
    VALIDATION_PATH.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(validation)
    print(
        json.dumps(
            {
                "shared_staging_security_controls_ready": validation["shared_staging_security_controls_ready"],
                "control_count": validation["control_count"],
                "failure_count": validation["failure_count"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
