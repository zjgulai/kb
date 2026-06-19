#!/usr/bin/env python3
"""Build reviewer-facing questionnaire for human-gold locator labels.

Boundary: local questionnaire packaging only. This script does not approve
labels, edit official decision templates, call a provider, deploy staging, or
ingest into a live KB.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-review.queue-20260619.csv"
QUESTIONNAIRE = ROOT / "shared/eval/consultant-agent/human-gold-locator-label-review.questionnaire-20260619.csv"
OUT_JSON = ROOT / "tmp/consultant-role-kb-human-label-reviewer-questionnaire-validation-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-human-label-reviewer-questionnaire-20260619.md"

OFFICIAL_TEMPLATE = "shared/eval/consultant-agent/human-gold-locator-label-decisions.template-20260619.jsonl"
PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0
APPROVAL_EFFECT_COUNT = 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def choice_options(label_type: str) -> list[str]:
    if label_type == "locator_gold_candidate":
        return ["approve", "override", "reject", "needs_discussion", "pending"]
    return ["approve", "reject", "needs_discussion", "pending"]


def mapping(label_type: str) -> str:
    if label_type == "locator_gold_candidate":
        payload: dict[str, Any] = {
            "approve": "approve proposed source/card/locator as human-gold label",
            "override": "replace source/card/locator with reviewer supplied fields",
            "reject": "reject the machine-seeded locator label",
            "needs_discussion": "keep blocked pending reviewer discussion",
            "pending": "no human decision yet",
        }
    else:
        payload = {
            "approve": "approve no-source refusal policy for this eval",
            "reject": "reject no-source refusal policy label",
            "needs_discussion": "keep blocked pending reviewer discussion",
            "pending": "no human decision yet",
        }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def questionnaire_row(row: dict[str, str]) -> dict[str, str]:
    options = choice_options(row["label_type"])
    return {
        "questionnaire_item_id": f"Q-{row['review_item_id']}",
        "review_item_id": row["review_item_id"],
        "label_id": row["label_id"],
        "eval_id": row["eval_id"],
        "label_type": row["label_type"],
        "category": row["category"],
        "workspace": row["workspace"],
        "question": row["question"],
        "choice_options": "|".join(options),
        "default_choice": "pending",
        "current_decision": row["current_decision"],
        "reviewer_response": "",
        "reviewer": "",
        "reviewed_at": "",
        "review_notes": "",
        "approved_source_id": "",
        "approved_card_id": "",
        "approved_locator": "",
        "approved_locator_type": "",
        "approved_no_source_policy": "",
        "proposed_source_id": row["proposed_source_id"],
        "proposed_source_title": row["proposed_source_title"],
        "proposed_card_id": row["proposed_card_id"],
        "proposed_locator": row["proposed_locator"],
        "proposed_locator_type": row["proposed_locator_type"],
        "proposed_evidence_grade": row["proposed_evidence_grade"],
        "proposed_license_status": row["proposed_license_status"],
        "must_cite_source": row["must_cite_source"],
        "expected_refusal": row["expected_refusal"],
        "blocked_actions_expected": row["blocked_actions_expected"],
        "official_template_path": OFFICIAL_TEMPLATE,
        "official_decision_id": row["review_item_id"],
        "choice_to_template_mapping": mapping(row["label_type"]),
        "repository_boundary": "production unchanged; no KB provider call; no live KB ingestion; no staging deployment",
        "approval_effect": "none_questionnaire_only",
        "validation_command": "python3 tmp/consultant_role_kb_human_label_questionnaire_intake_20260619.py",
    }


def write_questionnaire(rows: list[dict[str, str]]) -> None:
    fieldnames = list(questionnaire_row(rows[0]).keys())
    QUESTIONNAIRE.parent.mkdir(parents=True, exist_ok=True)
    with QUESTIONNAIRE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(questionnaire_row(row))


def main() -> None:
    queue_rows = read_csv(QUEUE)
    write_questionnaire(queue_rows)
    locator_count = sum(1 for row in queue_rows if row["label_type"] == "locator_gold_candidate")
    refusal_count = sum(1 for row in queue_rows if row["label_type"] == "refusal_policy_no_source")
    payload = {
        "ok": True,
        "questionnaire_ready": len(queue_rows) == 50 and locator_count == 48 and refusal_count == 2,
        "questionnaire": str(QUESTIONNAIRE.relative_to(ROOT)),
        "questionnaire_row_count": len(queue_rows),
        "locator_question_count": locator_count,
        "refusal_question_count": refusal_count,
        "official_decision_template_updated": False,
        "approval_effect_count": APPROVAL_EFFECT_COUNT,
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "questionnaire only; official reviewer decision file remains required",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Human Label Reviewer Questionnaire"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "shared/eval/consultant-agent/human-gold-locator-label-review.queue-20260619.csv"
scope: "human-facing questionnaire for pending human-gold label review"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "questionnaire only; no human-gold approvals recorded"
---

# Consultant Role KB Human Label Reviewer Questionnaire

## 0. Boundary

This questionnaire supports human review of machine-seeded locator labels. It
does not approve labels, edit official decision templates, call a provider,
deploy staging, or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| questionnaire_ready | {str(payload["questionnaire_ready"]).lower()} |
| questionnaire_row_count | {payload["questionnaire_row_count"]} |
| locator_question_count | {payload["locator_question_count"]} |
| refusal_question_count | {payload["refusal_question_count"]} |
| approval_effect_count | {payload["approval_effect_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

## 2. Use

Fill `shared/eval/consultant-agent/human-gold-locator-label-review.questionnaire-20260619.csv`
only after real human review. Then run:

```bash
python3 tmp/consultant_role_kb_human_label_questionnaire_intake_20260619.py
```

The converter writes a temporary candidate JSONL under `tmp/`; candidate files
are not human-gold evidence until accepted into the official decision file.
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "questionnaire_ready": payload["questionnaire_ready"],
                "questionnaire_row_count": payload["questionnaire_row_count"],
                "approval_effect_count": payload["approval_effect_count"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
