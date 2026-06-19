#!/usr/bin/env python3
"""Record product-owner staging decisions from the Q1-Q7 intake.

Boundary: local governance record only. This does not approve source licensing,
approve security controls, configure secrets, deploy staging, call a provider,
or ingest into a live KB.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "shared/governance/consultant-agent/product-owner-decision.schema-20260619.json"
DECISIONS = ROOT / "shared/governance/consultant-agent/product-owner-decisions.answered-20260619.jsonl"
OUT_JSON = ROOT / "tmp/consultant-role-kb-product-owner-decision-validation-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-product-owner-decision-record-20260619.md"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0


def now_z() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def decision_rows() -> list[dict[str, Any]]:
    recorded_at = now_z()
    common = {
        "recorded_at": recorded_at,
        "recorded_from": "chat_q1_q7_intake_20260619",
        "decision_role": "project_owner_product_owner",
        "decision_scope": "product_staging_strategy",
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
    }
    return [
        {
            **common,
            "decision_id": "PO-20260619-Q1-A",
            "question_id": "Q1",
            "answer": "A",
            "decision_type": "decision_actor_scope",
            "decision_value": "project_owner_product_owner",
            "effective_policy": {
                "can_record_product_intent": True,
                "can_record_legal_source_owner_clearance": False,
                "can_record_security_approval": False,
            },
            "decision_effect": "product intent only; legal/source-owner and security gates remain separate",
        },
        {
            **common,
            "decision_id": "PO-20260619-Q2-A",
            "question_id": "Q2",
            "answer": "A",
            "decision_type": "selected_source_staging_intent",
            "decision_value": "allow_all_80_selected_sources_for_internal_no_provider_staging_intent",
            "effective_policy": {
                "selected_source_count": 80,
                "internal_no_provider_staging_product_intent": True,
                "legal_source_owner_clearance_effect": False,
            },
            "decision_effect": "records product intent; selected source legal/source-owner clearance remains pending",
        },
        {
            **common,
            "decision_id": "PO-20260619-Q3-A",
            "question_id": "Q3",
            "answer": "A",
            "decision_type": "raw_source_distribution_policy",
            "decision_value": "do_not_commit_raw_consult_sources",
            "effective_policy": {
                "raw_consult_git_commit_allowed": False,
                "future_tencent_cloud_lighthouse_runtime_upload_candidate": True,
                "future_upload_requires_legal_security_deploy_gates": True,
            },
            "decision_effect": "raw consult source files stay out of GitHub; later server upload is a separate deployment gate",
        },
        {
            **common,
            "decision_id": "PO-20260619-Q4-D",
            "question_id": "Q4",
            "answer": "D",
            "decision_type": "human_gold_label_gate_policy",
            "decision_value": "defer_human_gold_labels_continue_machine_seeded_eval",
            "effective_policy": {
                "human_gold_labeling_enabled": False,
                "human_gold_label_gate_mode": "waive_for_staging_do_not_claim_human_gold",
                "human_label_approval_effect_count": 0,
                "machine_seeded_eval_continues": True,
                "human_gold_metrics_claimed": False,
            },
            "decision_effect": "human-gold labels remain unapproved; staging evidence may continue with machine-seeded eval only",
        },
        {
            **common,
            "decision_id": "PO-20260619-Q5-A",
            "question_id": "Q5",
            "answer": "A",
            "decision_type": "security_control_process_intent",
            "decision_value": "start_pending_to_approval_workflow",
            "effective_policy": {
                "security_approval_effect_count": 0,
                "security_controls_pending_to_approval_lane": True,
            },
            "decision_effect": "records approval-process intent; no security/operations control is approved",
        },
        {
            **common,
            "decision_id": "PO-20260619-Q6-C",
            "question_id": "Q6",
            "answer": "C",
            "decision_type": "provider_staging_policy",
            "decision_value": "provider_model_allowed_for_staging_design_not_called",
            "effective_policy": {
                "provider_model_allowed_in_staging_strategy": True,
                "provider_call_enabled": False,
                "provider_call_requires_runtime_policy_and_security_gate": True,
            },
            "decision_effect": "records future staging preference; current run remains no-provider",
        },
        {
            **common,
            "decision_id": "PO-20260619-Q7-A",
            "question_id": "Q7",
            "answer": "A",
            "decision_type": "next_decision_priority",
            "decision_value": "human_label_decisions",
            "effective_policy": {
                "priority_next_decision_file": "human_label_decisions",
                "human_label_decision_action": "record_defer_policy_not_label_approvals",
            },
            "decision_effect": "prioritizes human label decision handling while preserving Q4 defer policy",
        },
    ]


def write_schema() -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Consultant Role KB Product Owner Decision",
        "type": "object",
        "required": [
            "decision_id",
            "recorded_at",
            "recorded_from",
            "decision_role",
            "question_id",
            "answer",
            "decision_type",
            "decision_value",
            "effective_policy",
            "decision_effect",
            "production_impact",
            "provider_call_boundary",
            "live_kb_ingestion",
        ],
        "properties": {
            "decision_id": {"type": "string", "pattern": "^PO-20260619-Q[1-7]-[A-D]$"},
            "recorded_at": {"type": "string"},
            "recorded_from": {"type": "string"},
            "decision_role": {"const": "project_owner_product_owner"},
            "decision_scope": {"const": "product_staging_strategy"},
            "question_id": {"type": "string", "enum": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]},
            "answer": {"type": "string", "enum": ["A", "B", "C", "D"]},
            "decision_type": {"type": "string"},
            "decision_value": {"type": "string"},
            "effective_policy": {"type": "object"},
            "decision_effect": {"type": "string"},
            "production_impact": {"const": "production unchanged"},
            "provider_call_boundary": {"const": "no KB provider call"},
            "live_kb_ingestion": {"const": "no live KB ingestion"},
        },
        "additionalProperties": False,
    }
    SCHEMA.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    if len(rows) != 7:
        failures.append(f"expected 7 product-owner decisions, got {len(rows)}")
    expected_questions = {f"Q{index}" for index in range(1, 8)}
    observed_questions = {row.get("question_id") for row in rows}
    if observed_questions != expected_questions:
        failures.append(f"question coverage mismatch: {sorted(observed_questions)}")

    by_question = {row["question_id"]: row for row in rows}
    q1_policy = by_question["Q1"]["effective_policy"]
    if q1_policy.get("can_record_legal_source_owner_clearance") is not False:
        failures.append("Q1 must not imply legal/source-owner clearance")
    if q1_policy.get("can_record_security_approval") is not False:
        failures.append("Q1 must not imply security approval")

    q4_policy = by_question["Q4"]["effective_policy"]
    if q4_policy.get("human_gold_label_gate_mode") != "waive_for_staging_do_not_claim_human_gold":
        failures.append("Q4 must record machine-seeded eval only staging policy")
    if q4_policy.get("human_gold_metrics_claimed") is not False:
        failures.append("Q4 must not claim human-gold metrics")

    q6_policy = by_question["Q6"]["effective_policy"]
    if q6_policy.get("provider_call_enabled") is not False:
        failures.append("Q6 must not enable provider calls in this local run")
    return failures


def main() -> None:
    write_schema()
    rows = decision_rows()
    DECISIONS.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    failures = validate_rows(rows)
    by_question = {row["question_id"]: row for row in rows}
    payload = {
        "ok": not failures,
        "status": "valid" if not failures else "invalid",
        "decision_count": len(rows),
        "failure_count": len(failures),
        "failures": failures,
        "schema": str(SCHEMA.relative_to(ROOT)),
        "decisions": str(DECISIONS.relative_to(ROOT)),
        "product_owner_decision_recorded": True,
        "decision_role": "project_owner_product_owner",
        "internal_no_provider_staging_product_intent": True,
        "selected_source_count": 80,
        "legal_source_owner_clearance_effect": False,
        "raw_consult_git_commit_allowed": False,
        "future_tencent_cloud_lighthouse_runtime_upload_candidate": True,
        "human_gold_label_gate_mode": by_question["Q4"]["effective_policy"]["human_gold_label_gate_mode"],
        "human_gold_labeling_enabled": False,
        "human_gold_metrics_claimed": False,
        "human_label_approval_effect_count": 0,
        "machine_seeded_eval_continues": True,
        "security_controls_pending_to_approval_lane": True,
        "security_approval_effect_count": 0,
        "provider_model_allowed_in_staging_strategy": True,
        "provider_call_enabled": False,
        "provider_call_count": PROVIDER_CALL_COUNT,
        "live_kb_write_count": LIVE_KB_WRITE_COUNT,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "decision_effect_summary": {
            "can_change_human_label_gate_for_staging": True,
            "can_approve_human_gold_labels": False,
            "can_approve_legal_source_owner_clearance": False,
            "can_approve_security_controls": False,
            "can_enable_provider_call": False,
        },
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    REPORT.write_text(
        f"""---
