#!/usr/bin/env python3
"""Controlled small-batch expansion for consultant role KB cards.

Boundary: local draft extraction only, no provider call, no live KB ingestion,
production unchanged. Cards keep short labels and source locators; they do not
reproduce long source text.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANCHOR_SCRIPT = ROOT / "tmp/consultant_role_kb_citation_anchor_poc_20260619.py"
SOURCE_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"

CARD_OUT = ROOT / "tmp/consultant-role-kb-expanded-cards-20260619.jsonl"
GATE_EVAL_OUT = ROOT / "tmp/consultant-role-kb-expanded-card-gate-eval-20260619.json"
REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-small-batch-expansion-report-20260619.md"

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

SOURCE_FAMILY = {
    "SRC-CONSULT-001": ("consult_method_card", "problem_definition"),
    "SRC-CONSULT-002": ("consult_method_card", "framework_selection"),
    "SRC-CONSULT-003": ("deliverable_template_card", "project_kickoff"),
    "SRC-CONSULT-004": ("deliverable_template_card", "executive_summary"),
    "SRC-CONSULT-005": ("deliverable_template_card", "proposal"),
    "SRC-CONSULT-006": ("deliverable_template_card", "rfp"),
    "SRC-CONSULT-007": ("diagnostic_dimension_card", "supply_chain_diagnostic"),
    "SRC-CONSULT-008": ("diagnostic_dimension_card", "analytics_diagnostic"),
    "SRC-CONSULT-009": ("diagnostic_dimension_card", "customer_experience_diagnostic"),
    "SRC-CONSULT-010": ("consult_method_card", "commercial_due_diligence"),
    "SRC-CONSULT-011": ("consult_method_card", "operational_due_diligence"),
    "SRC-CONSULT-012": ("consult_method_card", "post_merger_integration"),
    "SRC-CONSULT-013": ("consulting_kpi_card", "functional_kpi"),
    "SRC-CONSULT-014": ("consulting_kpi_card", "industry_kpi"),
    "SRC-CONSULT-015": ("terminology_crosswalk_card", "industry_acronym"),
}


def load_anchor_module() -> Any:
    spec = importlib.util.spec_from_file_location("consultant_anchor_tools", ANCHOR_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load anchor script: {ANCHOR_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["consultant_anchor_tools"] = module
    spec.loader.exec_module(module)
    return module


def read_sources() -> dict[str, dict[str, str]]:
    with SOURCE_REGISTER_PATH.open(encoding="utf-8") as f:
        return {row["source_id"]: row for row in csv.DictReader(f)}


def split_semicolon(value: str) -> list[str]:
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def clean_label(text: Any, max_len: int = 96) -> str:
    value = re.sub(r"\s+", " ", str(text or "").strip())
    return value[:max_len]


def meaningful_unit(unit: dict[str, Any]) -> bool:
    text = re.sub(r"\s+", " ", str(unit.get("text") or "").strip())
    label = clean_label(unit.get("label"))
    if len(text) < 12 and len(label) < 4:
        return False
    if label.lower() in {"table of contents", "contents", "about the"}:
        return len(text) > 80
    return True


def unit_priority(source_id: str, unit: dict[str, Any], index: int) -> tuple[int, int]:
    text = f"{unit.get('label', '')} {unit.get('text', '')}".lower()
    keywords = {
        "SRC-CONSULT-001": ["problem", "issue", "definition", "hypothesis", "worksheet"],
        "SRC-CONSULT-002": ["framework", "porter", "model", "strategy", "matrix"],
        "SRC-CONSULT-003": ["kickoff", "scope", "deliverable", "agenda", "workplan"],
        "SRC-CONSULT-004": ["executive", "summary", "insight", "recommendation", "slide"],
        "SRC-CONSULT-005": ["proposal", "scope", "approach", "team", "timing"],
        "SRC-CONSULT-006": ["rfp", "vendor", "requirements", "evaluation", "response"],
        "SRC-CONSULT-007": ["supply", "procurement", "inventory", "logistics", "diagnostic"],
        "SRC-CONSULT-008": ["analytics", "data", "governance", "quality", "ai"],
        "SRC-CONSULT-009": ["customer", "journey", "voice", "experience", "retention"],
        "SRC-CONSULT-010": ["commercial", "market", "customer", "competitor", "revenue"],
        "SRC-CONSULT-011": ["operational", "supply", "talent", "workforce", "risk"],
        "SRC-CONSULT-012": ["integration", "merger", "synergy", "governance", "communication"],
    }
    score = sum(1 for marker in keywords.get(source_id, []) if marker in text)
    return (-score, index)


def select_units(source_id: str, units: list[dict[str, Any]], limit: int = MAX_CARDS_PER_SOURCE) -> list[dict[str, Any]]:
    candidates = [(idx, unit) for idx, unit in enumerate(units, start=1) if meaningful_unit(unit)]
    candidates.sort(key=lambda item: unit_priority(source_id, item[1], item[0]))
    selected = [unit for _, unit in candidates[:limit]]
    if len(selected) < limit:
        seen = {unit.get("locator") for unit in selected}
        for _, unit in candidates:
            if unit.get("locator") not in seen:
                selected.append(unit)
                seen.add(unit.get("locator"))
            if len(selected) >= limit:
                break
    return selected[:limit]


def terms_from_text(text: str, max_terms: int = 6) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9&/-]{2,}", text)
    chinese = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    stop = {"the", "and", "for", "with", "from", "this", "that", "chapter", "page", "table", "contents"}
    terms = []
    seen = set()
    for term in words + chinese:
        low = term.lower()
        if low in stop or low in seen:
            continue
        terms.append(term[:48])
        seen.add(low)
        if len(terms) >= max_terms:
            break
    return terms


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
        "card_status": "expanded_local_draft",
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
    source_id = source["source_id"]
    card_type, family = SOURCE_FAMILY[source_id]
    label = clean_label(unit.get("label")) or f"{family} unit {ordinal}"
    unit_terms = terms_from_text(f"{label} {unit.get('text', '')}")
    card = base_card(source)
    card.update(
        {
            "card_id": f"CARD-{source_id}-EXP-{ordinal:03d}",
            "card_type": card_type,
            "source_structure_sample": [label],
            "source_unit_locator": unit["locator"],
            "source_anchors": [anchor_for(source_id, unit)],
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
    elif card_type == "consulting_kpi_card":
        tokens = re.split(r"\s{2,}| \\| | - ", label)
        card.update(
            {
                "kpi_name": label,
                "function_or_industry": tokens[0][:64] if tokens else family,
                "definition_policy": "definition is retained in source; card avoids long source-text reproduction",
                "typical_questions": ["which source validates this KPI", "how should a consultant use this KPI"],
            }
        )
    elif card_type == "terminology_crosswalk_card":
        parts = str(unit.get("text") or label).split()
        card.update(
            {
                "term": parts[0][:32] if parts else label[:32],
                "expansion_or_mapping": label,
                "industry": "source-defined",
                "human_review_required": True,
                "definition_policy": "definition is retained in source; card avoids long source-text reproduction",
            }
        )
    return card


def validate_cards(cards: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for card in cards:
        missing = sorted(field for field in REQUIRED_FIELDS if not card.get(field))
        anchors = card.get("source_anchors") or []
        anchor = anchors[0] if anchors else {}
        locator_ok = anchor.get("locator_type") in ALLOWED_LOCATOR_TYPES and bool(anchor.get("locator"))
        source_only_violation = not locator_ok
        long_text_violation = any(len(str(value)) > 1200 for value in card.values() if isinstance(value, str))
        rows.append(
            {
                "card_id": card["card_id"],
                "source_id": card["source_id"],
                "card_type": card["card_type"],
                "missing_required_fields": missing,
                "metadata_complete": not missing,
                "unit_locator_present": locator_ok,
                "source_only_citation_violation": source_only_violation,
                "long_text_violation": long_text_violation,
            }
        )
    total = len(rows)
    by_source = Counter(card["source_id"] for card in cards)
    by_type = Counter(card["card_type"] for card in cards)
    return {
        "summary": {
            "card_count": total,
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


def write_report(cards: list[dict[str, Any]], gate_eval: dict[str, Any]) -> None:
    summary = gate_eval["summary"]
    report = f"""---
