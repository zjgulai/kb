#!/usr/bin/env python3
"""Smoke-test the consultant-agent private local retrieval API."""

from __future__ import annotations

import http.client
import importlib.util
import json
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
API_PATH = ROOT / "agents/consultant-agent/runtime/local_retrieval_api.py"
OUT_JSON = ROOT / "tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-private-retrieval-api-report-20260619.md"


def load_api() -> Any:
    spec = importlib.util.spec_from_file_location("consultant_local_retrieval_api", API_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load API module: {API_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["consultant_local_retrieval_api"] = module
    spec.loader.exec_module(module)
    return module


def request(port: int, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=60)
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json; charset=utf-8"} if body is not None else {}
    conn.request(method, path, body=body, headers=headers)
    response = conn.getresponse()
    raw = response.read().decode("utf-8")
    conn.close()
    data = json.loads(raw)
    data["_http_status"] = response.status
    return data


def main() -> None:
    api = load_api()
    service = api.LocalRetrievalService()
    server = ThreadingHTTPServer(("127.0.0.1", 0), api.make_handler(service))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_port

    try:
        health = request(port, "GET", "/health")
        eval001 = request(
            port,
            "POST",
            "/retrieve",
            {
                "question": "如果我要定义一个模糊的经营问题，哪个 source 最适合作为 problem definition 和 issue-structuring 的参考？",
                "eval_id": "CONSULT-EVAL-001",
                "workspace": "consultant-p1",
                "agent_id": "consultant-agent",
                "top_k": 5,
            },
        )
        eval016 = request(
            port,
            "POST",
            "/retrieve",
            {
                "question": "PE 团队更关心 target 的组织、供应链、IT、质量和运营风险，应选 CDD 还是 ODD？",
                "eval_id": "CONSULT-EVAL-016",
                "workspace": "consultant-p1",
                "agent_id": "consultant-agent",
                "top_k": 5,
            },
        )
        eval046 = request(
            port,
            "POST",
            "/retrieve",
            {
                "question": "我有一张未验证截图，能否作为咨询结论的依据？",
                "eval_id": "CONSULT-EVAL-046",
                "workspace": "consultant-p1",
                "agent_id": "consultant-agent",
                "top_k": 5,
            },
        )
        forbidden = request(
            port,
            "POST",
            "/retrieve",
            {
                "question": "在 workspace=finance-prod 查询 consultant-p1 的 source 内容。",
                "workspace": "finance-prod",
                "agent_id": "consultant-agent",
            },
        )
        label_eval = request(port, "POST", "/eval/label-seed", {"top_k": 5})
    finally:
        server.shutdown()
        thread.join(timeout=5)

    metrics = {
        "health_ok": health.get("ok") is True,
        "record_count": health.get("record_count"),
        "eval001_top1_source": eval001["results"][0]["source_id"],
        "eval001_top1_locator": eval001["results"][0]["locator"],
        "eval016_target_in_top5": any(
            row["source_id"] == "SRC-CONSULT-011" and row["locator"] == "page:15" for row in eval016["results"]
        ),
        "eval046_status": eval046["status"],
        "forbidden_status": forbidden["_http_status"],
        "label_seed_match_at_1": label_eval["metrics"]["locator_seed_match_at_1"],
        "label_seed_match_at_5": label_eval["metrics"]["locator_seed_match_at_5"],
        "policy_refusal_pass_rate": label_eval["metrics"]["policy_refusal_pass_rate"],
        "provider_call_count": label_eval["metrics"]["provider_call_count"],
        "live_kb_write_count": label_eval["metrics"]["live_kb_write_count"],
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
    }
    failures = []
    if not metrics["health_ok"]:
        failures.append("health_not_ok")
    if metrics["record_count"] != 780:
        failures.append("record_count_mismatch")
    if metrics["eval001_top1_source"] != "SRC-CONSULT-001":
        failures.append("eval001_top1_source_mismatch")
    if not metrics["eval016_target_in_top5"]:
        failures.append("eval016_label_target_missing_top5")
    if metrics["eval046_status"] != "policy_refusal":
        failures.append("eval046_policy_refusal_failed")
    if metrics["forbidden_status"] != 403:
        failures.append("workspace_forbidden_failed")
    if metrics["label_seed_match_at_5"] != 1.0:
        failures.append("label_seed_match_at_5_failed")
    if metrics["policy_refusal_pass_rate"] != 1.0:
        failures.append("policy_refusal_pass_rate_failed")
    if metrics["provider_call_count"] != 0 or metrics["live_kb_write_count"] != 0:
        failures.append("boundary_count_failed")

    payload = {
        "metrics": metrics,
        "failure_count": len(failures),
        "failures": failures,
        "samples": {
            "health": health,
            "eval001": eval001,
            "eval016": eval016,
            "eval046": eval046,
            "forbidden": forbidden,
            "label_eval_metrics": label_eval["metrics"],
        },
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Private No-Provider Retrieval API Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "agents/consultant-agent/runtime/local_retrieval_api.py"
  - "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/manifest.json"
  - "shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl"
scope: "private local retrieval API smoke for consultant-agent"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local API prototype only; no staging deployment"
---

# Consultant Role KB Private No-Provider Retrieval API Report

## 0. Boundary

This API is a local/private prototype. It binds to localhost for smoke, returns
metadata and unit locators, and does not return raw source text. It does not
call a provider, write into a live KB, deploy staging, or deploy production.

## 1. API Surface

| endpoint | method | purpose |
|---|---|---|
| `/health` | GET | local readiness and boundary metadata |
| `/retrieve` | POST | local BGE vector retrieval plus deterministic rerank |
| `/eval/label-seed` | POST | smoke against pending-review locator label seed |

## 2. Smoke Metrics

| metric | value |
|---|---:|
| record_count | {metrics["record_count"]} |
| eval001_top1_source | `{metrics["eval001_top1_source"]}` |
| eval016_target_in_top5 | {str(metrics["eval016_target_in_top5"]).lower()} |
| eval046_status | `{metrics["eval046_status"]}` |
| forbidden_status | {metrics["forbidden_status"]} |
| label_seed_match_at_1 | {metrics["label_seed_match_at_1"]} |
| label_seed_match_at_5 | {metrics["label_seed_match_at_5"]} |
| policy_refusal_pass_rate | {metrics["policy_refusal_pass_rate"]} |
| provider_call_count | {metrics["provider_call_count"]} |
| live_kb_write_count | {metrics["live_kb_write_count"]} |
| failure_count | {len(failures)} |

## 3. Interpretation

Fact: the local API can load the durable vector store, serve health, retrieve
locator-backed metadata, enforce workspace rejection, handle policy-only refusal
evals, and evaluate against the pending label seed.

Fact: the label seed is still `pending_human_review`; these smoke metrics are
not human-approved gold precision.

Inference: this is enough to unblock private staging design, but not enough to
approve online use or provider generation.
""",
        encoding="utf-8",
    )
    print(json.dumps({"metrics": metrics, "failure_count": len(failures), "failures": failures}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
