#!/usr/bin/env python3
"""Build a durable local vector-store package for all-extractable consultant cards.

Boundary: local indexing only. No provider call, no live KB ingestion, no
production deployment, and no raw source-text redistribution.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import sentence_transformers
import torch
import transformers
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[1]
BGE_SCRIPT = ROOT / "tmp/consultant_role_kb_real_embedding_poc_20260619.py"
RERANK_SCRIPT = ROOT / "tmp/consultant_role_kb_rerank_source_prior_poc_20260619.py"
CARD_PATH = ROOT / "tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl"
EVAL_SET_PATH = ROOT / "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
SOURCE_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"

INDEX_DIR = ROOT / "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619"
RECORDS_OUT = INDEX_DIR / "records.jsonl"
EMBEDDINGS_OUT = INDEX_DIR / "embeddings.float32.npy"
MANIFEST_OUT = INDEX_DIR / "manifest.json"
CHECKSUMS_OUT = INDEX_DIR / "checksums.json"
SMOKE_OUT = ROOT / "tmp/consultant-role-kb-all-extractable-vector-store-smoke-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-all-extractable-vector-store-report-20260619.md"

ANSWER_TRACE_FIXTURE_IDS = {
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
}


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_for_card(card: dict[str, Any], source: dict[str, str], embedding_row: int, retrieval_text: str) -> dict[str, Any]:
    anchors = card.get("source_anchors") or []
    anchor = anchors[0] if anchors else {}
    return {
        "embedding_row": embedding_row,
        "card_id": card["card_id"],
        "card_type": card["card_type"],
        "card_status": card.get("card_status"),
        "workspace": card["workspace"],
        "domain": card["domain"],
        "layer": card.get("layer"),
        "source_id": card["source_id"],
        "source_title": source["source_title"],
        "source_type": card["source_type"],
        "source_owner": card["source_owner"],
        "source_uri": card["source_uri"],
        "source_version": card["source_version"],
        "evidence_grade": card["evidence_grade"],
        "license_status": card["license_status"],
        "allowed_agents": card["allowed_agents"],
        "blocked_actions": card["blocked_actions"],
        "source_unit_locator": card.get("source_unit_locator"),
        "source_anchors": anchors,
        "locator_type": anchor.get("locator_type"),
        "locator": anchor.get("locator"),
        "indexed_text_sha256": hashlib.sha256(retrieval_text.encode("utf-8")).hexdigest(),
        "routing_text": retrieval_text.lower(),
        "retrieval_terms": anchor.get("matched_terms", [])[:8],
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
    }


def load_records_and_embeddings() -> tuple[list[dict[str, Any]], np.ndarray]:
    records = read_jsonl(RECORDS_OUT)
    embeddings = np.load(EMBEDDINGS_OUT)
    if len(records) != embeddings.shape[0]:
        raise RuntimeError(f"records/embeddings mismatch: {len(records)} vs {embeddings.shape[0]}")
    return records, embeddings


def best_by_source(ranked_rows: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for row in ranked_rows:
        source_id = row["source_id"]
        if source_id not in best or row["score"] > best[source_id]["score"]:
            best[source_id] = row
    return sorted(best.values(), key=lambda item: item["score"], reverse=True)[:top_k]


def vector_search(
    query_embedding: np.ndarray,
    records: list[dict[str, Any]],
    embeddings: np.ndarray,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    scores = embeddings @ query_embedding
    ranked_indices = np.argsort(-scores)[: min(len(scores), top_k * 12)]
    candidates = []
    for idx in ranked_indices:
        record = records[int(idx)]
        candidates.append(
            {
                "source_id": record["source_id"],
                "card_id": record["card_id"],
                "card_type": record["card_type"],
                "locator": record["locator"],
                "locator_type": record["locator_type"],
                "score": float(scores[int(idx)]),
            }
        )
    top = best_by_source(candidates, top_k=top_k)
    for row in top:
        row["score"] = round(row["score"], 6)
    return top


def reranked_search(
    eval_item: dict[str, Any],
    query_embedding: np.ndarray,
    records: list[dict[str, Any]],
    embeddings: np.ndarray,
    rerank: Any,
    source_text: dict[str, str],
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    rows = []
    scores = embeddings @ query_embedding
    for idx, record in enumerate(records):
        card = {
            "source_id": record["source_id"],
            "card_id": record["card_id"],
            "card_type": record["card_type"],
            "_text": record.get("routing_text", ""),
        }
        base_score = float(scores[idx])
        keyword_delta = rerank.keyword_prior(query, card, source_text)
        card_delta = rerank.category_card_prior(eval_item, card)
        source_intent_delta = rerank.source_intent_prior(eval_item, card)
        final_score = base_score + keyword_delta + card_delta + source_intent_delta
        rows.append(
            {
                "source_id": record["source_id"],
                "card_id": record["card_id"],
                "card_type": record["card_type"],
                "locator": record["locator"],
                "locator_type": record["locator_type"],
                "base_score": round(base_score, 6),
                "keyword_prior": round(keyword_delta, 6),
                "card_type_prior": round(card_delta, 6),
                "source_intent_prior": round(source_intent_delta, 6),
                "score": round(final_score, 6),
            }
        )
    return best_by_source(rows, top_k=top_k)


def eval_smoke(model: SentenceTransformer, bge: Any, rerank: Any) -> dict[str, Any]:
    eval_items = read_jsonl(EVAL_SET_PATH)
    records, embeddings = load_records_and_embeddings()
    source_text = {}
    for record in records:
        source_text.setdefault(record["source_id"], f"{record['source_title']} {record.get('routing_text', '')}".lower())
    query_texts = [bge.QUERY_INSTRUCTION + bge.query_text(item) for item in eval_items]
    query_embeddings = model.encode(
        query_texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype("float32")

    rows = []
    for item, embedding in zip(eval_items, query_embeddings, strict=True):
        vector_top_sources = vector_search(embedding, records, embeddings, top_k=5)
        reranked_top_sources = reranked_search(
            item,
            embedding,
            records,
            embeddings,
            rerank,
            source_text,
            bge.query_text(item),
            top_k=5,
        )
        allowed = set(item.get("allowed_source_ids", []))
        vector_top_ids = [row["source_id"] for row in vector_top_sources]
        reranked_top_ids = [row["source_id"] for row in reranked_top_sources]
        rows.append(
            {
                "eval_id": item["eval_id"],
                "category": item["category"],
                "answer_trace_fixture": item["eval_id"] in ANSWER_TRACE_FIXTURE_IDS,
                "allowed_source_ids": sorted(allowed),
                "vector_top_sources": vector_top_sources,
                "reranked_top_sources": reranked_top_sources,
                "vector_source_recall_at_1": bool(vector_top_ids and vector_top_ids[0] in allowed),
                "vector_source_recall_at_5": bool(allowed.intersection(vector_top_ids)),
                "reranked_source_recall_at_1": bool(reranked_top_ids and reranked_top_ids[0] in allowed),
                "reranked_source_recall_at_5": bool(allowed.intersection(reranked_top_ids)),
                "top1_has_unit_anchor": bool(reranked_top_sources and reranked_top_sources[0]["locator"]),
            }
        )

    answerable = [row for row in rows if row["allowed_source_ids"]]
    fixture_rows = [row for row in rows if row["answer_trace_fixture"] and row["allowed_source_ids"]]
    metrics = {
        "indexed_card_count": len(records),
        "embedding_rows": int(embeddings.shape[0]),
        "embedding_dimension": int(embeddings.shape[1]),
        "eval_count": len(rows),
        "answerable_eval_count": len(answerable),
        "answerable_vector_source_recall_at_1": round(sum(row["vector_source_recall_at_1"] for row in answerable) / len(answerable), 4),
        "answerable_vector_source_recall_at_5": round(sum(row["vector_source_recall_at_5"] for row in answerable) / len(answerable), 4),
        "answerable_reranked_source_recall_at_1": round(sum(row["reranked_source_recall_at_1"] for row in answerable) / len(answerable), 4),
        "answerable_reranked_source_recall_at_5": round(sum(row["reranked_source_recall_at_5"] for row in answerable) / len(answerable), 4),
        "fixture_answerable_reranked_source_recall_at_5": round(sum(row["reranked_source_recall_at_5"] for row in fixture_rows) / len(fixture_rows), 4),
        "top1_unit_anchor_rate": round(sum(row["top1_has_unit_anchor"] for row in rows) / len(rows), 4),
        "provider_call_count": 0,
        "live_kb_write_count": 0,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
    }
    payload = {"metrics": metrics, "results": rows}
    SMOKE_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def write_report(manifest: dict[str, Any], smoke: dict[str, Any]) -> None:
    metrics = smoke["metrics"]
    report = f"""---
