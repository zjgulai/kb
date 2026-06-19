#!/usr/bin/env python3
"""Validate consultant-role KB cards against register and parser manifests.

Boundary: local QA only. This script does not call a provider, write a live KB,
or approve source licensing.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CARDS = ROOT / "tmp/consultant-role-kb-expanded-cards-20260619.jsonl"
DEFAULT_REGISTER = ROOT / "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
DEFAULT_MANIFEST = ROOT / "tmp/consultant-role-kb-parser-unit-manifest-20260619.jsonl"
QA_OUT = ROOT / "tmp/consultant-role-kb-card-qa-validation-20260619.json"
QA_REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-card-qa-validation-report-20260619.md"

REQUIRED_FIELDS = {
    "card_id",
    "card_type",
    "workspace",
    "domain",
    "source_id",
    "source_type",
    "source_owner",
    "source_uri",
    "source_version",
    "evidence_grade",
    "license_status",
    "allowed_agents",
    "blocked_actions",
    "source_anchors",
}

ALLOWED_LOCATOR_TYPES = {"page", "slide", "sheet_row", "paragraph", "section", "csv_row"}
MUST_BLOCK = {"redistribute_source_text", "publish_client_deliverable", "expose_pii"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_register(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return {row["source_id"]: row for row in csv.DictReader(f)}


def read_manifest(path: Path) -> dict[str, set[str]]:
    manifest: dict[str, set[str]] = {}
    for row in read_jsonl(path):
        manifest[row["source_id"]] = {unit["locator"] for unit in row.get("units", [])}
    return manifest


def walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(walk_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(walk_strings(item))
        return strings
    return []


def as_set(value: Any) -> set[str]:
    if isinstance(value, list):
        return {str(item) for item in value if str(item).strip()}
    if isinstance(value, str):
        return {item.strip() for item in value.split(";") if item.strip()}
    return set()


def validate_card(
    card: dict[str, Any],
    register: dict[str, dict[str, str]],
    manifest: dict[str, set[str]],
) -> dict[str, Any]:
    source_id = card.get("source_id", "")
    source = register.get(source_id)
    anchors = card.get("source_anchors") or []
    primary_anchor = anchors[0] if anchors else {}
    locator = primary_anchor.get("locator", "")
    locator_type = primary_anchor.get("locator_type", "")
    blocked_actions = as_set(card.get("blocked_actions"))

    missing_fields = sorted(field for field in REQUIRED_FIELDS if not card.get(field))
    registered_source = source is not None
    locator_type_ok = locator_type in ALLOWED_LOCATOR_TYPES
    locator_present = bool(locator) and locator_type_ok
    locator_in_manifest = bool(source_id in manifest and locator in manifest[source_id])
    long_text_violation = any(len(text) > 1200 for text in walk_strings(card))
    source_only_citation_violation = not locator_present

    metadata_mismatches: list[str] = []
    if source:
        comparisons = {
            "workspace": source["workspace"],
            "domain": source["domain"],
            "source_type": source["source_type"],
            "source_owner": source["source_owner"],
            "source_uri": source["source_uri"],
            "evidence_grade": source["evidence_grade"],
            "license_status": source["license_status"],
        }
        for field, expected in comparisons.items():
            if str(card.get(field, "")) != str(expected):
                metadata_mismatches.append(field)

    high_risk_flags = set()
    if source:
        high_risk_flags = as_set(source.get("high_risk_flags"))
        high_risk_flags.discard("none")

    high_risk_review_routed = True
    if high_risk_flags:
        high_risk_review_routed = MUST_BLOCK.issubset(blocked_actions)
        if "transaction_or_investment_context" in high_risk_flags:
            high_risk_review_routed = high_risk_review_routed and "approve_transaction" in blocked_actions
        if "client_facing_context" in high_risk_flags:
            high_risk_review_routed = high_risk_review_routed and "send_client_email" in blocked_actions

    return {
        "card_id": card.get("card_id"),
        "source_id": source_id,
        "card_type": card.get("card_type"),
        "missing_required_fields": missing_fields,
        "metadata_complete": not missing_fields,
        "registered_source": registered_source,
        "metadata_mismatches": metadata_mismatches,
        "metadata_matches_register": registered_source and not metadata_mismatches,
        "locator_present": locator_present,
        "locator_in_manifest": locator_in_manifest,
        "source_only_citation_violation": source_only_citation_violation,
        "long_text_violation": long_text_violation,
        "blocked_actions_complete": MUST_BLOCK.issubset(blocked_actions),
        "high_risk_flags": sorted(high_risk_flags),
        "high_risk_review_routed": high_risk_review_routed,
    }


def rate(rows: list[dict[str, Any]], key: str) -> float | None:
    if not rows:
        return None
    return round(sum(bool(row[key]) for row in rows) / len(rows), 4)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_type = Counter(row["card_type"] for row in rows)
    by_source = Counter(row["source_id"] for row in rows)
    high_risk_rows = [row for row in rows if row["high_risk_flags"]]
    failures = [
        row
        for row in rows
        if not (
            row["metadata_complete"]
            and row["registered_source"]
            and row["metadata_matches_register"]
            and row["locator_present"]
            and row["locator_in_manifest"]
            and not row["source_only_citation_violation"]
            and not row["long_text_violation"]
            and row["blocked_actions_complete"]
            and row["high_risk_review_routed"]
        )
    ]
    return {
        "created_at": "2026-06-19",
        "scope": "consultant-role expanded card QA validation",
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "implementation_status": "local QA only; no live KB ingestion",
        "card_count": len(rows),
        "metadata_completeness": rate(rows, "metadata_complete"),
        "registered_source_coverage": rate(rows, "registered_source"),
        "metadata_match_rate": rate(rows, "metadata_matches_register"),
        "unit_locator_coverage": rate(rows, "locator_present"),
        "locator_manifest_coverage": rate(rows, "locator_in_manifest"),
        "source_only_citation_violation_count": sum(row["source_only_citation_violation"] for row in rows),
        "long_text_violation_count": sum(row["long_text_violation"] for row in rows),
        "blocked_actions_complete_rate": rate(rows, "blocked_actions_complete"),
        "high_risk_card_count": len(high_risk_rows),
        "high_risk_review_routed_rate": rate(high_risk_rows, "high_risk_review_routed"),
        "failure_count": len(failures),
        "by_card_type": dict(sorted(by_type.items())),
        "by_source": dict(sorted(by_source.items())),
    }


def write_report(summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    failures = [
        row
        for row in rows
        if row["missing_required_fields"]
        or not row["registered_source"]
        or not row["metadata_matches_register"]
        or not row["locator_in_manifest"]
        or row["source_only_citation_violation"]
        or row["long_text_violation"]
        or not row["blocked_actions_complete"]
        or not row["high_risk_review_routed"]
    ]
    report = f"""---
