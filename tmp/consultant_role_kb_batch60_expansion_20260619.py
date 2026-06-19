#!/usr/bin/env python3
"""Expand consultant-role KB cards from 30 to 60 registered sources.

Boundary: local draft batch expansion only. No provider call, no live KB
ingestion, no production change, and no source-text redistribution.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "tmp/consultant_role_kb_batch30_expansion_20260619.py"

SELECTION_OUT = ROOT / "drafts/analysis/consultant-role-kb-batch60-source-selection-20260619.csv"
CARDS_OUT = ROOT / "tmp/consultant-role-kb-batch60-cards-20260619.jsonl"
GATE_OUT = ROOT / "tmp/consultant-role-kb-batch60-card-gate-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-batch60-expansion-report-20260619.md"

BATCH_SIZE = 60


def load_base_module() -> Any:
    spec = importlib.util.spec_from_file_location("consultant_batch60_base_expansion", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load base expansion script: {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["consultant_batch60_base_expansion"] = module
    spec.loader.exec_module(module)
    return module


def candidate_source_ids(base: Any, sources: dict[str, dict[str, str]]) -> list[str]:
    selected = list(base.SELECTED_SOURCE_IDS)
    for source_id in sorted(sources):
        source = sources[source_id]
        if source_id in selected:
            continue
        if source.get("duplicate_policy") == "secondary_to_pdf_duplicate":
            continue
        selected.append(source_id)
    return selected


def write_selection(sources: dict[str, dict[str, str]], source_ids: list[str], base_source_ids: set[str]) -> None:
    columns = [
        "source_id",
        "source_title",
        "selection_group",
        "extraction_batch",
        "duplicate_policy",
        "license_status",
        "owner_review_status",
        "intake_status",
        "selection_reason",
    ]
    with SELECTION_OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for source_id in source_ids:
            source = sources[source_id]
            group = "retained_batch30" if source_id in base_source_ids else "batch60_addition"
            reason = (
                "retained from approved batch30 local expansion"
                if group == "retained_batch30"
                else "next non-duplicate registered source selected for local batch60 coverage"
            )
            writer.writerow(
                {
                    "source_id": source_id,
                    "source_title": source["source_title"],
                    "selection_group": group,
                    "extraction_batch": source.get("extraction_batch", ""),
                    "duplicate_policy": source.get("duplicate_policy", ""),
                    "license_status": source["license_status"],
                    "owner_review_status": source["owner_review_status"],
                    "intake_status": source["intake_status"],
                    "selection_reason": reason,
                }
            )


def normalize_batch60_card(card: dict[str, Any], source_id: str, ordinal: int) -> dict[str, Any]:
    card["card_id"] = f"CARD-{source_id}-B60-{ordinal:03d}"
    card["card_status"] = "batch60_local_draft"
    card["source_use_boundary"] = "internal local PoC only; no redistribution; no client-ready publishing"
    return card


def write_report(gate_eval: dict[str, Any]) -> None:
    summary = gate_eval["summary"]
    skipped = gate_eval.get("metadata", {}).get("skipped_sources", [])
    report = f"""---
title: "Consultant Role KB Batch-60 Expansion Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-batch60-source-selection-20260619.csv"
scope: "local batch expansion from 30 to 60 consultant-role sources"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local batch cards only; no live KB ingestion"
---

# Consultant Role KB Batch-60 Expansion Report

## 0. Boundary

This is local draft expansion only. It does not call a provider, ingest into a
live KB, deploy production code, approve source licensing, or reproduce long
source text.

## 1. Outputs

| artifact | path |
|---|---|
| source selection | `drafts/analysis/consultant-role-kb-batch60-source-selection-20260619.csv` |
| batch-60 cards | `tmp/consultant-role-kb-batch60-cards-20260619.jsonl` |
| gate eval | `tmp/consultant-role-kb-batch60-card-gate-eval-20260619.json` |

## 2. Gate Metrics

