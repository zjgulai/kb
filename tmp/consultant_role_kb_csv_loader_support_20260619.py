#!/usr/bin/env python3
"""Add CSV typed-card support for SRC-CONSULT-030 and SRC-CONSULT-031.

Boundary: local draft extraction only. No provider call, no live KB ingestion,
no production change, and no source-text redistribution.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "tmp/consultant_role_kb_batch30_expansion_20260619.py"
ALLX_SCRIPT = ROOT / "tmp/consultant_role_kb_all_extractable_expansion_20260619.py"

CSV_SOURCE_IDS = ["SRC-CONSULT-030", "SRC-CONSULT-031"]
FULL_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
SELECTION_OUT = ROOT / "drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv"
CARDS_OUT = ROOT / "tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl"
CSV_CARDS_OUT = ROOT / "tmp/consultant-role-kb-csv-supported-cards-20260619.jsonl"
GATE_OUT = ROOT / "tmp/consultant-role-kb-all-extractable-card-gate-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-csv-loader-support-report-20260619.md"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def read_sources() -> dict[str, dict[str, str]]:
    with FULL_REGISTER_PATH.open(encoding="utf-8") as handle:
        return {row["source_id"]: row for row in csv.DictReader(handle)}


def normalize_card(card: dict[str, Any], source_id: str, ordinal: int) -> dict[str, Any]:
    card["card_id"] = f"CARD-{source_id}-ALLX-{ordinal:03d}"
    card["card_status"] = "all_extractable_local_draft"
    card["source_use_boundary"] = "internal local PoC only; no redistribution; no client-ready publishing"
    return card


def generate_csv_cards(base: Any, anchor_tools: Any, sources: dict[str, dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cards: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    for source_id in CSV_SOURCE_IDS:
        source = sources[source_id]
        units = anchor_tools.load_units(Path(source["source_uri"]), {"source_id": source_id, "sheet_name": ""})
        selected_units = base.select_units(source, units)
        if len(selected_units) < base.MAX_CARDS_PER_SOURCE:
            raise RuntimeError(f"Expected at least {base.MAX_CARDS_PER_SOURCE} CSV units for {source_id}, got {len(selected_units)}")
        for ordinal, unit in enumerate(selected_units[: base.MAX_CARDS_PER_SOURCE], start=1):
            card = base.card_for_unit(source, unit, ordinal)
            card["source_unit_count"] = len(units)
            cards.append(normalize_card(card, source_id, ordinal))
        coverage.append(
            {
                "source_id": source_id,
                "source_title": source["source_title"],
                "csv_unit_count": len(units),
                "selected_card_count": base.MAX_CARDS_PER_SOURCE,
                "first_locator": selected_units[0]["locator"],
                "locator_type": selected_units[0]["locator_type"],
            }
        )
    return cards, coverage


def merge_cards(existing_cards: list[dict[str, Any]], csv_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    filtered = [card for card in existing_cards if card["source_id"] not in set(CSV_SOURCE_IDS)]
    merged = filtered + csv_cards
    seen: set[str] = set()
    duplicates: list[str] = []
    for card in merged:
        if card["card_id"] in seen:
            duplicates.append(card["card_id"])
        seen.add(card["card_id"])
    if duplicates:
        raise RuntimeError(f"duplicate card_id values: {duplicates[:5]}")
    return sorted(merged, key=lambda row: (row["source_id"], row["card_id"]))


def write_selection(sources: dict[str, dict[str, str]], selected_source_ids: set[str]) -> list[dict[str, Any]]:
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
    skipped: list[dict[str, Any]] = []
    with SELECTION_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for source_id in sorted(sources):
            source = sources[source_id]
            if source.get("duplicate_policy") == "secondary_to_pdf_duplicate":
                status = "skipped"
                group = "duplicate_secondary"
                reason = "duplicate_secondary"
                skipped.append(
                    {
                        "source_id": source_id,
                        "reason": "duplicate_secondary",
                        "extractable_unit_count": "",
                        "source_title": source["source_title"],
                    }
                )
            elif source_id in selected_source_ids:
                status = "selected"
                group = "csv_loader_addition" if source_id in CSV_SOURCE_IDS else "retained_all_extractable"
                reason = (
                    "selected after CSV row loader support"
                    if source_id in CSV_SOURCE_IDS
                    else "retained from previous all-extractable local expansion"
                )
            else:
                status = "not_selected"
                group = "not_in_merged_cards"
                reason = "not present in merged local cards"
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
    return skipped


def write_csv_report(summary: dict[str, Any], coverage: list[dict[str, Any]], selected_source_count: int) -> None:
    report = f"""---
