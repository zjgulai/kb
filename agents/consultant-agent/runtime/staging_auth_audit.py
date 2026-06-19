#!/usr/bin/env python3
"""Local staging auth/audit harness for consultant-agent retrieval.

Boundary: local validation only. No provider call, no live KB ingestion, no
staging deployment, and no raw source-text audit logging.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from local_retrieval_api import DEFAULT_HOST, DEFAULT_PORT, LocalRetrievalService


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_AUDIT_PATH = ROOT / "tmp/consultant-role-kb-local-staging-audit-events-20260619.jsonl"
PROTECTED_ENDPOINTS = {"/retrieve", "/eval/label-seed"}
ROLE_ENDPOINTS = {
    "retrieval_reader": {"/retrieve"},
    "reviewer": {"/retrieve", "/eval/label-seed"},
    "admin": {"/retrieve", "/eval/label-seed"},
}


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def bearer_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def utc_ts() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def audit_event_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"audit_{stamp}_{secrets.token_hex(6)}"


@dataclass(frozen=True)
class StagingAuthConfig:
    token_sha256: str
    audit_path: Path = DEFAULT_AUDIT_PATH
    production_impact: str = "production unchanged"
    provider_call_boundary: str = "no KB provider call"


class JsonlAuditWriter:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


class StagingAuthAuditService:
    def __init__(
        self,
        retrieval_service: LocalRetrievalService | None = None,
        config: StagingAuthConfig | None = None,
        audit_writer: JsonlAuditWriter | None = None,
    ) -> None:
        token_hash = os.environ.get("KB_STAGING_AUTH_TOKEN_SHA256", "")
        audit_path = Path(os.environ.get("KB_STAGING_AUDIT_PATH", str(DEFAULT_AUDIT_PATH)))
        self.config = config or StagingAuthConfig(token_sha256=token_hash, audit_path=audit_path)
        if not self.config.token_sha256:
            raise RuntimeError("KB_STAGING_AUTH_TOKEN_SHA256 is required for the local staging harness")
        self.retrieval_service = retrieval_service or LocalRetrievalService()
        self.audit_writer = audit_writer or JsonlAuditWriter(self.config.audit_path)

    def health(self) -> dict[str, Any]:
        base = self.retrieval_service.health()
        return {
            **base,
            "service": "consultant-agent-local-staging-auth-audit-harness",
            "auth_boundary": "bearer token hash; token not stored in repo",
            "audit_path": str(self.config.audit_path),
            "staging_deployment": "not deployed",
        }

    def handle(self, endpoint: str, headers: dict[str, str], payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        auth_status, blocked_reason, context = self._authorize(endpoint, headers)
        if auth_status != HTTPStatus.OK:
            response = self._error(blocked_reason, auth_status)
            self._audit(endpoint, payload, response, context, "denied", blocked_reason)
            return int(auth_status), response

        if endpoint == "/retrieve":
            body = {
                **payload,
                "workspace": "consultant-p1",
                "agent_id": "consultant-agent",
            }
            response = self.retrieval_service.retrieve(body)
        elif endpoint == "/eval/label-seed":
            response = self.retrieval_service.eval_label_seed(top_k=int(payload.get("top_k", 5)))
        else:
            response = self._error("not_found", HTTPStatus.NOT_FOUND)
            self._audit(endpoint, payload, response, context, "denied", "not_found")
            return HTTPStatus.NOT_FOUND, response

        decision = "allowed"
        if response.get("status") == "policy_refusal":
            decision = "policy_refusal"
        self._audit(endpoint, payload, response, context, decision, None)
        return HTTPStatus.OK, response

    def _authorize(self, endpoint: str, headers: dict[str, str]) -> tuple[HTTPStatus, str | None, dict[str, str]]:
        role = headers.get("x-kb-role", "")
        context = {
            "request_id": headers.get("x-kb-request-id", "missing-request-id"),
            "reviewer": headers.get("x-kb-reviewer", ""),
            "role": role if role in ROLE_ENDPOINTS else "retrieval_reader",
            "agent_id": headers.get("x-kb-agent", ""),
            "workspace": headers.get("x-kb-workspace", ""),
        }
        if endpoint not in PROTECTED_ENDPOINTS:
            return HTTPStatus.NOT_FOUND, "not_found", context
        if not context["request_id"] or context["request_id"] == "missing-request-id":
            return HTTPStatus.BAD_REQUEST, "missing_request_id", context
        if context["agent_id"] != "consultant-agent" or context["workspace"] != "consultant-p1":
            return HTTPStatus.FORBIDDEN, "workspace_or_agent_forbidden", context
        if not context["reviewer"]:
            return HTTPStatus.BAD_REQUEST, "missing_reviewer", context
        if role not in ROLE_ENDPOINTS:
            return HTTPStatus.FORBIDDEN, "role_forbidden", context
        if endpoint not in ROLE_ENDPOINTS[role]:
            return HTTPStatus.FORBIDDEN, "endpoint_forbidden_for_role", context
        auth = headers.get("authorization", "")
        prefix = "Bearer "
        if not auth.startswith(prefix):
            return HTTPStatus.UNAUTHORIZED, "missing_bearer_token", context
        token = auth[len(prefix) :]
        if not secrets.compare_digest(bearer_hash(token), self.config.token_sha256):
            return HTTPStatus.UNAUTHORIZED, "invalid_bearer_token", context
        return HTTPStatus.OK, None, context

    def _audit(
        self,
        endpoint: str,
        payload: dict[str, Any],
        response: dict[str, Any],
        context: dict[str, str],
        decision: str,
        blocked_reason: str | None,
    ) -> None:
        question = str(payload.get("question") or "")
        results = response.get("results") or []
        result_refs = []
        for row in results[:10]:
            if not {"source_id", "card_id", "locator", "evidence_grade", "license_status"}.issubset(row):
                continue
            result_refs.append(
                {
                    "source_id": row["source_id"],
                    "card_id": row["card_id"],
                    "locator": row["locator"],
                    "evidence_grade": row["evidence_grade"],
                    "license_status": row["license_status"],
                }
            )
        event = {
            "event_id": audit_event_id(),
            "ts": utc_ts(),
            "request_id": context.get("request_id") or "missing-request-id",
            "actor_id_hash": sha256_text(context.get("reviewer", "")),
            "actor_role": context.get("role", "retrieval_reader"),
            "agent_id": "consultant-agent",
            "workspace": "consultant-p1",
            "endpoint": endpoint if endpoint in PROTECTED_ENDPOINTS else "/retrieve",
            "retrieval_mode": (
                response.get("retrieval_mode") or "local_bge_vector_plus_deterministic_rerank"
                if decision == "allowed"
                else "none_policy_refusal"
            ),
            "query_sha256": sha256_text(question),
            "query_length": len(question),
            "eval_id": payload.get("eval_id"),
            "result_count": len(result_refs),
            "result_refs": result_refs,
            "decision": decision,
            "blocked_reason": blocked_reason,
            "provider_call_count": 0,
            "live_kb_write_count": 0,
            "production_impact": "production unchanged",
            "source_text_returned": False,
        }
        self.audit_writer.write(event)

    @staticmethod
    def _error(code: str | None, status: HTTPStatus) -> dict[str, Any]:
        return {
            "ok": False,
            "status": int(status),
            "error": {
                "code": code or "unknown_error",
                "message": "Request rejected by local staging auth/audit harness.",
            },
        }


def make_staging_handler(service: StagingAuthAuditService) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "ConsultantLocalStagingHarness/0.1"

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
            self._send(StagingAuthAuditService._error("not_found", HTTPStatus.NOT_FOUND), 404)

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except json.JSONDecodeError:
                payload = {}
            headers = {key.lower(): value for key, value in self.headers.items()}
            status, response = service.handle(self.path, headers, payload)
            self._send(response, int(status))

    return Handler


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    service = StagingAuthAuditService()
    server = ThreadingHTTPServer((host, port), make_staging_handler(service))
    print(json.dumps({"ok": True, "url": f"http://{host}:{server.server_port}", **service.health()}, ensure_ascii=False))
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run consultant-agent local staging auth/audit harness.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
