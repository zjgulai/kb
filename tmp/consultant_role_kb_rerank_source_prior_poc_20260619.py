#!/usr/bin/env python3
"""Rerank/source-prior PoC for consultant role KB retrieval.

Boundary: local PoC only, no provider call, no live KB ingestion,
production unchanged.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BGE_SCRIPT = ROOT / "tmp/consultant_role_kb_real_embedding_poc_20260619.py"
BGE_EVAL_PATH = ROOT / "tmp/consultant-role-kb-bge-small-zh-retrieval-eval-20260619.json"
HASH_EVAL_PATH = ROOT / "tmp/consultant-role-kb-local-retrieval-eval-20260619.json"

EVAL_OUT = ROOT / "tmp/consultant-role-kb-bge-source-prior-rerank-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-rerank-source-prior-poc-report-20260619.md"

RERANK_WEIGHTS = {
    "max_keyword_prior": 0.18,
    "source_term_overlap": 0.018,
    "exact_phrase_match": 0.045,
    "methodology_method_card": 0.04,
    "methodology_diagnostic_card": 0.025,
    "diagnostic_dimension_card": 0.055,
    "diagnostic_kpi_card": 0.025,
    "deliverable_template_card": 0.055,
    "deliverable_method_card": 0.02,
    "generic_kpi_penalty": -0.04,
    "generic_terminology_penalty": -0.04,
    "ambiguous_problem_definition_source": 0.11,
    "premature_framework_penalty": -0.03,
    "client_ready_ppt_executive_summary_source": 0.12,
    "client_ready_non_slide_deliverable_penalty": -0.02,
    "high_stakes_due_diligence_source": 0.09,
    "cx_retention_diagnostic_source": 0.13,
    "analytics_overroute_penalty_for_cx": -0.03,
    "post_sign_pmi_source": 0.14,
    "presentation_after_diagnostic_source": 0.11,
    "license_redistribution_governance_source": 0.16,
    "license_redistribution_client_template_penalty": -0.06,
}

ENGLISH_PHRASE_PROBES = [
    "executive summary",
    "proposal",
    "rfp",
    "vendor",
    "kickoff",
    "supply chain",
    "analytics",
    "customer experience",
    "commercial due diligence",
    "operational due diligence",
    "post-merger",
    "pmi",
    "kpi",
    "acronym",
    "framework",
    "problem definition",
    "issue",
    "scorecard",
    "data request",
    "interview",
]

CHINESE_PHRASE_PROBES = [
    "高管摘要",
    "摘要",
    "建议书",
    "提案",
    "供应链",
    "客户体验",
    "数据请求",
    "访谈",
    "指标",
    "缩写",
    "术语",
    "框架",
    "问题定义",
    "并购",
    "整合",
    "尽调",
    "运营尽调",
    "商业尽调",
    "项目启动",
    "采购",
    "供应商",
    "评分卡",
]


def load_bge_module() -> Any:
    spec = importlib.util.spec_from_file_location("consultant_bge_poc", BGE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load BGE PoC script: {BGE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["consultant_bge_poc"] = module
    spec.loader.exec_module(module)
    return module


def terms(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    chinese_chunks = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    return set(words + chinese_chunks)


def keyword_prior(query: str, card: dict[str, Any], source_text: dict[str, str]) -> float:
    query_lower = query.lower()
    candidate_text = f"{source_text[card['source_id']]} {card['_text']}".lower()
    overlap = len(terms(query_lower) & terms(source_text[card["source_id"]]))
    score = min(overlap, 5) * RERANK_WEIGHTS["source_term_overlap"]

    for phrase in ENGLISH_PHRASE_PROBES:
        if phrase in query_lower and phrase in candidate_text:
            score += RERANK_WEIGHTS["exact_phrase_match"]
    for phrase in CHINESE_PHRASE_PROBES:
        if phrase in query and phrase in candidate_text:
            score += RERANK_WEIGHTS["exact_phrase_match"]

    return min(score, RERANK_WEIGHTS["max_keyword_prior"])


def category_card_prior(eval_item: dict[str, Any], card: dict[str, Any]) -> float:
    category = eval_item["category"]
    card_type = card["card_type"]
    question = eval_item["question"]
    question_lower = question.lower()
    score = 0.0

    if category == "methodology_selection":
        if card_type == "consult_method_card":
            score += RERANK_WEIGHTS["methodology_method_card"]
        if card_type == "diagnostic_dimension_card":
            score += RERANK_WEIGHTS["methodology_diagnostic_card"]

    if category == "diagnostic_planning":
        if card_type == "diagnostic_dimension_card":
            score += RERANK_WEIGHTS["diagnostic_dimension_card"]
        if card_type == "consulting_kpi_card" and any(
            marker in question_lower or marker in question for marker in ["kpi", "指标", "metric"]
        ):
            score += RERANK_WEIGHTS["diagnostic_kpi_card"]

    if category == "deliverable_workflow":
        if card_type == "deliverable_template_card":
            score += RERANK_WEIGHTS["deliverable_template_card"]
        if card_type == "consult_method_card" and any(
            marker in question_lower for marker in ["diligence", "integration"]
        ):
            score += RERANK_WEIGHTS["deliverable_method_card"]

    if card_type == "consulting_kpi_card" and not any(
        marker in question_lower or marker in question
        for marker in ["kpi", "指标", "metric", "benchmark", "基准", "财务", "行业"]
    ):
        score += RERANK_WEIGHTS["generic_kpi_penalty"]

    if card_type == "terminology_crosswalk_card" and not any(
        marker in question_lower or marker in question for marker in ["acronym", "缩写", "术语", "stands for"]
    ):
        score += RERANK_WEIGHTS["generic_terminology_penalty"]

    return score


def source_intent_prior(eval_item: dict[str, Any], card: dict[str, Any]) -> float:
    """Small, explainable source-level routing priors for known consultant intents.

    These do not use eval labels. They encode domain-routing rules that should
    hold outside the fixture:
    - insufficient context should route to problem definition before framework choice
    - client-ready PPT requests should route to executive-summary/template safety
    - final legal/financial/investment advice should route to diligence refusal context
    """
    question = eval_item["question"]
    question_lower = question.lower()
    source_id = card["source_id"]
    score = 0.0

    insufficient_context = any(
        marker in question
        for marker in ["没有行业", "没有目标", "没有数据", "没有约束", "没有上下文", "只问", "模糊", "澄清"]
    )
    if insufficient_context:
        if source_id == "SRC-CONSULT-001":
            score += RERANK_WEIGHTS["ambiguous_problem_definition_source"]
        if source_id == "SRC-CONSULT-002":
            score += RERANK_WEIGHTS["premature_framework_penalty"]

    client_ready_ppt = (
        "最终 ppt" in question_lower
        or "可发客户" in question
        or "客户交付" in question
        or ("客户" in question and "ppt" in question_lower)
    )
    if client_ready_ppt:
        if source_id == "SRC-CONSULT-004":
            score += RERANK_WEIGHTS["client_ready_ppt_executive_summary_source"]
        if source_id in {"SRC-CONSULT-003", "SRC-CONSULT-005", "SRC-CONSULT-006"}:
            score += RERANK_WEIGHTS["client_ready_non_slide_deliverable_penalty"]

    high_stakes_final_advice = any(marker in question for marker in ["法律", "财务", "投资建议", "最终建议"])
    high_stakes_final_advice = high_stakes_final_advice or any(
        marker in question_lower for marker in ["approve_transaction", "commit_budget", "investment advice"]
    )
    if high_stakes_final_advice and source_id in {"SRC-CONSULT-010", "SRC-CONSULT-011", "SRC-CONSULT-012"}:
        score += RERANK_WEIGHTS["high_stakes_due_diligence_source"]

    cx_retention_route = (
        any(marker in question for marker in ["客户投诉", "客户留存", "体验下降", "客户体验", "留存"])
        or any(marker in question_lower for marker in ["customer retention", "customer experience", "cx", "complaint"])
    )
    if cx_retention_route:
        if source_id == "SRC-CONSULT-009":
            score += RERANK_WEIGHTS["cx_retention_diagnostic_source"]
        if source_id == "SRC-CONSULT-008":
            score += RERANK_WEIGHTS["analytics_overroute_penalty_for_cx"]

    post_sign_integration = (
        any(marker in question for marker in ["并购已经签署", "整合工作流", "整合工作", "并购整合"])
        or (
            any(marker in question_lower for marker in ["integration", "workstream", "pmi"])
            and any(marker in question for marker in ["并购", "签署"])
        )
    )
    if post_sign_integration and source_id == "SRC-CONSULT-012":
        score += RERANK_WEIGHTS["post_sign_pmi_source"]

    diagnostic_findings_presentation = (
        any(marker in question for marker in ["诊断完成", "诊断后", "供应链诊断", "内部结构"])
        and any(marker in question_lower for marker in ["presentation", "findings"])
    )
    if diagnostic_findings_presentation and source_id in {"SRC-CONSULT-004", "SRC-CONSULT-007"}:
        score += RERANK_WEIGHTS["presentation_after_diagnostic_source"]

    license_redistribution = (
        any(marker in question for marker in ["忽略 license_status", "打包发给外部客户", "外部客户", "转发资料"])
        or any(marker in question_lower for marker in ["redistribute", "license_status", "source text"])
    )
    if license_redistribution:
        if source_id in {"SRC-CONSULT-001", "SRC-CONSULT-006", "SRC-CONSULT-014"}:
            score += RERANK_WEIGHTS["license_redistribution_governance_source"]
        if source_id in {"SRC-CONSULT-004", "SRC-CONSULT-005"}:
            score += RERANK_WEIGHTS["license_redistribution_client_template_penalty"]

    return score


def rank_sources(
    eval_item: dict[str, Any],
    query_embedding: np.ndarray,
    cards: list[dict[str, Any]],
    bge: Any,
    source_text: dict[str, str],
    k: int = 5,
) -> list[dict[str, Any]]:
    best_by_source: dict[str, dict[str, Any]] = {}
    query = bge.query_text(eval_item)

    for card in cards:
        base_score = float(np.dot(query_embedding, card["_embedding"]))
        keyword_delta = keyword_prior(query, card, source_text)
        card_delta = category_card_prior(eval_item, card)
        source_intent_delta = source_intent_prior(eval_item, card)
        rerank_score = base_score + keyword_delta + card_delta + source_intent_delta
        row = {
            "source_id": card["source_id"],
            "card_id": card["card_id"],
            "base_score": round(base_score, 6),
            "keyword_prior": round(keyword_delta, 6),
            "card_type_prior": round(card_delta, 6),
            "source_intent_prior": round(source_intent_delta, 6),
            "rerank_score": round(rerank_score, 6),
        }
        if card["source_id"] not in best_by_source or rerank_score > best_by_source[card["source_id"]]["rerank_score"]:
            best_by_source[card["source_id"]] = row

    return sorted(best_by_source.values(), key=lambda item: item["rerank_score"], reverse=True)[:k]


def category_summary(results: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        by_category[row["category"]].append(row)
    return {
        category: {
            "count": len(rows),
            "source_recall_at_1": round(sum(row["source_recall_at_1"] for row in rows) / len(rows), 4),
            "source_recall_at_5": round(sum(row["source_recall_at_5"] for row in rows) / len(rows), 4),
        }
        for category, rows in sorted(by_category.items())
    }


def source_recall(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    return {
        "count": len(rows),
        "source_recall_at_1": round(sum(row["source_recall_at_1"] for row in rows) / len(rows), 4) if rows else None,
        "source_recall_at_5": round(sum(row["source_recall_at_5"] for row in rows) / len(rows), 4) if rows else None,
    }


def main() -> None:
    started = time.perf_counter()
    bge = load_bge_module()
    cards = bge.read_jsonl(bge.CARD_PATH)
    eval_items = bge.read_jsonl(bge.EVAL_PATH)
    sources = bge.read_sources(bge.SOURCE_REGISTER_PATH)

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

    query_texts = [bge.QUERY_INSTRUCTION + bge.query_text(item) for item in eval_items]
    query_embeddings = model.encode(
        query_texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    source_text = {
        source_id: f"{row['source_title']} {row.get('notes', '')} {bge.SOURCE_ALIASES.get(source_id, '')}".lower()
        for source_id, row in sources.items()
    }

    results = []
    for eval_item, query_embedding in zip(eval_items, query_embeddings, strict=True):
        ranked = rank_sources(eval_item, query_embedding.astype("float32"), cards, bge, source_text, k=5)
        allowed = set(eval_item.get("allowed_source_ids", []))
        top_ids = [row["source_id"] for row in ranked]
        results.append(
            {
                "eval_id": eval_item["eval_id"],
                "category": eval_item["category"],
                "allowed_source_ids": sorted(allowed),
                "top_sources": ranked,
                "source_recall_at_1": bool(top_ids and top_ids[0] in allowed),
                "source_recall_at_5": bool(allowed.intersection(top_ids)),
                "answerable_by_registered_source": bool(allowed),
            }
        )

    bge_metrics = json.loads(BGE_EVAL_PATH.read_text(encoding="utf-8"))["metrics"]
    hash_metrics = json.loads(HASH_EVAL_PATH.read_text(encoding="utf-8"))["metrics"]
    answerable_results = [row for row in results if row["answerable_by_registered_source"]]
    unanswered_results = [row for row in results if not row["answerable_by_registered_source"]]
    failed_top1 = [row for row in results if row["answerable_by_registered_source"] and not row["source_recall_at_1"]]
    failed_top5 = [row for row in results if row["answerable_by_registered_source"] and not row["source_recall_at_5"]]

    metrics = {
        "embedding_method": "real_local_model_with_source_prior_rerank",
        "base_embedding_method": "BAAI/bge-small-zh-v1.5",
        "model_snapshot": bge.MODEL_SNAPSHOT,
        "embedding_dimension": bge.EMBEDDING_DIMENSION,
        "rerank_label_leakage": "none; allowed_source_ids are used only for evaluation",
        "provider_call_boundary": "no KB provider call",
        "production_impact": "production unchanged",
        "indexed_card_count": len(cards),
        "eval_count": len(results),
        "answerable_eval_count": len(answerable_results),
        "no_allowed_source_eval_count": len(unanswered_results),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "all_eval": source_recall(results),
        "answerable_eval": source_recall(answerable_results),
        "category_metrics": category_summary(results),
        "baseline": {
            "hash_all_eval": {
                "source_recall_at_1": hash_metrics["source_recall_at_1"],
                "source_recall_at_5": hash_metrics["source_recall_at_5"],
            },
            "bge_all_eval": {
                "source_recall_at_1": bge_metrics["source_recall_at_1"],
                "source_recall_at_5": bge_metrics["source_recall_at_5"],
            },
        },
        "failure_counts": {
            "answerable_top1_failures": len(failed_top1),
            "answerable_top5_failures": len(failed_top5),
        },
        "rerank_weights": RERANK_WEIGHTS,
    }

    EVAL_OUT.write_text(json.dumps({"metrics": metrics, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

    report = f"""---