title: "Consultant Role KB Product Owner Decision Record"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "{payload["decisions"]}"
  - "{payload["schema"]}"
scope: "records product-owner Q1-Q7 answers without converting them into legal, security, or human-gold approvals"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local governance record only"
---

# Consultant Role KB Product Owner Decision Record

## 0. Boundary

This record captures the product-owner answers from the Q1-Q7 intake. It does
not approve source licensing, approve security controls, configure secrets,
deploy shared staging, call a provider, or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| status | {payload["status"]} |
| decision_count | {payload["decision_count"]} |
| failure_count | {payload["failure_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

## 2. Recorded Decisions

| question | answer | effect |
|---|---|---|
| Q1 | A | product owner intent can be recorded; legal/source-owner and security approvals remain separate |
| Q2 | A | product intent allows all 80 selected sources for internal no-provider staging, pending legal/source-owner clearance |
| Q3 | A | raw `consult/` source files must not be committed to GitHub; later Tencent Cloud Lighthouse upload is a separate deployment gate |
| Q4 | D | defer human-gold labeling; continue with machine-seeded eval and do not claim human-gold metrics |
| Q5 | A | start security pending-to-approval lane; no security control is approved by this record |
| Q6 | C | provider model is acceptable for future staging design, but current run remains no-provider and provider calls are disabled |
| Q7 | A | prioritize human label decision handling as a defer/waiver policy, not as label approval |

## 3. Downstream Effect

Fact: the human-gold label gate is waived for shared-staging evidence only when
the run explicitly stays machine-seeded and does not claim human-gold metrics.

Fact: legal/source-owner clearance remains pending for the selected 80 sources.

Fact: security/operations controls remain pending, including external secret
storage, append-only audit storage, rate limiting, rollback ownership, and
private ingress.

Fact: raw `consult/` source files remain excluded from GitHub. Any future upload
to Tencent Cloud Lighthouse must be handled as a separate runtime deployment
artifact after legal, security, and deployment gates.
""",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "decision_count": len(rows)}, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
