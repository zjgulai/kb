#!/usr/bin/env python3
"""Build the full consultant-role source register from the local source profile.

Boundary: local draft registration only. This script does not ingest into a
live KB, call a provider, redistribute raw source text, or change production.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "tmp/consult-role-kb-source-profile-20260619.json"
SEED_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
REGISTER_OUT = ROOT / "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
REGISTER_REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-full-source-register-report-20260619.md"

CREATED_AT = "2026-06-19"
OWNER = "李梁"
DOMAIN = "consulting-kb"
WORKSPACE = "consultant-p1"
ALLOWED_AGENTS = "consultant-agent"
DEFAULT_BLOCKED_ACTIONS = (
    "publish_client_deliverable;send_client_email;submit_rfp;commit_budget;"
    "approve_transaction;redistribute_source_text;expose_pii"
)

BASE_COLUMNS = [
    "source_id",
    "source_title",
    "domain",
    "layer",
    "source_type",
    "source_uri",
    "source_owner",
    "owner_review_status",
    "evidence_grade",
    "workspace",
    "version",
    "collected_at",
    "hash_sha256",
    "record_count",
    "pii_level",
    "license_status",
    "allowed_agents",
    "blocked_actions",
    "intake_status",
    "notes",
]

EXTRA_COLUMNS = [
    "parser_route",
    "source_suffix",
    "source_size_bytes",
    "candidate_categories",
    "extraction_batch",
    "high_risk_flags",
    "duplicate_group",
    "duplicate_policy",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_seed_register(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    by_hash: dict[str, dict[str, str]] = {}
    by_name: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("hash_sha256"):
                by_hash[row["hash_sha256"]] = row
            by_name[Path(row["source_uri"]).name] = row
    return by_hash, by_name


def clean_title(name: str) -> str:
    title = re.sub(r"\.[A-Za-z0-9]+$", "", name)
    title = title.replace("_", " ").replace("-", " ")
    title = re.sub(r"\s+", " ", title).strip()
    return title


def normalize_group_title(name: str) -> str:
    title = clean_title(name).lower()
    title = re.sub(r"\b(first|edition|v\d+|version|third|second)\b", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def primary_layer(record: dict[str, Any]) -> str:
    layers = record.get("candidate_layers") or []
    if "metrics-and-data" in layers:
        return "metrics-and-data"
    if "crosswalk" in layers:
        return "crosswalk"
    if "methodology" in layers:
        return "methodology"
    if "operations" in layers:
        return "operations"
    return layers[0] if layers else "methodology"


def extraction_batch(record: dict[str, Any]) -> str:
    categories = set(record.get("candidate_categories") or [])
    name = record.get("name", "").lower()
    if "diagnostic-guide" in categories:
        return "batch-02-diagnostics"
    if "transaction-advisory" in categories or any(
        marker in name for marker in ["due diligence", "merger", "private equity", "board"]
    ):
        return "batch-04-transaction-advisory"
    if "industry-analysis" in categories:
        return "batch-03-industry-analysis"
    if "reference-data" in categories:
        return "batch-05-reference-data"
    if "client-development" in categories:
        return "batch-06-client-development"
    if "consultant-delivery-craft" in categories:
        return "batch-01-delivery-craft"
    if "consulting-playbook" in categories or "strategy-management" in categories:
        return "batch-01-methodology-playbooks"
    return "batch-99-needs-human-triage"


def high_risk_flags(record: dict[str, Any]) -> str:
    flags: list[str] = []
    categories = set(record.get("candidate_categories") or [])
    name = record.get("name", "").lower()
    sample = str(record.get("text_sample") or "").lower()
    combined = f"{name} {sample}"
    if "transaction-advisory" in categories or any(
        marker in combined for marker in ["due diligence", "investment", "private equity", "transaction", "merger"]
    ):
        flags.append("transaction_or_investment_context")
    if any(marker in combined for marker in ["proposal", "rfp", "client", "email", "deliverable"]):
        flags.append("client_facing_context")
    if any(marker in combined for marker in ["all rights reserved", "may not be reproduced", "permission"]):
        flags.append("source_redistribution_restricted")
    if record.get("suffix") == ".csv":
        flags.append("tabular_data_review")
    if "unclassified" in categories:
        flags.append("classification_review")
    return ";".join(dict.fromkeys(flags)) or "none"


def unit_count(record: dict[str, Any]) -> str:
    for key in ("pages", "slide_count", "html_files", "row_count", "paragraph_count"):
        value = record.get(key)
        if value not in (None, ""):
            return str(value)
    return "unknown"


def duplicate_groups(records: list[dict[str, Any]]) -> dict[str, str]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[normalize_group_title(record["name"])].append(record)

    result: dict[str, str] = {}
    for idx, (group_title, group_records) in enumerate(sorted(grouped.items()), start=1):
        if len(group_records) <= 1:
            continue
        group_id = f"DUP-CONSULT-{idx:03d}"
        for record in group_records:
            result[record["sha256"]] = group_id
    return result


def duplicate_policy(record: dict[str, Any], group_id: str) -> str:
    if not group_id:
        return "not_duplicate"
    suffix = record.get("suffix")
    if suffix == ".pdf":
        return "prefer_pdf_for_page_anchors"
    if suffix == ".epub":
        return "secondary_to_pdf_duplicate"
    return "review_duplicate_group"


def build_rows(profile: dict[str, Any]) -> list[dict[str, str]]:
    seed_by_hash, seed_by_name = load_seed_register(SEED_REGISTER_PATH)
    records = profile["records"]
    dup_groups = duplicate_groups(records)
    next_id = 16
    rows: list[dict[str, str]] = []

    for record in records:
        seed = seed_by_hash.get(record["sha256"]) or seed_by_name.get(record["name"])
        if seed:
            row = dict(seed)
        else:
            row = {
                "source_id": f"SRC-CONSULT-{next_id:03d}",
                "source_title": clean_title(record["name"]),
                "domain": DOMAIN,
                "layer": primary_layer(record),
                "source_type": "external_reference",
                "source_uri": str((ROOT / record["path"]).resolve()),
                "source_owner": OWNER,
                "owner_review_status": "pending_review",
                "evidence_grade": "C",
                "workspace": WORKSPACE,
                "version": "profiled-20260619",
                "collected_at": CREATED_AT,
                "hash_sha256": record["sha256"],
                "record_count": unit_count(record),
                "pii_level": "unknown" if record.get("suffix") == ".csv" else "none",
                "license_status": "pending_legal_review",
                "allowed_agents": ALLOWED_AGENTS,
                "blocked_actions": DEFAULT_BLOCKED_ACTIONS,
                "intake_status": "registered",
                "notes": (
                    "Full-library draft registration only. Requires owner/legal review "
                    "before persistent KB storage or online use."
                ),
            }
            next_id += 1

        group_id = dup_groups.get(record["sha256"], "")
        row.update(
            {
                "parser_route": record.get("parser", "unknown"),
                "source_suffix": record.get("suffix", ""),
                "source_size_bytes": str(record.get("size_bytes", "")),
                "candidate_categories": ";".join(record.get("candidate_categories") or []),
                "extraction_batch": extraction_batch(record),
                "high_risk_flags": high_risk_flags(record),
                "duplicate_group": group_id,
                "duplicate_policy": duplicate_policy(record, group_id),
            }
        )
        rows.append({column: str(row.get(column, "")) for column in [*BASE_COLUMNS, *EXTRA_COLUMNS]})
    return rows


def write_register(rows: list[dict[str, str]]) -> None:
    with REGISTER_OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[*BASE_COLUMNS, *EXTRA_COLUMNS], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(profile: dict[str, Any], rows: list[dict[str, str]]) -> None:
    by_status = Counter(row["intake_status"] for row in rows)
    by_batch = Counter(row["extraction_batch"] for row in rows)
    by_suffix = Counter(row["source_suffix"] for row in rows)
    duplicate_groups_count = len({row["duplicate_group"] for row in rows if row["duplicate_group"]})
    high_risk = sum(1 for row in rows if row["high_risk_flags"] != "none")
    ready = sum(1 for row in rows if row["intake_status"] == "ready_for_poc")
    registered = sum(1 for row in rows if row["intake_status"] == "registered")

    report = f"""---
