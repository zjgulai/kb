#!/usr/bin/env python3
"""Smoke-test manual decision intake validation with temporary fixtures.

Boundary: local validation only. Synthetic fixture approvals created here are
not reviewer decisions and must not be used to clear shared staging.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tmp/manual-decision-intake-fixtures-20260619"
OUT_JSON = ROOT / "tmp/consultant-role-kb-manual-decision-intake-smoke-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-manual-decision-intake-smoke-20260619.md"

HUMAN_MODULE = ROOT / "tmp/consultant_role_kb_human_label_review_workflow_20260619.py"
LEGAL_MODULE = ROOT / "tmp/consultant_role_kb_legal_source_owner_decision_workflow_20260619.py"
SECURITY_MODULE = ROOT / "tmp/consultant_role_kb_security_staging_control_workflow_20260619.py"

HUMAN_TEMPLATE = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
LEGAL_TEMPLATE = ROOT / "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
SECURITY_TEMPLATE = ROOT / "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0
REVIEWED_AT = "2026-06-19T00:00:00Z"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def approve_human_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    approved: list[dict[str, Any]] = []
    for row in rows:
        next_row = dict(row)
        next_row["decision"] = "approve"
        next_row["reviewer"] = "synthetic-reviewer"
        next_row["reviewed_at"] = REVIEWED_AT
        next_row["review_notes"] = "Synthetic smoke fixture; not an actual manual approval."
        if next_row["label_type"] == "locator_gold_candidate":
            proposed = next_row["proposed"]
            next_row["approved_source_id"] = proposed["source_id"]
            next_row["approved_card_id"] = proposed["card_id"]
            next_row["approved_locator"] = proposed["locator"]
            next_row["approved_locator_type"] = proposed["locator_type"]
            next_row["approved_no_source_policy"] = False
        else:
            next_row["approved_source_id"] = None
            next_row["approved_card_id"] = None
            next_row["approved_locator"] = None
            next_row["approved_locator_type"] = None
            next_row["approved_no_source_policy"] = True
        approved.append(next_row)
    return approved


def approve_legal_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    approved: list[dict[str, Any]] = []
    for row in rows:
        next_row = dict(row)
        if next_row["included_in_all_extractable"]:
            next_row["decision"] = "approve_internal_staging_retrieval"
            next_row["legal_reviewer"] = "synthetic-legal-reviewer"
            next_row["source_owner_reviewer"] = "synthetic-source-owner"
            next_row["reviewed_at"] = REVIEWED_AT
            next_row["review_notes"] = "Synthetic smoke fixture; not an actual legal or source-owner approval."
            next_row["legal_decision"] = "approved"
            next_row["source_owner_decision"] = "approved"
            next_row["license_status_decision"] = "approved_internal_staging_no_provider"
            next_row["allowed_runtime_scope"] = "internal_no_provider_staging"
            next_row["permitted_actions"] = ["internal_no_provider_retrieval"]
        approved.append(next_row)
    return approved


def approve_security_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    approved: list[dict[str, Any]] = []
    for row in rows:
        next_row = dict(row)
        next_row["decision"] = "approved"
        next_row["security_reviewer"] = "synthetic-security-reviewer"
        next_row["ops_reviewer"] = "synthetic-ops-reviewer"
        next_row["reviewed_at"] = REVIEWED_AT
        next_row["review_notes"] = "Synthetic smoke fixture; not an actual security or operations approval."
        next_row["evidence_uri"] = f"synthetic://manual-decision-intake-smoke/{next_row['control_id']}"
        next_row["external_config_status"] = (
            "configured_externally" if next_row["external_config_required"] else "not_required"
        )
        next_row["permitted_actions"] = ["allow_shared_staging_control"]
        approved.append(next_row)
    return approved


def aggregate_summary(
    human_mod: ModuleType,
    legal_mod: ModuleType,
    security_mod: ModuleType,
    human_rows: list[dict[str, Any]],
    legal_rows: list[dict[str, Any]],
    security_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    seed_rows = human_mod.read_jsonl(human_mod.SEED_PATH)
    register_rows = legal_mod.read_csv(legal_mod.REGISTER)
    selection_rows = legal_mod.read_csv(legal_mod.SELECTION)
    selected_ids = {row["source_id"] for row in selection_rows if row["selection_status"] == "selected"}

    human_summary = human_mod.validate_workflow(seed_rows, human_rows)
    legal_summary = legal_mod.validate_workflow(register_rows, selected_ids, legal_rows)
    security_summary = security_mod.validate_workflow(security_rows)

    validation_failure_count = (
        human_summary["failure_count"]
        + legal_summary["failure_count"]
        + security_summary["failure_count"]
    )
    human_ready = (
        human_summary["failure_count"] == 0
        and human_summary["approved_decision_count"] == human_summary["seed_label_count"]
    )
    legal_ready = bool(legal_summary["shared_staging_legal_clearance_ready"])
    security_ready = bool(security_summary["shared_staging_security_controls_ready"])
    blockers = []
    if not human_ready:
        blockers.append("human_label_decisions_not_fully_approved")
    if not legal_ready:
        blockers.append("legal_source_owner_clearance_not_ready")
    if not security_ready:
        blockers.append("security_staging_controls_not_ready")
    ready = not blockers and validation_failure_count == 0
    return {
        "ready": ready,
        "blockers": blockers,
        "blocker_count": len(blockers),
        "validation_failure_count": validation_failure_count,
        "human_approved_decision_count": human_summary["approved_decision_count"],
        "human_seed_label_count": human_summary["seed_label_count"],
        "legal_selected_approved_internal_staging_count": legal_summary[
            "selected_approved_internal_staging_count"
        ],
        "legal_selected_source_count": legal_summary["selected_source_count"],
        "security_approved_control_count": security_summary["approved_control_count"],
        "security_control_count": security_summary["control_count"],
        "provider_call_count": max(
            PROVIDER_CALL_COUNT,
            human_summary["provider_call_count"],
            legal_summary["provider_call_count"],
            security_summary["provider_call_count"],
        ),
        "live_kb_write_count": max(
            LIVE_KB_WRITE_COUNT,
            human_summary["live_kb_write_count"],
            legal_summary["live_kb_write_count"],
            security_summary["live_kb_write_count"],
        ),
    }


def main() -> None:
    human_mod = load_module("human_label_review_workflow", HUMAN_MODULE)
    legal_mod = load_module("legal_source_owner_decision_workflow", LEGAL_MODULE)
    security_mod = load_module("security_staging_control_workflow", SECURITY_MODULE)

    human_default = read_jsonl(HUMAN_TEMPLATE)
    legal_default = read_jsonl(LEGAL_TEMPLATE)
    security_default = read_jsonl(SECURITY_TEMPLATE)

    human_approved = approve_human_rows(human_default)
    legal_approved = approve_legal_rows(legal_default)
    security_approved = approve_security_rows(security_default)

    invalid_human = [dict(row) for row in human_approved]
    invalid_human[0] = dict(invalid_human[0])
    invalid_human[0]["reviewer"] = None

    fixtures = {
        "synthetic-human-approved.jsonl": human_approved,
        "synthetic-legal-approved.jsonl": legal_approved,
        "synthetic-security-approved.jsonl": security_approved,
        "synthetic-human-invalid-missing-reviewer.jsonl": invalid_human,
    }
    for filename, rows in fixtures.items():
        write_jsonl(FIXTURE_DIR / filename, rows)

    scenarios = {
        "default_pending_templates": aggregate_summary(
            human_mod,
            legal_mod,
            security_mod,
            human_default,
            legal_default,
            security_default,
        ),
        "synthetic_all_approved": aggregate_summary(
            human_mod,
            legal_mod,
            security_mod,
            human_approved,
            legal_approved,
            security_approved,
        ),
        "synthetic_invalid_human_missing_reviewer": aggregate_summary(
            human_mod,
            legal_mod,
            security_mod,
            invalid_human,
            legal_approved,
            security_approved,
        ),
    }

    assertions = {
        "default_pending_blocks": not scenarios["default_pending_templates"]["ready"]
        and scenarios["default_pending_templates"]["blocker_count"] == 3,
        "synthetic_all_approved_ready": scenarios["synthetic_all_approved"]["ready"],
        "synthetic_invalid_human_fails": scenarios[
            "synthetic_invalid_human_missing_reviewer"
        ]["validation_failure_count"]
        > 0,
        "no_provider_calls": max(row["provider_call_count"] for row in scenarios.values()) == 0,
        "no_live_kb_writes": max(row["live_kb_write_count"] for row in scenarios.values()) == 0,
    }
    payload = {
        "ok": all(assertions.values()),
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "shared_staging_deployment": "not deployed",
        "fixture_boundary": "synthetic smoke fixtures only; not manual approvals",
        "fixture_dir": str(FIXTURE_DIR.relative_to(ROOT)),
        "fixture_dir_retained": False,
        "scenario_count": len(scenarios),
        "assertions": assertions,
        "scenarios": scenarios,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    scenario_rows = "\n".join(
        "| `{}` | {} | {} | {} | {} | {} |".format(
            name,
            str(summary["ready"]).lower(),
            summary["blocker_count"],
            summary["validation_failure_count"],
            summary["human_approved_decision_count"],
            summary["security_approved_control_count"],
        )
        for name, summary in scenarios.items()
    )
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Manual Decision Intake Smoke"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant_role_kb_manual_decision_intake_preflight_20260619.py"
  - "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
  - "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
  - "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"
scope: "synthetic smoke for manual decision intake validation behavior"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "synthetic local smoke only; no approval recorded"
---

# Consultant Role KB Manual Decision Intake Smoke

## 0. Boundary

This smoke creates temporary synthetic decision fixtures during execution and
removes them before exit. These fixtures are not manual approvals, do not
configure secrets, do not deploy shared staging, do not call a provider, and do
not ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| ok | {str(payload["ok"]).lower()} |
| scenario_count | {payload["scenario_count"]} |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 2. Scenarios

| scenario | ready | blocker_count | validation_failure_count | human_approved | security_approved |
|---|---:|---:|---:|---:|---:|
{scenario_rows}

## 3. Interpretation

Fact: the current default pending templates remain blocked.

Fact: a fully synthetic approved fixture can pass the intake readiness logic,
which proves the manual decision bridge can become green after valid reviewer
decisions are supplied.

Fact: an invalid synthetic human decision with missing reviewer is rejected by
the validator before it can clear readiness.

Boundary: the synthetic approved fixture is test data only and must not be used
as legal, source-owner, security, or human-gold evidence.
""",
        encoding="utf-8",
    )
    shutil.rmtree(FIXTURE_DIR, ignore_errors=True)
    print(json.dumps({"ok": payload["ok"], "scenario_count": len(scenarios)}, ensure_ascii=False))
    if not payload["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
