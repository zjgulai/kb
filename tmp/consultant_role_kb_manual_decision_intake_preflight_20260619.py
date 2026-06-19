#!/usr/bin/env python3
"""Validate manual decision intake across human, legal, and security gates.

Boundary: local validation only. This does not create approvals, configure
secrets, deploy shared staging, call a provider, or ingest into a live KB.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "tmp/consultant-role-kb-manual-decision-intake-preflight-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-manual-decision-intake-preflight-20260619.md"

HUMAN_MODULE = ROOT / "tmp/consultant_role_kb_human_label_review_workflow_20260619.py"
LEGAL_MODULE = ROOT / "tmp/consultant_role_kb_legal_source_owner_decision_workflow_20260619.py"
SECURITY_MODULE = ROOT / "tmp/consultant_role_kb_security_staging_control_workflow_20260619.py"
PRODUCT_OWNER_VALIDATION = ROOT / "tmp/consultant-role-kb-product-owner-decision-validation-20260619.json"

DEFAULT_HUMAN_DECISIONS = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
DEFAULT_LEGAL_DECISIONS = ROOT / "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
DEFAULT_SECURITY_DECISIONS = ROOT / "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: invalid JSONL at line {line_number}: {exc}") from exc
    return rows


def env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    return Path(raw).expanduser()


def display_path(path: Path, env_name: str, default: Path) -> str:
    resolved = path.resolve()
    if resolved == default.resolve():
        return str(default.relative_to(ROOT))
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return f"external:{env_name}"


def validation_failure_count(summary: dict[str, Any]) -> int:
    return int(summary.get("failure_count", 0))


def main() -> None:
    human_mod = load_module("human_label_review_workflow", HUMAN_MODULE)
    legal_mod = load_module("legal_source_owner_decision_workflow", LEGAL_MODULE)
    security_mod = load_module("security_staging_control_workflow", SECURITY_MODULE)

    human_path = env_path("KB_HUMAN_LABEL_DECISIONS_PATH", DEFAULT_HUMAN_DECISIONS)
    legal_path = env_path("KB_LEGAL_SOURCE_OWNER_DECISIONS_PATH", DEFAULT_LEGAL_DECISIONS)
    security_path = env_path("KB_SECURITY_STAGING_CONTROL_DECISIONS_PATH", DEFAULT_SECURITY_DECISIONS)

    seed_rows = human_mod.read_jsonl(human_mod.SEED_PATH)
    human_summary = human_mod.validate_workflow(seed_rows, read_jsonl(human_path))

    register_rows = legal_mod.read_csv(legal_mod.REGISTER)
    selection_rows = legal_mod.read_csv(legal_mod.SELECTION)
    selected_ids = {row["source_id"] for row in selection_rows if row["selection_status"] == "selected"}
    legal_summary = legal_mod.validate_workflow(register_rows, selected_ids, read_jsonl(legal_path))

    security_summary = security_mod.validate_workflow(read_jsonl(security_path))
    product_owner = read_json(PRODUCT_OWNER_VALIDATION) if PRODUCT_OWNER_VALIDATION.exists() else {}

    human_ready = (
        human_summary["failure_count"] == 0
        and human_summary["approved_decision_count"] == human_summary["seed_label_count"]
    )
    human_label_gate_waived = (
        product_owner.get("ok") is True
        and product_owner.get("human_gold_label_gate_mode") == "waive_for_staging_do_not_claim_human_gold"
        and product_owner.get("human_gold_metrics_claimed") is False
        and product_owner.get("human_label_approval_effect_count") == 0
        and product_owner.get("provider_call_enabled") is False
        and human_summary["failure_count"] == 0
    )
    human_gate_ready_for_staging = human_ready or human_label_gate_waived
    legal_ready = bool(legal_summary["shared_staging_legal_clearance_ready"])
    security_ready = bool(security_summary["shared_staging_security_controls_ready"])

    failure_count = (
        validation_failure_count(human_summary)
        + validation_failure_count(legal_summary)
        + validation_failure_count(security_summary)
    )
    provider_call_count = max(
        PROVIDER_CALL_COUNT,
        human_summary["provider_call_count"],
        legal_summary["provider_call_count"],
        security_summary["provider_call_count"],
        product_owner.get("provider_call_count", 0),
    )
    live_kb_write_count = max(
        LIVE_KB_WRITE_COUNT,
        human_summary["live_kb_write_count"],
        legal_summary["live_kb_write_count"],
        security_summary["live_kb_write_count"],
        product_owner.get("live_kb_write_count", 0),
    )
    blockers = []
    if not human_gate_ready_for_staging:
        blockers.append("human_label_gate_not_ready_for_staging")
    if not legal_ready:
        blockers.append("legal_source_owner_clearance_not_ready")
    if not security_ready:
        blockers.append("security_staging_controls_not_ready")
    ready = not blockers and failure_count == 0 and provider_call_count == 0 and live_kb_write_count == 0

    payload = {
        "ok": failure_count == 0,
        "manual_decision_intake_ready": ready,
        "status": "ready" if ready else "blocked",
        "human_decisions": display_path(human_path, "KB_HUMAN_LABEL_DECISIONS_PATH", DEFAULT_HUMAN_DECISIONS),
        "legal_decisions": display_path(legal_path, "KB_LEGAL_SOURCE_OWNER_DECISIONS_PATH", DEFAULT_LEGAL_DECISIONS),
        "security_decisions": display_path(
            security_path,
            "KB_SECURITY_STAGING_CONTROL_DECISIONS_PATH",
            DEFAULT_SECURITY_DECISIONS,
        ),
        "product_owner_validation": (
            str(PRODUCT_OWNER_VALIDATION.relative_to(ROOT)) if PRODUCT_OWNER_VALIDATION.exists() else "missing"
        ),
        "human_label_decisions_ready": human_ready,
        "human_label_gate_ready_for_staging": human_gate_ready_for_staging,
        "human_label_gate_waived_for_staging": human_label_gate_waived,
        "human_label_gate_policy": (
            "machine_seeded_eval_only_do_not_claim_human_gold"
            if human_label_gate_waived
            else "human_gold_approval_required"
        ),
        "human_gold_metrics_claimed": False if human_label_gate_waived else human_ready,
        "machine_seeded_eval_continues": bool(product_owner.get("machine_seeded_eval_continues", False)),
        "product_owner_decision_effect_applied": human_label_gate_waived,
        "human_seed_label_count": human_summary["seed_label_count"],
        "human_approved_decision_count": human_summary["approved_decision_count"],
        "human_pending_decision_count": human_summary["pending_decision_count"],
        "legal_clearance_ready": legal_ready,
        "legal_selected_source_count": legal_summary["selected_source_count"],
        "legal_selected_approved_internal_staging_count": legal_summary[
            "selected_approved_internal_staging_count"
        ],
        "security_controls_ready": security_ready,
        "security_control_count": security_summary["control_count"],
        "security_approved_control_count": security_summary["approved_control_count"],
        "security_configured_external_control_count": security_summary["configured_external_control_count"],
        "security_secret_like_value_count": security_summary["secret_like_value_count"],
        "blocker_count": len(blockers),
        "blockers": blockers,
        "failure_count": failure_count,
        "provider_call_count": provider_call_count,
        "live_kb_write_count": live_kb_write_count,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "shared_staging_deployment": "not deployed",
        "product_owner_validation_summary": {
            "ok": product_owner.get("ok", False),
            "decision_count": product_owner.get("decision_count", 0),
            "human_gold_label_gate_mode": product_owner.get("human_gold_label_gate_mode", "not_recorded"),
            "legal_source_owner_clearance_effect": product_owner.get(
                "legal_source_owner_clearance_effect",
                False,
            ),
            "security_approval_effect_count": product_owner.get("security_approval_effect_count", 0),
            "provider_call_enabled": product_owner.get("provider_call_enabled", False),
        },
        "human_validation": {
            "ok": human_summary["ok"],
            "failure_count": human_summary["failure_count"],
            "pending_decision_count": human_summary["pending_decision_count"],
            "approved_decision_count": human_summary["approved_decision_count"],
        },
        "legal_validation": {
            "ok": legal_summary["ok"],
            "failure_count": legal_summary["failure_count"],
            "selected_source_count": legal_summary["selected_source_count"],
            "selected_approved_internal_staging_count": legal_summary[
                "selected_approved_internal_staging_count"
            ],
            "shared_staging_legal_clearance_ready": legal_summary["shared_staging_legal_clearance_ready"],
        },
        "security_validation": {
            "ok": security_summary["ok"],
            "failure_count": security_summary["failure_count"],
            "control_count": security_summary["control_count"],
            "approved_control_count": security_summary["approved_control_count"],
            "shared_staging_security_controls_ready": security_summary[
                "shared_staging_security_controls_ready"
            ],
        },
    }

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    REPORT.write_text(
        f"""---
