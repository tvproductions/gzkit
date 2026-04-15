"""gzkit ARB (Agent Self-Reporting) middleware.

ARB wraps QA commands (ruff, ty, unittest, coverage, etc.) and emits
schema-validated JSON receipts to `artifacts/receipts/`. These receipts are
the canonical evidence cited in attestation-enrichment Heavy-lane claims —
see `.gzkit/rules/arb.md` and `.gzkit/rules/attestation-enrichment.md`.

Absorbed from airlineops/src/opsdev/arb/ under OBPI-0.25.0-33.
"""

from gzkit.arb.advisor import ArbAdvice, collect_arb_advice, render_arb_advice_text
from gzkit.arb.paths import receipts_root
from gzkit.arb.patterns import (
    PatternCandidate,
    PatternReport,
    collect_patterns,
    render_patterns_compact,
    render_patterns_markdown,
)
from gzkit.arb.ruff_reporter import run_ruff_via_arb
from gzkit.arb.step_reporter import run_step_via_arb
from gzkit.arb.validator import (
    ArbReceiptValidationResult,
    render_validation_text,
    validate_receipts,
)

__all__ = [
    "ArbAdvice",
    "ArbReceiptValidationResult",
    "PatternCandidate",
    "PatternReport",
    "collect_arb_advice",
    "collect_patterns",
    "receipts_root",
    "render_arb_advice_text",
    "render_patterns_compact",
    "render_patterns_markdown",
    "render_validation_text",
    "run_ruff_via_arb",
    "run_step_via_arb",
    "validate_receipts",
]
