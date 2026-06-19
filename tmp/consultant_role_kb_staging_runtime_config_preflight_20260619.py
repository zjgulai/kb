#!/usr/bin/env python3
"""Validate external runtime configuration for future shared staging.

Boundary: local preflight only. This does not configure secrets, approve
security controls, deploy staging, call a provider, or ingest into a live KB.
Secret values, raw tokens, passwords, private keys, and private contact details
must stay outside repository artifacts.
"""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "shared/governance/consultant-agent/staging-runtime-config.schema-20260619.json"
TEMPLATE = ROOT / "shared/governance/consultant-agent/staging-runtime-config.template-20260619.json"
OUT_JSON = ROOT / "tmp/consultant-role-kb-staging-runtime-config-preflight-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-staging-runtime-config-preflight-20260619.md"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0


def now_z() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_schema() -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Consultant Agent Staging Runtime Config",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "artifact_type",
            "created_at",
            "runtime_config_ready",
            "secret_redaction_boundary",
            "production_impact",
            "provider_call_boundary",
            "live_kb_ingestion",
        ],
        "properties": {
            "artifact_type": {
                "enum": ["staging_runtime_config_template", "staging_runtime_config_validation"],
            },
            "created_at": {"type": "string"},
            "schema": {"type": "string"},
            "template": {"type": "string"},
            "status": {"enum": ["ready", "blocked"]},
            "runtime_config_ready": {"type": "boolean"},
            "blocker_count": {"type": "integer"},
            "failure_count": {"type": "integer"},
            "blockers": {
                "type": "array",
                "items": {"type": "string"},
                "uniqueItems": True,
            },
            "required_environment": {
                "type": "array",
                "items": {"type": "object"},
            },
            "auth_token_hash_status": {
                "enum": ["missing", "configured_hash_present", "invalid_hash_format", "set_redacted"],
            },
            "audit_path_status": {
                "enum": [
                    "missing",
                    "inside_repo",
                    "parent_missing",
                    "parent_not_writable",
                    "external_writable_parent",
                ],
            },
            "rate_limit_status": {"enum": ["missing", "configured"]},
            "rollback_owner_status": {"enum": ["missing", "recorded_redacted"]},
            "private_ingress_status": {"enum": ["not_configured", "configured_externally", "localhost_only"]},
            "audit_path_detail": {"type": "string"},
            "private_ingress_note": {"type": "string"},
            "secret_value_logged": {"type": "boolean"},
            "private_contact_detail_logged": {"type": "boolean"},
            "source_text_returned": {"type": "boolean"},
            "provider_call_count": {"type": "integer"},
            "live_kb_write_count": {"type": "integer"},
            "secret_redaction_boundary": {
                "const": "do not store secret values, raw tokens, passwords, private keys, or private contact details in this repository",
            },
            "production_impact": {"const": "production unchanged"},
            "provider_call_boundary": {"const": "no KB provider call"},
            "live_kb_ingestion": {"const": "no live KB ingestion"},
        },
    }
    SCHEMA.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_template() -> None:
    template = {
        "artifact_type": "staging_runtime_config_template",
        "created_at": now_z(),
        "runtime_config_ready": False,
        "required_environment": [
            {
                "env": "KB_STAGING_AUTH_TOKEN_SHA256",
                "purpose": "SHA-256 hash of bearer token",
                "repository_rule": "hash status only; never commit raw token",
                "current_status": "not_configured",
            },
            {
                "env": "KB_STAGING_AUDIT_PATH",
                "purpose": "append-only audit JSONL path outside repository",
                "repository_rule": "path must resolve outside repository; audit content must avoid raw source text",
                "current_status": "not_configured",
            },
            {
                "env": "KB_STAGING_RATE_LIMIT_CONFIGURED",
                "purpose": "operator assertion that rate limiting is configured",
                "repository_rule": "status only; no private ingress config details",
                "current_status": "not_configured",
            },
            {
                "env": "KB_STAGING_ROLLBACK_OWNER",
                "purpose": "accountable rollback owner",
                "repository_rule": "record presence only; do not store private contact details",
                "current_status": "not_configured",
            },
            {
                "env": "KB_STAGING_PRIVATE_INGRESS_CONFIGURED",
                "purpose": "operator assertion for approved private ingress",
                "repository_rule": "status only; approval remains in security decision workflow",
                "current_status": "not_configured",
            },
        ],
        "secret_redaction_boundary": (
            "do not store secret values, raw tokens, passwords, private keys, or private contact details in this repository"
        ),
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
    }
    TEMPLATE.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def auth_token_hash_status() -> str:
    raw = os.environ.get("KB_STAGING_AUTH_TOKEN_SHA256", "").strip()
    if not raw:
        return "missing"
    if re.fullmatch(r"[0-9a-fA-F]{64}", raw):
        return "configured_hash_present"
    if any(term in raw.lower() for term in ["token", "secret", "password", "private"]):
        return "set_redacted"
    return "invalid_hash_format"