title: "Consultant Role KB All-Extractable Vector Store Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl"
  - "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/manifest.json"
scope: "durable local vector-store package for consultant-agent all-extractable cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local vector index only; no live KB ingestion"
---

# Consultant Role KB All-Extractable Vector Store Report

## 0. Boundary

This index is a local durable artifact. It does not call a provider, write into
a live KB, deploy production code, approve source licensing, or redistribute raw
source text.

## 1. Index Package

| artifact | path |
|---|---|
| manifest | `{manifest["files"]["manifest"]}` |
| records | `{manifest["files"]["records"]}` |
| embeddings | `{manifest["files"]["embeddings"]}` |
| checksums | `{manifest["files"]["checksums"]}` |
| smoke | `tmp/consultant-role-kb-all-extractable-vector-store-smoke-20260619.json` |

## 2. Build Metrics

| metric | value |
|---|---:|
| indexed_card_count | {metrics["indexed_card_count"]} |
| embedding_rows | {metrics["embedding_rows"]} |
| embedding_dimension | {metrics["embedding_dimension"]} |
| answerable_vector_source_recall@1 | {metrics["answerable_vector_source_recall_at_1"]} |
| answerable_vector_source_recall@5 | {metrics["answerable_vector_source_recall_at_5"]} |
| answerable_reranked_source_recall@1 | {metrics["answerable_reranked_source_recall_at_1"]} |
| answerable_reranked_source_recall@5 | {metrics["answerable_reranked_source_recall_at_5"]} |
| fixture_answerable_reranked_source_recall@5 | {metrics["fixture_answerable_reranked_source_recall_at_5"]} |
| top1_unit_anchor_rate | {metrics["top1_unit_anchor_rate"]} |
| provider_call_count | {metrics["provider_call_count"]} |
| live_kb_write_count | {metrics["live_kb_write_count"]} |

