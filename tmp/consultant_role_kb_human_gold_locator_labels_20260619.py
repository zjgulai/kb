#!/usr/bin/env python3
"""Build a pending-review locator-label seed set for consultant-agent evals."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVAL_SET = ROOT / "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
ANCHORED_EVAL = ROOT / "tmp/consultant-role-kb-all-extractable-anchored-retrieval-citation-eval-20260619.json"
RECORDS = ROOT / "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/records.jsonl"
SOURCE_REGISTER = ROOT / "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
OUT_LABELS = ROOT / "shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl"
OUT_QA = ROOT / "tmp/consultant-role-kb-human-gold-locator-labels-qa-20260619.json"
OUT_REPORT = ROOT / "drafts/analysis/consultant-role-kb-human-gold-locator-labels-report-20260619.md"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_records(path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for row in load_jsonl(path):
        records[row["card_id"]] = row
    return records


def load_source_register(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["source_id"]: row for row in csv.DictReader(handle)}


def short_text(value: str | None, *, max_chars: int = 120) -> str:
    if not value:
        return ""
    collapsed = " ".join(str(value).split())
    return collapsed if len(collapsed) <= max_chars else collapsed[: max_chars - 1].rstrip() + "..."


def find_ranked_candidate(
    result: dict[str, Any],
    allowed_source_ids: list[str],
) -> tuple[int | None, dict[str, Any] | None]:
    allowed = set(allowed_source_ids)
    for rank, candidate in enumerate(result.get("top_sources", []), start=1):
        if candidate.get("source_id") in allowed:
            return rank, candidate
    return None, None


def build_label(
    eval_item: dict[str, Any],
    result: dict[str, Any] | None,
    records_by_card: dict[str, dict[str, Any]],
    register_by_source: dict[str, dict[str, str]],
) -> dict[str, Any]:
    eval_id = eval_item["eval_id"]
    allowed_source_ids = eval_item.get("allowed_source_ids", [])
    must_cite = bool(eval_item.get("must_cite_source"))
    blocked_actions = eval_item.get("blocked_actions_expected", [])
    expected_type = eval_item.get("expected_answer_type")

    base = {
        "label_id": f"HGLABEL-{eval_id}-20260619",
        "eval_id": eval_id,
        "label_status": "pending_human_review",
        "label_source": "machine_seed_from_all_extractable_local_eval",
        "human_review": {
            "reviewer": None,
            "decision": "pending",
            "reviewed_at": None,
            "override_source_id": None,
            "override_card_id": None,
            "override_locator": None,
            "notes": None,
        },
        "question": eval_item.get("question"),
        "category": eval_item.get("category"),
        "expected_answer_type": expected_type,
        "must_cite_source": must_cite,
        "expected_source_ids": allowed_source_ids,
        "blocked_actions_expected": blocked_actions,
        "workspace": eval_item.get("workspace", "consultant-p1"),
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "manual_review_boundary": "manual review required before treating as gold",
    }

    if not allowed_source_ids or not must_cite:
        base.update(
            {
                "label_type": "refusal_policy_no_source",
                "gold_candidate": None,
                "retrieval_expectation": {
                    "requires_source": False,
                    "requires_locator": False,
                    "expected_refusal": True,
                    "reason": "Eval is designed to refuse without relying on a registered source citation.",
                },
                "seed_confidence": "policy_only",
            }
        )
        return base

    rank, candidate = find_ranked_candidate(result or {}, allowed_source_ids)
    if not candidate:
        base.update(
            {
                "label_type": "locator_source_missing_in_top5",
                "gold_candidate": None,
                "retrieval_expectation": {
                    "requires_source": True,
                    "requires_locator": True,
                    "expected_refusal": expected_type == "refusal",
                    "reason": "No allowed source was found in the current top5 retrieval output.",
                },
                "seed_confidence": "blocked_needs_manual_label",
            }
        )
        return base

    anchor = candidate.get("citation_anchor", {})
    card_id = candidate.get("card_id")
    record = records_by_card.get(card_id, {})
    source_id = candidate.get("source_id")
    source_row = register_by_source.get(source_id, {})
    seed_confidence = "high" if rank == 1 else "medium_rank_not_top1"
    if anchor.get("anchor_confidence") != "high":
        seed_confidence = "medium_anchor_not_high"

    base.update(
        {
            "label_type": "locator_gold_candidate",
            "gold_candidate": {
                "source_id": source_id,
                "card_id": card_id,
                "retrieval_rank": rank,
                "locator": anchor.get("locator") or candidate.get("locator"),
                "locator_type": anchor.get("locator_type") or candidate.get("locator_type"),
                "anchor_confidence": anchor.get("anchor_confidence"),
                "anchor_match_score": anchor.get("anchor_match_score"),
                "anchor_label_short": short_text(anchor.get("anchor_label")),
                "source_title": record.get("source_title") or source_row.get("source_title"),
                "source_type": record.get("source_type") or source_row.get("source_type"),
                "source_owner": record.get("source_owner") or source_row.get("source_owner"),
                "evidence_grade": record.get("evidence_grade") or source_row.get("evidence_grade"),
                "license_status": record.get("license_status") or source_row.get("license_status"),
                "workspace": record.get("workspace") or source_row.get("workspace"),
                "allowed_agents": record.get("allowed_agents") or source_row.get("allowed_agents"),
                "blocked_actions": record.get("blocked_actions") or source_row.get("blocked_actions"),
                "indexed_text_sha256": record.get("indexed_text_sha256"),
            },
            "retrieval_expectation": {
                "requires_source": True,
                "requires_locator": True,
                "expected_refusal": expected_type == "refusal",
                "accepted_source_ids": allowed_source_ids,
                "accepted_locator_match": "source_id + locator",
            },
            "seed_confidence": seed_confidence,
        }
    )
    return base


def validate(labels: list[dict[str, Any]]) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    counts = Counter(label["label_type"] for label in labels)
    statuses = Counter(label["label_status"] for label in labels)

    for label in labels:
        if label["label_status"] != "pending_human_review":
            failures.append({"label_id": label["label_id"], "reason": "label_status_not_pending_human_review"})
        if label["provider_call_boundary"] != "no KB provider call":
            failures.append({"label_id": label["label_id"], "reason": "provider_boundary_violation"})
        if label["live_kb_ingestion"] != "no live KB ingestion":
            failures.append({"label_id": label["label_id"], "reason": "live_ingestion_boundary_violation"})
        if label["label_type"] == "locator_gold_candidate":
            candidate = label.get("gold_candidate") or {}
            for field in ["source_id", "card_id", "locator", "locator_type", "evidence_grade", "license_status"]:
                if not candidate.get(field):
                    failures.append({"label_id": label["label_id"], "reason": f"missing_{field}"})
            if candidate.get("evidence_grade") == "D":
                failures.append({"label_id": label["label_id"], "reason": "d_grade_gold_candidate"})
            if candidate.get("license_status") != "pending_legal_review":
                failures.append({"label_id": label["label_id"], "reason": "unexpected_license_status"})
        if label["label_type"] == "refusal_policy_no_source" and label["must_cite_source"]:
            failures.append({"label_id": label["label_id"], "reason": "refusal_no_source_but_must_cite"})

    locator_labels = counts["locator_gold_candidate"]
    rank_not_top1 = sum(
        1
        for label in labels
        if label["label_type"] == "locator_gold_candidate"
        and (label.get("gold_candidate") or {}).get("retrieval_rank") != 1
    )

    return {
        "label_count": len(labels),
        "label_type_counts": dict(counts),
        "label_status_counts": dict(statuses),
        "locator_label_count": locator_labels,
        "refusal_policy_no_source_count": counts["refusal_policy_no_source"],
        "locator_coverage_rate": round(locator_labels / 48, 4),
        "rank_not_top1_count": rank_not_top1,
        "provider_call_count": 0,
        "live_kb_write_count": 0,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "failure_count": len(failures),
        "failures": failures,
    }


def write_report(metrics: dict[str, Any]) -> None:
    OUT_REPORT.write_text(
        """---
