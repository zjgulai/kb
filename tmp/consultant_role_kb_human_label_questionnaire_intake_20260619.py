#!/usr/bin/env python3
"""Convert answered human-label questionnaire rows into candidate JSONL.

Boundary: local candidate generation and validation only. This script does not
overwrite the official human-label decision template, create human-gold labels,
call providers, deploy staging, or ingest into a live KB.
"""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUESTIONNAIRE = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-review.questionnaire-20260619.csv"
OFFICIAL_TEMPLATE = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
WORKFLOW_MODULE = ROOT / "tmp/consultant_role_kb_human_label_review_workflow_20260619.py"

OUT_DECISIONS = ROOT / "tmp/consultant-role-kb-human-label-questionnaire-derived-decisions-20260619.jsonl"
OUT_JSON = ROOT / "tmp/consultant-role-kb-human-label-questionnaire-intake-validation-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-human-label-questionnaire-intake-20260619.md"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0
OFFICIAL_TEMPLATE_WRITE_COUNT = 0
APPROVAL_EFFECT_COUNT = 0

LOCATOR_CHOICES = {"approve", "override", "reject", "needs_discussion", "pending", ""}
REFUSAL_CHOICES = {"approve", "reject", "needs_discussion", "pending", ""}


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("human_label_review_workflow", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def response(row: dict[str, str]) -> str:
    return row.get("reviewer_response", "").strip() or row.get("default_choice", "pending").strip() or "pending"


def blank_to_none(value: str) -> str | None:
    value = value.strip()
    return value or None


def bool_from_cell(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "approve"}


def overlay_decision(base: dict[str, Any], row: dict[str, str]) -> dict[str, Any]:
    item = dict(base)
    choice = response(row)
    if choice == "pending":
        return item
    item["decision"] = choice
    item["reviewer"] = blank_to_none(row.get("reviewer", ""))
    item["reviewed_at"] = blank_to_none(row.get("reviewed_at", ""))
    item["review_notes"] = blank_to_none(row.get("review_notes", ""))
    if row["label_type"] == "locator_gold_candidate":
        if choice == "approve":
            item["approved_source_id"] = row["proposed_source_id"] or None
            item["approved_card_id"] = row["proposed_card_id"] or None
            item["approved_locator"] = row["proposed_locator"] or None
            item["approved_locator_type"] = row["proposed_locator_type"] or None
        elif choice == "override":
            item["approved_source_id"] = blank_to_none(row.get("approved_source_id", ""))
            item["approved_card_id"] = blank_to_none(row.get("approved_card_id", ""))
            item["approved_locator"] = blank_to_none(row.get("approved_locator", ""))
            item["approved_locator_type"] = blank_to_none(row.get("approved_locator_type", ""))
        else:
            item["approved_source_id"] = None
            item["approved_card_id"] = None
            item["approved_locator"] = None
            item["approved_locator_type"] = None
        item["approved_no_source_policy"] = False
    else:
        item["approved_no_source_policy"] = choice == "approve" or bool_from_cell(
            row.get("approved_no_source_policy", "")
        )
        item["approved_source_id"] = None
        item["approved_card_id"] = None
        item["approved_locator"] = None
        item["approved_locator_type"] = None
    return item


def validate_responses(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        item_id = row["questionnaire_item_id"]
        choice = response(row)
        if item_id in seen:
            failures.append({"item_id": item_id, "failure": "duplicate questionnaire item"})
        seen.add(item_id)
        allowed = LOCATOR_CHOICES if row["label_type"] == "locator_gold_candidate" else REFUSAL_CHOICES
        if choice not in allowed:
            failures.append({"item_id": item_id, "failure": f"invalid response: {choice}"})
        if choice not in {"", "pending"}:
            if not row.get("reviewer", "").strip() or not row.get("reviewed_at", "").strip():
                failures.append({"item_id": item_id, "failure": "non-pending response requires reviewer and reviewed_at"})
        if choice in {"reject", "needs_discussion"} and not row.get("review_notes", "").strip():
            failures.append({"item_id": item_id, "failure": f"{choice} requires review_notes"})
        if choice == "override":
            for field in ["approved_source_id", "approved_card_id", "approved_locator", "approved_locator_type"]:
                if not row.get(field, "").strip():
                    failures.append({"item_id": item_id, "failure": f"override requires {field}"})
    return failures


def main() -> None:
    workflow = load_module(WORKFLOW_MODULE)
    questionnaire_rows = read_csv(QUESTIONNAIRE)
    template_rows = read_jsonl(OFFICIAL_TEMPLATE)
    by_id = {row["decision_id"]: row for row in template_rows}
    response_failures = validate_responses(questionnaire_rows)

    decisions = [dict(row) for row in template_rows]
    index = {row["decision_id"]: idx for idx, row in enumerate(decisions)}
    answered_count = 0
    for row in questionnaire_rows:
        choice = response(row)
        if choice not in {"", "pending"}:
            answered_count += 1
        decision_id = row["official_decision_id"]
        decisions[index[decision_id]] = overlay_decision(by_id[decision_id], row)

    write_jsonl(OUT_DECISIONS, decisions)
    seed_rows = workflow.read_jsonl(workflow.SEED_PATH)
    validation = workflow.validate_workflow(seed_rows, decisions)
    failure_count = len(response_failures) + int(validation["failure_count"])
    provider_call_count = max(PROVIDER_CALL_COUNT, int(validation["provider_call_count"]))
    live_kb_write_count = max(LIVE_KB_WRITE_COUNT, int(validation["live_kb_write_count"]))
    payload = {
        "ok": failure_count == 0,
        "status": "valid_candidate" if failure_count == 0 else "invalid_candidate",
        "questionnaire": str(QUESTIONNAIRE.relative_to(ROOT)),
        "derived_decisions": str(OUT_DECISIONS.relative_to(ROOT)),
        "official_decision_template_updated": False,
        "official_template_write_count": OFFICIAL_TEMPLATE_WRITE_COUNT,
        "questionnaire_row_count": len(questionnaire_rows),
        "answered_response_count": answered_count,
        "response_failure_count": len(response_failures),
        "response_failures": response_failures,
        "seed_label_count": validation["seed_label_count"],
        "derived_decision_count": len(decisions),
        "pending_decision_count": validation["pending_decision_count"],
        "approved_decision_count": validation["approved_decision_count"],
        "failure_count": failure_count,
        "approval_effect_count": APPROVAL_EFFECT_COUNT,
        "provider_call_count": provider_call_count,
        "live_kb_write_count": live_kb_write_count,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "candidate JSONL only; official reviewer decision file remains required",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Human Label Questionnaire Intake"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/eval/consultant-agent/human-gold-locator-label-review.questionnaire-20260619.csv"
  - "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
scope: "local conversion and validation of answered human-label questionnaire rows"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "candidate JSONL only; official human-label decisions unchanged"
---

# Consultant Role KB Human Label Questionnaire Intake

## 0. Boundary

This intake converts answered human-label questionnaire rows into a temporary
candidate decision JSONL under `tmp/`. It does not overwrite the official
decision template, create human-gold labels, call a provider, deploy staging,
or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| ok | {str(payload["ok"]).lower()} |
| status | {payload["status"]} |
| questionnaire_row_count | {payload["questionnaire_row_count"]} |
| answered_response_count | {payload["answered_response_count"]} |
| pending_decision_count | {payload["pending_decision_count"]} |
| approved_decision_count | {payload["approved_decision_count"]} |
| official_template_write_count | {payload["official_template_write_count"]} |
| approval_effect_count | {payload["approval_effect_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

## 2. Candidate Output

- Candidate decisions: `tmp/consultant-role-kb-human-label-questionnaire-derived-decisions-20260619.jsonl`
- Validation: `tmp/consultant-role-kb-human-label-questionnaire-intake-validation-20260619.json`

## 3. Interpretation

Fact: with the current unfilled questionnaire, all derived decisions remain
pending and no official decision template is updated.

Boundary: candidate files under `tmp/` are not human-gold evidence until a
human reviewer accepts them and the official decision file is filled or supplied
to manual intake through a reviewed path.
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "ok": payload["ok"],
                "answered_response_count": payload["answered_response_count"],
                "approved_decision_count": payload["approved_decision_count"],
                "failure_count": payload["failure_count"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