## 3. Interpretation

Fact: the all-extractable card set now has a reusable local vector-store package
with row-aligned metadata, routing text, and normalized BGE embeddings.

Inference: the raw vector index should be used with the deterministic rerank
layer for agent retrieval; raw vector-only recall is recorded as a lower-bound
diagnostic, not the acceptance path.

Unknown: this does not prove production readiness, legal clearance, human-gold
locator precision, or provider-backed answer quality.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    started = time.perf_counter()
    bge = load_module("consultant_bge_vector_store", BGE_SCRIPT)
    rerank = load_module("consultant_rerank_vector_store", RERANK_SCRIPT)
    cards = read_jsonl(CARD_PATH)
    sources = read_sources(SOURCE_REGISTER_PATH)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(str(bge.MODEL_PATH), local_files_only=True, device="cpu")
    texts: list[str] = []
    records: list[dict[str, Any]] = []
    for row_id, card in enumerate(cards):
        source = sources[card["source_id"]]
        text = bge.indexed_text(card, source)
        texts.append(text)
        records.append(record_for_card(card, source, row_id, text))

    embeddings = model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype("float32")
    np.save(EMBEDDINGS_OUT, embeddings)
    RECORDS_OUT.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )

    checksums = {
        "records_sha256": sha256_file(RECORDS_OUT),
        "embeddings_sha256": sha256_file(EMBEDDINGS_OUT),
        "source_cards_sha256": sha256_file(CARD_PATH),
    }
    CHECKSUMS_OUT.write_text(json.dumps(checksums, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "created_at": "2026-06-19",
        "index_id": "consultant-agent-all-extractable-bge-small-zh-v1-5-20260619",
        "role_agent": "consultant-agent",
        "domain": "consulting-kb",
        "workspace": "consultant-p1",
        "status": "local_draft",
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "implementation_status": "local vector index only; no live KB ingestion",
        "source_cards": str(CARD_PATH.relative_to(ROOT)),
        "source_register": str(SOURCE_REGISTER_PATH.relative_to(ROOT)),
        "model": {
            "model_id": bge.MODEL_ID,
            "model_snapshot": bge.MODEL_SNAPSHOT,
            "model_path": str(bge.MODEL_PATH),
            "model_license": bge.MODEL_LICENSE,
            "embedding_dimension": int(embeddings.shape[1]),
            "normalize_embeddings": True,
            "query_instruction": bge.QUERY_INSTRUCTION,
        },
        "runtime": {
            "python": sys.executable,
            "python_version": platform.python_version(),
            "torch_version": torch.__version__,
            "transformers_version": transformers.__version__,
            "sentence_transformers_version": sentence_transformers.__version__,
        },
        "counts": {
            "records": len(records),
            "embedding_rows": int(embeddings.shape[0]),
            "source_count": len({record["source_id"] for record in records}),
        },
        "files": {
            "manifest": str(MANIFEST_OUT.relative_to(ROOT)),
            "records": str(RECORDS_OUT.relative_to(ROOT)),
            "embeddings": str(EMBEDDINGS_OUT.relative_to(ROOT)),
            "checksums": str(CHECKSUMS_OUT.relative_to(ROOT)),
        },
        "checksums": checksums,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    # Recompute manifest checksum after manifest is written.
    checksums["manifest_sha256"] = sha256_file(MANIFEST_OUT)
    CHECKSUMS_OUT.write_text(json.dumps(checksums, ensure_ascii=False, indent=2), encoding="utf-8")

    smoke = eval_smoke(model, bge, rerank)
    manifest["smoke_metrics"] = smoke["metrics"]
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    checksums["manifest_sha256"] = sha256_file(MANIFEST_OUT)
    checksums["smoke_sha256"] = sha256_file(SMOKE_OUT)
    CHECKSUMS_OUT.write_text(json.dumps(checksums, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(manifest, smoke)

    print(
        json.dumps(
            {
                "manifest": manifest,
                "smoke_metrics": smoke["metrics"],
                "outputs": [
                    str(MANIFEST_OUT),
                    str(RECORDS_OUT),
                    str(EMBEDDINGS_OUT),
                    str(CHECKSUMS_OUT),
                    str(SMOKE_OUT),
                    str(REPORT_OUT),
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
