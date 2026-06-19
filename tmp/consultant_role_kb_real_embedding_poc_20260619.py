#!/usr/bin/env python3
"""Real local embedding/indexing PoC for consultant role KB typed cards.

Runtime: Homebrew Python 3.12 with local sentence-transformers/torch.
Model: local cached BAAI/bge-small-zh-v1.5 snapshot.
Boundary: no provider call, no live KB ingestion, production unchanged.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import sentence_transformers
import torch
import transformers
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = ROOT / "tmp/consultant-role-kb-card-samples-20260619.jsonl"
EVAL_PATH = ROOT / "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
SOURCE_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
HASH_EVAL_PATH = ROOT / "tmp/consultant-role-kb-local-retrieval-eval-20260619.json"

MODEL_ID = "BAAI/bge-small-zh-v1.5"
MODEL_SNAPSHOT = "7999e1d3359715c523056ef9478215996d62a620"
MODEL_PATH = Path.home() / ".cache/huggingface/hub/models--BAAI--bge-small-zh-v1.5/snapshots" / MODEL_SNAPSHOT
MODEL_LICENSE = "MIT"
EMBEDDING_DIMENSION = 512
QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："

INDEX_OUT = ROOT / "tmp/consultant-role-kb-bge-small-zh-index-20260619.json"
EVAL_OUT = ROOT / "tmp/consultant-role-kb-bge-small-zh-retrieval-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-real-embedding-indexing-poc-report-20260619.md"
ADR_OUT = ROOT / "drafts/analysis/consultant-role-kb-embedding-adr-001-bge-small-zh-v1.5-20260619.md"

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
    return " ".join(
        [
            eval_item["question"],
            " ".join(eval_item.get("required_domains", [])),
            " ".join(eval_item.get("required_shared_layers", [])),
            eval_item.get("category", ""),
        ]
    )


def top_sources(query_embedding: np.ndarray, indexed_cards: list[dict[str, Any]], k: int = 5) -> list[dict[str, Any]]:
    best_by_source: dict[str, dict[str, Any]] = {}
    for item in indexed_cards:
        score = float(np.dot(query_embedding, item["embedding"]))
        source_id = item["source_id"]
        if source_id not in best_by_source or score > best_by_source[source_id]["score"]:
            best_by_source[source_id] = {
                "source_id": source_id,
                "card_id": item["card_id"],
                "score": round(score, 6),
            }
    return sorted(best_by_source.values(), key=lambda row: row["score"], reverse=True)[:k]


def category_summary(results: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    counts: dict[str, int] = defaultdict(int)
    top1: dict[str, int] = defaultdict(int)
    top5: dict[str, int] = defaultdict(int)
    for row in results:
        category = row["category"]
        counts[category] += 1
        top1[category] += int(row["source_recall_at_1"])
        top5[category] += int(row["source_recall_at_5"])
    return {
        category: {
            "count": count,
            "source_recall_at_1": round(top1[category] / count, 4),
            "source_recall_at_5": round(top5[category] / count, 4),
        }
        for category, count in sorted(counts.items())
    }


def load_hash_metrics() -> dict[str, Any] | None:
    if not HASH_EVAL_PATH.exists():
        return None
    return json.loads(HASH_EVAL_PATH.read_text(encoding="utf-8"))["metrics"]


def main() -> None:
    started = time.perf_counter()
    cards = read_jsonl(CARD_PATH)
    eval_items = read_jsonl(EVAL_PATH)
    sources = read_sources(SOURCE_REGISTER_PATH)

    if not MODEL_PATH.exists():
        raise SystemExit(f"Missing local model snapshot: {MODEL_PATH}")

    model = SentenceTransformer(str(MODEL_PATH), local_files_only=True, device="cpu")
    smoke = model.encode(["维度确认"], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    dimension = int(smoke.shape[1])
    if dimension != EMBEDDING_DIMENSION:
        raise SystemExit(f"Unexpected embedding dimension: {dimension}")

    card_texts = []
    indexed_cards = []
    for card in cards:
        source = sources[card["source_id"]]
        text = indexed_text(card, source)
        card_texts.append(text)
        indexed_cards.append(
            {
                "card_id": card["card_id"],
                "card_type": card["card_type"],
                "source_id": card["source_id"],
                "workspace": card["workspace"],
                "evidence_grade": card["evidence_grade"],
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )

    card_embeddings = model.encode(
        card_texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    for item, embedding in zip(indexed_cards, card_embeddings, strict=True):
        item["embedding"] = embedding.astype("float32")

    query_texts = [QUERY_INSTRUCTION + query_text(item) for item in eval_items]
    query_embeddings = model.encode(
        query_texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    eval_results = []
    for item, q_embedding in zip(eval_items, query_embeddings, strict=True):
        ranked = top_sources(q_embedding.astype("float32"), indexed_cards, k=5)
        allowed = set(item.get("allowed_source_ids", []))
        top_ids = [row["source_id"] for row in ranked]
        eval_results.append(
            {
                "eval_id": item["eval_id"],
                "category": item["category"],
                "allowed_source_ids": sorted(allowed),
                "top_sources": ranked,
                "source_recall_at_1": bool(top_ids and top_ids[0] in allowed),
                "source_recall_at_5": bool(allowed.intersection(top_ids)),
            }
        )

    elapsed = round(time.perf_counter() - started, 3)
    total = len(eval_results)
    hash_metrics = load_hash_metrics()
    metrics = {
        "embedding_method": "real_local_model",
        "model_id": MODEL_ID,
        "model_snapshot": MODEL_SNAPSHOT,
        "model_path": str(MODEL_PATH),
        "model_license": MODEL_LICENSE,
        "embedding_dimension": dimension,
        "query_instruction": QUERY_INSTRUCTION,
        "provider_call_boundary": "no KB provider call",
        "production_impact": "production unchanged",
        "runtime_python": sys.executable,
        "runtime_python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "sentence_transformers_version": sentence_transformers.__version__,
        "indexed_card_count": len(indexed_cards),
        "eval_count": total,
        "elapsed_seconds": elapsed,
        "source_recall_at_1": round(sum(r["source_recall_at_1"] for r in eval_results) / total, 4),
        "source_recall_at_5": round(sum(r["source_recall_at_5"] for r in eval_results) / total, 4),
        "category_metrics": category_summary(eval_results),
        "hash_poc_baseline": {
            "source_recall_at_1": hash_metrics.get("source_recall_at_1") if hash_metrics else None,
            "source_recall_at_5": hash_metrics.get("source_recall_at_5") if hash_metrics else None,
        },
    }

    index_payload = {
        "metadata": {
            "created_at": "2026-06-19",
            "embedding_method": "real_local_model",
            "model_id": MODEL_ID,
            "model_snapshot": MODEL_SNAPSHOT,
            "model_license": MODEL_LICENSE,
            "embedding_dimension": dimension,
            "provider_call_boundary": "no KB provider call",
            "production_impact": "production unchanged",
            "source": str(CARD_PATH.relative_to(ROOT)),
        },
        "cards": [
            {key: value for key, value in item.items() if key != "embedding"}
            for item in indexed_cards
        ],
    }
    INDEX_OUT.write_text(json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    EVAL_OUT.write_text(
        json.dumps({"metrics": metrics, "results": eval_results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report = f"""---