title: "Consultant Role KB Human-Gold Locator Label Seed Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-eval-set-50.draft.jsonl"
  - "tmp/consultant-role-kb-all-extractable-anchored-retrieval-citation-eval-20260619.json"
  - "shared/indexes/consultant-agent/all-extractable-bge-small-zh-v1-5-20260619/records.jsonl"
scope: "pending-review locator label seed set for consultant-agent retrieval evaluation"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local draft labels only; manual review required"
---

# Consultant Role KB Human-Gold Locator Label Seed Report

## 0. Boundary

This artifact is a machine-generated seed for human review. It is not an
approved human-gold set until a reviewer fills the `human_review` fields and
changes label decisions explicitly.

It does not call a provider, write into a live KB, deploy production code,
approve source licensing, or redistribute raw source text.

## 1. Outputs

| artifact | path |
|---|---|
| label seed | `shared/eval/consultant-agent/human-gold-locator-labels.seed-20260619.jsonl` |
| QA result | `tmp/consultant-role-kb-human-gold-locator-labels-qa-20260619.json` |
| generator | `tmp/consultant_role_kb_human_gold_locator_labels_20260619.py` |

## 2. Metrics

| metric | value |
|---|---:|
| label_count | {label_count} |
| locator_gold_candidate | {locator_count} |
| refusal_policy_no_source | {refusal_count} |
| locator_coverage_rate_for_48_citable_evals | {locator_coverage_rate} |
| rank_not_top1_count | {rank_not_top1_count} |
| pending_human_review | {pending_count} |
| failure_count | {failure_count} |
| provider_call_count | {provider_call_count} |
| live_kb_write_count | {live_kb_write_count} |