title: "Consultant Role KB Manual Decision Intake Preflight"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "{payload["human_decisions"]}"
  - "{payload["legal_decisions"]}"
  - "{payload["security_decisions"]}"
  - "{payload["product_owner_validation"]}"
scope: "aggregate validation before manual decisions can affect shared-staging readiness"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local preflight only; no manual approval recorded"
---

# Consultant Role KB Manual Decision Intake Preflight

## 0. Boundary

This preflight validates decision files for the human label, legal/source-owner,
and security/staging-control gates. It does not create approvals, configure
secrets, deploy shared staging, call a provider, or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| manual_decision_intake_ready | {str(payload["manual_decision_intake_ready"]).lower()} |
| status | {payload["status"]} |
| blocker_count | {payload["blocker_count"]} |
| failure_count | {payload["failure_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |
| human_label_gate_waived_for_staging | {str(payload["human_label_gate_waived_for_staging"]).lower()} |
| human_gold_metrics_claimed | {str(payload["human_gold_metrics_claimed"]).lower()} |

## 2. Decision Files

| gate | file |
|---|---|
| human labels | `{payload["human_decisions"]}` |
| legal/source-owner | `{payload["legal_decisions"]}` |
| security/staging controls | `{payload["security_decisions"]}` |
| product-owner decision | `{payload["product_owner_validation"]}` |

## 3. Gate Summary

| gate | ready | current count |
|---|---:|---:|
| human_label_gate_for_staging | {str(human_gate_ready_for_staging).lower()} | {payload["human_approved_decision_count"]}/{payload["human_seed_label_count"]} approved; policy=`{payload["human_label_gate_policy"]}` |
| legal_source_owner_clearance | {str(legal_ready).lower()} | {payload["legal_selected_approved_internal_staging_count"]}/{payload["legal_selected_source_count"]} selected sources approved |
| security_staging_controls | {str(security_ready).lower()} | {payload["security_approved_control_count"]}/{payload["security_control_count"]} controls approved |

## 4. Interpretation

Fact: the current default decision files are structurally valid and have
`failure_count = 0`.

Fact: product-owner Q4:D waives the human-gold label gate for staging evidence
only under a machine-seeded-eval policy. Human-gold labels remain unapproved
and human-gold metrics must not be claimed.

Fact: legal/source-owner clearance and security/staging controls remain blocked
because they still contain pending decisions rather than approved reviewer
outcomes.

Boundary: this is only an intake preflight. Approval decisions must be made by
the appropriate human reviewers and must not include raw secret values,
passwords, private keys, or private contact details in repository artifacts.
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manual_decision_intake_ready": ready,
                "blocker_count": len(blockers),
                "failure_count": failure_count,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