title: "Consultant Role KB CSV Loader Support Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv"
  - "tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl"
scope: "CSV row typed-card support for SRC-CONSULT-030 and SRC-CONSULT-031"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local draft extraction only; no live KB ingestion"
---

# Consultant Role KB CSV Loader Support Report

## 0. Boundary

This report covers local CSV row extraction into typed cards. It does not call a
provider, ingest into a live KB, approve source licensing, or redistribute raw
CSV source files.

## 1. Outputs

| artifact | path |
|---|---|
| CSV cards | `tmp/consultant-role-kb-csv-supported-cards-20260619.jsonl` |
| merged all-extractable cards | `tmp/consultant-role-kb-all-extractable-cards-20260619.jsonl` |
| updated source selection | `drafts/analysis/consultant-role-kb-all-extractable-source-selection-20260619.csv` |
| updated gate eval | `tmp/consultant-role-kb-all-extractable-card-gate-eval-20260619.json` |

## 2. CSV Source Coverage

| source_id | source_title | csv_unit_count | selected_card_count | locator_type | first_locator |
|---|---|---:|---:|---|---|
"""
    for row in coverage:
        report += (
            f"| {row['source_id']} | {row['source_title']} | {row['csv_unit_count']} | "
            f"{row['selected_card_count']} | {row['locator_type']} | {row['first_locator']} |\n"
        )

    report += f"""
## 3. Updated All-Extractable Gate Metrics

| metric | value |
|---|---:|
| selected_source_count | {selected_source_count} |
| card_count | {summary['card_count']} |
| source_count | {summary['source_count']} |
| metadata_completeness | {summary['metadata_completeness']} |
| unit_locator_coverage | {summary['unit_locator_coverage']} |
| source_only_citation_violation_count | {summary['source_only_citation_violation_count']} |
| long_text_violation_count | {summary['long_text_violation_count']} |
| provider_call_count | {summary['provider_call_count']} |
| live_kb_write_count | {summary['live_kb_write_count']} |

## 4. Interpretation

Fact: `SRC-CONSULT-030` and `SRC-CONSULT-031` now produce `csv_row` locator
cards and are selected in the all-extractable local card set.

Fact: `SRC-CONSULT-016` remains skipped as a duplicate secondary EPUB.

Inference: the local typed-card extraction ceiling now covers all
non-duplicate registered sources under the current local parser stack.

Unknown: the durable vector store and retrieval API still need a later rebuild
if the project wants the new CSV cards indexed.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    base = load_module("consultant_csv_loader_base_expansion", BASE_SCRIPT)
    allx = load_module("consultant_csv_loader_allx_expansion", ALLX_SCRIPT)
    anchor_tools = base.load_anchor_module()
    sources = read_sources()

    existing_cards = read_jsonl(CARDS_OUT)
    csv_cards, coverage = generate_csv_cards(base, anchor_tools, sources)
    merged_cards = merge_cards(existing_cards, csv_cards)
    selected_source_ids = {card["source_id"] for card in merged_cards}
    skipped_sources = write_selection(sources, selected_source_ids)

    write_jsonl(CSV_CARDS_OUT, csv_cards)
    write_jsonl(CARDS_OUT, merged_cards)
    gate_eval = base.validate_cards(merged_cards)
    gate_eval["metadata"] = {
        "created_at": "2026-06-19",
        "scope": "all-extractable consultant-role card expansion with CSV row support",
        "provider_call_boundary": "no KB provider call",
        "production_impact": "production unchanged",
        "implementation_status": "local batch cards only; no live KB ingestion",
        "source_register": str(FULL_REGISTER_PATH.relative_to(ROOT)),
        "source_selection": str(SELECTION_OUT.relative_to(ROOT)),
        "cards": str(CARDS_OUT.relative_to(ROOT)),
        "csv_cards": str(CSV_CARDS_OUT.relative_to(ROOT)),
        "csv_source_ids": CSV_SOURCE_IDS,
        "skipped_sources": skipped_sources,
    }
    GATE_OUT.write_text(json.dumps(gate_eval, ensure_ascii=False, indent=2), encoding="utf-8")
    allx.write_report(gate_eval)
    write_csv_report(gate_eval["summary"], coverage, len(selected_source_ids))
    print(
        json.dumps(
            {
                "summary": gate_eval["summary"],
                "csv_coverage": coverage,
                "skipped_sources": skipped_sources,
                "outputs": [
                    str(CSV_CARDS_OUT),
                    str(CARDS_OUT),
                    str(SELECTION_OUT),
                    str(GATE_OUT),
                    str(REPORT_OUT),
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