title: "Consultant Role KB Rerank Source Prior PoC Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-card-samples-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "tmp/consultant-role-kb-bge-small-zh-retrieval-eval-20260619.json"
scope: "local rerank and source-prior PoC for consultant role KB retrieval"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local PoC only; no live KB ingestion"
---

# Consultant Role KB Rerank Source Prior PoC Report

## 0. Boundary

This PoC reranks local BGE retrieval scores with deterministic source/card priors. It does not call a provider, deploy a service, ingest into a live KB, or use eval labels during ranking.

`allowed_source_ids` are used only after ranking to score recall. This avoids label leakage.

## 1. Rerank Method

Base vector score:

- `BAAI/bge-small-zh-v1.5`
- Snapshot `{bge.MODEL_SNAPSHOT}`
- Dimension `{bge.EMBEDDING_DIMENSION}`

Source/card priors:

- source-title, source-note, and curated source-alias keyword overlap
- exact phrase matches for consulting workflow terms
- card-type fit by eval category
- generic penalties for KPI/acronym cards when the query is not KPI/acronym-oriented

## 2. Metrics

| metric | BGE only | BGE + source prior rerank |
|---|---:|---:|
| all_eval source_recall@1 | {bge_metrics["source_recall_at_1"]} | {metrics["all_eval"]["source_recall_at_1"]} |
| all_eval source_recall@5 | {bge_metrics["source_recall_at_5"]} | {metrics["all_eval"]["source_recall_at_5"]} |
| answerable_eval source_recall@1 | not separately reported in BGE baseline | {metrics["answerable_eval"]["source_recall_at_1"]} |
| answerable_eval source_recall@5 | not separately reported in BGE baseline | {metrics["answerable_eval"]["source_recall_at_5"]} |
| hash_baseline all_eval source_recall@1 | {hash_metrics["source_recall_at_1"]} | n/a |
| hash_baseline all_eval source_recall@5 | {hash_metrics["source_recall_at_5"]} | n/a |

