#!/usr/bin/env python3
"""Private local retrieval API for consultant-agent.

Boundary: localhost/private use only. No provider call, no live KB ingestion,
no production deployment, and no raw source-text response.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = ROOT / "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619"
MANIFEST_PATH = INDEX_DIR / "manifest.json"
RECORDS_PATH = INDEX_DIR / "records.jsonl"
EMBEDDINGS_PATH = INDEX_DIR / "embeddings.float32.npy"
EVAL_SET_PATH = ROOT / "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
LABEL_SEED_PATH = ROOT / "shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl"
BGE_SCRIPT = ROOT / "tmp/consultant_role_kb_real_embedding_poc_20260619.py"
RERANK_SCRIPT = ROOT / "tmp/consultant_role_kb_rerank_source_prior_poc_20260619.py"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_TOP_K = 10


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


def best_by_source(rows: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for row in rows:
        source_id = row["source_id"]
        if source_id not in best or row["score"] > best[source_id]["score"]:
            best[source_id] = row
    return sorted(best.values(), key=lambda item: item["score"], reverse=True)[:top_k]


def public_result(row: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record["source_id"],
        "source_title": record["source_title"],
        "source_type": record["source_type"],
        "source_uri": record["source_uri"],
        "card_id": record["card_id"],
        "card_type": record["card_type"],
        "locator": record["locator"],
        "locator_type": record["locator_type"],
        "workspace": record["workspace"],
        "evidence_grade": record["evidence_grade"],
        "license_status": record["license_status"],
        "allowed_agents": record["allowed_agents"],
        "blocked_actions": record["blocked_actions"],
        "scores": {
            "base_score": row.get("base_score"),
            "keyword_prior": row.get("keyword_prior"),
            "card_type_prior": row.get("card_type_prior"),
            "source_intent_prior": row.get("source_intent_prior"),
            "final_score": row["score"],
        },
        "source_trace": {
            "source_id": record["source_id"],
            "source_uri": record["source_uri"],
            "source_unit_locator": record["source_unit_locator"],
            "indexed_text_sha256": record["indexed_text_sha256"],
        },
        "content_boundary": "no raw source text returned",
    }


class LocalRetrievalService:
    """Local-only retrieval service backed by the durable vector store."""

    def __init__(self) -> None:
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.records = read_jsonl(RECORDS_PATH)
        self.embeddings = np.load(EMBEDDINGS_PATH, mmap_mode="r")
        self.eval_items = {row["eval_id"]: row for row in read_jsonl(EVAL_SET_PATH)}
        self.labels = {row["eval_id"]: row for row in read_jsonl(LABEL_SEED_PATH)}
        self.bge = load_module("consultant_agent_api_bge", BGE_SCRIPT)
        self.rerank = load_module("consultant_agent_api_rerank", RERANK_SCRIPT)
        self.model: SentenceTransformer | None = None
        self.source_text: dict[str, str] = {}
        for record in self.records:
            self.source_text.setdefault(
                record["source_id"],
                f"{record['source_title']} {record.get('routing_text', '')}".lower(),
            )
        self.records_by_card = {record["card_id"]: record for record in self.records}
        self._validate_index()

    def _validate_index(self) -> None:
        if len(self.records) != int(self.embeddings.shape[0]):
            raise RuntimeError(f"records/embeddings mismatch: {len(self.records)} vs {self.embeddings.shape[0]}")
        if self.manifest["provider_call_boundary"] != "no KB provider call":
            raise RuntimeError("manifest provider boundary mismatch")
        if self.manifest["implementation_status"] != "local vector index only; no live KB ingestion":
            raise RuntimeError("manifest ingestion boundary mismatch")

    def _model(self) -> SentenceTransformer:
        if self.model is None:
            self.model = SentenceTransformer(str(self.bge.MODEL_PATH), local_files_only=True, device="cpu")
        return self.model

    def _query_embedding(self, eval_item: dict[str, Any]) -> np.ndarray:
        query = self.bge.QUERY_INSTRUCTION + self.bge.query_text(eval_item)
        return self._model().encode([query], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)[
            0
        ].astype("float32")

    def health(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "consultant-agent-local-retrieval-api",
            "status": "local_draft",
            "host_boundary": "localhost/private",
            "production_impact": "production unchanged",
            "provider_call_boundary": "no KB provider call",
            "live_kb_ingestion": "no live KB ingestion",
            "record_count": len(self.records),
            "embedding_rows": int(self.embeddings.shape[0]),
            "embedding_dimension": int(self.embeddings.shape[1]),
            "label_seed_status": "pending_human_review",
        }

    def retrieve(self, payload: dict[str, Any]) -> dict[str, Any]:
        question = str(payload.get("question") or "").strip()
        if not question:
            return self.error("missing_question", "Request body must include a non-empty question.", HTTPStatus.BAD_REQUEST)
        workspace = payload.get("workspace", "consultant-p1")
        agent_id = payload.get("agent_id", "consultant-agent")
        if workspace != "consultant-p1" or agent_id != "consultant-agent":
            return self.error("workspace_or_agent_forbidden", "Only consultant-agent in consultant-p1 is allowed.", HTTPStatus.FORBIDDEN)
        top_k = max(1, min(int(payload.get("top_k", 5)), MAX_TOP_K))
        eval_id = payload.get("eval_id")
        eval_item = dict(self.eval_items.get(eval_id) or {})
        if eval_item:
            eval_item["question"] = question
        else:
            eval_item = {
                "eval_id": eval_id or "ADHOC",
                "question": question,
                "category": payload.get("category", "ad_hoc"),
                "required_domains": ["consulting-kb"],
                "required_shared_layers": [],
                "allowed_source_ids": [],
            }

        label = self.labels.get(eval_id)
        if label and label["label_type"] == "refusal_policy_no_source":
            return {
                "ok": True,
                "status": "policy_refusal",
                "eval_id": eval_id,
                "question": question,
                "retrieval_required": False,
                "results": [],
                "policy": self.policy_block(),
                "reason": "Label seed expects a refusal without registered-source citation.",
            }

        embedding = self._query_embedding(eval_item)
        scores = self.embeddings @ embedding
        rows: list[dict[str, Any]] = []
        for idx, record in enumerate(self.records):
            card = {
                "source_id": record["source_id"],
                "card_id": record["card_id"],
                "card_type": record["card_type"],
                "_text": record.get("routing_text", ""),
            }
            base_score = float(scores[idx])
            keyword_delta = self.rerank.keyword_prior(question, card, self.source_text)
            card_delta = self.rerank.category_card_prior(eval_item, card)
            source_intent_delta = self.rerank.source_intent_prior(eval_item, card)
            rows.append(
                {
                    "record_index": idx,
                    "source_id": record["source_id"],
                    "score": round(base_score + keyword_delta + card_delta + source_intent_delta, 6),
                    "base_score": round(base_score, 6),
                    "keyword_prior": round(keyword_delta, 6),
                    "card_type_prior": round(card_delta, 6),
                    "source_intent_prior": round(source_intent_delta, 6),
                }
            )

        deduped = best_by_source(rows, top_k)
        results = [public_result(row, self.records[row["record_index"]]) for row in deduped]
        return {
            "ok": True,
            "status": "retrieved",
            "eval_id": eval_id,
            "question": question,
            "retrieval_required": True,
            "retrieval_mode": "local_bge_vector_plus_deterministic_rerank",
            "results": results,
            "policy": self.policy_block(),
        }

    def eval_label_seed(self, top_k: int = 5) -> dict[str, Any]:
        rows = []
        locator_labels = [label for label in self.labels.values() if label["label_type"] == "locator_gold_candidate"]
        refusal_labels = [label for label in self.labels.values() if label["label_type"] == "refusal_policy_no_source"]
        for label in sorted(self.labels.values(), key=lambda item: item["eval_id"]):
            response = self.retrieve(
                {
                    "question": label["question"],
                    "eval_id": label["eval_id"],
                    "workspace": label["workspace"],
                    "agent_id": "consultant-agent",
                    "top_k": top_k,
                }
            )
            if label["label_type"] == "refusal_policy_no_source":
                policy_pass = (
                    response.get("status") == "policy_refusal"
                    and not response.get("results")
                ) or (
                    response.get("ok") is False
                    and (response.get("error") or {}).get("code") == "workspace_or_agent_forbidden"
                )
                rows.append(
                    {
                        "eval_id": label["eval_id"],
                        "label_type": label["label_type"],
                        "pass": policy_pass,
                        "status": response.get("status"),
                        "error_code": (response.get("error") or {}).get("code"),
                    }
                )
                continue
            candidate = label["gold_candidate"]
            target = (candidate["source_id"], candidate["locator"])
            ranked = [(row["source_id"], row["locator"]) for row in response["results"]]
            rows.append(
                {
                    "eval_id": label["eval_id"],
                    "label_type": label["label_type"],
                    "target_source_id": candidate["source_id"],
                    "target_locator": candidate["locator"],
                    "match_at_1": bool(ranked and ranked[0] == target),
                    "match_at_5": target in ranked,
                    "top1_source_id": response["results"][0]["source_id"] if response["results"] else None,
                    "top1_locator": response["results"][0]["locator"] if response["results"] else None,
                }
            )

        match_at_1 = sum(row.get("match_at_1", False) for row in rows if row["label_type"] == "locator_gold_candidate")
        match_at_5 = sum(row.get("match_at_5", False) for row in rows if row["label_type"] == "locator_gold_candidate")
        refusal_pass = sum(row.get("pass", False) for row in rows if row["label_type"] == "refusal_policy_no_source")
        return {
            "ok": True,
            "label_seed_status": "pending_human_review",
            "metrics": {
                "label_count": len(self.labels),
                "locator_label_count": len(locator_labels),
                "refusal_policy_no_source_count": len(refusal_labels),
                "locator_seed_match_at_1": round(match_at_1 / len(locator_labels), 4),
                "locator_seed_match_at_5": round(match_at_5 / len(locator_labels), 4),
                "policy_refusal_pass_rate": round(refusal_pass / len(refusal_labels), 4),
                "provider_call_count": 0,
                "live_kb_write_count": 0,
                "production_impact": "production unchanged",
                "provider_call_boundary": "no KB provider call",
            },
            "results": rows,
        }

    @staticmethod
    def policy_block() -> dict[str, Any]:
        return {
            "production_impact": "production unchanged",
            "provider_call_boundary": "no KB provider call",
            "live_kb_ingestion": "no live KB ingestion",
            "license_status_boundary": "pending_legal_review",
            "manual_review_boundary": "manual review required for label approval and client-ready output",
            "blocked_response_content": ["raw_source_text", "client_ready_publication", "provider_generation"],
        }

    @staticmethod
    def error(code: str, message: str, status: HTTPStatus) -> dict[str, Any]:
        return {"ok": False, "status": int(status), "error": {"code": code, "message": message}}


def make_handler(service: LocalRetrievalService) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "ConsultantLocalRetrievalAPI/0.1"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

        def _send(self, payload: dict[str, Any], status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send(service.health())
                return
            self._send(LocalRetrievalService.error("not_found", "Unknown endpoint.", HTTPStatus.NOT_FOUND), 404)

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send(LocalRetrievalService.error("invalid_json", "Request body must be JSON.", HTTPStatus.BAD_REQUEST), 400)
                return
            if self.path == "/retrieve":
                response = service.retrieve(payload)
                self._send(response, int(response.get("status", 200)) if not response.get("ok") else 200)
                return
            if self.path == "/eval/label-seed":
                response = service.eval_label_seed(top_k=int(payload.get("top_k", 5)))
                self._send(response)
                return
            self._send(LocalRetrievalService.error("not_found", "Unknown endpoint.", HTTPStatus.NOT_FOUND), 404)

    return Handler


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    service = LocalRetrievalService()
    server = ThreadingHTTPServer((host, port), make_handler(service))
    print(json.dumps({"ok": True, "url": f"http://{host}:{server.server_port}", **service.health()}, ensure_ascii=False))
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run consultant-agent private local retrieval API.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
