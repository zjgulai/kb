#!/usr/bin/env python3
"""Build a consolidated clearance execution pack for shared staging gates.

Boundary: local governance packaging only. This does not approve sources,
approve security controls, configure secrets, deploy staging, call a provider,
or ingest into a live KB.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEGAL_QUEUE = ROOT / "shared/governance/consultant-agent/legal-source-owner-review.queue-20260619.csv"
SECURITY_QUEUE = ROOT / "shared/governance/consultant-agent/security-staging-control-review.queue-20260619.csv"
LEGAL_VALIDATION = ROOT / "tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json"
SECURITY_VALIDATION = ROOT / "tmp/consultant-role-kb-security-staging-control-validation-20260619.json"
MANUAL_INTAKE = ROOT / "tmp/consultant-role-kb-manual-decision-intake-preflight-20260619.json"
RUNTIME_CONFIG = ROOT / "tmp/consultant-role-kb-staging-runtime-config-preflight-20260619.json"
SHARED_PREFLIGHT = ROOT / "tmp/consultant-role-kb-shared-staging-readiness-preflight-20260619.json"

CHECKLIST = ROOT / "shared/governance/consultant-agent/clearance-execution-checklist-20260619.csv"
OUT_JSON = ROOT / "tmp/consultant-role-kb-clearance-execution-pack-validation-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-clearance-execution-pack-20260619.md"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def checklist_rows(legal_rows: list[dict[str, str]], security_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    selected_legal = [row for row in legal_rows if row["included_in_all_extractable"] == "true"]
    for row in selected_legal:
        rows.append(
            {
                "lane": "legal_source_owner",
                "item_id": row["source_id"],
                "title": row["source_title"],
                "required_decision": "approve_internal_staging_retrieval_or_restrict",
                "current_status": row["current_decision"],
                "required_reviewer": "legal_reviewer_and_source_owner_reviewer",
                "required_evidence": "filled legal/source-owner decision JSONL row; no raw source text",
                "blocks_shared_staging": "true",
                "repository_boundary": "no raw source redistribution; no provider call; no live KB ingestion",
            }
        )
    for row in security_rows:
        rows.append(
            {
                "lane": "security_operations",
                "item_id": row["control_id"],
                "title": row["control_title"],
                "required_decision": "approved_or_restrict",
                "current_status": row["current_decision"],
                "required_reviewer": "security_reviewer_and_ops_reviewer",
                "required_evidence": row["required_evidence"],
                "blocks_shared_staging": "true",
                "repository_boundary": "redacted status only; no secret values or private contact details",
            }
        )
    return rows


def write_checklist(rows: list[dict[str, str]]) -> None:
    CHECKLIST.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "lane",
        "item_id",
        "title",
        "required_decision",
        "current_status",
        "required_reviewer",
        "required_evidence",
        "blocks_shared_staging",
        "repository_boundary",
    ]
    with CHECKLIST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    legal_rows = read_csv(LEGAL_QUEUE)
    security_rows = read_csv(SECURITY_QUEUE)
    legal_validation = read_json(LEGAL_VALIDATION)
    security_validation = read_json(SECURITY_VALIDATION)
    manual_intake = read_json(MANUAL_INTAKE)
    runtime_config = read_json(RUNTIME_CONFIG)
    shared_preflight = read_json(SHARED_PREFLIGHT)

    rows = checklist_rows(legal_rows, security_rows)
    write_checklist(rows)

    selected_legal_pending = int(legal_validation["selected_source_count"]) - int(
        legal_validation["selected_approved_internal_staging_count"]
    )
    security_pending = int(security_validation["control_count"]) - int(
        security_validation["approved_control_count"]
    )
    runtime_pending = int(runtime_config["blocker_count"])
    human_gold_ready = bool(manual_intake["human_label_gate_waived_for_staging"]) and not bool(
        manual_intake["human_gold_metrics_claimed"]
    )

    blockers = []
    if selected_legal_pending:
        blockers.append("legal_source_owner_selected_sources_pending")
    if security_pending:
        blockers.append("security_operations_controls_pending")
    if runtime_pending:
        blockers.append("runtime_external_config_pending")
    if not human_gold_ready:
        blockers.append("human_label_gate_policy_not_ready")

    payload = {
        "ok": True,
        "status": "blocked" if blockers else "ready",
        "clearance_execution_ready": not blockers,
        "checklist": str(CHECKLIST.relative_to(ROOT)),
        "legal_selected_source_count": legal_validation["selected_source_count"],
        "legal_selected_approved_internal_staging_count": legal_validation[
            "selected_approved_internal_staging_count"
        ],
        "legal_selected_pending_count": selected_legal_pending,
        "security_control_count": security_validation["control_count"],
        "security_approved_control_count": security_validation["approved_control_count"],
        "security_pending_count": security_pending,
        "runtime_config_ready": runtime_config["runtime_config_ready"],
        "runtime_config_blocker_count": runtime_pending,
        "manual_decision_intake_ready": manual_intake["manual_decision_intake_ready"],
        "human_label_gate_waived_for_staging": manual_intake["human_label_gate_waived_for_staging"],
        "human_gold_metrics_claimed": manual_intake["human_gold_metrics_claimed"],
        "shared_ready_for_staging": shared_preflight["ready_for_shared_staging"],
        "shared_staging_blocker_count": shared_preflight["blocker_count"],
        "checklist_row_count": len(rows),
        "legal_checklist_row_count": sum(1 for row in rows if row["lane"] == "legal_source_owner"),
        "security_checklist_row_count": sum(1 for row in rows if row["lane"] == "security_operations"),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "legal, source-owner, security, and operations reviewers must fill decision files",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    REPORT.write_text(
        f"""---