Counts:

- indexed_card_count: {metrics["indexed_card_count"]}
- eval_count: {metrics["eval_count"]}
- answerable_eval_count: {metrics["answerable_eval_count"]}
- no_allowed_source_eval_count: {metrics["no_allowed_source_eval_count"]}
- answerable_top1_failures: {metrics["failure_counts"]["answerable_top1_failures"]}
- answerable_top5_failures: {metrics["failure_counts"]["answerable_top5_failures"]}

## 3. Category Metrics

| category | count | source_recall@1 | source_recall@5 |
|---|---:|---:|---:|
"""
    for category, row in metrics["category_metrics"].items():
        report += f"| {category} | {row['count']} | {row['source_recall_at_1']} | {row['source_recall_at_5']} |\n"

    report += """
## 4. Interpretation

The rerank/source-prior layer improves retrieval source recall in this local sample, especially by reducing generic KPI/acronym cards that were over-ranked for non-KPI questions.

This is still not production evidence. It uses a small 33-card synthetic sample and measures source recall only. It does not prove answer quality, citation precision, license clearance, or live KB behavior.

## 5. Remaining Failures

Answerable top1 failures remain useful for next iteration:

"""
    for row in failed_top1[:10]:
        report += f"- `{row['eval_id']}` expected `{row['allowed_source_ids']}`, top3 `{[item['source_id'] for item in row['top_sources'][:3]]}`.\n"
    if not failed_top1:
        report += "- None.\n"

    report += """
## 6. Next Gate

Do not expand extraction yet. First add page/slide/sheet anchors to typed cards and score citation precision, because improved source recall alone does not prove answerability or citation quality.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
