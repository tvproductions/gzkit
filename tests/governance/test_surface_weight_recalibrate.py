"""Tests for the surface-weight recalibration emitter (GHI #791).

ADR-0.0.33 § Anti-patterns item 3 declares band changes to be ledger events,
not config tweaks, and OBPI-0.0.33-02 REQ 4 declares that a recalibration MUST
update ``data/surface_weight_floor.json`` AND emit a
``surface_weight_recalibrated`` event. No verb could emit that event: the
prescribed ``gz adr emit-receipt --event`` is a closed enum of
``{completed, validated, closed}``, so the ledger carried zero such events and
the bands had already moved once as an unwitnessed config tweak.

These assert the emitter's *behavior*, never the band values themselves — the
band constants are doctrine that recalibrates by design, and a test pinning
them would fail on the next legitimate ruling (``.gzkit/rules/tests.md``
§ The discriminator).

The fail-safe write ORDER is the load-bearing property. The floor snapshot is
written before the event is appended, because the reverse order breaks the gate
it is meant to serve: ``_check_floor_drift`` fails closed once a recalibration
event postdates the floor by >24h, so an appended-event-then-failed-floor-write
leaves a red gate, while a written-floor-then-failed-append leaves a green one.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest import mock

from gzkit.governance.trust_audits.surface_weight import (
    _GREEN_CEILING,
    _YELLOW_CEILING,
    recalibrate_surface_weight,
    validate_surface_weight,
)

_STALE_FLOOR_LINES = 400
_CORPUS_LINES = 900


def _make_tree(tmp: str, *, corpus_lines: int, floor_lines: int, floor_age_hours: int) -> Path:
    """Build a sandbox project root with a deliberately stale floor snapshot."""
    root = Path(tmp)
    body = "\n".join(f"line {i}" for i in range(1, corpus_lines + 1))
    (root / "AGENTS.md").write_text(body, encoding="utf-8")
    (root / "CLAUDE.md").write_text("", encoding="utf-8")
    rules = root / ".claude" / "rules"
    rules.mkdir(parents=True, exist_ok=True)
    (rules / "placeholder.md").write_text("", encoding="utf-8")

    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)
    stale_ts = (datetime.now(tz=UTC) - timedelta(hours=floor_age_hours)).isoformat()
    (data / "surface_weight_floor.json").write_text(
        json.dumps({"lines": floor_lines, "timestamp": stale_ts, "note": "sandbox"}),
        encoding="utf-8",
    )
    (data / "surface_weight_waivers.json").write_text("[]", encoding="utf-8")

    gz = root / ".gzkit"
    gz.mkdir(parents=True, exist_ok=True)
    (gz / "ledger.jsonl").write_text("", encoding="utf-8")
    return root


def _read_floor(root: Path) -> dict:
    return json.loads((root / "data" / "surface_weight_floor.json").read_text(encoding="utf-8"))


def _read_events(root: Path) -> list[dict]:
    raw = (root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


class TestRecalibrationEmitsBothHalves(unittest.TestCase):
    """A recalibration moves the floor AND appends its witnessing event."""

    def test_event_is_appended_to_the_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            recalibrate_surface_weight(root, attestor="g0", reason="band ruling")
            events = _read_events(root)
            self.assertEqual(
                [e["event"] for e in events],
                ["surface_weight_recalibrated"],
                "Recalibration must append exactly one witnessing event",
            )

    def test_floor_snapshot_is_rewritten_to_the_measured_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            recalibrate_surface_weight(root, attestor="g0", reason="band ruling")
            self.assertEqual(
                _read_floor(root)["lines"],
                _CORPUS_LINES,
                "Floor must be re-snapshotted to the corpus actually measured",
            )

    def test_outcome_reports_the_superseded_floor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            outcome = recalibrate_surface_weight(root, attestor="g0", reason="band ruling")
            self.assertEqual(outcome.previous_floor_lines, _STALE_FLOOR_LINES)
            self.assertEqual(outcome.floor_lines, _CORPUS_LINES)


class TestEventWitnessesTheBands(unittest.TestCase):
    """The event records WHICH bands were in force, not merely that a change occurred."""

    def test_event_carries_the_live_band_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            recalibrate_surface_weight(root, attestor="g0", reason="band ruling")
            event = _read_events(root)[0]
            self.assertEqual(event["green_ceiling"], _GREEN_CEILING)
            self.assertEqual(event["yellow_ceiling"], _YELLOW_CEILING)

    def test_event_carries_attestor_and_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            recalibrate_surface_weight(
                root, attestor="g0", reason="raised to 3000/3400 by operator ruling"
            )
            event = _read_events(root)[0]
            self.assertEqual(event["attestor"], "g0")
            self.assertIn("3000/3400", event["reason"])


class TestAttestationIsFailClosed(unittest.TestCase):
    """An unattested recalibration writes nothing at all."""

    def test_empty_attestor_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            with self.assertRaises(ValueError):
                recalibrate_surface_weight(root, attestor="   ", reason="band ruling")

    def test_empty_reason_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            with self.assertRaises(ValueError):
                recalibrate_surface_weight(root, attestor="g0", reason="")

    def test_refusal_mutates_neither_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            with self.assertRaises(ValueError):
                recalibrate_surface_weight(root, attestor="", reason="")
            self.assertEqual(
                _read_floor(root)["lines"],
                _STALE_FLOOR_LINES,
                "A refused recalibration must leave the floor untouched",
            )
            self.assertEqual(
                _read_events(root), [], "A refused recalibration must write no ledger event"
            )


class TestRecalibrationClosesTheDriftCoupling(unittest.TestCase):
    """After recalibrating, the gate the event would otherwise trip reads clean."""

    def test_gate_is_clean_after_recalibration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            recalibrate_surface_weight(root, attestor="g0", reason="band ruling")
            self.assertEqual(
                validate_surface_weight(root),
                [],
                "Recalibration must leave the surface-weight gate green, not merely "
                "append an event that trips floor drift",
            )


class TestFailSafeWriteOrder(unittest.TestCase):
    """The floor is written before the event, so a failed append leaves a green gate."""

    def test_failed_event_append_still_leaves_floor_advanced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp, corpus_lines=_CORPUS_LINES, floor_lines=_STALE_FLOOR_LINES, floor_age_hours=72
            )
            with (
                mock.patch("gzkit.ledger.Ledger.append", side_effect=OSError("disk full")),
                self.assertRaises(OSError),
            ):
                recalibrate_surface_weight(root, attestor="g0", reason="band ruling")

            self.assertEqual(
                _read_floor(root)["lines"],
                _CORPUS_LINES,
                "Floor must be committed before the append is attempted",
            )
            self.assertEqual(
                validate_surface_weight(root),
                [],
                "A failed append must leave the gate green — the reverse write order "
                "would strand a red gate no operator action could clear",
            )
