"""Ledger ts-order across the rows one completion writes (GHI #842).

``LedgerEvent.ts`` defaults at CONSTRUCTION (``gzkit/ledger.py``), but the
append-only ledger orders rows by ``ts`` at WRITE time. ``gz obpi complete``
builds its rows in one order and writes them in another: the receipt is built
before the Step-4b gate runs so ``--dry-run`` can print it, the adversarial
verdict is built after that gate and written ABOVE the receipt, and the
security-floor override is built earliest of the three and written LAST. Both
pairs emit a ``ts`` that runs backwards against the row above, and the ledger's
own ts-order gate then refuses the push -- a completed, attested OBPI that no
governed route can land.

The rows here carry EXPLICIT construction-order stamps rather than leaning on
wall-clock gaps: the observed inversion was 0.74 ms, small enough that a
timing-dependent test would pass by luck on a fast machine.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.commands.obpi_complete import (
    _emit_security_floor_override_best_effort,
    _execute_transaction,
)
from gzkit.commands.obpi_complete_adversarial import _build_adversarial_event
from gzkit.ledger import Ledger
from gzkit.ledger_events import (
    obpi_receipt_emitted_event,
    security_floor_overridden_event,
)
from gzkit.validate_pkg.ledger_check import parse_ledger_ts, validate_ledger

_OBPI = "OBPI-0.35.0-09-codex-playback-wiring"
_ADR = "ADR-0.35.0-canon-entry-corpus-landing"

# Construction order in ``obpi_complete``: the override is built first (the
# security floor is resolved early), the receipt second (``--dry-run`` prints
# it), the adversarial verdict last (after the Step-4b gate). Write order puts
# the verdict FIRST and the override LAST, so these three stamps are the exact
# inversion the defect produced.
_BASE = datetime(2026, 8, 22, 8, 23, 56, tzinfo=UTC)
_OVERRIDE_BUILT_AT = _BASE
_RECEIPT_BUILT_AT = _BASE + timedelta(milliseconds=1)
_VERDICT_BUILT_AT = _BASE + timedelta(milliseconds=2)


def _run_completion(*, with_override: bool) -> Path:
    """Write one completion's rows through the real transaction; return the ledger path."""
    root = Path(tempfile.mkdtemp(prefix="gzkit-tsorder-"))
    adr_dir = root / "adr"
    adr_dir.mkdir(parents=True)
    obpi_file = adr_dir / "brief.md"
    obpi_file.write_text("original\n", encoding="utf-8")
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")

    receipt = obpi_receipt_emitted_event(
        obpi_id=_OBPI,
        receipt_event="completed",
        attestor="g0",
        evidence={"parent_lane": "heavy"},
        parent_adr=_ADR,
        obpi_completion="completed",
    ).model_copy(update={"ts": _RECEIPT_BUILT_AT.isoformat()})

    verdict = _build_adversarial_event(
        obpi_id=_OBPI,
        verdict="refuted",
        adversary="codex/gpt-5.4",
        job_id=None,
        refuted_claim=None,
        resolution="claim re-derived and the adversary's own check re-run",
    )
    assert verdict is not None
    verdict = verdict.model_copy(update={"ts": _VERDICT_BUILT_AT.isoformat()})

    _execute_transaction(
        obpi_file=obpi_file,
        original_content="original\n",
        new_content="completed\n",
        adr_dir=adr_dir,
        audit_entry={"obpi_id": _OBPI, "attestor": "g0"},
        ledger=ledger,
        receipt_event=receipt,
        adversarial_event=verdict,
    )

    if with_override:
        override = security_floor_overridden_event(
            obpi_id=_OBPI,
            surfaces="auth_boundaries",
            reason="operator reviewed overlap; change is structurally defensive",
            attestor="g0",
        ).model_copy(update={"ts": _OVERRIDE_BUILT_AT.isoformat()})
        _emit_security_floor_override_best_effort(ledger, override)

    return ledger.path


def _rows(path: Path) -> list[tuple[str, datetime]]:
    """Return (event name, parsed ts) in FILE order."""
    parsed: list[tuple[str, datetime]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        ts = parse_ledger_ts(entry.get("ts"))
        assert ts is not None, f"unparseable ts on row: {entry}"
        parsed.append((str(entry["event"]), ts))
    return parsed


class TestCompletionRowsAreTsOrdered(unittest.TestCase):
    """Whatever ts the events were BUILT with, the rows WRITTEN are ts-ordered."""

    def test_adversarial_verdict_row_does_not_run_backwards(self) -> None:
        rows = _rows(_run_completion(with_override=False))
        self.assertEqual(
            [name for name, _ in rows],
            ["adversarial_validation", "obpi_receipt_emitted"],
            "GHI #676 write order: the verdict that gated the receipt lands above it",
        )
        (_, verdict_ts), (_, receipt_ts) = rows
        self.assertLessEqual(
            verdict_ts,
            receipt_ts,
            "the verdict is written ABOVE the receipt, so its ts may not follow the "
            "receipt's -- the append-only contract orders rows by ts",
        )

    def test_security_floor_override_row_does_not_run_backwards(self) -> None:
        rows = _rows(_run_completion(with_override=True))
        self.assertEqual(
            [name for name, _ in rows],
            [
                "adversarial_validation",
                "obpi_receipt_emitted",
                "security_floor_overridden",
            ],
            "the override witness is emitted after the transaction commits",
        )
        stamps = [ts for _, ts in rows]
        self.assertEqual(
            stamps,
            sorted(stamps),
            "the override is BUILT before the receipt and WRITTEN after it; its ts "
            "may not precede the rows above it",
        )


class TestEmittedLedgerPassesItsOwnTsGate(unittest.TestCase):
    """The runtime may not emit a ledger its own append-only gate refuses."""

    def test_real_validator_reports_no_ts_inversion(self) -> None:
        path = _run_completion(with_override=True)
        inversions = [err for err in validate_ledger(path) if err.field == "ts"]
        self.assertEqual(
            [err.message for err in inversions],
            [],
            "gz validate refuses a ledger whose ts runs backwards; a completion that "
            "produces one cannot be pushed by any governed route",
        )


if __name__ == "__main__":
    unittest.main()
