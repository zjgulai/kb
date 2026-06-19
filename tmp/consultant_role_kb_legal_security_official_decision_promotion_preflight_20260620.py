#!/usr/bin/env python3
"""Preflight legal/security reviewer candidates before official acceptance.

Boundary: local validation and diff packaging only. This script does not
overwrite official legal/source-owner or security decision templates, approve
sources, approve controls, configure secrets, deploy staging, call a provider,
or ingest into a live KB.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

LEGAL_MODULE = ROOT / "tmp/consultant_role_kb_legal_source_owner_decision_workflow_20260619.py"
SECURITY_MODULE = ROOT / "tmp/consultant_role_kb_security_staging_control_workflow_20260619.py"

DEFAULT_LEGAL_CANDIDATE = ROOT / "tmp/consultant-role-kb-reviewer-questionnaire-derived-legal-decisions-20260619.jsonl"
DEFAULT_SECURITY_CANDIDATE = (
    ROOT / "tmp/consultant-role-kb-reviewer-questionnaire-derived-security-decisions-20260619.jsonl"
)
OFFICIAL_LEGAL_TEMPLATE = ROOT / "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
OFFICIAL_SECURITY_TEMPLATE = (
    ROOT / "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"
)

OUT_JSON = ROOT / "tmp/consultant-role-kb-legal-security-official-decision-promotion-preflight-20260620.json"
OUT_CHECKLIST = ROOT / "shared/governance/consultant-agent/legal-security-official-decision-promotion-checklist-20260620.csv"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-legal-security-official-decision-promotion-preflight-20260620.md"

AUTH_ENV = "KB_LEGAL_SECURITY_DECISION_PROMOTION_ACCEPTANCE"
AUTH_VALUE = "accept-reviewed-legal-security-candidate"
PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0
OFFICIAL_TEMPLATE_WRITE_COUNT = 0
APPROVAL_EFFECT_COUNT = 0

LEGAL_TRACKED_FIELDS = [
    "decision",
    "legal_reviewer",
    "source_owner_reviewer",
    "reviewed_at",
    "review_notes",
    "legal_decision",
    "source_owner_decision",
    "license_status_decision",
    "allowed_runtime_scope",
    "permitted_actions",
    "conditions",
]
SECURITY_TRACKED_FIELDS = [
    "decision",
    "security_reviewer",
    "ops_reviewer",
    "reviewed_at",
    "review_notes",
    "evidence_uri",
    "external_config_status",
    "permitted_actions",
    "conditions",
]


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
        if not line.strip():
            continue
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


def display_path(path: Path, env_name: str) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return f"external:{env_name}"


def by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def changed_fields(official: dict[str, Any], candidate: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if official.get(field) != candidate.get(field)]


def legal_counts(rows: list[dict[str, Any]], selected_ids: set[str]) -> dict[str, int]:
    counts = {
        "decision_count": len(rows),
        "pending_count": 0,
        "non_pending_count": 0,
        "selected_pending_count": 0,
        "selected_approved_internal_staging_count": 0,
        "reviewed_metadata_count": 0,
    }
    for row in rows:
        if row["decision"] == "pending_review":
            counts["pending_count"] += 1
        else:
            counts["non_pending_count"] += 1
        if row["source_id"] in selected_ids and row["decision"] == "pending_review":
            counts["selected_pending_count"] += 1
        if row["source_id"] in selected_ids and row["decision"] == "approve_internal_staging_retrieval":
            counts["selected_approved_internal_staging_count"] += 1
        if row.get("legal_reviewer") and row.get("source_owner_reviewer") and row.get("reviewed_at"):
            counts["reviewed_metadata_count"] += 1
    return counts


def security_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "decision_count": len(rows),
        "pending_count": 0,
        "non_pending_count": 0,
        "approved_count": 0,
        "configured_external_count": 0,
        "reviewed_metadata_count": 0,
    }
    for row in rows:
        if row["decision"] == "pending_review":
            counts["pending_count"] += 1
        else:
            counts["non_pending_count"] += 1
        if row["decision"] == "approved":
            counts["approved_count"] += 1
        if row.get("external_config_status") == "configured_externally":
            counts["configured_external_count"] += 1
        if row.get("security_reviewer") and row.get("ops_reviewer") and row.get("reviewed_at"):
            counts["reviewed_metadata_count"] += 1
    return counts


def checklist_rows(
    lane: str,
    id_key: str,
    official_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    tracked_fields: list[str],
) -> list[dict[str, Any]]:
    official_by_id = by_id(official_rows, id_key)
    candidate_by_id = by_id(candidate_rows, id_key)
    rows: list[dict[str, Any]] = []
    for item_id in sorted(set(official_by_id) | set(candidate_by_id)):
        official = official_by_id.get(item_id)
        candidate = candidate_by_id.get(item_id)
        if official is None:
            rows.append(
                {
                    "lane": lane,
                    "item_id": item_id,
                    "decision_id": candidate.get("decision_id", ""),
                    "candidate_decision": candidate.get("decision", ""),
                    "official_decision": "missing",
                    "changed_fields": "candidate_missing_from_official",
                    "promotion_action": "block_id_mismatch",
                    "reviewer_fields_present": "false",
                }
            )
            continue
        if candidate is None:
            rows.append(
                {
                    "lane": lane,
                    "item_id": item_id,
                    "decision_id": official.get("decision_id", ""),
                    "candidate_decision": "missing",
                    "official_decision": official.get("decision", ""),
                    "changed_fields": "candidate_missing",
                    "promotion_action": "block_id_mismatch",
                    "reviewer_fields_present": "false",
                }
            )
            continue
        fields = changed_fields(official, candidate, tracked_fields)
        if lane == "legal_source_owner":
            reviewer_fields_present = bool(
                candidate.get("legal_reviewer")
                and candidate.get("source_owner_reviewer")
                and candidate.get("reviewed_at")
            )
        else:
            reviewer_fields_present = bool(
                candidate.get("security_reviewer")
                and candidate.get("ops_reviewer")
                and candidate.get("reviewed_at")
            )
        if candidate["decision"] == "pending_review":
            action = "no_change_pending"
        elif not reviewer_fields_present:
            action = "block_missing_review_metadata"
        elif fields:
            action = "candidate_change_requires_acceptance"
        else:
            action = "no_change"
        rows.append(
            {
                "lane": lane,
                "item_id": item_id,
                "decision_id": candidate.get("decision_id", ""),
                "candidate_decision": candidate.get("decision", ""),
                "official_decision": official.get("decision", ""),
                "changed_fields": "|".join(fields),
                "promotion_action": action,
                "reviewer_fields_present": str(reviewer_fields_present).lower(),
            }
        )
    return rows


def write_checklist(rows: list[dict[str, Any]]) -> None:
    OUT_CHECKLIST.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "lane",
        "item_id",
        "decision_id",
        "candidate_decision",
        "official_decision",
        "changed_fields",
        "promotion_action",
        "reviewer_fields_present",
    ]
    with OUT_CHECKLIST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    legal_mod = load_module("legal_decision_workflow", LEGAL_MODULE)
    security_mod = load_module("security_decision_workflow", SECURITY_MODULE)
    legal_candidate_path = env_path("KB_LEGAL_SOURCE_OWNER_PROMOTION_CANDIDATE_PATH", DEFAULT_LEGAL_CANDIDATE)
    security_candidate_path = env_path("KB_SECURITY_STAGING_PROMOTION_CANDIDATE_PATH", DEFAULT_SECURITY_CANDIDATE)

    official_legal = read_jsonl(OFFICIAL_LEGAL_TEMPLATE)
    official_security = read_jsonl(OFFICIAL_SECURITY_TEMPLATE)
    candidate_legal = read_jsonl(legal_candidate_path)
    candidate_security = read_jsonl(security_candidate_path)

    register_rows = legal_mod.read_csv(legal_mod.REGISTER)
    selection_rows = legal_mod.read_csv(legal_mod.SELECTION)
    selected_ids = {row["source_id"] for row in selection_rows if row["selection_status"] == "selected"}

    official_legal_validation = legal_mod.validate_workflow(register_rows, selected_ids, official_legal)
    candidate_legal_validation = legal_mod.validate_workflow(register_rows, selected_ids, candidate_legal)
    official_security_validation = security_mod.validate_workflow(official_security)
    candidate_security_validation = security_mod.validate_workflow(candidate_security)

    legal_id_sets_match = {row["source_id"] for row in official_legal} == {row["source_id"] for row in candidate_legal}
    security_id_sets_match = {row["control_id"] for row in official_security} == {
        row["control_id"] for row in candidate_security
    }
    legal_summary = legal_counts(candidate_legal, selected_ids)
    security_summary = security_counts(candidate_security)
    legal_checklist = checklist_rows(
        "legal_source_owner",
        "source_id",
        official_legal,
        candidate_legal,
        LEGAL_TRACKED_FIELDS,
    )
    security_checklist = checklist_rows(
        "security_operations",
        "control_id",
        official_security,
        candidate_security,
        SECURITY_TRACKED_FIELDS,
    )
    checklist = legal_checklist + security_checklist
    write_checklist(checklist)

    changed_row_count = sum(1 for row in checklist if row["changed_fields"])
    candidate_non_pending_count = legal_summary["non_pending_count"] + security_summary["non_pending_count"]
    acceptance_authorized = os.environ.get(AUTH_ENV, "").strip() == AUTH_VALUE

    blockers: list[str] = []
    if official_legal_validation["failure_count"] != 0:
        blockers.append("official_legal_template_validation_failed")
    if official_security_validation["failure_count"] != 0:
        blockers.append("official_security_template_validation_failed")
    if candidate_legal_validation["failure_count"] != 0:
        blockers.append("candidate_legal_validation_failed")
    if candidate_security_validation["failure_count"] != 0:
        blockers.append("candidate_security_validation_failed")
    if not legal_id_sets_match:
        blockers.append("legal_source_id_set_mismatch")
    if not security_id_sets_match:
        blockers.append("security_control_id_set_mismatch")
    if candidate_non_pending_count == 0:
        blockers.append("no_reviewed_legal_or_security_candidate_decisions")
    if changed_row_count == 0:
        blockers.append("no_candidate_changes_to_accept")
    if legal_summary["selected_pending_count"] > 0:
        blockers.append("legal_selected_sources_still_pending")
    if security_summary["pending_count"] > 0:
        blockers.append("security_controls_still_pending")
    if not acceptance_authorized:
        blockers.append("explicit_acceptance_authorization_missing")

    provider_call_count = max(
        PROVIDER_CALL_COUNT,
        official_legal_validation["provider_call_count"],
        candidate_legal_validation["provider_call_count"],
        official_security_validation["provider_call_count"],
        candidate_security_validation["provider_call_count"],
    )
    live_kb_write_count = max(
        LIVE_KB_WRITE_COUNT,
        official_legal_validation["live_kb_write_count"],
        candidate_legal_validation["live_kb_write_count"],
        official_security_validation["live_kb_write_count"],
        candidate_security_validation["live_kb_write_count"],
    )
    formal_acceptance_ready = not blockers and provider_call_count == 0 and live_kb_write_count == 0
    shared_staging_ready_after_candidate = bool(
        candidate_legal_validation["shared_staging_legal_clearance_ready"]
        and candidate_security_validation["shared_staging_security_controls_ready"]
        and formal_acceptance_ready
    )

    payload = {
        "ok": (
            official_legal_validation["ok"]
            and candidate_legal_validation["ok"]
            and official_security_validation["ok"]
            and candidate_security_validation["ok"]
            and legal_id_sets_match
            and security_id_sets_match
        ),
        "status": "ready_for_explicit_acceptance" if formal_acceptance_ready else "blocked",
        "legal_candidate_decisions": display_path(
            legal_candidate_path,
            "KB_LEGAL_SOURCE_OWNER_PROMOTION_CANDIDATE_PATH",
        ),
        "security_candidate_decisions": display_path(
            security_candidate_path,
            "KB_SECURITY_STAGING_PROMOTION_CANDIDATE_PATH",
        ),
        "official_legal_template": str(OFFICIAL_LEGAL_TEMPLATE.relative_to(ROOT)),
        "official_security_template": str(OFFICIAL_SECURITY_TEMPLATE.relative_to(ROOT)),
        "promotion_checklist": str(OUT_CHECKLIST.relative_to(ROOT)),
        "official_template_write_count": OFFICIAL_TEMPLATE_WRITE_COUNT,
        "approval_effect_count": APPROVAL_EFFECT_COUNT,
        "acceptance_authorized": acceptance_authorized,
        "acceptance_env": AUTH_ENV,
        "required_acceptance_value": AUTH_VALUE,
        "legal_source_id_sets_match": legal_id_sets_match,
        "security_control_id_sets_match": security_id_sets_match,
        "changed_row_count": changed_row_count,
        "candidate_non_pending_count": candidate_non_pending_count,
        "legal_decision_count": legal_summary["decision_count"],
        "legal_pending_count": legal_summary["pending_count"],
        "legal_non_pending_count": legal_summary["non_pending_count"],
        "legal_selected_source_count": len(selected_ids),
        "legal_selected_pending_count": legal_summary["selected_pending_count"],
        "legal_selected_approved_internal_staging_count": legal_summary[
            "selected_approved_internal_staging_count"
        ],
        "legal_reviewed_metadata_count": legal_summary["reviewed_metadata_count"],
        "legal_failure_count": candidate_legal_validation["failure_count"],
        "security_decision_count": security_summary["decision_count"],
        "security_pending_count": security_summary["pending_count"],
        "security_non_pending_count": security_summary["non_pending_count"],
        "security_approved_control_count": security_summary["approved_count"],
        "security_configured_external_control_count": security_summary["configured_external_count"],
        "security_reviewed_metadata_count": security_summary["reviewed_metadata_count"],
        "security_failure_count": candidate_security_validation["failure_count"],
        "shared_staging_ready_after_candidate": shared_staging_ready_after_candidate,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "provider_call_count": provider_call_count,
        "live_kb_write_count": live_kb_write_count,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "shared_staging_deployment": "not deployed",
        "manual_review_boundary": "promotion preflight only; official decision templates remain unchanged",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Legal Security Official Decision Promotion Preflight"
status: "draft"
created_at: "2026-06-20"
source_documents:
  - "{payload["legal_candidate_decisions"]}"
  - "{payload["security_candidate_decisions"]}"
  - "{payload["official_legal_template"]}"
  - "{payload["official_security_template"]}"
scope: "fail-closed preflight before accepting legal/source-owner and security reviewer candidates into official decision records"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "preflight only; official decision templates unchanged"
---

# Consultant Role KB Legal Security Official Decision Promotion Preflight

## 0. Boundary

This preflight validates whether legal/source-owner and security candidate
JSONL files are safe to accept into their official decision records. It does
not overwrite official templates, approve sources, approve controls, configure
secrets, deploy shared staging, call a provider, or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| status | {payload["status"]} |
| blocker_count | {payload["blocker_count"]} |
| changed_row_count | {payload["changed_row_count"]} |
| candidate_non_pending_count | {payload["candidate_non_pending_count"]} |
| legal_selected_approved_internal_staging_count | {payload["legal_selected_approved_internal_staging_count"]}/{payload["legal_selected_source_count"]} |
| security_approved_control_count | {payload["security_approved_control_count"]}/{payload["security_decision_count"]} |
| shared_staging_ready_after_candidate | {str(payload["shared_staging_ready_after_candidate"]).lower()} |
| official_template_write_count | {payload["official_template_write_count"]} |
| approval_effect_count | {payload["approval_effect_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

## 2. Promotion Checklist

- Checklist CSV: `shared/governance/consultant-agent/legal-security-official-decision-promotion-checklist-20260620.csv`
- Legal candidate: `{payload["legal_candidate_decisions"]}`
- Security candidate: `{payload["security_candidate_decisions"]}`

## 3. Current Blockers

```json
{json.dumps(payload["blockers"], ensure_ascii=False, indent=2)}
```

## 4. Acceptance Rule

The preflight becomes acceptance-ready only when candidate files pass the
existing legal/security validators, contain reviewed non-pending changes, keep
source/control ID sets aligned with official templates, and the operator
supplies explicit authorization:

```bash
{AUTH_ENV}={AUTH_VALUE} python3 tmp/consultant_role_kb_legal_security_official_decision_promotion_preflight_20260620.py
```

Boundary: even an authorized ready preflight is evidence for acceptance
readiness only. The official decision files must be updated by a later
deliberate, reviewed write step.
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "blocker_count": payload["blocker_count"],
                "candidate_non_pending_count": payload["candidate_non_pending_count"],
                "official_template_write_count": payload["official_template_write_count"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
