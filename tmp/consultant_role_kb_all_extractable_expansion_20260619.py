#!/usr/bin/env python3
"""Expand consultant-role KB cards to all currently extractable sources.

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

SELECTION_OUT = ROOT / "drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv"
CARDS_OUT = ROOT / "tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl"
GATE_OUT = ROOT / "tmp/consultant-role-kb-all-extractable-card-gate-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-all-extractable-expansion-report-20260619.md"


def load_base_module() -> Any:
    spec = importlib.util.spec_from_file_location("consultant_all_extractable_base_expansion", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load base expansion script: {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["consultant_all_extractable_base_expansion"] = module
    spec.loader.exec_module(module)
    return module


def candidate_source_ids(sources: dict[str, dict[str, str]]) -> list[str]:
    return sorted(sources)


def write_selection(
    sources: dict[str, dict[str, str]],
    selected_ids: list[str],
    skipped_sources: list[dict[str, Any]],
    batch60_ids: set[str],
) -> None:
    columns = [
        "source_id",
        "source_title",
        "selection_status",
        "selection_group",
        "extraction_batch",
        "duplicate_policy",
        "license_status",
        "owner_review_status",
        "intake_status",
        "selection_reason",
    ]
    skipped_by_id = {item["source_id"]: item for item in skipped_sources}
    with SELECTION_OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for source_id in candidate_source_ids(sources):
            source = sources[source_id]
            skipped = skipped_by_id.get(source_id)
            if skipped:
                status = "skipped"
                group = skipped["reason"]
                reason = skipped["reason"]
            else:
                status = "selected" if source_id in selected_ids else "not_selected"
                group = "retained_batch60" if source_id in batch60_ids else "all_extractable_addition"
                reason = "retained from batch60" if source_id in batch60_ids else "selected as currently extractable registered source"
            writer.writerow(
                {
                    "source_id": source_id,
                    "source_title": source["source_title"],
                    "selection_status": status,
                    "selection_group": group,
                    "extraction_batch": source.get("extraction_batch", ""),
                    "duplicate_policy": source.get("duplicate_policy", ""),
                    "license_status": source["license_status"],
                    "owner_review_status": source["owner_review_status"],
                    "intake_status": source["intake_status"],
                    "selection_reason": reason,
                }
            )


def normalize_card(card: dict[str, Any], source_id: str, ordinal: int) -> dict[str, Any]:
    card["card_id"] = f"CARD-{source_id}-ALLX-{ordinal:03d}"
    card["card_status"] = "all_extractable_local_draft"
    card["source_use_boundary"] = "internal local PoC only; no redistribution; no client-ready publishing"
    return card


def write_report(gate_eval: dict[str, Any]) -> None:
    summary = gate_eval["summary"]
    skipped = gate_eval.get("metadata", {}).get("skipped_sources", [])
    selected_count = summary["source_count"]
    skipped_duplicate = [item for item in skipped if item["reason"] == "duplicate_secondary"]
    skipped_insufficient = [item for item in skipped if item["reason"] == "insufficient_extractable_units"]
    report = f"""---
title: "Consultant Role KB All-Extractable Expansion Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv"
scope: "local expansion to all currently extractable consultant-role sources"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local batch cards only; no live KB ingestion"
---

# Consultant Role KB All-Extractable Expansion Report

## 0. Boundary

This is local draft expansion only. It does not call a provider, ingest into a
live KB, deploy production code, approve source licensing, or reproduce long
source text.

## 1. Outputs

| artifact | path |
|---|---|
| source selection | `drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv` |
| all-extractable cards | `tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl` |
| gate eval | `tmp/consultant-role-kb-all-extractable-card-gate-eval-20260619.json` |

## 2. Gate Metrics

| metric | value |
|---|---:|
| selected_source_count | {selected_count} |
| card_count | {summary["card_count"]} |
| metadata_completeness | {summary["metadata_completeness"]} |
| unit_locator_coverage | {summary["unit_locator_coverage"]} |
| source_only_citation_violation_count | {summary["source_only_citation_violation_count"]} |
| long_text_violation_count | {summary["long_text_violation_count"]} |
| provider_call_count | {summary["provider_call_count"]} |
| live_kb_write_count | {summary["live_kb_write_count"]} |
| skipped_duplicate_sources | {len(skipped_duplicate)} |
| skipped_insufficient_unit_sources | {len(skipped_insufficient)} |

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
            report += f"| {item['source_id']} | {item['reason']} | {item.get('extractable_unit_count', '')} |\n"
    else:
        report += "None.\n"

    report += """
## 5. Interpretation

Fact: all currently extractable non-duplicate sources were converted into local
draft cards with complete required metadata and unit locators.

Inference: this is the current full typed-card extraction ceiling under the
existing local parser/loader stack.

Unknown: legal/source-owner clearance, human-gold citation precision, and
online production answer quality are still not proven.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    base = load_base_module()
    anchor_tools = base.load_anchor_module()
    sources = base.read_sources()
    batch60_ids = set()
    batch60_selection = ROOT / "drafts/analysis/consultant-role-kb-batch60-source-selection-20260619.csv"
    if batch60_selection.exists():
        with batch60_selection.open(encoding="utf-8") as f:
            batch60_ids = {row["source_id"] for row in csv.DictReader(f)}

    cards: list[dict[str, Any]] = []
    source_ids: list[str] = []
    skipped_sources: list[dict[str, Any]] = []
    for source_id in candidate_source_ids(sources):
        source = sources[source_id]
        if source.get("duplicate_policy") == "secondary_to_pdf_duplicate":
            skipped_sources.append(
                {
                    "source_id": source_id,
                    "reason": "duplicate_secondary",
                    "extractable_unit_count": "",
                    "source_title": source["source_title"],
                }
            )
            continue
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
            cards.append(normalize_card(card, source_id, ordinal))

    write_selection(sources, source_ids, skipped_sources, batch60_ids)
    CARDS_OUT.write_text(
        "\n".join(json.dumps(card, ensure_ascii=False, sort_keys=True) for card in cards) + "\n",
        encoding="utf-8",
    )
    gate_eval = base.validate_cards(cards)
    gate_eval["metadata"] = {
        "created_at": "2026-06-19",
        "scope": "all-extractable consultant-role card expansion",
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
                "skipped_sources": skipped_sources,
                "outputs": [str(SELECTION_OUT), str(CARDS_OUT), str(GATE_OUT), str(REPORT_OUT)],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
