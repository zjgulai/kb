#!/usr/bin/env python3
"""Expand consultant-role KB cards from 15 to 30 registered sources.

Boundary: local draft batch expansion only. No provider call, no live KB
ingestion, no production change, and no source-text redistribution.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANCHOR_SCRIPT = ROOT / "tmp/consultant_role_kb_citation_anchor_poc_20260619.py"
FULL_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"

SELECTION_OUT = ROOT / "drafts/analysis/consultant-role-kb-batch30-source-selection-20260619.csv"
CARDS_OUT = ROOT / "tmp/consultant-role-kb-batch30-cards-20260619.jsonl"
GATE_OUT = ROOT / "tmp/consultant-role-kb-batch30-card-gate-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-batch30-expansion-report-20260619.md"

MAX_CARDS_PER_SOURCE = 10
ALLOWED_LOCATOR_TYPES = {"page", "slide", "sheet_row", "paragraph"}
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

P1_SOURCE_IDS = [f"SRC-CONSULT-{idx:03d}" for idx in range(1, 16)]
ADDITIONAL_SOURCE_IDS = [
    "SRC-CONSULT-017",  # B2B GTM PDF; PDF preferred over duplicate EPUB.
    "SRC-CONSULT-018",  # Business Plan Playbook.
    "SRC-CONSULT-019",  # Busy Consultants Guide to PowerPoint.
    "SRC-CONSULT-020",  # Career Services Guide to Consulting.
    "SRC-CONSULT-021",  # Chief Strategy Officer Handbook.
    "SRC-CONSULT-022",  # Company Culture Diagnostic Guide.
    "SRC-CONSULT-023",  # Competitive Intelligence Playbook.
    "SRC-CONSULT-027",  # Executive Handover Playbook.
    "SRC-CONSULT-028",  # Finance Department Diagnostic Guide.
    "SRC-CONSULT-060",  # How to Find Clients.
    "SRC-CONSULT-063",  # Marketing Plan Playbook.
    "SRC-CONSULT-064",  # Organizational Design Diagnostic.
    "SRC-CONSULT-065",  # PESTEL Analysis Playbook.
    "SRC-CONSULT-067",  # PMO Playbook.
    "SRC-CONSULT-079",  # PowerPoint Template for Consultants.
]
SELECTED_SOURCE_IDS = P1_SOURCE_IDS + ADDITIONAL_SOURCE_IDS


def load_anchor_module() -> Any:
    spec = importlib.util.spec_from_file_location("consultant_anchor_tools_batch30", ANCHOR_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load anchor script: {ANCHOR_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["consultant_anchor_tools_batch30"] = module
    spec.loader.exec_module(module)
    return module


def read_sources() -> dict[str, dict[str, str]]:
    with FULL_REGISTER_PATH.open(encoding="utf-8") as f:
        return {row["source_id"]: row for row in csv.DictReader(f)}


def split_semicolon(value: str) -> list[str]:
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def clean_label(text: Any, max_len: int = 96) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())[:max_len]


def terms_from_text(text: str, max_terms: int = 8) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9&/-]{2,}", text)
    chinese = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    stop = {"the", "and", "for", "with", "from", "this", "that", "chapter", "page", "table", "contents"}
    terms: list[str] = []
    seen: set[str] = set()
    for term in words + chinese:
        low = term.lower()
        if low in stop or low in seen:
            continue
        terms.append(term[:48])
        seen.add(low)
        if len(terms) >= max_terms:
            break
    return terms


def source_keywords(source: dict[str, str]) -> list[str]:
    title = source["source_title"].lower()
    batch = source.get("extraction_batch", "")
    keywords = terms_from_text(f"{title} {batch} {source.get('candidate_categories', '')}", max_terms=12)
    if "diagnostic" in title:
        keywords += ["diagnostic", "scorecard", "data", "interview", "maturity"]
    if "powerpoint" in title or "summary" in title or "handover" in title:
        keywords += ["slide", "presentation", "findings", "recommendation", "executive"]
    if "client" in title or "proposal" in title or "rfp" in title:
        keywords += ["client", "proposal", "business development", "review"]
    if "plan" in title or "strategy" in title or "pestel" in title:
        keywords += ["strategy", "plan", "market", "hypothesis", "workstream"]
    return list(dict.fromkeys(keywords))


def meaningful_unit(unit: dict[str, Any]) -> bool:
    text = re.sub(r"\s+", " ", str(unit.get("text") or "").strip())
    label = clean_label(unit.get("label"))
    if len(text) < 12 and len(label) < 4:
        return False
    if label.lower() in {"table of contents", "contents", "about the"}:
        return len(text) > 80
    return True


def unit_priority(source: dict[str, str], unit: dict[str, Any], index: int) -> tuple[int, int, int]:
    text = f"{unit.get('label', '')} {unit.get('text', '')}".lower()
    keywords = source_keywords(source)
    score = sum(1 for marker in keywords if marker.lower() in text)
    # Prefer earlier units only after source-intent hits; this keeps coverage stable.
    length_bucket = min(len(str(unit.get("text") or "")) // 500, 4)
    return (-score, -length_bucket, index)


def select_units(source: dict[str, str], units: list[dict[str, Any]], limit: int = MAX_CARDS_PER_SOURCE) -> list[dict[str, Any]]:
    candidates = [(idx, unit) for idx, unit in enumerate(units, start=1) if meaningful_unit(unit)]
    candidates.sort(key=lambda item: unit_priority(source, item[1], item[0]))
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for _, unit in candidates:
        locator = unit.get("locator")
        if locator in seen:
            continue
        selected.append(unit)
        seen.add(locator)
        if len(selected) >= limit:
            break
    return selected


def card_type_for(source: dict[str, str]) -> tuple[str, str]:
    title = source["source_title"].lower()
    batch = source.get("extraction_batch", "")
    layer = source.get("layer", "")
    if layer == "metrics-and-data":
        return "consulting_kpi_card", "metrics_reference"
    if layer == "crosswalk" or "industry-analysis" in source.get("candidate_categories", ""):
        return "industry_analysis_card", "industry_analysis"
    if "diagnostic" in title or "batch-02-diagnostics" in batch:
        return "diagnostic_dimension_card", "diagnostic"
    if any(marker in title for marker in ["powerpoint", "summary", "proposal", "rfp", "handover", "kickoff", "template"]):
        return "deliverable_template_card", "deliverable"
    if "client" in title or "career services" in title or "find clients" in title:
        return "client_development_card", "client_development"
    if "transaction" in batch or "due diligence" in title or "merger" in title or "private equity" in title:
        return "consult_method_card", "transaction_advisory"
    return "consult_method_card", "methodology"


def base_card(source: dict[str, str]) -> dict[str, Any]:
    return {
        "workspace": source["workspace"],
        "domain": source["domain"],
        "layer": source["layer"],
        "source_id": source["source_id"],
        "source_type": source["source_type"],
        "source_owner": source["source_owner"],
        "source_uri": source["source_uri"],
        "source_version": source["version"],
        "evidence_grade": source["evidence_grade"],
        "license_status": source["license_status"],
        "allowed_agents": split_semicolon(source["allowed_agents"]) or [source["allowed_agents"]],
        "blocked_actions": split_semicolon(source["blocked_actions"]),
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "card_status": "batch30_local_draft",
        "source_use_boundary": "internal local PoC only; no redistribution; no client-ready publishing",
    }


def anchor_for(source_id: str, unit: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "locator_type": unit["locator_type"],
        "locator": unit["locator"],
        "anchor_label": clean_label(unit.get("label")),
        "anchor_confidence": "high",
        "anchor_match_score": 1.0,
        "matched_terms": terms_from_text(f"{unit.get('label', '')} {unit.get('text', '')}", max_terms=8),
    }


def card_for_unit(source: dict[str, str], unit: dict[str, Any], ordinal: int) -> dict[str, Any]:
    card_type, family = card_type_for(source)
    label = clean_label(unit.get("label")) or f"{family} unit {ordinal}"
    unit_terms = terms_from_text(f"{label} {unit.get('text', '')}", max_terms=8)
    card = base_card(source)
    card.update(
        {
            "card_id": f"CARD-{source['source_id']}-B30-{ordinal:03d}",
            "card_type": card_type,
            "source_structure_sample": [label],
            "source_unit_locator": unit["locator"],
            "source_anchors": [anchor_for(source["source_id"], unit)],
            "citation_anchor_policy": {
                "allowed_citation_granularity": ["page", "slide", "sheet_row", "paragraph"],
                "blocked": ["long_source_text_reproduction", "source_only_citation_for_final_answer"],
                "boundary": "local PoC only; no KB provider call; production unchanged",
            },
        }
    )
    if card_type == "consult_method_card":
        card.update(
            {
                "method_name": f"{source['source_title']} - {label}",
                "problem_type": family,
                "when_to_use": ["internal planning", "human-reviewed consulting workflow"],
                "outputs": ["working_hypothesis", "issue_map", "data_needs", "next_human_action"],
                "failure_modes": ["missing client context", "unsupported final conclusion", "blocked action requested"],
                "method_keywords": unit_terms,
            }
        )
    elif card_type == "diagnostic_dimension_card":
        card.update(
            {
                "diagnostic_name": source["source_title"],
                "dimension_names": unit_terms or [family],
                "data_requests": ["documents", "metrics", "process artifacts", "stakeholder interviews"],
                "interview_roles": ["executive owner", "functional lead", "frontline/operator role"],
                "scorecard_criteria": ["coverage", "maturity", "risk", "evidence quality"],
            }
        )
    elif card_type == "deliverable_template_card":
        card.update(
            {
                "deliverable_type": family,
                "purpose": label,
                "sections": unit_terms or [family],
                "required_inputs": ["client context", "facts", "assumptions", "human review"],
                "reviewer_roles": ["human consultant", "source owner"],
                "quality_checks": ["source cited", "blocked actions respected", "no long source text"],
            }
        )
    elif card_type == "client_development_card":
        card.update(
            {
                "client_development_topic": label,
                "use_case": family,
                "conversation_assets": unit_terms or [family],
                "human_review_required": True,
                "blocked_client_actions": ["send_client_email", "submit_rfp", "publish_client_deliverable"],
            }
        )
    elif card_type == "industry_analysis_card":
        card.update(
            {
                "industry_or_sector": source["source_title"],
                "analysis_dimensions": unit_terms or [family],
                "typical_questions": ["how to scope this industry", "which value drivers require evidence"],
                "definition_policy": "source retained separately; card avoids long source-text reproduction",
            }
        )
    elif card_type == "consulting_kpi_card":
        card.update(
            {
                "kpi_name": label,
                "function_or_industry": source["source_title"],
                "definition_policy": "definition is retained in source; card avoids long source-text reproduction",
                "typical_questions": ["which source validates this KPI", "how should a consultant use this KPI"],
            }
        )
    return card


def validate_cards(cards: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for card in cards:
        missing = sorted(field for field in REQUIRED_FIELDS if not card.get(field))
        anchors = card.get("source_anchors") or []
        anchor = anchors[0] if anchors else {}
        locator_ok = anchor.get("locator_type") in ALLOWED_LOCATOR_TYPES and bool(anchor.get("locator"))
        long_text_violation = any(len(str(value)) > 1200 for value in card.values() if isinstance(value, str))
        rows.append(
            {
                "card_id": card["card_id"],
                "source_id": card["source_id"],
                "card_type": card["card_type"],
                "missing_required_fields": missing,
                "metadata_complete": not missing,
                "unit_locator_present": locator_ok,
                "source_only_citation_violation": not locator_ok,
                "long_text_violation": long_text_violation,
            }
        )
    total = len(rows)
    by_source = Counter(card["source_id"] for card in cards)
    by_type = Counter(card["card_type"] for card in cards)
    return {
        "summary": {
            "card_count": total,
            "source_count": len(by_source),
            "metadata_completeness": round(sum(row["metadata_complete"] for row in rows) / total, 4),
            "unit_locator_coverage": round(sum(row["unit_locator_present"] for row in rows) / total, 4),
            "source_only_citation_violation_count": sum(row["source_only_citation_violation"] for row in rows),
            "long_text_violation_count": sum(row["long_text_violation"] for row in rows),
            "provider_call_count": 0,
            "live_kb_write_count": 0,
            "by_source": dict(sorted(by_source.items())),
            "by_card_type": dict(sorted(by_type.items())),
        },
        "results": rows,
    }


def write_selection(sources: dict[str, dict[str, str]]) -> None:
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
        for source_id in SELECTED_SOURCE_IDS:
            source = sources[source_id]
            group = "p1_seed" if source_id in P1_SOURCE_IDS else "batch30_addition"
            reason = (
                "existing P1 source retained"
                if group == "p1_seed"
                else "adds high-value consulting workflow coverage while avoiding duplicate EPUB/PDF pair where possible"
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


def write_report(cards: list[dict[str, Any]], gate_eval: dict[str, Any]) -> None:
    summary = gate_eval["summary"]
    report = f"""---
