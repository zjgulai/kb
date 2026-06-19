#!/usr/bin/env python3
"""Smoke-test local staging auth/audit harness for consultant-agent."""

from __future__ import annotations

import hashlib
import http.client
import importlib.util
import json
import secrets
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = ROOT / "agents/consultant-agent/runtime/staging_auth_audit.py"
CONTRACT_PATH = ROOT / "tmp/consultant_role_kb_staging_auth_audit_contract_20260619.py"
OUT_JSON = ROOT / "tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json"
AUDIT_JSONL = ROOT / "tmp/consultant-role-kb-local-staging-audit-events-20260619.jsonl"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-local-staging-auth-audit-smoke-report-20260619.md"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    sys.path.insert(0, str(path.parent))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def request(
    port: int,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=90)
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request_headers = {"Content-Type": "application/json; charset=utf-8"} if body is not None else {}
    request_headers.update(headers or {})
    conn.request(method, path, body=body, headers=request_headers)
    response = conn.getresponse()
    raw = response.read().decode("utf-8")
    conn.close()
    data = json.loads(raw)
    data["_http_status"] = response.status
    return data


def auth_headers(token: str, role: str = "reviewer", request_id: str = "kb-staging-smoke-0001") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "X-KB-Agent": "consultant-agent",
        "X-KB-Workspace": "consultant-p1",
        "X-KB-Reviewer": "local-smoke-reviewer",
        "X-KB-Request-Id": request_id,
        "X-KB-Role": role,
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    harness = load_module("consultant_staging_auth_audit", HARNESS_PATH)
    contract = load_module("consultant_staging_contract_validator", CONTRACT_PATH)
    token = secrets.token_urlsafe(24)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    if AUDIT_JSONL.exists():
        AUDIT_JSONL.unlink()

    service = harness.StagingAuthAuditService(
        config=harness.StagingAuthConfig(token_sha256=token_hash, audit_path=AUDIT_JSONL)
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), harness.make_staging_handler(service))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_port

    q_allowed = "如果我要定义一个模糊的经营问题，哪个 source 最适合作为 problem definition 和 issue-structuring 的参考？"
    q_refusal = "我有一张未验证截图，能否作为咨询结论的依据？"
    q_denied = "缺少 bearer token 的 staging smoke 请求"

    try:
        health = request(port, "GET", "/health")
        allowed = request(
            port,
            "POST",
            "/retrieve",
            {
                "question": q_allowed,
                "eval_id": "CONSULT-EVAL-001",
                "top_k": 5,
            },
            auth_headers(token, role="reviewer", request_id="kb-staging-smoke-0001"),
        )
        policy_refusal = request(
            port,
            "POST",
            "/retrieve",
            {
                "question": q_refusal,
                "eval_id": "CONSULT-EVAL-046",
                "top_k": 5,
            },
            auth_headers(token, role="reviewer", request_id="kb-staging-smoke-0002"),
        )
        missing_token = request(
            port,
            "POST",
            "/retrieve",
            {
                "question": q_denied,
                "eval_id": "ADHOC",
            },
            {
                key: value
                for key, value in auth_headers(token, role="reviewer", request_id="kb-staging-smoke-0003").items()
                if key != "Authorization"
            },
        )
        rbac_denied = request(
            port,
            "POST",
            "/eval/label-seed",
            {"top_k": 5},
            auth_headers(token, role="retrieval_reader", request_id="kb-staging-smoke-0004"),
        )
        label_eval = request(
            port,
            "POST",
            "/eval/label-seed",
            {"top_k": 5},
            auth_headers(token, role="reviewer", request_id="kb-staging-smoke-0005"),
        )
    finally:
        server.shutdown()
        thread.join(timeout=5)

    events = read_jsonl(AUDIT_JSONL)
    schema = json.loads(contract.SCHEMA_PATH.read_text(encoding="utf-8"))
    event_failures = []
    for event in events:
        failures = contract.validate_object("event", event, schema)
        failures.extend(contract.governance_checks(event))
        event_failures.extend(f"{event['event_id']}: {failure}" for failure in failures)

    serialized_events = AUDIT_JSONL.read_text(encoding="utf-8")
    forbidden_terms = [token, q_allowed, q_refusal, q_denied, "Bearer ", "Authorization"]
    leakage_failures = [term for term in forbidden_terms if term and term in serialized_events]
    event_decisions = {}
    for event in events:
        event_decisions[event["decision"]] = event_decisions.get(event["decision"], 0) + 1

    metrics = {
        "health_ok": health.get("ok") is True,
        "record_count": health.get("record_count"),
        "allowed_status": allowed.get("status"),
        "allowed_http_status": allowed["_http_status"],
        "allowed_result_count": len(allowed.get("results") or []),
        "policy_refusal_status": policy_refusal.get("status"),
        "policy_refusal_http_status": policy_refusal["_http_status"],
        "missing_token_status": missing_token["_http_status"],
        "rbac_denied_status": rbac_denied["_http_status"],
        "label_seed_match_at_5": label_eval["metrics"]["locator_seed_match_at_5"],
        "policy_refusal_pass_rate": label_eval["metrics"]["policy_refusal_pass_rate"],
        "audit_event_count": len(events),
        "allowed_event_count": event_decisions.get("allowed", 0),
        "denied_event_count": event_decisions.get("denied", 0),
        "policy_refusal_event_count": event_decisions.get("policy_refusal", 0),
        "audit_schema_failure_count": len(event_failures),
        "audit_forbidden_leak_count": len(leakage_failures),
        "provider_call_count": label_eval["metrics"]["provider_call_count"],
        "live_kb_write_count": label_eval["metrics"]["live_kb_write_count"],
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
    }
    failures = []
    if metrics["record_count"] != 800:
        failures.append("record_count_mismatch")
    if allowed["_http_status"] != 200 or allowed.get("status") != "retrieved":
        failures.append("allowed_retrieve_failed")
    if policy_refusal["_http_status"] != 200 or policy_refusal.get("status") != "policy_refusal":
        failures.append("policy_refusal_failed")
    if missing_token["_http_status"] != 401:
        failures.append("missing_token_not_401")
    if rbac_denied["_http_status"] != 403:
        failures.append("rbac_denied_not_403")
    if metrics["label_seed_match_at_5"] != 1.0:
        failures.append("label_seed_match_at_5_failed")
    if metrics["policy_refusal_pass_rate"] != 1.0:
        failures.append("policy_refusal_pass_rate_failed")
    if metrics["audit_event_count"] != 5:
        failures.append("audit_event_count_mismatch")
    if metrics["allowed_event_count"] != 2 or metrics["denied_event_count"] != 2 or metrics["policy_refusal_event_count"] != 1:
        failures.append("audit_decision_count_mismatch")
    if event_failures:
        failures.append("audit_schema_or_governance_failed")
    if leakage_failures:
        failures.append("audit_forbidden_leak_failed")
    if metrics["provider_call_count"] != 0 or metrics["live_kb_write_count"] != 0:
        failures.append("boundary_count_failed")

    payload = {
        "metrics": metrics,
        "failure_count": len(failures),
        "failures": failures,
        "audit_schema_failures": event_failures,
        "audit_forbidden_leaks": leakage_failures,
        "outputs": {
            "audit_events": str(AUDIT_JSONL.relative_to(ROOT)),
            "report": str(REPORT.relative_to(ROOT)),
        },
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Local Staging Auth Audit Smoke Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "agents/consultant-agent/runtime/staging_auth_audit.py"
  - "agents/consultant-agent/runtime/local_retrieval_api.py"
  - "shared/audit/consultant-agent/staging-audit-event.schema-20260619.json"
scope: "local smoke for consultant-agent staging auth and audit harness"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local validation only; no staging deployment"
---

# Consultant Role KB Local Staging Auth Audit Smoke Report

## 0. Boundary

This smoke runs a localhost-only staging harness. It does not deploy staging,
call a provider, write into a live KB, approve labels, or return raw source text.

## 1. Smoke Metrics

| metric | value |
|---|---:|
| record_count | {metrics["record_count"]} |
| allowed_http_status | {metrics["allowed_http_status"]} |
| policy_refusal_http_status | {metrics["policy_refusal_http_status"]} |
| missing_token_status | {metrics["missing_token_status"]} |
| rbac_denied_status | {metrics["rbac_denied_status"]} |
| label_seed_match_at_5 | {metrics["label_seed_match_at_5"]} |
| policy_refusal_pass_rate | {metrics["policy_refusal_pass_rate"]} |
| audit_event_count | {metrics["audit_event_count"]} |
| allowed_event_count | {metrics["allowed_event_count"]} |
| denied_event_count | {metrics["denied_event_count"]} |
| policy_refusal_event_count | {metrics["policy_refusal_event_count"]} |
| audit_schema_failure_count | {metrics["audit_schema_failure_count"]} |
| audit_forbidden_leak_count | {metrics["audit_forbidden_leak_count"]} |
| provider_call_count | {metrics["provider_call_count"]} |
| live_kb_write_count | {metrics["live_kb_write_count"]} |
| failure_count | {len(failures)} |

## 2. Interpretation

Fact: the local harness enforces bearer-token auth, role-gated endpoint access,
workspace/agent headers, and one audit event per protected request.

Fact: audit events validate against the staging audit schema and store only
hashed actor/query identifiers plus source/card/locator references.

Boundary: this is not a staging deployment and does not approve provider use,
live KB ingestion, source licensing, or human-gold label status.
""",
        encoding="utf-8",
    )
    print(json.dumps({"metrics": metrics, "failure_count": len(failures), "failures": failures}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
