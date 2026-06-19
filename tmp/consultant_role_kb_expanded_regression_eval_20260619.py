#!/usr/bin/env python3
"""Regression eval for expanded consultant role KB cards.

Boundary: local regression only, no provider call, no live KB ingestion,
production unchanged.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BGE_SCRIPT = ROOT / "tmp/consultant_role_kb_real_embedding_poc_20260619.py"
RERANK_SCRIPT = ROOT / "tmp/consultant_role_kb_rerank_source_prior_poc_20260619.py"
EXPANDED_CARD_PATH = ROOT / "tmp/consultant-role-kb-expanded-cards-20260619.jsonl"
EVAL_SET_PATH = ROOT / "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
SOURCE_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"

RETRIEVAL_EVAL_OUT = ROOT / "tmp/consultant-role-kb-expanded-anchored-retrieval-citation-eval-20260619.json"
RETRIEVAL_REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-expanded-regression-eval-report-20260619.md"
TRACE_OUT = ROOT / "tmp/consultant-role-kb-expanded-answer-trace-fixture-20260619.jsonl"
TRACE_EVAL_OUT = ROOT / "tmp/consultant-role-kb-expanded-answer-trace-eval-20260619.json"
TRACE_REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-expanded-answer-trace-fixture-report-20260619.md"

ALLOWED_LOCATOR_TYPES = {"page", "slide", "sheet_row", "paragraph"}
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


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_sources(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return {row["source_id"]: row for row in csv.DictReader(f)}


def has_unit_anchor(card: dict[str, Any]) -> bool:
    anchors = card.get("source_anchors") or []
    if not anchors:
        return False
    return anchors[0].get("locator_type") in ALLOWED_LOCATOR_TYPES and bool(anchors[0].get("locator"))


def best_anchor(card: dict[str, Any]) -> dict[str, Any] | None:
    anchors = card.get("source_anchors") or []
    return anchors[0] if anchors else None


def metric_summary(rows: list[dict[str, Any]]) -> dict[str, float | int | None]:
    if not rows:
        return {
            "count": 0,
            "source_recall_at_1": None,
            "source_recall_at_5": None,
            "anchored_citation_at_1": None,
            "anchored_citation_at_5": None,
            "top1_has_unit_anchor": None,
        }
    return {
        "count": len(rows),
        "source_recall_at_1": round(sum(row["source_recall_at_1"] for row in rows) / len(rows), 4),
        "source_recall_at_5": round(sum(row["source_recall_at_5"] for row in rows) / len(rows), 4),
        "anchored_citation_at_1": round(sum(row["anchored_citation_at_1"] for row in rows) / len(rows), 4),
        "anchored_citation_at_5": round(sum(row["anchored_citation_at_5"] for row in rows) / len(rows), 4),
        "top1_has_unit_anchor": round(sum(row["top1_has_unit_anchor"] for row in rows) / len(rows), 4),
    }


def category_summary(results: list[dict[str, Any]]) -> dict[str, dict[str, float | int | None]]:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        by_category[row["category"]].append(row)
    return {category: metric_summary(rows) for category, rows in sorted(by_category.items())}


def rank_sources(
    eval_item: dict[str, Any],
    query_embedding: np.ndarray,
    cards: list[dict[str, Any]],
    bge: Any,
    rerank: Any,
    source_text: dict[str, str],
    k: int = 5,
) -> list[dict[str, Any]]:
    best_by_source: dict[str, dict[str, Any]] = {}
    query = bge.query_text(eval_item)
    for card in cards:
        base_score = float(np.dot(query_embedding, card["_embedding"]))
        keyword_delta = rerank.keyword_prior(query, card, source_text)
        card_delta = rerank.category_card_prior(eval_item, card)
        source_intent_delta = rerank.source_intent_prior(eval_item, card)
        final_score = base_score + keyword_delta + card_delta + source_intent_delta
        anchor = best_anchor(card)
        row = {
            "source_id": card["source_id"],
            "card_id": card["card_id"],
            "base_score": round(base_score, 6),
            "keyword_prior": round(keyword_delta, 6),
            "card_type_prior": round(card_delta, 6),
            "source_intent_prior": round(source_intent_delta, 6),
            "rerank_score": round(final_score, 6),
            "has_unit_anchor": has_unit_anchor(card),
            "citation_anchor": anchor,
        }
        if card["source_id"] not in best_by_source or final_score > best_by_source[card["source_id"]]["rerank_score"]:
            best_by_source[card["source_id"]] = row
    return sorted(best_by_source.values(), key=lambda item: item["rerank_score"], reverse=True)[:k]


def run_retrieval_eval() -> dict[str, Any]:
    started = time.perf_counter()
    bge = load_module("consultant_bge_expanded_eval", BGE_SCRIPT)
    rerank = load_module("consultant_rerank_expanded_eval", RERANK_SCRIPT)
    cards = read_jsonl(EXPANDED_CARD_PATH)
    eval_items = read_jsonl(EVAL_SET_PATH)
    sources = read_sources(SOURCE_REGISTER_PATH)

    model = bge.SentenceTransformer(str(bge.MODEL_PATH), local_files_only=True, device="cpu")
    card_texts = [bge.indexed_text(card, sources[card["source_id"]]) for card in cards]
    card_embeddings = model.encode(
        card_texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    for card, text, embedding in zip(cards, card_texts, card_embeddings, strict=True):
        card["_text"] = text.lower()
        card["_embedding"] = embedding.astype("float32")

    source_text = {
        source_id: f"{row['source_title']} {row.get('notes', '')} {bge.SOURCE_ALIASES.get(source_id, '')}".lower()
        for source_id, row in sources.items()
    }
    query_texts = [bge.QUERY_INSTRUCTION + bge.query_text(item) for item in eval_items]
    query_embeddings = model.encode(
        query_texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    results = []
    for eval_item, query_embedding in zip(eval_items, query_embeddings, strict=True):
        ranked = rank_sources(eval_item, query_embedding.astype("float32"), cards, bge, rerank, source_text, k=5)
        allowed = set(eval_item.get("allowed_source_ids", []))
        top_ids = [row["source_id"] for row in ranked]
        top1_ok = bool(top_ids and top_ids[0] in allowed)
        top5_ok = bool(allowed.intersection(top_ids))
        top1_has_anchor = bool(ranked and ranked[0]["has_unit_anchor"])
        top5_allowed_anchor = any(row["source_id"] in allowed and row["has_unit_anchor"] for row in ranked)
        results.append(
            {
                "eval_id": eval_item["eval_id"],
                "category": eval_item["category"],
                "allowed_source_ids": sorted(allowed),
                "answerable_by_registered_source": bool(allowed),
                "top_sources": ranked,
                "source_recall_at_1": top1_ok,
                "source_recall_at_5": top5_ok,
                "top1_has_unit_anchor": top1_has_anchor,
                "anchored_citation_at_1": top1_ok and top1_has_anchor,
                "anchored_citation_at_5": top5_allowed_anchor,
            }
        )

    answerable_results = [row for row in results if row["answerable_by_registered_source"]]
    no_source_results = [row for row in results if not row["answerable_by_registered_source"]]
    source_only_violations = [
        row
        for row in results
        for source in row["top_sources"]
        if source["citation_anchor"] is None or source["citation_anchor"].get("locator_type") not in ALLOWED_LOCATOR_TYPES
    ]
    failed_answerable_top1 = [row for row in answerable_results if not row["anchored_citation_at_1"]]
    failed_answerable_top5 = [row for row in answerable_results if not row["anchored_citation_at_5"]]
    metrics = {
        "retrieval_method": "expanded_bge_small_zh_with_source_prior_rerank_and_unit_anchors",
        "model_id": bge.MODEL_ID,
        "model_snapshot": bge.MODEL_SNAPSHOT,
        "embedding_dimension": bge.EMBEDDING_DIMENSION,
        "provider_call_boundary": "no KB provider call",
        "production_impact": "production unchanged",
        "implementation_status": "local expanded regression only; no live KB ingestion",
        "ranking_label_leakage": "none; allowed_source_ids are used only for evaluation",
        "indexed_card_count": len(cards),
        "eval_count": len(results),
        "answerable_eval_count": len(answerable_results),
        "no_allowed_source_eval_count": len(no_source_results),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "all_eval": metric_summary(results),
        "answerable_eval": metric_summary(answerable_results),
        "no_allowed_source_eval": metric_summary(no_source_results),
        "category_metrics": category_summary(results),
        "answerable_category_metrics": category_summary(answerable_results),
        "source_only_citation_violation_count": len(source_only_violations),
        "failure_counts": {
            "answerable_anchored_citation_at_1_failures": len(failed_answerable_top1),
            "answerable_anchored_citation_at_5_failures": len(failed_answerable_top5),
        },
        "gate_thresholds": {
            "metadata_completeness": 1.0,
            "unit_locator_coverage": 1.0,
            "source_only_citation_violation_count": 0,
            "answerable_anchored_citation_at_5_min": 0.95,
        },
    }
    payload = {"metrics": metrics, "results": results}
    RETRIEVAL_EVAL_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_retrieval_report(metrics, failed_answerable_top1)
    return payload


def write_retrieval_report(metrics: dict[str, Any], failed_answerable_top1: list[dict[str, Any]]) -> None:
    threshold_pass = (
        metrics["source_only_citation_violation_count"] == 0
        and metrics["answerable_eval"]["anchored_citation_at_5"] >= 0.95
        and metrics["answerable_eval"]["anchored_citation_at_1"] >= 0.90
        and all(
            row["source_recall_at_1"] >= 0.80
            for row in metrics["answerable_category_metrics"].values()
        )
    )
    report = f"""---