## 3. Interpretation

Fact: all 50 eval items now have a structured label seed. The 48 citable evals
have source-and-locator candidates; the 2 no-source refusal evals have explicit
policy-only expectations.

Fact: every label remains `pending_human_review`; this file must not be treated
as approved human-gold evidence.

Inference: this label seed is sufficient to unblock a no-provider retrieval API
contract and future reviewer workflow, but not enough to claim human-approved
locator precision.

Unknown: final human judgment may override source, card, or locator selections.
""".format(
            label_count=metrics["label_count"],
            locator_count=metrics["label_type_counts"].get("locator_gold_candidate", 0),
            refusal_count=metrics["label_type_counts"].get("refusal_policy_no_source", 0),
            locator_coverage_rate=metrics["locator_coverage_rate"],
            rank_not_top1_count=metrics["rank_not_top1_count"],
            pending_count=metrics["label_status_counts"].get("pending_human_review", 0),
            failure_count=metrics["failure_count"],
            provider_call_count=metrics["provider_call_count"],
            live_kb_write_count=metrics["live_kb_write_count"],
        ),
        encoding="utf-8",
    )


def main() -> None:
    eval_items = load_jsonl(EVAL_SET)
    anchored = json.loads(ANCHORED_EVAL.read_text(encoding="utf-8"))
    results_by_eval = {row["eval_id"]: row for row in anchored["results"]}
    records_by_card = load_records(RECORDS)
    register_by_source = load_source_register(SOURCE_REGISTER)

    labels = [
        build_label(item, results_by_eval.get(item["eval_id"]), records_by_card, register_by_source)
        for item in eval_items
    ]
    metrics = validate(labels)

    OUT_LABELS.parent.mkdir(parents=True, exist_ok=True)
    OUT_QA.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)

    OUT_LABELS.write_text(
        "\n".join(json.dumps(label, ensure_ascii=False, sort_keys=True) for label in labels) + "\n",
        encoding="utf-8",
    )
    OUT_QA.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