title: "Consultant Role KB Real Local Embedding Indexing PoC Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-card-samples-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
scope: "real local embedding and indexing PoC for consultant role KB typed cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local PoC only; no live KB ingestion"
---

# Consultant Role KB Real Local Embedding Indexing PoC Report

## 0. Boundary

This PoC uses a local cached embedding model through local Python dependencies. It does not call a provider, does not deploy a service, and does not write to a live KB.

The index is a local artifact for evaluating typed-card retrieval plumbing and source recall. It is not production-ready.

## 1. Model Lock

| field | value |
|---|---|
| model_id | `{MODEL_ID}` |
| model_snapshot | `{MODEL_SNAPSHOT}` |
| model_license | `{MODEL_LICENSE}` |
| embedding_dimension | {dimension} |
| query_instruction | `{QUERY_INSTRUCTION}` |
| runtime_python | `{sys.executable}` |
| torch_version | `{torch.__version__}` |
| transformers_version | `{transformers.__version__}` |
| sentence_transformers_version | `{sentence_transformers.__version__}` |

## 2. Inputs And Outputs

| artifact | path |
|---|---|
| input cards | `tmp/consultant-role-kb-card-samples-20260619.jsonl` |
| eval set | `drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl` |
| source register | `drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv` |
| local index metadata | `tmp/consultant-role-kb-bge-small-zh-index-20260619.json` |
| retrieval eval result | `tmp/consultant-role-kb-bge-small-zh-retrieval-eval-20260619.json` |

