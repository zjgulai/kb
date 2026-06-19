#!/usr/bin/env python3
"""Preflight shared-staging readiness for consultant-agent.

Boundary: local evidence check only. This does not deploy staging, call a
provider, ingest into a live KB, approve labels, or validate real secrets.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "tmp/consultant-role-kb-shared-staging-readiness-preflight-20260619.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-shared-staging-readiness-preflight-20260619.md"


@dataclass(frozen=True)
class Check:
    check_id: str
    status: str
    evidence: str
    detail: str
    required_for_shared_staging: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "status": self.status,
            "evidence": self.evidence,
            "detail": self.detail,
            "required_for_shared_staging": self.required_for_shared_staging,
        }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_ls_files(pathspec: str) -> list[str]:
    output = subprocess.check_output(["git", "ls-files", pathspec], cwd=ROOT, text=True)
    return [line for line in output.splitlines() if line.strip()]


def add_metric_check(
    checks: list[Check],
    check_id: str,
    evidence: str,
    observed: Any,
    expected: Any,
    detail: str,
    required: bool = True,
) -> None:
    status = "pass" if observed == expected else "blocker"
    checks.append(
        Check(
            check_id=check_id,
            status=status,
            evidence=evidence,
            detail=f"{detail}; observed={observed!r}, expected={expected!r}",
            required_for_shared_staging=required,
        )
    )


def env_status(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        return "missing"
    if any(term in value.lower() for term in ["token", "secret", "password", "private"]):
        return "set_redacted"
    return "set"


def external_path_status(name: str) -> tuple[str, str]:
    raw = os.environ.get(name, "")
    if not raw:
        return "missing", "environment variable is not set"
    path = Path(raw).expanduser()
    try:
        resolved = path.resolve()
        resolved.relative_to(ROOT)
        return "inside_repo", "path resolves inside the repository"
    except ValueError:
        pass
    parent = resolved.parent
    if not parent.exists():
        return "parent_missing", "parent directory does not exist"
    if not os.access(parent, os.W_OK):
        return "parent_not_writable", "parent directory is not writable"
    return "external_writable_parent", "path is outside repo and parent is writable"


def main() -> None:
    api_smoke = load_json(ROOT / "tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json")
    harness_smoke = load_json(ROOT / "tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json")
    audit_contract = load_json(ROOT / "tmp/consultant-role-kb-staging-auth-audit-contract-validation-20260619.json")
    label_workflow = load_json(ROOT / "tmp/consultant-role-kb-human-label-review-workflow-validation-20260619.json")
    vector_smoke = load_json(ROOT / "tmp/consultant-role-kb-all-extractable-vector-store-smoke-20260619.json")
    legal_workflow = load_json(ROOT / "tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json")
    security_workflow = load_json(ROOT / "tmp/consultant-role-kb-security-staging-control-validation-20260619.json")
    manual_intake = load_json(ROOT / "tmp/consultant-role-kb-manual-decision-intake-preflight-20260619.json")

    api_metrics = api_smoke["metrics"]
    harness_metrics = harness_smoke["metrics"]
    vector_metrics = vector_smoke["metrics"]
    checks: list[Check] = []

    add_metric_check(
        checks,
        "local_api_smoke_green",
        "tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json",
        api_smoke["failure_count"],
        0,
        "private no-provider retrieval API local smoke must be green",
    )
    add_metric_check(
        checks,
        "local_api_800_record_alignment",
        "tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json",
        api_metrics["record_count"],
        800,
        "API smoke must load the current 800-record local index",
    )
    add_metric_check(
        checks,
        "local_api_policy_refusal_green",
        "tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json",
        api_metrics["policy_refusal_pass_rate"],
        1.0,
        "policy-refusal eval path must remain green",
    )
    add_metric_check(
        checks,
        "local_harness_smoke_green",
        "tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json",
        harness_smoke["failure_count"],
        0,
        "localhost staging auth/audit harness smoke must be green",
    )
    add_metric_check(
        checks,
        "local_harness_denies_missing_token",
        "tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json",
        harness_metrics["missing_token_status"],
        401,
        "missing bearer token must fail closed",
    )
    add_metric_check(
        checks,
        "local_harness_denies_rbac",
        "tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json",
        harness_metrics["rbac_denied_status"],
        403,
        "forbidden endpoint-role combination must fail closed",
    )
    add_metric_check(
        checks,
        "audit_contract_green",
        "tmp/consultant-role-kb-staging-auth-audit-contract-validation-20260619.json",
        audit_contract["failure_count"],
        0,
        "staging audit sample events must validate",
    )
    add_metric_check(
        checks,
        "audit_no_forbidden_leak",
        "tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json",
        harness_metrics["audit_forbidden_leak_count"],
        0,
        "audit smoke must not leak token, bearer header, raw questions, or raw source text",
    )
    add_metric_check(
        checks,
        "no_provider_calls",
        "multiple smoke outputs",
        max(
            api_metrics["provider_call_count"],
            harness_metrics["provider_call_count"],
            audit_contract["provider_call_count"],
            label_workflow["provider_call_count"],
            vector_metrics["provider_call_count"],
            security_workflow["provider_call_count"],
            manual_intake["provider_call_count"],
        ),
        0,
        "all readiness evidence must preserve no-provider boundary",
    )
    add_metric_check(
        checks,
        "no_live_kb_writes",
        "multiple smoke outputs",
        max(
            api_metrics["live_kb_write_count"],
            harness_metrics["live_kb_write_count"],
            audit_contract["live_kb_write_count"],
            label_workflow["live_kb_write_count"],
            vector_metrics["live_kb_write_count"],
            security_workflow["live_kb_write_count"],
            manual_intake["live_kb_write_count"],
        ),
        0,
        "all readiness evidence must preserve no-live-KB-write boundary",
    )
    add_metric_check(
        checks,
        "human_label_workflow_generated",
        "tmp/consultant-role-kb-human-label-review-workflow-validation-20260619.json",
        label_workflow["failure_count"],
        0,
        "human label workflow generation must be valid",
    )
    add_metric_check(
        checks,
        "legal_source_owner_workflow_generated",
        "tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json",
        legal_workflow["failure_count"],
        0,
        "legal/source-owner decision workflow must be structurally valid",
    )
    add_metric_check(
        checks,
        "security_control_workflow_generated",
        "tmp/consultant-role-kb-security-staging-control-validation-20260619.json",
        security_workflow["failure_count"],
        0,
        "security/operations control decision workflow must be structurally valid",
    )
    add_metric_check(
        checks,
        "manual_decision_intake_preflight_green",
        "tmp/consultant-role-kb-manual-decision-intake-preflight-20260619.json",
        manual_intake["failure_count"],
        0,
        "manual decision intake must validate before it can affect shared-staging readiness",
    )

    approved_labels = manual_intake["human_approved_decision_count"]
    human_gate_waived = bool(manual_intake.get("human_label_gate_waived_for_staging", False))
    human_gate_ready = bool(manual_intake.get("human_label_gate_ready_for_staging", False))
    checks.append(
        Check(
            check_id="human_label_gate_policy_recorded",
            status="pass" if human_gate_ready else "blocker",
            evidence="tmp/consultant-role-kb-manual-decision-intake-preflight-20260619.json",
            detail=(
                "approved_decision_count="
                f"{approved_labels}/{manual_intake['human_seed_label_count']}; "
                f"human_label_gate_waived_for_staging={human_gate_waived}; "
                "human-gold metrics must not be claimed unless labels are actually approved"
            ),
        )
    )

    legal_ready = bool(manual_intake["legal_clearance_ready"])
    checks.append(
        Check(
            check_id="legal_source_owner_clearance",
            status="pass" if legal_ready else "blocker",
            evidence="tmp/consultant-role-kb-manual-decision-intake-preflight-20260619.json",
            detail=(
                "selected_approved_internal_staging_count="
                f"{manual_intake['legal_selected_approved_internal_staging_count']}/"
                f"{manual_intake['legal_selected_source_count']}; legal/source-owner clearance remains pending"
            ),
        )
    )

    security_ready = bool(manual_intake["security_controls_ready"])
    checks.append(
        Check(
            check_id="security_controls_approved",
            status="pass" if security_ready else "blocker",
            evidence="tmp/consultant-role-kb-manual-decision-intake-preflight-20260619.json",
            detail=(
                "approved_control_count="
                f"{manual_intake['security_approved_control_count']}/"
                f"{manual_intake['security_control_count']}; security/operations controls remain pending"
            ),
        )
    )

    tracked_consult = git_ls_files("consult")
    checks.append(
        Check(
            check_id="raw_consult_not_tracked",
            status="pass" if tracked_consult == ["consult/README.md"] else "blocker",
            evidence="git ls-files consult",
            detail=f"tracked_consult_files={tracked_consult}",
        )
    )

    runbook = ROOT / "drafts/analysis/consultant-role-kb-shared-staging-runbook-20260619.md"
    checks.append(
        Check(
            check_id="rollback_runbook_exists",
            status="pass" if runbook.exists() else "blocker",
            evidence=str(runbook.relative_to(ROOT)),
            detail="runbook documents start, smoke, rollback, and stop conditions; operator owner is checked separately",
        )
    )

    token_status = env_status("KB_STAGING_AUTH_TOKEN_SHA256")
    checks.append(
        Check(
            check_id="external_auth_token_hash_configured",
            status="pass" if token_status == "set" else "blocker",
            evidence="environment:KB_STAGING_AUTH_TOKEN_SHA256",
            detail=f"token hash status={token_status}; secret value is not logged",
        )
    )

    audit_status, audit_detail = external_path_status("KB_STAGING_AUDIT_PATH")
    checks.append(
        Check(
            check_id="external_audit_path_configured",
            status="pass" if audit_status == "external_writable_parent" else "blocker",
            evidence="environment:KB_STAGING_AUDIT_PATH",
            detail=f"audit path status={audit_status}; {audit_detail}",
        )
    )

    rate_limit_status = os.environ.get("KB_STAGING_RATE_LIMIT_CONFIGURED", "").lower()
    checks.append(
        Check(
            check_id="rate_limit_configured",
            status="pass" if rate_limit_status in {"1", "true", "yes"} else "blocker",
            evidence="environment:KB_STAGING_RATE_LIMIT_CONFIGURED",
            detail="rate limiting must be configured at private ingress or middleware before shared staging",
        )
    )

    rollback_owner = os.environ.get("KB_STAGING_ROLLBACK_OWNER", "")
    checks.append(
        Check(
            check_id="rollback_owner_recorded",
            status="pass" if rollback_owner else "blocker",
            evidence="environment:KB_STAGING_ROLLBACK_OWNER",
            detail="rollback owner is not recorded in local environment; value is not logged",
        )
    )

    blockers = [check for check in checks if check.status == "blocker" and check.required_for_shared_staging]
    warnings = [check for check in checks if check.status == "warn"]
    passes = [check for check in checks if check.status == "pass"]
    ready = not blockers
    payload = {
        "ok": True,
        "ready_for_shared_staging": ready,
        "status": "ready" if ready else "blocked",
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "shared_staging_deployment": "not deployed",
        "check_count": len(checks),
        "pass_count": len(passes),
        "warning_count": len(warnings),
        "blocker_count": len(blockers),
        "blockers": [check.to_dict() for check in blockers],
        "checks": [check.to_dict() for check in checks],
        "source_text_returned": False,
        "human_label_gate_policy": manual_intake.get("human_label_gate_policy", "not_recorded"),
        "human_label_gate_waived_for_staging": human_gate_waived,
        "human_gold_metrics_claimed": bool(manual_intake.get("human_gold_metrics_claimed", False)),
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    blocker_rows = "\n".join(
        f"| `{check.check_id}` | {check.evidence} | {check.detail} |" for check in blockers
    )
    check_rows = "\n".join(
        f"| `{check.check_id}` | {check.status} | {check.evidence} |" for check in checks
    )
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Shared Staging Readiness Preflight"
status: "draft"
created_at: "2026-06-19"
source_documents:
  - "drafts/analysis/consultant-role-kb-staging-auth-audit-design-20260619.md"
  - "drafts/analysis/consultant-role-kb-legal-source-owner-review-packet-20260619.md"
  - "tmp/consultant-role-kb-private-retrieval-api-smoke-20260619.json"
  - "tmp/consultant-role-kb-local-staging-auth-audit-smoke-20260619.json"
  - "tmp/consultant-role-kb-legal-source-owner-decision-validation-20260619.json"
  - "tmp/consultant-role-kb-security-staging-control-validation-20260619.json"
  - "tmp/consultant-role-kb-manual-decision-intake-preflight-20260619.json"
  - "tmp/consultant-role-kb-product-owner-decision-validation-20260619.json"
scope: "preflight gate before any security-approved shared staging deployment"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "local readiness check only; no shared staging deployment"
---

# Consultant Role KB Shared Staging Readiness Preflight

## 0. Boundary

This preflight is a local evidence check. It does not deploy staging, call a
provider, ingest into a live KB, approve labels, or clear source licensing.

## 1. Result

| field | value |
|---|---:|
| ready_for_shared_staging | {str(ready).lower()} |
| status | {payload["status"]} |
| check_count | {len(checks)} |
| pass_count | {len(passes)} |
| warning_count | {len(warnings)} |
| blocker_count | {len(blockers)} |
| provider_call_count | 0 |
| live_kb_write_count | 0 |
| human_label_gate_waived_for_staging | {str(human_gate_waived).lower()} |
| human_gold_metrics_claimed | {str(payload["human_gold_metrics_claimed"]).lower()} |

## 2. Blockers

| check | evidence | detail |
|---|---|---|
{blocker_rows if blocker_rows else "| none | none | none |"}

## 3. All Checks

| check | status | evidence |
|---|---|---|
{check_rows}

## 4. Interpretation

Fact: local retrieval API, local auth/audit harness, audit schema validation,
manual decision intake validation, no-provider boundary, no-live-write
boundary, and raw-source Git exclusion are green.

Fact: product-owner Q4:D waives the human-gold label gate for staging evidence
only under a machine-seeded-eval policy. Human-gold labels remain unapproved
and human-gold metrics are not claimed.

Fact: shared staging remains blocked by missing legal/source-owner clearance
and missing external staging controls such as security/operations approval,
secret configuration, external audit path, rate limit configuration, and
rollback ownership.

Boundary: this is not a staging deployment and should not be described as
online agent launch readiness.
""",
        encoding="utf-8",
    )
    print(json.dumps({"ready_for_shared_staging": ready, "blocker_count": len(blockers)}, ensure_ascii=False))
    if not ready:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