title: "Consultant Role KB Full Source Register Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "tmp/consult-role-kb-source-profile-20260619.json"
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
scope: "full 81-source draft registration for consultant-agent"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "draft source registration only; no live KB ingestion"
---

# Consultant Role KB Full Source Register Report

## 0. Boundary

This register is a draft planning artifact. It does not approve legal use,
persist derived cards into a live KB, call a provider, or redistribute raw
source material.

## 1. Outputs

| artifact | path |
|---|---|
| full source register | `drafts/analysis/consultant-role-kb-full-source-register-20260619.csv` |

## 2. Register Summary

| metric | value |
|---|---:|
| total_sources | {len(rows)} |
| profiled_sources | {profile['summary']['total_files_profiled']} |
| ready_for_poc_seed_sources | {ready} |
| registered_pending_review_sources | {registered} |
| duplicate_groups | {duplicate_groups_count} |
| sources_with_high_risk_flags | {high_risk} |
| provider_call_count | 0 |
| live_kb_write_count | 0 |

## 3. Sources By Suffix

| suffix | count |
|---|---:|
"""
    for suffix, count in sorted(by_suffix.items()):
        report += f"| {suffix or 'unknown'} | {count} |\n"

    report += """
## 4. Sources By Intake Status

| intake_status | count |
|---|---:|
"""
    for status, count in sorted(by_status.items()):
        report += f"| {status} | {count} |\n"

    report += """
## 5. Sources By Extraction Batch

| extraction_batch | count |
|---|---:|
"""
    for batch, count in sorted(by_batch.items()):
        report += f"| {batch} | {count} |\n"

    report += """
## 6. Interpretation

Fact: all profiled `consult/` files now have draft source-register rows,
including stable source IDs, hash, parser route, license status, allowed agent,
blocked actions, extraction batch, high-risk flags, and duplicate policy.

Inference: the project can now run parser manifest generation across the full
library without starting from unregistered files.

Unknown: legal/license clearance and persistent derived-card storage remain
pending human review.
"""
    REGISTER_REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    profile = load_json(PROFILE_PATH)
    rows = build_rows(profile)
    ids = [row["source_id"] for row in rows]
    if len(ids) != len(set(ids)):
        duplicates = [source_id for source_id, count in Counter(ids).items() if count > 1]
        raise SystemExit(f"Duplicate source IDs: {duplicates}")
    if len(rows) != profile["summary"]["total_files_profiled"]:
        raise SystemExit("Register row count does not match source profile count")
    write_register(rows)
    write_report(profile, rows)
    print(
        json.dumps(
            {
                "source_count": len(rows),
                "register": str(REGISTER_OUT),
                "report": str(REGISTER_REPORT_OUT),
                "provider_call_count": 0,
                "live_kb_write_count": 0,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
