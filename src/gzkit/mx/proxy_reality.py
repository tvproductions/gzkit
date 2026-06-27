"""MX proxy-reality distance detector (OBPI-0.0.74-13).

Reads the ledger for the canonical "a gate went green AND reality was later
found wrong" signal — a ``obpi_completion_repudiated`` event with
``cause == model-induced-fabrication`` — and produces a record naming the
gate that cleared each instance plus a count.

This module is *grader-gaming*'s live §5 negative control: the ``@enforces``
registration here is the structural proof that the floor claim is enforced
and not merely named (ADR-0.0.74 Boundary Invariant #5).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from gzkit.enforcement import enforces, get_enforcement_registry, set_known_claims
from gzkit.ledger import Ledger

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

_PROXY_REALITY_CLAIM_IDS: frozenset[str] = frozenset({"grader-gaming"})

# The gate that "cleared" every repudiated completion is Gate 5 — the human
# attestation step that the fabrication fooled.
_CLEARING_GATE = "gate5"

# The canonical cause for a proxy-reality-distance signal.
_FABRICATION_CAUSE = "model-induced-fabrication"


class ProxyRealityRecord(BaseModel):
    """One "gate went green AND reality was later found wrong" instance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str
    repudiated_receipt: str
    clearing_gate: str
    cause: str


class ProxyRealityScanResult(BaseModel):
    """Result of a proxy-reality distance scan over the ledger."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    records: list[ProxyRealityRecord]
    count: int


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


def scan(root: Path | None = None) -> ProxyRealityScanResult:
    """Read the ledger for gate-green-but-reality-wrong signals.

    Finds every ``obpi_completion_repudiated`` event with
    ``cause == model-induced-fabrication`` and returns a named record for each
    plus a count — turning grader-gaming from a conviction into a number.

    Args:
        root: Project root whose ``.gzkit/ledger.jsonl`` is scanned.
              Defaults to the current working directory.

    """
    if root is None:
        root = Path.cwd()

    ledger_path = root / ".gzkit" / "ledger.jsonl"
    ledger = Ledger(ledger_path)
    events = ledger.query(event_type="obpi_completion_repudiated")

    records: list[ProxyRealityRecord] = []
    for event in events:
        if event.extra.get("cause") != _FABRICATION_CAUSE:
            continue
        records.append(
            ProxyRealityRecord(
                obpi_id=event.id,
                repudiated_receipt=event.extra.get("repudiated_receipt", ""),
                clearing_gate=_CLEARING_GATE,
                cause=_FABRICATION_CAUSE,
            )
        )

    return ProxyRealityScanResult(records=records, count=len(records))


# ---------------------------------------------------------------------------
# Live negative control (REQ-0.0.74-13-02 + §5 enforcement-claim)
# ---------------------------------------------------------------------------


def _build_proxy_reality_violation() -> Path:
    """Plant a known proxy-reality violation: a ledger with a model-induced-fabrication
    repudiation event.

    The runner removes the temp dir after the entrypoint runs; the fixture uses
    ``mkdtemp`` rather than a context manager per the qc_binding NC convention.
    """
    root = Path(tempfile.mkdtemp(prefix="gzkit-proxy-reality-nc-"))
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)
    (gzkit_dir / "ledger.jsonl").write_text(
        json.dumps(
            {
                "schema": "gzkit.ledger.v1",
                "event": "obpi_completion_repudiated",
                "id": "OBPI-0.0.74-13-nc-planted",
                "ts": "2026-01-01T00:00:00+00:00",
                "repudiated_receipt": "nc-planted-receipt",
                "cause": "model-induced-fabrication",
                "attestor": "nc-fixture",
                "reason": "planted violation for live negative control",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def _ep_proxy_reality(root: Path) -> int:
    """Production entrypoint: run the real ``scan()`` on the fixture root.

    Returns ``count`` — truthy (> 0) when the violation is caught, falsy (0)
    when it is not. Genuineness is structural: this callable invokes the
    production path; no forcing kwargs are pre-bound.
    """
    return scan(root).count


def _marker() -> None:
    """Inert carrier for ``@enforces`` registration."""


def _ensure_grader_gaming_registered() -> None:
    """(Re)register the grader-gaming enforcement claim (idempotent, reset-safe).

    Extends the known-claims set with ``grader-gaming`` before decorating so the
    import-time validation accepts it, then registers the claim if not already
    present. Production discovery wiring is OBPI-0.0.74-19 (floor wiring, strict
    no-debt); this module registers the claim but does not auto-join ``gz check``
    at import time.
    """
    from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
        _KNOWN_QC_CLAIM_IDS,
    )

    set_known_claims(_KNOWN_QC_CLAIM_IDS | _PROXY_REALITY_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if "grader-gaming" not in existing:
        enforces("grader-gaming", _build_proxy_reality_violation, _ep_proxy_reality)(_marker)
