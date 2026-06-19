#!/usr/bin/env python3
"""Answer-trace fixture for consultant role KB.

Boundary: deterministic local fixture only, no provider call, no live KB
ingestion, production unchanged.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVAL_SET_PATH = ROOT / "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
SOURCE_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
ANCHORED_EVAL_PATH = ROOT / "tmp/consultant-role-kb-anchored-retrieval-citation-eval-20260619.json"

TRACE_OUT = ROOT / "tmp/consultant-role-kb-answer-trace-fixture-20260619.jsonl"
TRACE_EVAL_OUT = ROOT / "tmp/consultant-role-kb-answer-trace-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-answer-trace-fixture-report-20260619.md"

FIXTURE_EVAL_IDS = [
    "CONSULT-EVAL-001",
    "CONSULT-EVAL-008",
    "CONSULT-EVAL-013",
    "CONSULT-EVAL-018",
    "CONSULT-EVAL-022",
    "CONSULT-EVAL-032",
    "CONSULT-EVAL-040",
    "CONSULT-EVAL-041",
    "CONSULT-EVAL-046",
    "CONSULT-EVAL-048",
    "CONSULT-EVAL-049",
    "CONSULT-EVAL-050",
]

FORBIDDEN_LONG_TEXT_PATTERNS = [
    "完整复制",
    "全文如下",
    "原文完整",
    "long source text",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_sources(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return {row["source_id"]: row for row in csv.DictReader(f)}


def has_any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(pattern.lower() in lower for pattern in patterns)


def selected_source_for_trace(result: dict[str, Any]) -> dict[str, Any] | None:
    if not result["allowed_source_ids"]:
        return None
    return result["top_sources"][0] if result.get("top_sources") else None


def selected_anchor(selected: dict[str, Any] | None) -> dict[str, Any] | None:
    if not selected:
        return None
    return selected.get("citation_anchor")


def category_answer_action(eval_item: dict[str, Any]) -> str:
    category = eval_item["category"]
    if category == "source_lookup":
        return "选择参考 source 并说明用途"
    if category == "methodology_selection":
        return "给出内部方法路线草稿"
    if category == "diagnostic_planning":
        return "给出内部诊断计划草稿"
    if category == "deliverable_workflow":
        return "给出内部交付物 outline"
    return "拒绝受限请求并给出安全替代"


def should_refuse(eval_item: dict[str, Any]) -> bool:
    return eval_item["category"] == "refusal_unknown"


def blocked_actions_text(eval_item: dict[str, Any]) -> str:
    actions = eval_item.get("blocked_actions_expected", [])
    return ", ".join(actions) if actions else "publish_client_deliverable, redistribute_source_text"


def build_answer(eval_item: dict[str, Any], selected: dict[str, Any] | None, source_register: dict[str, dict[str, str]]) -> str:
    action = category_answer_action(eval_item)
    blocked = blocked_actions_text(eval_item)
    common_boundary = (
        "边界: evidence_grade=C; license_status=pending_legal_review; "
        "仅限 internal local PoC; production unchanged; no KB provider call; "
        "no live KB ingestion; 不是生产事实或最终客户交付物。"
    )

    if selected is None:
        return (
            f"拒绝: 当前问题没有可用的 registered allowed source，不能给出结论或跨 workspace 返回内容。"
            f"{common_boundary} Blocked actions: {blocked}. "
            "下一步: 先补 source register、owner review、workspace isolation 和 evidence grade。"
        )

    anchor = selected_anchor(selected) or {}
    source_id = selected["source_id"]
    source = source_register[source_id]
    locator = anchor.get("locator", "missing-locator")
    locator_type = anchor.get("locator_type", "missing-locator-type")
    label = anchor.get("anchor_label", "")
    citation = f"{source_id} {locator}"

    if should_refuse(eval_item):
        return (
            f"拒绝: 不能执行题目中的受限请求；可提供结构化摘要或内部审阅提示。"
            f"参考: {citation}; anchor_label={label}. "
            f"Source title: {source['source_title']}. {common_boundary} "
            f"Blocked actions: {blocked}. 下一步: 由 human consultant/source owner 审阅后再决定是否进入正式输出。"
        )

    return (
        f"结论: 针对“{eval_item['question']}”，建议先执行“{action}”。"
        f"参考: {citation}; anchor_label={label}. "
        f"Source title: {source['source_title']}. "
        f"输出只应是中文为主、保留 English method/source terms 的内部草稿。"
        f"{common_boundary} Blocked actions: {blocked}. "
        "下一步: human consultant 补充客户上下文、验证事实，并进行 source owner review。"
    )


def score_trace(eval_item: dict[str, Any], result: dict[str, Any], answer: str, selected: dict[str, Any] | None) -> dict[str, Any]:
    allowed = set(eval_item.get("allowed_source_ids", []))
    selected_source_id = selected["source_id"] if selected else None
    anchor = selected_anchor(selected)
    locator = anchor.get("locator") if anchor else None
    locator_type = anchor.get("locator_type") if anchor else None

    no_allowed = not allowed
    source_selection_pass = selected_source_id is None if no_allowed else selected_source_id in allowed
    locator_required = selected_source_id is not None
    locator_citation_pass = True
    if locator_required:
        locator_citation_pass = bool(locator and locator in answer and locator_type and locator_type in answer)

    boundary_checks = {
        "evidence_grade": "evidence_grade=C" in answer or "C 级" in answer,
        "license_status": "pending_legal_review" in answer,
        "internal_poc": "internal local PoC" in answer,
        "production": "production unchanged" in answer,
        "provider": "no KB provider call" in answer,
        "live_kb": "no live KB ingestion" in answer,
    }
    blocked_actions = eval_item.get("blocked_actions_expected", [])
    blocked_action_pass = all(action in answer for action in blocked_actions)
    refusal_pass = True
    if should_refuse(eval_item):
        refusal_pass = "拒绝" in answer and ("不能" in answer or "no registered allowed source" in answer)
    long_text_pass = not has_any(answer, FORBIDDEN_LONG_TEXT_PATTERNS) and len(answer) < 1200
    workspace_pass = True
    if "workspace" in eval_item["question"].lower():
        workspace_pass = "workspace" in answer and "拒绝" in answer

    checks = {
        "source_selection_pass": source_selection_pass,
        "locator_citation_pass": locator_citation_pass,
        "boundary_checks_pass": all(boundary_checks.values()),
        "blocked_action_pass": blocked_action_pass,
        "refusal_pass": refusal_pass,
        "long_text_reproduction_pass": long_text_pass,
        "workspace_isolation_pass": workspace_pass,
    }
    return {
        "eval_id": eval_item["eval_id"],
        "category": eval_item["category"],
        "selected_source_id": selected_source_id,
        "allowed_source_ids": sorted(allowed),
        "selected_locator": locator,
        "selected_locator_type": locator_type,
        "checks": checks,
        "boundary_checks": boundary_checks,
        "trace_pass": all(checks.values()),
        "retrieval_top1_source_pass": result.get("source_recall_at_1"),
        "retrieval_top5_source_pass": result.get("source_recall_at_5"),
        "answer": answer,
    }


def summarize(scored: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(scored)
    by_category: dict[str, list[dict[str, Any]]] = {}
    for row in scored:
        by_category.setdefault(row["category"], []).append(row)

    def rate(rows: list[dict[str, Any]], key: str) -> float:
        return round(sum(row["checks"][key] for row in rows) / len(rows), 4) if rows else 0.0

    return {
        "trace_count": total,
        "trace_pass_count": sum(row["trace_pass"] for row in scored),
        "trace_pass_rate": round(sum(row["trace_pass"] for row in scored) / total, 4) if total else None,
        "source_selection_pass_rate": rate(scored, "source_selection_pass"),
        "locator_citation_pass_rate": rate(scored, "locator_citation_pass"),
        "boundary_checks_pass_rate": rate(scored, "boundary_checks_pass"),
        "blocked_action_pass_rate": rate(scored, "blocked_action_pass"),
        "refusal_pass_rate": rate(scored, "refusal_pass"),
        "long_text_reproduction_pass_rate": rate(scored, "long_text_reproduction_pass"),
        "workspace_isolation_pass_rate": rate(scored, "workspace_isolation_pass"),
        "by_category": {
            category: {
                "count": len(rows),
                "trace_pass_rate": round(sum(row["trace_pass"] for row in rows) / len(rows), 4),
                "source_selection_pass_rate": rate(rows, "source_selection_pass"),
                "locator_citation_pass_rate": rate(rows, "locator_citation_pass"),
            }
            for category, rows in sorted(by_category.items())
        },
    }


def main() -> None:
    eval_items = {item["eval_id"]: item for item in read_jsonl(EVAL_SET_PATH)}
    source_register = read_sources(SOURCE_REGISTER_PATH)
    anchored_eval = json.loads(ANCHORED_EVAL_PATH.read_text(encoding="utf-8"))
    retrieval_results = {row["eval_id"]: row for row in anchored_eval["results"]}

    traces = []
    for eval_id in FIXTURE_EVAL_IDS:
        eval_item = eval_items[eval_id]
        result = retrieval_results[eval_id]
        selected = selected_source_for_trace(result)
        answer = build_answer(eval_item, selected, source_register)
        traces.append(score_trace(eval_item, result, answer, selected))

    TRACE_OUT.write_text(
        "\n".join(json.dumps(trace, ensure_ascii=False, sort_keys=True) for trace in traces) + "\n",
        encoding="utf-8",
    )

    summary = summarize(traces)
    payload = {
        "metadata": {
            "created_at": "2026-06-19",
            "scope": "deterministic answer-trace fixture for consultant role KB",
            "provider_call_boundary": "no KB provider call",
            "production_impact": "production unchanged",
            "implementation_status": "local fixture only; no live KB ingestion",
            "fixture_eval_ids": FIXTURE_EVAL_IDS,
            "input_retrieval_eval": str(ANCHORED_EVAL_PATH.relative_to(ROOT)),
            "trace_output": str(TRACE_OUT.relative_to(ROOT)),
        },
        "summary": summary,
        "results": traces,
    }
    TRACE_EVAL_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    failures = [trace for trace in traces if not trace["trace_pass"]]
    report = f"""---
