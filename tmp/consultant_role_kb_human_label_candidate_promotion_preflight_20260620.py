#!/usr/bin/env python3
"""Preflight a human-label candidate JSONL before official acceptance.

Boundary: local validation and diff packaging only. This script does not
overwrite the official human-label decision template, create human-gold labels,
call providers, deploy staging, or ingest into a live KB.
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
WORKFLOW_MODULE = ROOT / "tmp/consultant_role_kb_human_label_review_workflow_20260619.py"
DEFAULT_CANDIDATE = ROOT / "tmp/consultant-role-kb-human-label-questionnaire-derived-decisions-20260619.jsonl"
OFFICIAL_TEMPLATE = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"

OUT_JSON = ROOT / "tmp/consultant-role-kb-human-label-candidate-promotion-preflight-20260620.json"
OUT_CHECKLIST = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-promotion-checklist-20260620.csv"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-human-label-candidate-promotion-preflight-20260620.md"

AUTH_ENV = "KB_HUMAN_LABEL_PROMOTION_ACCEPTANCE"
AUTH_VALUE = "accept-reviewed-human-label-candidate"
PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0
OFFICIAL_TEMPLATE_WRITE_COUNT = 0
APPROVAL_EFFECT_COUNT = 0


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("human_label_review_workflow", path)
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


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return "external:KB_HUMAN_LABEL_PROMOTION_CANDIDATE_PATH"


def by_decision_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["decision_id"]: row for row in rows}


def summarize_candidate(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "decision_count": len(rows),
        "pending_count": 0,
        "non_pending_count": 0,
        "approved_count": 0,
        "reject_count": 0,
        "needs_discussion_count": 0,
        "reviewed_metadata_count": 0,
    }
    for row in rows:
        decision = row["decision"]
        if decision == "pending":
            counts["pending_count"] += 1
        else:
            counts["non_pending_count"] += 1
        if decision in {"approve", "override"}:
            counts["approved_count"] += 1
        if decision == "reject":
            counts["reject_count"] += 1
        if decision == "needs_discussion":
            counts["needs_discussion_count"] += 1
        if row.get("reviewer") and row.get("reviewed_at"):
            counts["reviewed_metadata_count"] += 1
    return counts


def changed_fields(official: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    tracked_fields = [
        "decision",
        "reviewer",
        "reviewed_at",
        "review_notes",
        "approved_source_id",
        "approved_card_id",
        "approved_locator",
        "approved_locator_type",
        "approved_no_source_policy",
    ]
    return [field for field in tracked_fields if official.get(field) != candidate.get(field)]


def checklist_rows(official_rows: list[dict[str, Any]], candidate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    official_by_id = by_decision_id(official_rows)
    candidate_by_id = by_decision_id(candidate_rows)
    rows: list[dict[str, Any]] = []
    for decision_id in sorted(set(official_by_id) | set(candidate_by_id)):
        official = official_by_id.get(decision_id)
        candidate = candidate_by_id.get(decision_id)
        if official is None:
            rows.append(
                {
                    "decision_id": decision_id,
                    "label_id": candidate.get("label_id", ""),
                    "eval_id": candidate.get("eval_id", ""),
                    "candidate_decision": candidate.get("decision", ""),
                    "official_decision": "missing",
                    "changed_fields": "candidate_missing_from_official",
                    "promotion_action": "block_id_mismatch",
                    "reviewer": candidate.get("reviewer") or "",
                    "reviewed_at": candidate.get("reviewed_at") or "",
                }
            )
            continue
        if candidate is None:
            rows.append(
                {
                    "decision_id": decision_id,
                    "label_id": official.get("label_id", ""),
                    "eval_id": official.get("eval_id", ""),
                    "candidate_decision": "missing",
                    "official_decision": official.get("decision", ""),
                    "changed_fields": "candidate_missing",
                    "promotion_action": "block_id_mismatch",
                    "reviewer": "",
                    "reviewed_at": "",
                }
            )
            continue
        fields = changed_fields(official, candidate)
        if candidate["decision"] == "pending":
            action = "no_change_pending"
        elif not candidate.get("reviewer") or not candidate.get("reviewed_at"):
            action = "block_missing_review_metadata"
        elif fields:
            action = "candidate_change_requires_acceptance"
        else:
            action = "no_change"
        rows.append(
            {
                "decision_id": decision_id,
                "label_id": candidate.get("label_id", ""),
                "eval_id": candidate.get("eval_id", ""),
                "candidate_decision": candidate.get("decision", ""),
                "official_decision": official.get("decision", ""),
                "changed_fields": "|".join(fields),
                "promotion_action": action,
                "reviewer": candidate.get("reviewer") or "",
                "reviewed_at": candidate.get("reviewed_at") or "",
            }
        )
    return rows


def write_checklist(rows: list[dict[str, Any]]) -> None:
    OUT_CHECKLIST.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "decision_id",
        "label_id",
        "eval_id",
        "candidate_decision",
        "official_decision",
        "changed_fields",
        "promotion_action",
        "reviewer",
        "reviewed_at",
    ]
    with OUT_CHECKLIST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    workflow = load_module(WORKFLOW_MODULE)
    candidate_path = env_path("KB_HUMAN_LABEL_PROMOTION_CANDIDATE_PATH", DEFAULT_CANDIDATE)
    official_rows = read_jsonl(OFFICIAL_TEMPLATE)
    candidate_rows = read_jsonl(candidate_path)
    seed_rows = workflow.read_jsonl(workflow.SEED_PATH)

    official_validation = workflow.validate_workflow(seed_rows, official_rows)
    candidate_validation = workflow.validate_workflow(seed_rows, candidate_rows)
    candidate_counts = summarize_candidate(candidate_rows)
    rows = checklist_rows(official_rows, candidate_rows)
    write_checklist(rows)

    official_ids = {row["decision_id"] for row in official_rows}
    candidate_ids = {row["decision_id"] for row in candidate_rows}
    id_sets_match = official_ids == candidate_ids
    changed_row_count = sum(1 for row in rows if row["changed_fields"])
    acceptance_authorized = os.environ.get(AUTH_ENV, "").strip() == AUTH_VALUE
    full_human_gold_ready = (
        candidate_validation["failure_count"] == 0
        and candidate_counts["decision_count"] == candidate_validation["seed_label_count"]
        and candidate_counts["approved_count"] == candidate_validation["seed_label_count"]
        and candidate_counts["pending_count"] == 0
    )

    blockers: list[str] = []
    if official_validation["failure_count"] != 0:
        blockers.append("official_template_validation_failed")
    if candidate_validation["failure_count"] != 0:
        blockers.append("candidate_validation_failed")
    if not id_sets_match:
        blockers.append("decision_id_set_mismatch")
    if candidate_counts["non_pending_count"] == 0:
        blockers.append("no_reviewed_candidate_decisions")
    if candidate_counts["pending_count"] > 0:
        blockers.append("candidate_has_pending_decisions")
    if not full_human_gold_ready:
        blockers.append("candidate_not_ready_for_human_gold_metrics")
    if not acceptance_authorized:
        blockers.append("explicit_acceptance_authorization_missing")

    provider_call_count = max(
        PROVIDER_CALL_COUNT,
        official_validation["provider_call_count"],
        candidate_validation["provider_call_count"],
    )
    live_kb_write_count = max(
        LIVE_KB_WRITE_COUNT,
        official_validation["live_kb_write_count"],
        candidate_validation["live_kb_write_count"],
    )
    promotion_ready = not blockers and provider_call_count == 0 and live_kb_write_count == 0
    payload = {
        "ok": official_validation["ok"] and candidate_validation["ok"] and id_sets_match,
        "status": "ready_for_explicit_acceptance" if promotion_ready else "blocked",
        "candidate_decisions": display_path(candidate_path),
        "official_template": str(OFFICIAL_TEMPLATE.relative_to(ROOT)),
        "promotion_checklist": str(OUT_CHECKLIST.relative_to(ROOT)),
        "official_template_write_count": OFFICIAL_TEMPLATE_WRITE_COUNT,
        "approval_effect_count": APPROVAL_EFFECT_COUNT,
        "acceptance_authorized": acceptance_authorized,
        "acceptance_env": AUTH_ENV,
        "required_acceptance_value": AUTH_VALUE,
        "decision_id_sets_match": id_sets_match,
        "changed_row_count": changed_row_count,
        "seed_label_count": candidate_validation["seed_label_count"],
        "candidate_decision_count": candidate_counts["decision_count"],
        "candidate_pending_count": candidate_counts["pending_count"],
        "candidate_non_pending_count": candidate_counts["non_pending_count"],
        "candidate_approved_count": candidate_counts["approved_count"],
        "candidate_reject_count": candidate_counts["reject_count"],
        "candidate_needs_discussion_count": candidate_counts["needs_discussion_count"],
        "candidate_reviewed_metadata_count": candidate_counts["reviewed_metadata_count"],
        "candidate_failure_count": candidate_validation["failure_count"],
        "official_failure_count": official_validation["failure_count"],
        "full_human_gold_ready": full_human_gold_ready,
        "human_gold_metrics_claimable": full_human_gold_ready and acceptance_authorized,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "provider_call_count": provider_call_count,
        "live_kb_write_count": live_kb_write_count,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "shared_staging_deployment": "not deployed",
        "manual_review_boundary": "promotion preflight only; official template remains unchanged",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Human Label Candidate Promotion Preflight"
status: "draft"
created_at: "2026-06-20"
source_documents:
  - "{payload["candidate_decisions"]}"
  - "{payload["official_template"]}"
scope: "fail-closed preflight before accepting reviewed human-label candidates into the official decision record"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "preflight only; official decision template unchanged"
---

# Consultant Role KB Human Label Candidate Promotion Preflight

## 0. Boundary

This preflight validates whether a human-label candidate JSONL is safe to
accept into the official decision record. It does not overwrite the official
template, create human-gold labels, call a provider, deploy staging, or ingest
into a live KB.

## 1. Result

| field | value |
|---|---:|
| status | {payload["status"]} |
| blocker_count | {payload["blocker_count"]} |
| candidate_decision_count | {payload["candidate_decision_count"]} |
| candidate_pending_count | {payload["candidate_pending_count"]} |
| candidate_non_pending_count | {payload["candidate_non_pending_count"]} |
| candidate_approved_count | {payload["candidate_approved_count"]} |
| changed_row_count | {payload["changed_row_count"]} |
| full_human_gold_ready | {str(payload["full_human_gold_ready"]).lower()} |
| human_gold_metrics_claimable | {str(payload["human_gold_metrics_claimable"]).lower()} |
| official_template_write_count | {payload["official_template_write_count"]} |
| approval_effect_count | {payload["approval_effect_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

## 2. Promotion Checklist

- Checklist CSV: `shared/eval/consultant-agent/human-gold-locator-label-promotion-checklist-20260620.csv`
- Candidate: `{payload["candidate_decisions"]}`
- Official template: `{payload["official_template"]}`

## 3. Current Blockers

```json
{json.dumps(payload["blockers"], ensure_ascii=False, indent=2)}
```

## 4. Acceptance Rule

The preflight is ready only when the candidate passes schema/logic validation,
the decision ID set matches the official template, all 50 labels are reviewed
and approved or overridden, no labels remain pending, and the operator supplies
explicit acceptance authorization:

```bash
{AUTH_ENV}={AUTH_VALUE} python3 tmp/consultant_role_kb_human_label_candidate_promotion_preflight_20260620.py
```

Boundary: even an authorized ready preflight is evidence for acceptance
readiness; the official decision file must be updated by a deliberate,
reviewed step, not by this preflight script.
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