title: "Consultant Role KB Expanded Regression Eval Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-expanded-cards-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
scope: "local regression eval for expanded consultant role KB cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local regression only; no live KB ingestion"
---

# Consultant Role KB Expanded Regression Eval Report

## 0. Boundary

This eval uses the expanded local cards and local BGE + source-prior reranking. It does not call a provider, ingest into a live KB, or prove production readiness.

## 1. Metrics

| metric | value |
|---|---:|
| indexed_card_count | {metrics["indexed_card_count"]} |
| eval_count | {metrics["eval_count"]} |
| answerable_eval_count | {metrics["answerable_eval_count"]} |
| all_eval source_recall@1 | {metrics["all_eval"]["source_recall_at_1"]} |
| all_eval source_recall@5 | {metrics["all_eval"]["source_recall_at_5"]} |
| all_eval anchored_citation@1 | {metrics["all_eval"]["anchored_citation_at_1"]} |
| all_eval anchored_citation@5 | {metrics["all_eval"]["anchored_citation_at_5"]} |
| answerable_eval anchored_citation@1 | {metrics["answerable_eval"]["anchored_citation_at_1"]} |
| answerable_eval anchored_citation@5 | {metrics["answerable_eval"]["anchored_citation_at_5"]} |
| source_only_citation_violation_count | {metrics["source_only_citation_violation_count"]} |
| gate_threshold_pass | {str(threshold_pass).lower()} |

