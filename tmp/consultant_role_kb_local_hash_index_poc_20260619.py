#!/usr/bin/env python3
"""Local no-provider hash embedding/indexing PoC for consultant role KB cards."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = ROOT / "tmp/consultant-role-kb-card-samples-20260619.jsonl"
EVAL_PATH = ROOT / "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
SOURCE_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
INDEX_OUT = ROOT / "tmp/consultant-role-kb-local-hash-index-20260619.json"
EVAL_OUT = ROOT / "tmp/consultant-role-kb-local-retrieval-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-local-embedding-indexing-poc-report-20260619.md"

DIM = 1024

SOURCE_ALIASES = {
    "SRC-CONSULT-001": "问题定义 模糊问题 经营问题 issue tree problem definition issue structuring 假设 澄清",
    "SRC-CONSULT-002": "咨询框架 框架选择 framework catalog framework selection 方法论",
    "SRC-CONSULT-003": "项目启动 kickoff scope deliverables resources cadence agenda 项目范围 交付节奏",
    "SRC-CONSULT-004": "executive summary 摘要 高管摘要 slide section presentation findings recommendation",
    "SRC-CONSULT-005": "proposal 咨询建议书 提案 proposal template 章节 context objectives scope approach team timeline",
    "SRC-CONSULT-006": "RFP vendor selection 供应商评选 采购流程 request for proposal response package submit_rfp",
    "SRC-CONSULT-007": "供应链诊断 supply chain diagnostic data request interview scorecard logistics procurement inventory",
    "SRC-CONSULT-008": "analytics diagnostic 数据分析 数据治理 data warehouse data quality AI decision making scorecard",
    "SRC-CONSULT-009": "customer experience diagnostic 客户体验 CX VOC NPS journey retention PII",
    "SRC-CONSULT-010": "Commercial Due Diligence CDD 收购 acquisition target 市场 收入质量 market revenue customer competitor",
    "SRC-CONSULT-011": "Operational Due Diligence ODD 运营尽调 组织 供应链 IT 质量 风险 operating risk",
    "SRC-CONSULT-012": "Post-Merger Integration PMI 并购整合 integration workstream governance communication synergy",
    "SRC-CONSULT-013": "functional KPI function department 部门指标 accounts receivable finance KPI dashboard",
    "SRC-CONSULT-014": "industry KPI 行业指标 aerospace retail SaaS industry metric benchmark",
    "SRC-CONSULT-015": "acronym terminology crosswalk 术语 缩写 行业缩写 stands for definition mapping",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_sources(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return {row["source_id"]: row for row in csv.DictReader(f)}


def flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    if isinstance(value, dict):
        return " ".join(f"{key} {flatten(val)}" for key, val in value.items())
    return str(value)


def tokenize(text: str) -> list[str]:
    lower = text.lower()
    tokens = re.findall(r"[a-z0-9][a-z0-9_./:-]*", lower)
    cjk_runs = re.findall(r"[\u4e00-\u9fff]+", text)
    for run in cjk_runs:
        tokens.extend(run)
        tokens.extend(run[i : i + 2] for i in range(max(0, len(run) - 1)))
        tokens.extend(run[i : i + 3] for i in range(max(0, len(run) - 2)))
    return [token for token in tokens if token]


def hashed_vector(text: str) -> dict[int, float]:
    counts: Counter[int] = Counter()
    for token in tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % DIM
        sign = 1 if digest[4] % 2 == 0 else -1
        counts[index] += sign
    if not counts:
        return {}
    norm = math.sqrt(sum(v * v for v in counts.values()))
    return {idx: val / norm for idx, val in counts.items()}


def cosine(left: dict[int, float], right: dict[int, float]) -> float:
    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    return sum(val * right.get(idx, 0.0) for idx, val in left.items())


def indexed_text(card: dict[str, Any], source: dict[str, str]) -> str:
    fields = [
        card.get("card_id"),
        card.get("card_type"),
        card.get("domain"),
        card.get("layer"),
        card.get("method_name"),
        card.get("problem_type"),
        card.get("diagnostic_name"),
        card.get("dimension_names"),
        card.get("deliverable_type"),
        card.get("purpose"),
        card.get("sections"),
        card.get("outputs"),
        card.get("kpi_name"),
        card.get("function_or_industry"),
        card.get("group"),
        card.get("term"),
        card.get("expansion_or_mapping"),
        card.get("typical_questions"),
        card.get("source_structure_sample"),
        source.get("source_id"),
        source.get("source_title"),
        source.get("notes"),
        SOURCE_ALIASES.get(source.get("source_id", ""), ""),
    ]
    return " ".join(flatten(field) for field in fields)


def query_text(eval_item: dict[str, Any]) -> str:
    # Query uses only user-facing question plus routing fields that a real agent/router would know.
    return " ".join(
        [
            eval_item["question"],
            " ".join(eval_item.get("required_domains", [])),
            " ".join(eval_item.get("required_shared_layers", [])),
            eval_item.get("category", ""),
        ]
    )


def top_sources(query_vec: dict[int, float], indexed_cards: list[dict[str, Any]], k: int = 5) -> list[dict[str, Any]]:
    best_by_source: dict[str, dict[str, Any]] = {}
    for item in indexed_cards:
        score = cosine(query_vec, item["vector"])
        source_id = item["source_id"]
        if source_id not in best_by_source or score > best_by_source[source_id]["score"]:
            best_by_source[source_id] = {
                "source_id": source_id,
                "card_id": item["card_id"],
                "score": round(score, 6),
            }
    return sorted(best_by_source.values(), key=lambda row: row["score"], reverse=True)[:k]


def main() -> None:
    cards = read_jsonl(CARD_PATH)
    eval_items = read_jsonl(EVAL_PATH)
    sources = read_sources(SOURCE_REGISTER_PATH)

    indexed_cards = []
    for card in cards:
        source = sources[card["source_id"]]
        text = indexed_text(card, source)
        indexed_cards.append(
            {
                "card_id": card["card_id"],
                "card_type": card["card_type"],
                "source_id": card["source_id"],
                "workspace": card["workspace"],
                "evidence_grade": card["evidence_grade"],
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "token_count": len(tokenize(text)),
                "vector": hashed_vector(text),
            }
        )

    eval_results = []
    category_counts: dict[str, int] = defaultdict(int)
    category_top1: dict[str, int] = defaultdict(int)
    category_top5: dict[str, int] = defaultdict(int)

    for item in eval_items:
        qvec = hashed_vector(query_text(item))
        ranked = top_sources(qvec, indexed_cards, k=5)
        allowed = set(item.get("allowed_source_ids", []))
        top_ids = [row["source_id"] for row in ranked]
        top1_hit = bool(top_ids and top_ids[0] in allowed)
        top5_hit = bool(allowed.intersection(top_ids))
        category = item["category"]
        category_counts[category] += 1
        category_top1[category] += int(top1_hit)
        category_top5[category] += int(top5_hit)
        eval_results.append(
            {
                "eval_id": item["eval_id"],
                "category": category,
                "allowed_source_ids": sorted(allowed),
                "top_sources": ranked,
                "source_recall_at_1": top1_hit,
                "source_recall_at_5": top5_hit,
            }
        )

    total = len(eval_results)
    metrics = {
        "embedding_method": "local_hash_embedding",
        "embedding_dimension": DIM,
        "provider_call_boundary": "no KB provider call",
        "production_impact": "production unchanged",
        "indexed_card_count": len(indexed_cards),
        "eval_count": total,
        "source_recall_at_1": round(sum(r["source_recall_at_1"] for r in eval_results) / total, 4),
        "source_recall_at_5": round(sum(r["source_recall_at_5"] for r in eval_results) / total, 4),
        "category_metrics": {
            category: {
                "count": count,
                "source_recall_at_1": round(category_top1[category] / count, 4),
                "source_recall_at_5": round(category_top5[category] / count, 4),
            }
            for category, count in sorted(category_counts.items())
        },
    }

    index_payload = {
        "metadata": {
            "created_at": "2026-06-19",
            "embedding_method": "local_hash_embedding",
            "embedding_dimension": DIM,
            "provider_call_boundary": "no KB provider call",
            "production_impact": "production unchanged",
            "source": str(CARD_PATH.relative_to(ROOT)),
        },
        "cards": [
            {
                key: val
                for key, val in card.items()
                if key not in {"vector"}
            }
            for card in indexed_cards
        ],
    }
    INDEX_OUT.write_text(json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    EVAL_OUT.write_text(
        json.dumps({"metrics": metrics, "results": eval_results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report = f"""---