def audit_path_status() -> tuple[str, str]:
    raw = os.environ.get("KB_STAGING_AUDIT_PATH", "").strip()
    if not raw:
        return "missing", "environment variable is not set"
    path = Path(raw).expanduser()
    try:
        resolved = path.resolve()
        resolved.relative_to(ROOT)
        return "inside_repo", "path resolves inside repository"
    except ValueError:
        pass
    parent = resolved.parent
    if not parent.exists():
        return "parent_missing", "parent directory does not exist"
    if not os.access(parent, os.W_OK):
        return "parent_not_writable", "parent directory is not writable"
    return "external_writable_parent", "path is outside repository and parent is writable"


def boolean_env_status(name: str) -> str:
    raw = os.environ.get(name, "").strip().lower()
    return "configured" if raw in {"1", "true", "yes"} else "missing"


def rollback_owner_status() -> str:
    return "recorded_redacted" if os.environ.get("KB_STAGING_ROLLBACK_OWNER", "").strip() else "missing"


def private_ingress_status() -> str:
    raw = os.environ.get("KB_STAGING_PRIVATE_INGRESS_CONFIGURED", "").strip().lower()
    if raw in {"1", "true", "yes"}:
        return "configured_externally"
    if os.environ.get("KB_STAGING_HOST", "127.0.0.1").strip() in {"127.0.0.1", "localhost", ""}:
        return "localhost_only"
    return "not_configured"


def build_payload() -> dict[str, Any]:
    auth_status = auth_token_hash_status()
    audit_status, audit_detail = audit_path_status()
    rate_limit_status = boolean_env_status("KB_STAGING_RATE_LIMIT_CONFIGURED")
    rollback_status = rollback_owner_status()
    ingress_status = private_ingress_status()

    blockers = []
    if auth_status != "configured_hash_present":
        blockers.append("external_auth_token_hash_not_configured")
    if audit_status != "external_writable_parent":
        blockers.append("external_audit_path_not_configured")
    if rate_limit_status != "configured":
        blockers.append("rate_limit_not_configured")
    if rollback_status != "recorded_redacted":
        blockers.append("rollback_owner_not_recorded")

    ready = not blockers
    return {
        "ok": True,
        "artifact_type": "staging_runtime_config_validation",
        "created_at": now_z(),
        "schema": str(SCHEMA.relative_to(ROOT)),
        "template": str(TEMPLATE.relative_to(ROOT)),
        "runtime_config_ready": ready,
        "status": "ready" if ready else "blocked",
        "blocker_count": len(blockers),
        "failure_count": 0,
        "blockers": blockers,
        "auth_token_hash_status": auth_status,
        "audit_path_status": audit_status,
        "audit_path_detail": audit_detail,
        "rate_limit_status": rate_limit_status,
        "rollback_owner_status": rollback_status,
        "private_ingress_status": ingress_status,
        "private_ingress_note": "security approval remains required before non-local shared access",
        "secret_value_logged": False,
        "private_contact_detail_logged": False,
        "source_text_returned": False,
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "secret_redaction_boundary": (
            "do not store secret values, raw tokens, passwords, private keys, or private contact details in this repository"
        ),
    }


def write_outputs(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    auth_status = payload["auth_token_hash_status"]
    audit_status = payload["audit_path_status"]
    rate_limit_status = payload["rate_limit_status"]
    rollback_status = payload["rollback_owner_status"]
    ingress_status = payload["private_ingress_status"]
    ready = bool(payload["runtime_config_ready"])
    blockers = payload["blockers"]
    blocker_rows = "\n".join(f"| `{item}` |" for item in blockers)
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Staging Runtime Config Preflight"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "{payload["template"]}"
  - "{payload["schema"]}"
scope: "external runtime configuration status before any future shared staging start"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local preflight only; no external configuration applied"
---

# Consultant Role KB Staging Runtime Config Preflight

## 0. Boundary

This preflight records external runtime configuration status only. It does not
configure secrets, approve security controls, deploy staging, call a provider,
or ingest into a live KB. Secret values, raw tokens, passwords, private keys,
and private contact details must remain outside repository artifacts.

## 1. Result

| field | value |
|---|---:|
| runtime_config_ready | {str(ready).lower()} |
| status | {payload["status"]} |
| blocker_count | {payload["blocker_count"]} |
| failure_count | {payload["failure_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |
| secret_value_logged | {str(payload["secret_value_logged"]).lower()} |
| private_contact_detail_logged | {str(payload["private_contact_detail_logged"]).lower()} |

## 2. Runtime Status

| item | status |
|---|---|
| auth_token_hash | `{auth_status}` |
| audit_path | `{audit_status}` |
| rate_limit | `{rate_limit_status}` |
| rollback_owner | `{rollback_status}` |
| private_ingress | `{ingress_status}` |

## 3. Blockers

| blocker |
|---|
{blocker_rows if blocker_rows else "| none |"}

## 4. Tencent Cloud Lighthouse Note

Tencent Cloud Lighthouse can be a future runtime target, but repository
artifacts must still contain only redacted status. Any raw `consult/` source
upload, credential material, private ingress configuration, or service start
requires separate legal, security, and deployment approval.
""",
        encoding="utf-8",
    )


def main() -> None:
    write_schema()
    write_template()
    payload = build_payload()
    write_outputs(payload)
    ready = bool(payload["runtime_config_ready"])
    print(json.dumps({"runtime_config_ready": ready, "blocker_count": payload["blocker_count"]}, ensure_ascii=False))
    if not ready:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
