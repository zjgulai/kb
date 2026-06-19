#!/usr/bin/env python3
"""Run local retrieval/citation regression for batch-30 consultant-role cards.

Boundary: local regression only, no provider call, no live KB ingestion,
production unchanged.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE_REGRESSION_SCRIPT = ROOT / "tmp/consultant_role_kb_expanded_regression_eval_20260619.py"

BATCH30_CARD_PATH = ROOT / "tmp/consultant-role-kb-batch30-cards-20260619.jsonl"
FULL_SOURCE_REGISTER_PATH = ROOT / "drafts/analysis/consultant-role-kb-full-source-register-20260619.csv"

RETRIEVAL_EVAL_OUT = ROOT / "tmp/consultant-role-kb-batch30-anchored-retrieval-citation-eval-20260619.json"
RETRIEVAL_REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-batch30-regression-eval-report-20260619.md"
TRACE_OUT = ROOT / "tmp/consultant-role-kb-batch30-answer-trace-fixture-20260619.jsonl"
TRACE_EVAL_OUT = ROOT / "tmp/consultant-role-kb-batch30-answer-trace-eval-20260619.json"
TRACE_REPORT_OUT = ROOT / "drafts/analysis/consultant-role-kb-batch30-answer-trace-fixture-report-20260619.md"


def load_base_module() -> Any:
    spec = importlib.util.spec_from_file_location("consultant_batch30_base_regression", BASE_REGRESSION_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load base regression script: {BASE_REGRESSION_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["consultant_batch30_base_regression"] = module
    spec.loader.exec_module(module)
    return module


def rewrite_report_header(report_path: Path) -> None:
    text = report_path.read_text(encoding="utf-8")
    text = text.replace("Consultant Role KB Expanded Regression Eval Report", "Consultant Role KB Batch-30 Regression Eval Report")
    text = text.replace("expanded local cards", "batch-30 local cards")
    text = text.replace("tmp/consultant-role-kb-expanded-cards-20260619.jsonl", "tmp/consultant-role-kb-batch30-cards-20260619.jsonl")
    text = text.replace("local regression eval for expanded consultant role KB cards", "local regression eval for batch-30 consultant role KB cards")
    report_path.write_text(text, encoding="utf-8")


def main() -> None:
    base = load_base_module()
    base.EXPANDED_CARD_PATH = BATCH30_CARD_PATH
    base.SOURCE_REGISTER_PATH = FULL_SOURCE_REGISTER_PATH
    base.RETRIEVAL_EVAL_OUT = RETRIEVAL_EVAL_OUT
    base.RETRIEVAL_REPORT_OUT = RETRIEVAL_REPORT_OUT
    base.TRACE_OUT = TRACE_OUT
    base.TRACE_EVAL_OUT = TRACE_EVAL_OUT
    base.TRACE_REPORT_OUT = TRACE_REPORT_OUT

    retrieval_payload = base.run_retrieval_eval()
    trace_payload = base.run_answer_trace(retrieval_payload)
    rewrite_report_header(RETRIEVAL_REPORT_OUT)
    print(
        json.dumps(
            {
                "retrieval_summary": retrieval_payload["metrics"],
                "trace_summary": trace_payload["summary"],
                "outputs": [
                    str(RETRIEVAL_EVAL_OUT),
                    str(RETRIEVAL_REPORT_OUT),
                    str(TRACE_OUT),
                    str(TRACE_EVAL_OUT),
                    str(TRACE_REPORT_OUT),
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