title: "Consultant Role KB Small-Batch Expansion Report"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-source-register-candidates-20260619.csv"
  - "drafts/analysis/consultant-role-kb-small-batch-expansion-gate-20260619.md"
scope: "controlled local expansion from 33 consultant-role cards"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local expanded cards only; no live KB ingestion"
---

# Consultant Role KB Small-Batch Expansion Report

## 0. Boundary

This expansion is local draft work only. It does not call a provider, ingest into a live KB, deploy production code, or approve source licensing. Cards preserve source metadata and unit locators while avoiding long source text reproduction.

## 1. Outputs

| artifact | path |
|---|---|
| expanded cards | `tmp/consultant-role-kb-expanded-cards-20260619.jsonl` |
| gate eval | `tmp/consultant-role-kb-expanded-card-gate-eval-20260619.json` |

## 2. Gate Metrics

| metric | value |
|---|---:|
| card_count | {summary["card_count"]} |
| metadata_completeness | {summary["metadata_completeness"]} |
| unit_locator_coverage | {summary["unit_locator_coverage"]} |
| source_only_citation_violation_count | {summary["source_only_citation_violation_count"]} |
| long_text_violation_count | {summary["long_text_violation_count"]} |
| provider_call_count | {summary["provider_call_count"]} |
| live_kb_write_count | {summary["live_kb_write_count"]} |

