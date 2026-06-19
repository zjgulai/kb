#!/usr/bin/env python3
"""Anchored retrieval/citation eval for consultant role KB.

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
RERANK_SCRIPT = ROOT / "tmp/consultant_role_kb_rerank_source_prior_poc_20260619.py"
ANCHORED_CARD_PATH = ROOT / "tmp/consultant-role-kb-card-samples-anchored-20260619.jsonl"
BGE_RERANK_EVAL_PATH = ROOT / "tmp/consultant-role-kb-bge-source-prior-rerank-eval-20260619.json"

EVAL_OUT = ROOT / "tmp/consultant-role-kb-anchored-retrieval-citation-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-anchored-retrieval-citation-eval-report-20260619.md"

ALLOWED_LOCATOR_TYPES = {"page", "slide", "sheet_row", "paragraph"}


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


def has_unit_anchor(card: dict[str, Any]) -> bool:
    anchors = card.get("source_anchors") or []
    if not anchors:
        return False
    return anchors[0].get("locator_type") in ALLOWED_LOCATOR_TYPES and bool(anchors[0].get("locator"))


def best_anchor(card: dict[str, Any]) -> dict[str, Any] | None:
    anchors = card.get("source_anchors") or []
    return anchors[0] if anchors else None


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


def main() -> None:
    started = time.perf_counter()
    bge = load_module("consultant_bge_poc_for_anchored_eval", BGE_SCRIPT)
    rerank = load_module("consultant_rerank_poc_for_anchored_eval", RERANK_SCRIPT)

    cards = read_jsonl(ANCHORED_CARD_PATH)
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

    baseline = json.loads(BGE_RERANK_EVAL_PATH.read_text(encoding="utf-8"))["metrics"]
    answerable_results = [row for row in results if row["answerable_by_registered_source"]]
    no_source_results = [row for row in results if not row["answerable_by_registered_source"]]
    source_only_violations = [
        row
        for row in results
        for source in row["top_sources"]
        if source["citation_anchor"] is None or source["citation_anchor"].get("locator_type") not in ALLOWED_LOCATOR_TYPES
    ]
    failed_answerable_top1 = [
        row for row in answerable_results if not row["anchored_citation_at_1"]
    ]
    failed_answerable_top5 = [
        row for row in answerable_results if not row["anchored_citation_at_5"]
    ]

    metrics = {
        "retrieval_method": "bge_small_zh_with_source_prior_rerank_and_unit_anchors",
        "model_id": bge.MODEL_ID,
        "model_snapshot": bge.MODEL_SNAPSHOT,
        "embedding_dimension": bge.EMBEDDING_DIMENSION,
        "provider_call_boundary": "no KB provider call",
        "production_impact": "production unchanged",
        "implementation_status": "local PoC only; no live KB ingestion",
        "ranking_label_leakage": "none; allowed_source_ids are used only for evaluation",
        "citation_precision_scope": "proxy over retrieved typed-card anchors; no human gold locator labels yet",
        "indexed_card_count": len(cards),
        "eval_count": len(results),
        "answerable_eval_count": len(answerable_results),
        "no_allowed_source_eval_count": len(no_source_results),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "all_eval": metric_summary(results),
        "answerable_eval": metric_summary(answerable_results),
        "no_allowed_source_eval": metric_summary(no_source_results),
        "category_metrics": category_summary(results),
        "baseline_rerank_source_recall": {
            "all_eval": baseline["all_eval"],
            "answerable_eval": baseline["answerable_eval"],
        },
        "source_only_citation_violation_count": len(source_only_violations),
        "failure_counts": {
            "answerable_anchored_citation_at_1_failures": len(failed_answerable_top1),
            "answerable_anchored_citation_at_5_failures": len(failed_answerable_top5),
        },
    }

    EVAL_OUT.write_text(json.dumps({"metrics": metrics, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

    report = f"""---
title: "Consultant Role KB Anchored Retrieval Citation Eval Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-card-samples-anchored-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "tmp/consultant-role-kb-bge-source-prior-rerank-eval-20260619.json"
scope: "local anchored retrieval and citation eval for consultant role KB typed cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local PoC only; no live KB ingestion"
---

# Consultant Role KB Anchored Retrieval Citation Eval Report

## 0. Boundary

This eval uses anchored typed cards and local BGE + source-prior reranking. It does not call a provider, ingest into a live KB, or prove production readiness.

`allowed_source_ids` are used only after ranking to score eval results. The citation score is a proxy: it verifies that the retrieved typed card carries a unit-level locator, not that a human has approved the exact locator for a final answer.

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
| top1_has_unit_anchor | {metrics["all_eval"]["top1_has_unit_anchor"]} |
| source_only_citation_violation_count | {metrics["source_only_citation_violation_count"]} |

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
## 3. Remaining Failures

Answerable anchored-citation top1 failures:

"""
    for row in failed_answerable_top1[:10]:
        top3 = [
            {
                "source_id": item["source_id"],
                "locator": item["citation_anchor"]["locator"] if item.get("citation_anchor") else None,
            }
            for item in row["top_sources"][:3]
        ]
        report += f"- `{row['eval_id']}` expected `{row['allowed_source_ids']}`, top3 `{top3}`.\n"
    if not failed_answerable_top1:
        report += "- None.\n"

    report += """
## 4. Interpretation

The anchored eval confirms that retrieval results can carry unit-level citation locators instead of source-only references. The remaining failures are source-selection failures at rank 1, not missing-anchor failures.

This still does not prove final answer quality or human-approved citation precision. The next gate should be a small answer-trace fixture that checks whether generated answers cite the selected locator and preserve evidence boundaries.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