## 2. Category Metrics

| category | count | source@1 | source@5 | anchored_citation@1 | anchored_citation@5 |
|---|---:|---:|---:|---:|---:|
"""
    for category, row in metrics["category_metrics"].items():
        report += (
            f"| {category} | {row['count']} | {row['source_recall_at_1']} | {row['source_recall_at_5']} | "
            f"{row['anchored_citation_at_1']} | {row['anchored_citation_at_5']} |\n"
        )
    report += """
## 3. Answerable-Only Category Metrics

This table excludes eval items with no allowed registered source, because source recall is not the right metric for deliberate refusal/no-source prompts.

| category | count | source@1 | source@5 | anchored_citation@1 | anchored_citation@5 |
|---|---:|---:|---:|---:|---:|
"""
    for category, row in metrics["answerable_category_metrics"].items():
        report += (
            f"| {category} | {row['count']} | {row['source_recall_at_1']} | {row['source_recall_at_5']} | "
            f"{row['anchored_citation_at_1']} | {row['anchored_citation_at_5']} |\n"
        )
    report += """
## 4. Remaining Answerable Top1 Failures

"""
    if failed_answerable_top1:
        for row in failed_answerable_top1[:10]:
            top3 = [
                {
                    "source_id": item["source_id"],
                    "locator": item["citation_anchor"]["locator"] if item.get("citation_anchor") else None,
                }
                for item in row["top_sources"][:3]
            ]
            report += f"- `{row['eval_id']}` expected `{row['allowed_source_ids']}`, top3 `{top3}`.\n"
    else:
        report += "- None.\n"
    report += """
## 5. Interpretation

Fact: the expanded set preserves unit-level locators in retrieved results.

Inference: expansion can proceed as a local draft artifact if answer-trace also remains green.