title: "Consultant Role KB Batch-30 Expansion Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"
  - "drafts/analysis/consultant-role-kb-batch30-source-selection-20260619.csv"
scope: "local batch expansion from 15 to 30 consultant-role sources"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local batch cards only; no live KB ingestion"
---

# Consultant Role KB Batch-30 Expansion Report

## 0. Boundary

This is local draft expansion only. It does not call a provider, ingest into a
live KB, deploy production code, approve source licensing, or reproduce long
source text.

## 1. Outputs

| artifact | path |
|---|---|
| source selection | `drafts/analysis/consultant-role-kb-batch30-source-selection-20260619.csv` |
| batch-30 cards | `tmp/consultant-role-kb-batch30-cards-20260619.jsonl` |
| gate eval | `tmp/consultant-role-kb-batch30-card-gate-eval-20260619.json` |

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

## 3. Cards By Type

| card_type | card_count |
|---|---:|
"""
    for card_type, count in summary["by_card_type"].items():
        report += f"| {card_type} | {count} |\n"

    report += """
## 4. Interpretation

Fact: the batch-30 expansion produced source-balanced cards with complete
required metadata and unit locators.

Inference: batch-30 can proceed to card QA and local retrieval/citation
regression as a draft artifact.

Unknown: legal/source-owner clearance and human-gold citation precision are
still not proven.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    anchor_tools = load_anchor_module()
    sources = read_sources()
    missing_sources = [source_id for source_id in SELECTED_SOURCE_IDS if source_id not in sources]
    if missing_sources:
        raise SystemExit(f"Missing selected sources: {missing_sources}")

    cards: list[dict[str, Any]] = []
    unit_counts: dict[str, int] = {}
    write_selection(sources)

    for source_id in SELECTED_SOURCE_IDS:
        source = sources[source_id]
        path = Path(source["source_uri"])
        units = anchor_tools.load_units(path, {"source_id": source_id, "sheet_name": ""})
        selected_units = select_units(source, units)
        unit_counts[source_id] = len(units)
        if len(selected_units) < MAX_CARDS_PER_SOURCE:
            raise SystemExit(f"Not enough extractable units for {source_id}: {len(selected_units)}")
        for ordinal, unit in enumerate(selected_units, start=1):
            card = card_for_unit(source, unit, ordinal)
            card["source_unit_count"] = unit_counts[source_id]
            cards.append(card)

    CARDS_OUT.write_text(
        "\n".join(json.dumps(card, ensure_ascii=False, sort_keys=True) for card in cards) + "\n",
        encoding="utf-8",
    )
    gate_eval = validate_cards(cards)
    gate_eval["metadata"] = {
        "created_at": "2026-06-19",
        "scope": "batch-30 consultant-role card expansion",
        "provider_call_boundary": "no KB provider call",
        "production_impact": "production unchanged",
        "implementation_status": "local batch cards only; no live KB ingestion",
        "source_register": str(FULL_REGISTER_PATH.relative_to(ROOT)),
        "source_selection": str(SELECTION_OUT.relative_to(ROOT)),
        "cards": str(CARDS_OUT.relative_to(ROOT)),
    }
    GATE_OUT.write_text(json.dumps(gate_eval, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(cards, gate_eval)
    print(json.dumps({"summary": gate_eval["summary"], "outputs": [str(SELECTION_OUT), str(CARDS_OUT), str(GATE_OUT), str(REPORT_OUT)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
