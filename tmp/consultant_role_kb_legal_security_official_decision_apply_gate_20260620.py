#!/usr/bin/env python3
"""Gate official legal/security decision template updates.

Boundary: fail-closed local apply gate. By default this script performs a
dry-run and writes only validation/report artifacts. It writes official
legal/security decision templates only when the promotion preflight is ready
and both explicit acceptance and explicit apply mode are present.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_SCRIPT = ROOT / "tmp/consultant_role_kb_legal_security_official_decision_promotion_preflight_20260620.py"
PREFLIGHT_JSON = ROOT / "tmp/consultant-role-kb-legal-security-official-decision-promotion-preflight-20260620.json"

OUT_JSON = ROOT / "tmp/consultant-role-kb-legal-security-official-decision-apply-gate-20260620.json"
REPORT = ROOT / "drafts/analysis/consultant-role-kb-legal-security-official-decision-apply-gate-20260620.md"

OFFICIAL_LEGAL_TEMPLATE = ROOT / "shared/governance/consultant-agent/legal-source-owner-decisions.template-20260619.jsonl"
OFFICIAL_SECURITY_TEMPLATE = (
    ROOT / "shared/governance/consultant-agent/security-staging-control-decisions.template-20260619.jsonl"
)

APPLY_ENV = "KB_LEGAL_SECURITY_DECISION_APPLY_MODE"
APPLY_VALUE = "write-official-decision-templates"
PROMOTION_AUTH_ENV = "KB_LEGAL_SECURITY_DECISION_PROMOTION_ACCEPTANCE"
PROMOTION_AUTH_VALUE = "accept-reviewed-legal-security-candidate"

PROVIDER_CALL_COUNT = 0
LIVE_KB_WRITE_COUNT = 0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_text(source: Path, target: Path) -> None:
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def candidate_path(preflight: dict[str, Any], key: str) -> Path | None:
    raw = str(preflight[key])
    if raw.startswith("external:"):
        return None
    return ROOT / raw


def run_preflight() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(PREFLIGHT_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "promotion preflight failed: "
            f"exit={completed.returncode}; stdout={completed.stdout}; stderr={completed.stderr}"
        )
    return read_json(PREFLIGHT_JSON)


def main() -> None:
    preflight = run_preflight()
    apply_mode = os.environ.get(APPLY_ENV, "").strip()
    apply_authorized = apply_mode == APPLY_VALUE
    promotion_authorized = os.environ.get(PROMOTION_AUTH_ENV, "").strip() == PROMOTION_AUTH_VALUE

    blockers: list[str] = []
    if not preflight.get("ok"):
        blockers.append("promotion_preflight_not_ok")
    if preflight.get("status") != "ready_for_explicit_acceptance":
        blockers.append("promotion_preflight_not_ready")
    if not preflight.get("acceptance_authorized"):
        blockers.append("promotion_acceptance_authorization_missing")
    if not promotion_authorized:
        blockers.append("promotion_authorization_env_missing")
    if not apply_authorized:
        blockers.append("apply_mode_authorization_missing")
    if preflight.get("provider_call_count") != 0:
        blockers.append("provider_call_count_not_zero")
    if preflight.get("live_kb_write_count") != 0:
        blockers.append("live_kb_write_count_not_zero")

    legal_candidate = candidate_path(preflight, "legal_candidate_decisions")
    security_candidate = candidate_path(preflight, "security_candidate_decisions")
    if legal_candidate is None or not legal_candidate.exists():
        blockers.append("legal_candidate_path_not_local_or_missing")
    if security_candidate is None or not security_candidate.exists():
        blockers.append("security_candidate_path_not_local_or_missing")

    official_template_write_count = 0
    write_performed = False
    if not blockers:
        assert legal_candidate is not None
        assert security_candidate is not None
        copy_text(legal_candidate, OFFICIAL_LEGAL_TEMPLATE)
        copy_text(security_candidate, OFFICIAL_SECURITY_TEMPLATE)
        official_template_write_count = 2
        write_performed = True

    provider_call_count = max(PROVIDER_CALL_COUNT, int(preflight.get("provider_call_count", 0)))
    live_kb_write_count = max(LIVE_KB_WRITE_COUNT, int(preflight.get("live_kb_write_count", 0)))
    payload = {
        "ok": not blockers,
        "status": "applied" if write_performed else "blocked",
        "write_performed": write_performed,
        "apply_mode": apply_mode or "dry_run",
        "apply_authorized": apply_authorized,
        "apply_env": APPLY_ENV,
        "required_apply_value": APPLY_VALUE,
        "promotion_acceptance_authorized": bool(preflight.get("acceptance_authorized")) and promotion_authorized,
        "promotion_acceptance_env": PROMOTION_AUTH_ENV,
        "required_promotion_acceptance_value": PROMOTION_AUTH_VALUE,
        "promotion_preflight": str(PREFLIGHT_JSON.relative_to(ROOT)),
        "legal_candidate_decisions": preflight.get("legal_candidate_decisions"),
        "security_candidate_decisions": preflight.get("security_candidate_decisions"),
        "official_legal_template": str(OFFICIAL_LEGAL_TEMPLATE.relative_to(ROOT)),
        "official_security_template": str(OFFICIAL_SECURITY_TEMPLATE.relative_to(ROOT)),
        "official_template_write_count": official_template_write_count,
        "approval_effect_count": 0,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "preflight_status": preflight.get("status"),
        "preflight_blocker_count": preflight.get("blocker_count"),
        "preflight_blockers": preflight.get("blockers"),
        "preflight_changed_row_count": preflight.get("changed_row_count"),
        "preflight_candidate_non_pending_count": preflight.get("candidate_non_pending_count"),
        "preflight_legal_selected_approved_internal_staging_count": preflight.get(
            "legal_selected_approved_internal_staging_count"
        ),
        "preflight_security_approved_control_count": preflight.get("security_approved_control_count"),
        "provider_call_count": provider_call_count,
        "live_kb_write_count": live_kb_write_count,
        "production_impact": "production unchanged",
        "provider_call_boundary": "no KB provider call",
        "live_kb_ingestion": "no live KB ingestion",
        "shared_staging_deployment": "not deployed",
        "manual_review_boundary": "apply gate only; official templates unchanged unless status=applied",
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"""---
title: "Consultant Role KB Legal Security Official Decision Apply Gate"
status: "draft"
created_at: "2026-06-20"
source_documents:
  - "{payload["promotion_preflight"]}"
  - "{payload["legal_candidate_decisions"]}"
  - "{payload["security_candidate_decisions"]}"