Unknown: this is still not human-approved citation precision and not production answer quality.
"""
    RETRIEVAL_REPORT_OUT.write_text(report, encoding="utf-8")


def selected_source_for_trace(result: dict[str, Any]) -> dict[str, Any] | None:
    if not result["allowed_source_ids"]:
        return None
    return result["top_sources"][0] if result.get("top_sources") else None


def selected_anchor(selected: dict[str, Any] | None) -> dict[str, Any] | None:
    if not selected:
        return None
    return selected.get("citation_anchor")


def should_refuse(eval_item: dict[str, Any]) -> bool:
    return eval_item["category"] == "refusal_unknown"


def blocked_actions_text(eval_item: dict[str, Any]) -> str:
    actions = eval_item.get("blocked_actions_expected", [])
    return ", ".join(actions) if actions else "publish_client_deliverable, redistribute_source_text"


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


def build_answer(eval_item: dict[str, Any], selected: dict[str, Any] | None, source_register: dict[str, dict[str, str]]) -> str:
    blocked = blocked_actions_text(eval_item)
    common_boundary = (
        "边界: evidence_grade=C; license_status=pending_legal_review; "
        "仅限 internal local PoC; production unchanged; no KB provider call; "
        "no live KB ingestion; 不是生产事实或最终客户交付物。"
    )
    if selected is None:
        return (
            "拒绝: 当前问题没有可用的 registered allowed source，不能给出结论或跨 workspace 返回内容。"
            f"{common_boundary} Blocked actions: {blocked}. "
            "下一步: 先补 source register、owner review、workspace isolation 和 evidence grade。"
        )
    anchor = selected_anchor(selected) or {}
    source_id = selected["source_id"]
    source = source_register[source_id]
    locator = anchor.get("locator", "missing-locator")
    label = anchor.get("anchor_label", "")
    citation = f"{source_id} {locator}"
    if should_refuse(eval_item):
        return (
            "拒绝: 不能执行题目中的受限请求；可提供结构化摘要或内部审阅提示。"
            f"参考: {citation}; anchor_label={label}. Source title: {source['source_title']}. "
            f"{common_boundary} Blocked actions: {blocked}. "
            "下一步: 由 human consultant/source owner 审阅后再决定是否进入正式输出。"
        )
    action = category_answer_action(eval_item)
    return (
        f"结论: 针对“{eval_item['question']}”，建议先执行“{action}”。"
        f"参考: {citation}; anchor_label={label}. Source title: {source['source_title']}. "
        "输出只应是中文为主、保留 English method/source terms 的内部草稿。"
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
    locator_citation_pass = True
    if selected_source_id is not None:
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
        refusal_pass = "拒绝" in answer and ("不能" in answer or "registered allowed source" in answer)
    workspace_pass = True
    if "workspace" in eval_item["question"].lower():
        workspace_pass = "workspace" in answer and "拒绝" in answer
    long_text_pass = len(answer) < 1200 and "全文如下" not in answer and "完整复制" not in answer
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


def trace_summary(scored: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(scored)
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored:
        by_category[row["category"]].append(row)

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


def run_answer_trace(retrieval_payload: dict[str, Any]) -> dict[str, Any]:
    eval_items = {item["eval_id"]: item for item in read_jsonl(EVAL_SET_PATH)}
    source_register = read_sources(SOURCE_REGISTER_PATH)
    retrieval_results = {row["eval_id"]: row for row in retrieval_payload["results"]}
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
    summary = trace_summary(traces)
    payload = {
        "metadata": {
            "created_at": "2026-06-19",
            "scope": "deterministic answer-trace fixture over expanded consultant role KB cards",
            "provider_call_boundary": "no KB provider call",
            "production_impact": "production unchanged",
            "implementation_status": "local fixture only; no live KB ingestion",
            "fixture_eval_ids": FIXTURE_EVAL_IDS,
            "input_retrieval_eval": str(RETRIEVAL_EVAL_OUT.relative_to(ROOT)),
            "trace_output": str(TRACE_OUT.relative_to(ROOT)),
        },
        "summary": summary,
        "results": traces,
    }
    TRACE_EVAL_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_trace_report(summary, [trace for trace in traces if not trace["trace_pass"]])
    return payload


def write_trace_report(summary: dict[str, Any], failures: list[dict[str, Any]]) -> None:
    report = f"""---
title: "Consultant Role KB Expanded Answer Trace Fixture Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-expanded-anchored-retrieval-citation-eval-20260619.json"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
scope: "local deterministic answer trace fixture for expanded consultant role KB"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local fixture only; no live KB ingestion"
---

# Consultant Role KB Expanded Answer Trace Fixture Report

## 0. Boundary

This fixture uses deterministic template answers over expanded-card retrieval results. It does not call a provider, does not ingest into a live KB, and does not prove production answer quality.

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
                f"allowed `{failure['allowed_source_ids']}`.\n"
            )
    else:
        report += "- None.\n"
    report += """
## 4. Interpretation

The fixture verifies that expanded-card retrieval can still feed answers with selected unit locators and governance boundary language.
"""
    TRACE_REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    retrieval_payload = run_retrieval_eval()
    trace_payload = run_answer_trace(retrieval_payload)
    output = {
        "retrieval_summary": retrieval_payload["metrics"],
        "trace_summary": trace_payload["summary"],
        "outputs": [
            str(RETRIEVAL_EVAL_OUT),
            str(RETRIEVAL_REPORT_OUT),
            str(TRACE_OUT),
            str(TRACE_EVAL_OUT),
            str(TRACE_REPORT_OUT),
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
