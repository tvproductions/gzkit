"""Deterministic advisor-QC verdict-record engine — ADR-0.0.37, OBPI-0.0.37-24.

The advisor-QC stage sits between compress (OBPI-21) and commit (OBPI-22): an
agent wielding the ``gz-advisor-qc`` skill judges the information-retained-per-byte
of a candidate rendition and records its verdict as an ARB receipt the operator
cites at Gate 5. This module is the **deterministic record half** — it performs
NO in-code LLM or network call. The judgment is the skill's; the engine only:

1. validates receipt shape (explanation-before-verdict; ADR-0.0.39 doctrine),
2. assembles the verdict-shaped ARB receipt payload, and
3. writes it under the configured ARB receipts root.

It is **advisory, never gating** (ADR-0.0.39 Evidentiary invariant): any score —
including 0.0 — is recorded and the engine returns normally. The ONLY fail-closed
path is a structurally malformed receipt: an empty/absent explanation raises
``ValueError`` and writes no file (fail-closed-before-write).

The receipt ``run_id`` uses step name ``judge`` (``arb-step-judge-<32hex>``) so it
binds against the canonical receipt-id regex in
``gzkit.governance.trust_audits.attestation_receipts`` and is citable in a Gate-5
attestation. The step segment forbids a hyphen, so ``advisor-qc`` is not a legal
step name — ``judge`` is the doctrine-aligned form (plan booked decision,
2026-06-14).
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from gzkit.arb.paths import receipts_root

#: Receipt envelope schema id — distinct from the command-execution
#: ``gzkit.arb.step_receipt.v1`` because this receipt is verdict-shaped.
SCHEMA_ID = "gzkit.arb.advisor_verdict.v1"

#: The metric the advisor scores — information retained per byte of the rendition.
METRIC = "information-retained-per-byte"

#: ARB step name; ``arb-step-judge-<32hex>`` binds the canonical receipt-id regex.
_STEP_NAME = "judge"


def _new_run_id() -> str:
    """Mint a canonical ``arb-step-judge-<32hex>`` run id."""
    return f"arb-step-{_STEP_NAME}-{uuid.uuid4().hex}"


def record_verdict(
    *,
    root: Path,
    surface: str,
    consumer: str | None,
    explanation: str,
    score: float,
    run_id: str | None = None,
    timestamp: str | None = None,
) -> Path:
    """Assemble and write the advisor-QC ARB receipt; return its path.

    Args:
        root: Project root; the receipts directory is resolved relative to it.
        surface: The control surface scored (e.g. ``AGENTS.md``).
        consumer: The target vendor consumer (e.g. ``codex``), or ``None``.
        explanation: The advisor's reasoning. MUST be non-empty — it is
            serialized BEFORE the verdict (ADR-0.0.39 explanation-before-verdict).
        score: The information-retained-per-byte verdict value. ANY value is
            recorded — the engine never gates on it (advisory, never gating).
        run_id: Optional pinned run id (deterministic-test seam); minted when
            omitted.
        timestamp: Optional pinned ISO-8601 timestamp (deterministic-test seam);
            stamped from the clock when omitted.

    Returns:
        The path to the written receipt JSON.

    Raises:
        ValueError: If ``explanation`` is empty or whitespace-only. No receipt
            is written in this case (fail-closed-before-write) — the verdict
            value is never the fail-closed trigger; only malformed shape is.
        OSError: If the receipt cannot be written.

    """
    if not explanation or not explanation.strip():
        raise ValueError(
            "advisor-QC receipt is malformed: explanation is empty. "
            "ADR-0.0.39 requires the explanation before the verdict; a verdict "
            "without reasoning is never recorded. No receipt written."
        )

    resolved_run_id = run_id or _new_run_id()
    resolved_ts = timestamp or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Field construction order is fixed and explanation precedes the verdict
    # block, so json.dumps (no sort_keys) is both deterministic given the
    # inputs AND honors explanation-before-verdict.
    receipt: dict[str, object] = {
        "schema": SCHEMA_ID,
        "run_id": resolved_run_id,
        "step": {"name": _STEP_NAME, "metric": METRIC},
        "surface": surface,
        "consumer": consumer,
        "explanation": explanation,
        "verdict": {"metric": METRIC, "score": score},
        "timestamp_utc": resolved_ts,
        "exit_status": 0,
    }

    out_dir = receipts_root(project_root=root)
    path = out_dir / f"{resolved_run_id}.json"
    # Trailing newline keeps end-of-file-fixer from rewriting receipts on every
    # pre-commit run (mirrors gzkit.arb.step_reporter._write_receipt).
    path.write_text(
        json.dumps(receipt, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


__all__ = ["METRIC", "SCHEMA_ID", "record_verdict"]