title: "Consultant Role KB Local Embedding Indexing PoC Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-card-samples-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
scope: "local no-provider embedding and indexing PoC for consultant role KB typed cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local PoC only; no live KB ingestion"
---

# Consultant Role KB Local Embedding Indexing PoC Report

## 0. Boundary

This PoC uses a deterministic local hash embedding and an in-memory cosine search implementation. It does not use a provider, does not download a model, does not deploy a service, and does not write to a live KB.

This is a plumbing proof for typed-card indexing and source recall. It is not evidence that final semantic retrieval quality is good enough for production.

## 1. Inputs And Outputs

| artifact | path |
|---|---|
| input cards | `tmp/consultant-role-kb-card-samples-20260619.jsonl` |
| eval set | `drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl` |
| source register | `drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv` |
| local index metadata | `tmp/consultant-role-kb-local-hash-index-20260619.json` |
| retrieval eval result | `tmp/consultant-role-kb-local-retrieval-eval-20260619.json` |

## 2. Metrics

| metric | value |
|---|---:|
| indexed_card_count | {metrics["indexed_card_count"]} |
| eval_count | {metrics["eval_count"]} |
| embedding_dimension | {metrics["embedding_dimension"]} |
| source_recall_at_1 | {metrics["source_recall_at_1"]} |
| source_recall_at_5 | {metrics["source_recall_at_5"]} |

## 3. Category Metrics

| category | count | source_recall_at_1 | source_recall_at_5 |
|---|---:|---:|---:|
"""
    for category, row in metrics["category_metrics"].items():
        report += f"| {category} | {row['count']} | {row['source_recall_at_1']} | {row['source_recall_at_5']} |\n"

    report += """
## 4. Interpretation

The local index path is mechanically viable: typed cards can be embedded, indexed, searched, and evaluated by source recall while preserving `workspace`, `source_id`, `evidence_grade`, and blocked-action metadata.

Because the embedding is a deterministic hash embedding, any misses or hits should be treated as local plumbing evidence only. A future quality gate should replace this with the selected local embedding model and rerun the same eval set.

The `refusal_unknown` category has lower source recall because some refusal cases intentionally have no allowed source or primarily test policy routing rather than source retrieval. Future eval should score refusal-policy compliance separately from source recall.

## 5. Next Gates

1. Select a real local embedding model and lock dimensions before any durable index.
2. Re-run this eval with the real embedding model and compare source recall, citation precision, and refusal quality.
3. Keep all source rows at `evidence_grade=C` and `license_status=pending_legal_review` until legal/source-owner review is complete.
4. Do not promote this to production; permitted statement remains `local embedding/indexing PoC executed`.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