title: "Consultant Role KB Answer Trace Fixture Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-anchored-retrieval-citation-eval-20260619.json"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
scope: "local deterministic answer trace fixture for consultant role KB"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local fixture only; no live KB ingestion"
---

# Consultant Role KB Answer Trace Fixture Report

## 0. Boundary

This fixture uses deterministic template answers over anchored retrieval results. It does not call a provider, does not ingest into a live KB, and does not prove production answer quality.

The fixture is intentionally strict: if retrieval selected the wrong top1 source, the answer trace fails source selection even if it cites a valid locator.

## 1. Metrics

| metric | value |
|---|---:|
| trace_count | {summary["trace_count"]} |
| trace_pass_count | {summary["trace_pass_count"]} |
| trace_pass_rate | {summary["trace_pass_rate"]} |
| source_selection_pass_rate | {summary["source_selection_pass_rate"]} |
| locator_citation_pass_rate | {summary["locator_citation_pass_rate"]} |
| boundary_checks_pass_rate | {summary["boundary_checks_pass_rate"]} |
| blocked_action_pass_rate | {summary["blocked_action_pass_rate"]} |
| refusal_pass_rate | {summary["refusal_pass_rate"]} |
| long_text_reproduction_pass_rate | {summary["long_text_reproduction_pass_rate"]} |
| workspace_isolation_pass_rate | {summary["workspace_isolation_pass_rate"]} |

## 2. Category Summary

| category | count | trace_pass_rate | source_selection_pass_rate | locator_citation_pass_rate |
|---|---:|---:|---:|---:|
"""
    for category, row in summary["by_category"].items():
        report += (
            f"| {category} | {row['count']} | {row['trace_pass_rate']} | "
            f"{row['source_selection_pass_rate']} | {row['locator_citation_pass_rate']} |\n"
        )

    report += """
## 3. Failed Traces

"""
    if failures:
        for failure in failures:
            failed_checks = [key for key, value in failure["checks"].items() if not value]
            report += (
                f"- `{failure['eval_id']}` failed `{failed_checks}`; selected `{failure['selected_source_id']}`; "
                f"allowed `{failure['allowed_source_ids']}`; locator `{failure['selected_locator']}`.\n"
            )
    else:
        report += "- None.\n"

    report += """
## 4. Interpretation

The fixture confirms that answer text can carry selected unit locators and governance boundary language. Remaining failures should be treated as retrieval/source-selection issues, not answer-template citation issues.

This is still not production readiness. A provider-backed or agent-generated answer eval would require separate approval and should preserve the same boundary checks.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")

    print(json.dumps({"summary": summary, "failed_eval_ids": [row["eval_id"] for row in failures]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