title: "Consultant Role KB Card QA Validation Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consultant-role-kb-expanded-cards-20260619.jsonl"
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "tmp/consultant-role-kb-parser-unit-manifest-20260619.jsonl"
scope: "card QA gate for consultant-agent extraction pipeline"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local QA only; no live KB ingestion"
---

# Consultant Role KB Card QA Validation Report

## 0. Boundary

This QA pass validates local draft cards. It does not approve source licensing,
write cards to a live KB, call a provider, or deploy production.

## 1. Outputs

| artifact | path |
|---|---|
| QA result JSON | `tmp/consultant-role-kb-card-qa-validation-20260619.json` |

## 2. Gate Metrics

| metric | value |
|---|---:|
| card_count | {summary['card_count']} |
| metadata_completeness | {summary['metadata_completeness']} |
| registered_source_coverage | {summary['registered_source_coverage']} |
| metadata_match_rate | {summary['metadata_match_rate']} |
| unit_locator_coverage | {summary['unit_locator_coverage']} |
| locator_manifest_coverage | {summary['locator_manifest_coverage']} |
| source_only_citation_violation_count | {summary['source_only_citation_violation_count']} |
| long_text_violation_count | {summary['long_text_violation_count']} |
| blocked_actions_complete_rate | {summary['blocked_actions_complete_rate']} |
| high_risk_card_count | {summary['high_risk_card_count']} |
| high_risk_review_routed_rate | {summary['high_risk_review_routed_rate']} |
| failure_count | {summary['failure_count']} |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 3. Cards By Type

| card_type | count |
|---|---:|
"""
    for card_type, count in summary["by_card_type"].items():
        report += f"| {card_type} | {count} |\n"

    report += """
## 4. Failures

"""
    if failures:
        for row in failures[:30]:
            report += (
                f"- `{row['card_id']}` source `{row['source_id']}` "
                f"missing={row['missing_required_fields']} "
                f"mismatch={row['metadata_mismatches']} "
                f"locator_in_manifest={row['locator_in_manifest']}.\n"
            )
    else:
        report += "- None.\n"

    report += """
## 5. Interpretation

Fact: this validator checks cards against the full source register and parser
unit manifest before any indexing or online agent use.

Inference: if this gate stays green during full extraction batches, the project
has a repeatable metadata/citation QA layer.

Unknown: this gate does not score semantic answer quality, human citation gold
labels, or legal clearance.
"""
    QA_REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards", default=str(DEFAULT_CARDS))
    parser.add_argument("--register", default=str(DEFAULT_REGISTER))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    args = parser.parse_args()

    cards = read_jsonl(Path(args.cards))
    register = read_register(Path(args.register))
    manifest = read_manifest(Path(args.manifest))
    results = [validate_card(card, register, manifest) for card in cards]
    summary = summarize(results)
    QA_OUT.write_text(
        json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_report(summary, results)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