title: "Consultant Role KB Clearance Execution Pack"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/governance/consultant-agent/legal-source-owner-review.queue-20260619.csv"
  - "shared/governance/consultant-agent/security-staging-control-review.queue-20260619.csv"
  - "tmp/consultant-role-kb-manual-decision-intake-preflight-20260619.json"
  - "tmp/consultant-role-kb-staging-runtime-config-preflight-20260619.json"
  - "tmp/consultant-role-kb-shared-staging-readiness-preflight-20260619.json"
scope: "combined execution checklist for legal/source-owner and security/operations gates"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "manual review package only; no approvals recorded"
---

# Consultant Role KB Clearance Execution Pack

## 0. Boundary

This pack consolidates the remaining legal/source-owner and security/operations
gates. It does not approve any source, approve any security control, configure
secrets, deploy shared staging, call a provider, or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| clearance_execution_ready | {str(payload["clearance_execution_ready"]).lower()} |
| status | {payload["status"]} |
| blocker_count | {payload["blocker_count"]} |
| checklist_row_count | {payload["checklist_row_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

## 2. Decision Work

| lane | required | current |
|---|---:|---:|
| legal/source-owner selected sources | {payload["legal_selected_source_count"]} | {payload["legal_selected_approved_internal_staging_count"]} approved |
| security/operations controls | {payload["security_control_count"]} | {payload["security_approved_control_count"]} approved |
| runtime external config blockers | 0 | {payload["runtime_config_blocker_count"]} blockers |
| human-gold metrics | not claimed | {str(payload["human_gold_metrics_claimed"]).lower()} |

## 3. Artifacts To Fill

| artifact | purpose |
|---|---|
| `shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl` | legal/source-owner decision rows for all 81 sources; 80 selected rows must be cleared before shared staging |
| `shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl` | security/operations decision rows for 8 controls |
| `shared/governance/consultant-agent/clearance-execution-checklist-20260619.csv` | combined checklist of the 80 selected legal rows and 8 security controls |

## 4. Validation Commands

Use external paths if filled reviewer files should remain outside the default
templates:

```bash
KB_LEGAL_SOURCE_OWNER_DECISIONS_PATH=/path/to/legal-decisions.jsonl \\
KB_SECURITY_STAGING_CONTROL_DECISIONS_PATH=/path/to/security-decisions.jsonl \\
python3 tmp/consultant_role_kb_manual_decision_intake_preflight_20260619.py

python3 tmp/consultant_role_kb_staging_runtime_config_preflight_20260619.py
python3 tmp/consultant_role_kb_shared_staging_readiness_preflight_20260619.py
```

## 5. Current Blockers

- `legal_source_owner_selected_sources_pending`: {selected_legal_pending}
- `security_operations_controls_pending`: {security_pending}
- `runtime_external_config_pending`: {runtime_pending}

Human-gold labels remain unapproved by reviewers. Product-owner Q4:D allows
machine-seeded staging evidence only and human-gold metrics are not claimed.
""",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "blocker_count": len(blockers)}, ensure_ascii=False))
    if not payload["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