| metric | value |
|---|---:|
| source_count | {summary["source_count"]} |
| card_count | {summary["card_count"]} |
| metadata_completeness | {summary["metadata_completeness"]} |
| unit_locator_coverage | {summary["unit_locator_coverage"]} |
| source_only_citation_violation_count | {summary["source_only_citation_violation_count"]} |
| long_text_violation_count | {summary["long_text_violation_count"]} |
| provider_call_count | {summary["provider_call_count"]} |
| live_kb_write_count | {summary["live_kb_write_count"]} |
| skipped_insufficient_unit_sources | {len(skipped)} |

## 3. Cards By Type

| card_type | card_count |
|---|---:|
"""
    for card_type, count in summary["by_card_type"].items():
        report += f"| {card_type} | {count} |\n"

    report += "\n## 4. Skipped Sources\n\n"
    if skipped:
        report += "| source_id | reason | extractable_unit_count |\n|---|---|---:|\n"
        for item in skipped:
            report += f"| {item['source_id']} | {item['reason']} | {item['extractable_unit_count']} |\n"
    else:
        report += "None.\n"

    report += """
## 5. Interpretation

Fact: the batch-60 expansion produced source-balanced cards with complete
required metadata and unit locators.

Inference: batch-60 can proceed to card QA and local retrieval/citation
regression as a draft artifact.

Unknown: legal/source-owner clearance and human-gold citation precision are
still not proven.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    base = load_base_module()
    anchor_tools = base.load_anchor_module()
    sources = base.read_sources()
    base_source_ids = set(base.SELECTED_SOURCE_IDS)

    cards: list[dict[str, Any]] = []
    source_ids: list[str] = []
    skipped_sources: list[dict[str, Any]] = []
    for source_id in candidate_source_ids(base, sources):
        if len(source_ids) >= BATCH_SIZE:
            break
        source = sources[source_id]
        units = anchor_tools.load_units(Path(source["source_uri"]), {"source_id": source_id, "sheet_name": ""})
        selected_units = base.select_units(source, units)
        if len(selected_units) < base.MAX_CARDS_PER_SOURCE:
            skipped_sources.append(
                {
                    "source_id": source_id,
                    "reason": "insufficient_extractable_units",
                    "extractable_unit_count": len(selected_units),
                    "source_title": source["source_title"],
                }
            )
            continue
        source_ids.append(source_id)
        for ordinal, unit in enumerate(selected_units, start=1):
            card = base.card_for_unit(source, unit, ordinal)
            card["source_unit_count"] = len(units)
            cards.append(normalize_batch60_card(card, source_id, ordinal))

    if len(source_ids) != BATCH_SIZE:
        raise SystemExit(f"Expected {BATCH_SIZE} selected sources, got {len(source_ids)}; skipped={skipped_sources}")
    write_selection(sources, source_ids, base_source_ids)

    CARDS_OUT.write_text(
        "\n".join(json.dumps(card, ensure_ascii=False, sort_keys=True) for card in cards) + "\n",
        encoding="utf-8",
    )
    gate_eval = base.validate_cards(cards)
    gate_eval["metadata"] = {
        "created_at": "2026-06-19",
        "scope": "batch-60 consultant-role card expansion",
        "provider_call_boundary": "no KB provider call",
        "production_impact": "production unchanged",
        "implementation_status": "local batch cards only; no live KB ingestion",
        "source_register": str(base.FULL_REGISTER_PATH.relative_to(ROOT)),
        "source_selection": str(SELECTION_OUT.relative_to(ROOT)),
        "cards": str(CARDS_OUT.relative_to(ROOT)),
        "skipped_sources": skipped_sources,
    }
    GATE_OUT.write_text(json.dumps(gate_eval, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(gate_eval)
    print(
        json.dumps(
            {
                "summary": gate_eval["summary"],
                "outputs": [str(SELECTION_OUT), str(CARDS_OUT), str(GATE_OUT), str(REPORT_OUT)],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
