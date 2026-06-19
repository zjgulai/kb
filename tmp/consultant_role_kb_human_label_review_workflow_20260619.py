#!/usr/bin/env python3
"""Generate and validate the consultant-agent human label review workflow.

This script creates a review queue and a pending decision template from the
machine-generated label seed. It does not approve labels, call providers, or
write into a live KB.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl"
SCHEMA_PATH = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-review.schema-20260619.json"
QUEUE_PATH = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-review.queue-20260619.csv"
TEMPLATE_PATH = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
VALIDATION_PATH = ROOT / "tmp/consultant-role-kb-human-label-review-workflow-validation-20260619.json"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def seed_proposed(row: dict[str, Any]) -> dict[str, Any]:
    candidate = row.get("gold_candidate") or {}
    expectation = row.get("retrieval_expectation") or {}
    return {
        "source_id": candidate.get("source_id"),
        "source_title": candidate.get("source_title"),
        "card_id": candidate.get("card_id"),
        "locator": candidate.get("locator"),
        "locator_type": candidate.get("locator_type"),
        "evidence_grade": candidate.get("evidence_grade"),
        "license_status": candidate.get("license_status"),
        "workspace": row["workspace"],
        "expected_refusal": bool(expectation.get("expected_refusal")),
    }


def queue_row(row: dict[str, Any]) -> dict[str, Any]:
    proposed = seed_proposed(row)
    if row["label_type"] == "locator_gold_candidate":
        options = "approve|override|reject|needs_discussion|pending"
        instruction = "Verify source_id, card_id, locator, evidence/license boundaries, then decide."
    else:
        options = "approve|reject|needs_discussion|pending"
        instruction = "Verify no-source refusal policy and workspace boundary; do not add a source citation."
    return {
        "review_item_id": f"HGREVIEW-{row['eval_id']}-20260619",
        "label_id": row["label_id"],
        "eval_id": row["eval_id"],
        "label_type": row["label_type"],
        "category": row["category"],
        "workspace": row["workspace"],
        "question": row["question"],
        "seed_confidence": row["seed_confidence"],
        "must_cite_source": str(row["must_cite_source"]).lower(),
        "expected_refusal": str(proposed["expected_refusal"]).lower(),
        "proposed_source_id": proposed["source_id"] or "",
        "proposed_source_title": proposed["source_title"] or "",
        "proposed_card_id": proposed["card_id"] or "",
        "proposed_locator": proposed["locator"] or "",
        "proposed_locator_type": proposed["locator_type"] or "",
        "proposed_evidence_grade": proposed["evidence_grade"] or "",
        "proposed_license_status": proposed["license_status"] or "",
        "blocked_actions_expected": "|".join(row.get("blocked_actions_expected") or []),
        "review_action_options": options,
        "review_instruction": instruction,
        "current_decision": "pending",
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
    }


def decision_template(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": f"HGREVIEW-{row['eval_id']}-20260619",
        "label_id": row["label_id"],
        "eval_id": row["eval_id"],
        "label_type": row["label_type"],
        "decision": "pending",
        "reviewer": None,
        "reviewed_at": None,
        "review_notes": None,
        "approved_source_id": None,
        "approved_card_id": None,
        "approved_locator": None,
        "approved_locator_type": None,
        "approved_no_source_policy": False,
        "proposed": seed_proposed(row),
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "manual review required before treating as gold",
    }


def write_queue(rows: list[dict[str, Any]]) -> None:
    fieldnames = list(queue_row(rows[0]).keys())
    with QUEUE_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(queue_row(row))


def write_template(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions = [decision_template(row) for row in rows]
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
    if isinstance(value, str):
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            failures.append(f"{name}: above maxLength")
        if "pattern" in schema and not re.match(schema["pattern"], value):
            failures.append(f"{name}: pattern mismatch")
    if isinstance(value, dict):
        failures.extend(validate_object(name, value, schema))
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


def validate_decision_logic(decision: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    state = decision["decision"]
    label_type = decision["label_type"]
    if state == "pending":
        if decision["reviewer"] or decision["reviewed_at"]:
            failures.append("pending decision must not include reviewer approval fields")
        if any(decision[field] for field in ["approved_source_id", "approved_card_id", "approved_locator"]):
            failures.append("pending decision must not include approved locator fields")
        if decision["approved_no_source_policy"]:
            failures.append("pending decision must not approve no-source policy")
        return failures

    if not decision["reviewer"] or not decision["reviewed_at"]:
        failures.append("non-pending decision requires reviewer and reviewed_at")
    if state in {"reject", "needs_discussion"} and not decision["review_notes"]:
        failures.append(f"{state} decision requires review_notes")
    if state in {"approve", "override"} and label_type == "locator_gold_candidate":
        for field in ["approved_source_id", "approved_card_id", "approved_locator", "approved_locator_type"]:
            if not decision[field]:
                failures.append(f"{state} locator decision requires {field}")
        if decision["approved_no_source_policy"]:
            failures.append("locator decision must not approve no-source policy")
    if state == "approve" and label_type == "refusal_policy_no_source":
        if not decision["approved_no_source_policy"]:
            failures.append("refusal approval requires approved_no_source_policy=true")
        for field in ["approved_source_id", "approved_card_id", "approved_locator", "approved_locator_type"]:
            if decision[field]:
                failures.append(f"refusal approval must not include {field}")
    return failures


def validate_workflow(seed_rows: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    failures: list[dict[str, Any]] = []
    seed_label_ids = [row["label_id"] for row in seed_rows]
    decision_label_ids = [row["label_id"] for row in decisions]
    if len(seed_label_ids) != len(set(seed_label_ids)):
        failures.append({"scope": "seed", "failure": "duplicate seed label_id"})
    if len(decision_label_ids) != len(set(decision_label_ids)):
        failures.append({"scope": "decision", "failure": "duplicate decision label_id"})
    if set(seed_label_ids) != set(decision_label_ids):
        failures.append({"scope": "decision", "failure": "decision label_id set does not match seed"})

    for decision in decisions:
        row_failures = validate_object("decision", decision, schema)
        row_failures.extend(validate_decision_logic(decision))
        if row_failures:
            failures.append({"label_id": decision.get("label_id"), "failures": row_failures})

    label_type_counts = Counter(row["label_type"] for row in seed_rows)
    decision_counts = Counter(row["decision"] for row in decisions)
    return {
        "ok": not failures,
        "seed": str(SEED_PATH.relative_to(ROOT)),
        "queue": str(QUEUE_PATH.relative_to(ROOT)),
        "decision_template": str(TEMPLATE_PATH.relative_to(ROOT)),
        "schema": str(SCHEMA_PATH.relative_to(ROOT)),
        "seed_label_count": len(seed_rows),
        "review_queue_count": sum(1 for _ in csv.DictReader(QUEUE_PATH.open(encoding="utf-8"))),
        "decision_template_count": len(decisions),
        "locator_candidate_count": label_type_counts["locator_gold_candidate"],
        "policy_refusal_count": label_type_counts["refusal_policy_no_source"],
        "pending_decision_count": decision_counts["pending"],
        "approved_decision_count": decision_counts["approve"] + decision_counts["override"],
        "failure_count": sum(len(item.get("failures", [item.get("failure")])) for item in failures),
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "manual review required before treating as gold",
        "failures": failures,
    }


def main() -> None:
    seed_rows = read_jsonl(SEED_PATH)
    write_queue(seed_rows)
    decisions = write_template(seed_rows)
    summary = validate_workflow(seed_rows, decisions)
    VALIDATION_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not summary["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