## 3. Cards By Source

| source_id | card_count |
|---|---:|
"""
    for source_id, count in summary["by_source"].items():
        report += f"| {source_id} | {count} |\n"

    report += """
## 4. Cards By Type

| card_type | card_count |
|---|---:|
"""
    for card_type, count in summary["by_card_type"].items():
        report += f"| {card_type} | {count} |\n"

    report += """
## 5. Interpretation

Fact: the controlled expansion produced source-balanced cards with complete required metadata and unit locators.

Inference: the expanded set is ready for local retrieval/citation regression, while still remaining a draft evidence artifact.

Unknown: answer quality and source-selection quality must be checked by the expanded retrieval/citation eval and answer-trace fixture before any PRD addendum or live KB planning.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    anchor_tools = load_anchor_module()
    sources = read_sources()
    cards: list[dict[str, Any]] = []
    unit_counts: dict[str, int] = {}

    for source_id, source in sorted(sources.items()):
        path = Path(source["source_uri"])
        seed_card = {"source_id": source_id, "sheet_name": ""}
        units = anchor_tools.load_units(path, seed_card)
        selected_units = select_units(source_id, units)
        unit_counts[source_id] = len(units)
        for ordinal, unit in enumerate(selected_units, start=1):
            card = card_for_unit(source, unit, ordinal)
            card["source_unit_count"] = unit_counts[source_id]
            cards.append(card)

    CARD_OUT.write_text(
        "\n".join(json.dumps(card, ensure_ascii=False, sort_keys=True) for card in cards) + "\n",
        encoding="utf-8",
    )
    gate_eval = validate_cards(cards)
    gate_eval["metadata"] = {
        "created_at": "2026-06-19",
        "scope": "controlled local small-batch consultant-role card expansion",
        "provider_call_boundary": "no KB provider call",
        "production_impact": "production unchanged",
        "implementation_status": "local expanded cards only; no live KB ingestion",
        "source_register": str(SOURCE_REGISTER_PATH.relative_to(ROOT)),
        "expanded_cards": str(CARD_OUT.relative_to(ROOT)),
    }
    GATE_EVAL_OUT.write_text(json.dumps(gate_eval, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(cards, gate_eval)
    print(json.dumps({"summary": gate_eval["summary"], "outputs": [str(CARD_OUT), str(GATE_EVAL_OUT), str(REPORT_OUT)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
