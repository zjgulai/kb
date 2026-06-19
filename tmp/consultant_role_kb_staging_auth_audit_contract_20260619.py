#!/usr/bin/env python3
"""Validate the draft staging auth/audit contract for consultant-agent.

This validator is local-only. It does not call a provider, does not run a
server, does not write to a live KB, and does not include raw source text in
audit events.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "shared/audit/consultant-agent/staging-audit-event.schema-20260619.json"
OUT_PATH = ROOT / "tmp/consultant-role-kb-staging-auth-audit-contract-validation-20260619.json"
EVENTS_PATH = ROOT / "tmp/consultant-role-kb-staging-auth-audit-sample-events-20260619.jsonl"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0


def sha256(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def now_ts() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def base_event(**overrides: Any) -> dict[str, Any]:
    event: dict[str, Any] = {
        "event_id": "audit_20260619T081500Z_contract01",
        "ts": now_ts(),
        "request_id": "kb-staging-smoke-0001",
        "actor_id_hash": sha256("reviewer:li-liang"),
        "actor_role": "reviewer",
        "agent_id": "consultant-agent",
        "workspace": "consultant-p1",
        "endpoint": "/retrieve",
        "retrieval_mode": "local_bge_vector_plus_deterministic_rerank",
        "query_sha256": sha256("如何搭建 CDD 的 revenue quality 分析框架？"),
        "query_length": len("如何搭建 CDD 的 revenue quality 分析框架？"),
        "eval_id": "CONSULT-EVAL-016",
        "result_count": 1,
        "result_refs": [
            {
                "source_id": "SRC-CONSULT-001",
                "card_id": "SRC-CONSULT-001_card_0001",
                "locator": "slide:3",
                "evidence_grade": "C",
                "license_status": "pending_legal_review",
            }
        ],
        "decision": "allowed",
        "blocked_reason": None,
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "source_text_returned": False,
    }
    event.update(overrides)
    return event


def build_events() -> list[dict[str, Any]]:
    allowed = base_event()
    denied = base_event(
        event_id="audit_20260619T081501Z_contract02",
        request_id="kb-staging-smoke-0002",
        endpoint="/retrieve",
        retrieval_mode="none_policy_refusal",
        query_sha256=sha256("forbidden workspace smoke"),
        query_length=len("forbidden workspace smoke"),
        eval_id="ADHOC",
        result_count=0,
        result_refs=[],
        decision="denied",
        blocked_reason="workspace_or_agent_forbidden",
    )
    return [allowed, denied]


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
        if "minLength" in schema and len(value) < schema["minLength"]:
            failures.append(f"{name}: below minLength")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            failures.append(f"{name}: above maxLength")
        if "pattern" in schema and not re.match(schema["pattern"], value):
            failures.append(f"{name}: pattern mismatch")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            failures.append(f"{name}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            failures.append(f"{name}: above maximum")
    if isinstance(value, list):
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            failures.append(f"{name}: above maxItems")
        item_schema = schema.get("items")
        if item_schema:
            for idx, item in enumerate(value):
                failures.extend(validate_object(f"{name}[{idx}]", item, item_schema))
    return failures


def validate_object(name: str, event: Any, schema: dict[str, Any]) -> list[str]:
    if not isinstance(event, dict):
        return [f"{name}: expected object"]
    failures: list[str] = []
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    missing = sorted(required.difference(event))
    failures.extend(f"{name}: missing required field {field}" for field in missing)
    if schema.get("additionalProperties") is False:
        extras = sorted(set(event).difference(properties))
        failures.extend(f"{name}: unexpected field {field}" for field in extras)
    for field, value in event.items():
        if field in properties:
            failures.extend(validate_value(f"{name}.{field}", value, properties[field]))
    return failures


def governance_checks(event: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    serialized = json.dumps(event, ensure_ascii=False)
    forbidden_terms = [
        "如何搭建 CDD 的 revenue quality 分析框架？",
        "forbidden workspace smoke",
        "raw_source_text",
        "Authorization",
        "Bearer ",
        "password",
        "private key",
        "token=",
    ]
    for term in forbidden_terms:
        if term in serialized:
            failures.append(f"forbidden raw or secret term leaked: {term}")
    if event["provider_call_count"] != 0:
        failures.append("provider_call_count must remain 0")
    if event["live_kb_write_count"] != 0:
        failures.append("live_kb_write_count must remain 0")
    if event["source_text_returned"] is not False:
        failures.append("source_text_returned must be false")
    if not str(event["actor_id_hash"]).startswith("sha256:"):
        failures.append("actor_id_hash must be hashed")
    if not str(event["query_sha256"]).startswith("sha256:"):
        failures.append("query_sha256 must be hashed")
    if event["decision"] == "denied" and not event.get("blocked_reason"):
        failures.append("denied event must include blocked_reason")
    if event["decision"] == "allowed" and event["result_count"] != len(event["result_refs"]):
        failures.append("allowed event result_count must match result_refs length")
    return failures


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    events = build_events()
    rows = []
    failure_count = 0
    for event in events:
        failures = validate_object("event", event, schema)
        failures.extend(governance_checks(event))
        rows.append(
            {
                "event_id": event["event_id"],
                "decision": event["decision"],
                "pass": not failures,
                "failures": failures,
            }
        )
        failure_count += len(failures)

    EVENTS_PATH.write_text(
        "\n".join(json.dumps(event, ensure_ascii=False, sort_keys=True) for event in events) + "\n",
        encoding="utf-8",
    )
    summary = {
        "ok": failure_count == 0,
        "schema": str(SCHEMA_PATH.relative_to(ROOT)),
        "sample_events": str(EVENTS_PATH.relative_to(ROOT)),
        "event_count": len(events),
        "allowed_event_count": sum(1 for row in rows if row["decision"] == "allowed"),
        "denied_event_count": sum(1 for row in rows if row["decision"] == "denied"),
        "failure_count": failure_count,
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "source_text_returned": False,
        "results": rows,
    }
    OUT_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if failure_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
