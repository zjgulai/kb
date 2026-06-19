#!/usr/bin/env python3
"""Smoke-test redacted runtime config fixture behavior.

Boundary: local fixture validation only. This does not configure secrets,
approve security controls, deploy staging, call a provider, or ingest into a
live KB. Scenario outputs record statuses and counts only, never raw secrets,
tokens, passwords, private keys, or private contact details.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_MODULE = ROOT / "tmp/consultant_role_kb_staging_runtime_config_preflight_20260619.py"
OUT_JSON = ROOT / "tmp/consultant-role-kb-runtime-config-redacted-fixture-smoke-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-runtime-config-redacted-fixture-smoke-20260619.md"

RUNTIME_ENV_KEYS = [
    "KB_STAGING_AUTH_TOKEN_SHA256",
    "KB_STAGING_AUDIT_PATH",
    "KB_STAGING_RATE_LIMIT_CONFIGURED",
    "KB_STAGING_ROLLBACK_OWNER",
    "KB_STAGING_PRIVATE_INGRESS_CONFIGURED",
    "KB_STAGING_HOST",
]

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("staging_runtime_config_preflight", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def patched_env(values: dict[str, str]) -> Iterator[None]:
    original = {key: os.environ.get(key) for key in RUNTIME_ENV_KEYS}
    try:
        for key in RUNTIME_ENV_KEYS:
            os.environ.pop(key, None)
        os.environ.update(values)
        yield
    finally:
        for key in RUNTIME_ENV_KEYS:
            os.environ.pop(key, None)
            if original[key] is not None:
                os.environ[key] = original[key] or ""


def sensitive_values(values: dict[str, str]) -> list[str]:
    return [
        values[key]
        for key in ["KB_STAGING_AUTH_TOKEN_SHA256", "KB_STAGING_ROLLBACK_OWNER"]
        if values.get(key)
    ]


def secret_like_count(values: dict[str, str]) -> int:
    patterns = [
        r"-----BEGIN",
        r"sk-[A-Za-z0-9_-]{20,}",
        r"ghp_[A-Za-z0-9_]{20,}",
        r"github_pat_[A-Za-z0-9_]{20,}",
        r"AKIA[0-9A-Z]{16}",
        r"xox[baprs]-[A-Za-z0-9-]{20,}",
        r"password",
        r"private[_ -]?key",
        r"raw[_ -]?token",
    ]
    count = 0
    for value in sensitive_values(values):
        if any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns):
            count += 1
    return count


def private_contact_like_count(values: dict[str, str]) -> int:
    count = 0
    for value in [values.get("KB_STAGING_ROLLBACK_OWNER", "")]:
        if re.search(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            count += 1
        elif re.search(r"\+?[0-9][0-9 .-]{7,}[0-9]", value):
            count += 1
    return count


def redaction_leak_count(payload: dict[str, Any], forbidden_fragments: list[str]) -> int:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return sum(1 for item in forbidden_fragments if item and item in text)


def scenario_result(
    module: ModuleType,
    scenario_id: str,
    env_values: dict[str, str],
    expected_ready: bool,
    forbidden_fragments: list[str],
) -> dict[str, Any]:
    with patched_env(env_values):
        payload = module.build_payload()
    leak_count = redaction_leak_count(payload, forbidden_fragments)
    secret_inputs = secret_like_count(env_values)
    private_contact_inputs = private_contact_like_count(env_values)
    ok = (
        payload["runtime_config_ready"] is expected_ready
        and payload["secret_value_logged"] is False
        and payload["private_contact_detail_logged"] is False
        and payload["provider_call_count"] == 0
        and payload["live_kb_write_count"] == 0
        and leak_count == 0
    )
    return {
        "scenario_id": scenario_id,
        "ok": ok,
        "expected_runtime_config_ready": expected_ready,
        "runtime_config_ready": payload["runtime_config_ready"],
        "status": payload["status"],
        "blocker_count": payload["blocker_count"],
        "blockers": payload["blockers"],
        "auth_token_hash_status": payload["auth_token_hash_status"],
        "audit_path_status": payload["audit_path_status"],
        "rate_limit_status": payload["rate_limit_status"],
        "rollback_owner_status": payload["rollback_owner_status"],
        "private_ingress_status": payload["private_ingress_status"],
        "secret_like_input_count": secret_inputs,
        "private_contact_like_input_count": private_contact_inputs,
        "redaction_leak_count": leak_count,
        "secret_value_logged": payload["secret_value_logged"],
        "private_contact_detail_logged": payload["private_contact_detail_logged"],
        "provider_call_count": payload["provider_call_count"],
        "live_kb_write_count": payload["live_kb_write_count"],
    }


def main() -> None:
    module = load_module(PREFLIGHT_MODULE)
    with tempfile.TemporaryDirectory(prefix="kb-runtime-config-", dir="/tmp") as tmpdir:
        audit_path = str(Path(tmpdir) / "audit.jsonl")
        ready_env = {
            "KB_STAGING_AUTH_TOKEN_SHA256": "a" * 64,
            "KB_STAGING_AUDIT_PATH": audit_path,
            "KB_STAGING_RATE_LIMIT_CONFIGURED": "true",
            "KB_STAGING_ROLLBACK_OWNER": "rollback-owner-redacted",
            "KB_STAGING_PRIVATE_INGRESS_CONFIGURED": "true",
            "KB_STAGING_HOST": "127.0.0.1",
        }
        secret_like_value = "raw_" + "token_" + "x" * 24
        private_contact = "owner" + "@example.invalid"
        secret_env = {
            "KB_STAGING_AUTH_TOKEN_SHA256": secret_like_value,
            "KB_STAGING_AUDIT_PATH": str(ROOT / "tmp" / "bad-audit.jsonl"),
            "KB_STAGING_RATE_LIMIT_CONFIGURED": "false",
            "KB_STAGING_ROLLBACK_OWNER": private_contact,
            "KB_STAGING_PRIVATE_INGRESS_CONFIGURED": "false",
            "KB_STAGING_HOST": "0.0.0.0",
        }
        scenarios = [
            scenario_result(module, "default_missing_config", {}, False, []),
            scenario_result(module, "redacted_ready_fixture", ready_env, True, sensitive_values(ready_env)),
            scenario_result(module, "secret_like_rejected_fixture", secret_env, False, sensitive_values(secret_env)),
        ]

    payload = {
        "ok": all(row["ok"] for row in scenarios),
        "scenario_count": len(scenarios),
        "pass_count": sum(1 for row in scenarios if row["ok"]),
        "fail_count": sum(1 for row in scenarios if not row["ok"]),
        "scenarios": scenarios,
        "fixture_scope": "redacted runtime status only; no raw secrets or private contact details retained",
        "official_runtime_config_updated": False,
        "external_configuration_applied": False,
        "shared_staging_deployment": "not deployed",
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = "\n".join(
        "| {scenario_id} | {ok} | {ready} | {blocker_count} | {secret_like_input_count} | {private_contact_like_input_count} | {redaction_leak_count} |".format(
            scenario_id=row["scenario_id"],
            ok=str(row["ok"]).lower(),
            ready=str(row["runtime_config_ready"]).lower(),
            blocker_count=row["blocker_count"],
            secret_like_input_count=row["secret_like_input_count"],
            private_contact_like_input_count=row["private_contact_like_input_count"],
            redaction_leak_count=row["redaction_leak_count"],
        )
        for row in scenarios
    )
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Runtime Config Redacted Fixture Smoke"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant_role_kb_staging_runtime_config_preflight_20260619.py"
  - "shared/governance/consultant-agent/staging-runtime-config.schema-20260619.json"
scope: "redacted fixture validation for future shared-staging runtime configuration"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "fixture smoke only; no external configuration applied"
---

# Consultant Role KB Runtime Config Redacted Fixture Smoke

## 0. Boundary

This smoke validates runtime configuration status handling with temporary
fixtures. It does not configure secrets, approve security controls, deploy
shared staging, call a provider, or ingest into a live KB. Scenario outputs
record status and counts only; raw secret-like values and private contacts are
not retained.

## 1. Result

| field | value |
|---|---:|
| ok | {str(payload["ok"]).lower()} |
| scenario_count | {payload["scenario_count"]} |
| pass_count | {payload["pass_count"]} |
| fail_count | {payload["fail_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

## 2. Scenarios

| scenario | ok | runtime_config_ready | blocker_count | secret_like_input_count | private_contact_like_input_count | redaction_leak_count |
|---|---:|---:|---:|---:|---:|---:|
{rows}

## 3. Interpretation

Fact: the default configuration remains blocked.

Fact: a fully redacted ready fixture can pass runtime-config checks without
logging raw secret values or private contact details.

Fact: a secret-like/private-contact fixture remains blocked and the raw values
are not emitted in the smoke output.

Boundary: even a ready redacted fixture is not a security approval, not an
external configuration action, and not a shared-staging deployment.
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "ok": payload["ok"],
                "scenario_count": payload["scenario_count"],
                "pass_count": payload["pass_count"],
                "fail_count": payload["fail_count"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