## 3. Metrics

| metric | value |
|---|---:|
| indexed_card_count | {metrics["indexed_card_count"]} |
| eval_count | {metrics["eval_count"]} |
| elapsed_seconds | {metrics["elapsed_seconds"]} |
| source_recall_at_1 | {metrics["source_recall_at_1"]} |
| source_recall_at_5 | {metrics["source_recall_at_5"]} |
| hash_baseline_source_recall_at_1 | {metrics["hash_poc_baseline"]["source_recall_at_1"]} |
| hash_baseline_source_recall_at_5 | {metrics["hash_poc_baseline"]["source_recall_at_5"]} |

## 4. Category Metrics

| category | count | source_recall_at_1 | source_recall_at_5 |
|---|---:|---:|---:|
"""
    for category, row in metrics["category_metrics"].items():
        report += f"| {category} | {row['count']} | {row['source_recall_at_1']} | {row['source_recall_at_5']} |\n"

    report += """
## 5. Interpretation

The real local embedding path is executable with the cached BGE model and preserves typed-card metadata through indexing and retrieval eval.

This still does not prove production readiness. The eval measures source recall over 33 synthetic typed-card samples, not answer quality, citation precision, legal clearance, or live KB behavior.

`refusal_unknown` should continue to be scored with refusal-policy compliance in addition to retrieval source recall, because several refusal cases intentionally have no allowed source or test blocked-action routing.

## 6. Next Gates

1. Treat `BAAI/bge-small-zh-v1.5` with 512 dimensions as the locked P1 local embedding candidate unless a formal ADR replaces it.
2. Expand card extraction beyond 33 samples only after schema review.
3. Add citation precision checks once cards carry page/slide/sheet anchors.
4. Keep all sources at `evidence_grade=C` and `license_status=pending_legal_review`.
5. Do not promote this to production; permitted statement remains `real local embedding/indexing PoC executed`.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")

    adr = f"""---
title: "ADR-001 Consultant Role KB Local Embedding Model"
status: "draft"
created_at: "2026-06-19"
scope: "embedding model lock for consultant role KB P1 local PoC"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
---

# ADR-001 Consultant Role KB Local Embedding Model

## Decision

Use `{MODEL_ID}` as the P1 local embedding candidate for the consultant-role KB PoC.

## Locked Parameters

| field | value |
|---|---|
| model_id | `{MODEL_ID}` |
| model_snapshot | `{MODEL_SNAPSHOT}` |
| embedding_dimension | {dimension} |
| license | `{MODEL_LICENSE}` based on local model README |
| runtime | Homebrew Python 3.12 + sentence-transformers |
| query_instruction | `{QUERY_INSTRUCTION}` |
| passage_instruction | none |

## Rationale

- The role KB output is Chinese-first with retained English methodology terms.
- The model is already cached locally and can run without a provider call.
- The measured output dimension is 512 and therefore can be locked before durable indexing.
- The local README marks the model/license line as MIT.

## Constraints

- This is a P1 local PoC lock, not production model selection.
- Any future model replacement requires full re-embedding and eval rerun.
- License remains recorded from local README and should still be included in broader legal review.
"""
    ADR_OUT.write_text(adr, encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