scope: "guarded write gate for official legal/source-owner and security decision records"
production_impact: "production unchanged"
provider_call_boundary: "no KB provider call"
implementation_status: "dry-run blocked unless all explicit gates pass"
---

# Consultant Role KB Legal Security Official Decision Apply Gate

## 0. Boundary

This apply gate runs the promotion preflight and blocks by default. It does not
write official decision templates unless the candidate files are ready, the
promotion acceptance environment variable is set, and the explicit apply mode
is set. It does not configure secrets, deploy shared staging, call a provider,
or ingest into a live KB.

## 1. Result

| field | value |
|---|---:|
| status | {payload["status"]} |
| write_performed | {str(payload["write_performed"]).lower()} |
| apply_mode | {payload["apply_mode"]} |
| blocker_count | {payload["blocker_count"]} |
| official_template_write_count | {payload["official_template_write_count"]} |
| approval_effect_count | {payload["approval_effect_count"]} |
| provider_call_count | {payload["provider_call_count"]} |
| live_kb_write_count | {payload["live_kb_write_count"]} |

## 2. Current Blockers

```json
{json.dumps(payload["blockers"], ensure_ascii=False, indent=2)}
```

## 3. Write Command

Only after reviewed candidates pass preflight:

```bash
{PROMOTION_AUTH_ENV}={PROMOTION_AUTH_VALUE} \\
{APPLY_ENV}={APPLY_VALUE} \\
python3 tmp/consultant_role_kb_legal_security_official_decision_apply_gate_20260620.py
```

Boundary: this command updates only the two official decision JSONL templates.
It is not legal/source-owner clearance unless the candidate itself contains
valid reviewer approvals, and it is not shared-staging deployment.
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "write_performed": payload["write_performed"],
                "blocker_count": payload["blocker_count"],
                "official_template_write_count": payload["official_template_write_count"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
