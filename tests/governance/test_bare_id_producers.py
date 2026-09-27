"""Producers record an artifact's slug id, never the bare id typed (GHI #1118).

An ADR or OBPI's canonical id is its on-disk slug (``ADR-0.35.0-canon-...``).
Events booked under the bare form (``ADR-0.35.0``) were orphaned from the
artifact until an operator ran ``gz migrate-semver``: 87 rows under 21 bare ids
from ``gz adr evaluate``, the OBPI lock verbs and the airlock. A lock keyed by
the bare id also let a second agent claim the same brief under its slug.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.airlock.enter import airlock_enter
from gzkit.airlock.exit import airlock_exit
from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.governance.trust_audits.evaluation_justify_binding import (
    validate_evaluation_justify_binding,
)
from gzkit.ledger import Ledger, slug_id_for
from gzkit.ledger_events import adr_evaluation_event, artifact_renamed_event
from tests.commands.common import CliRunner, _quick_init

_OBPI_SLUG = "OBPI-0.1.0-01-thing"
_OBPI_BARE = "OBPI-0.1.0-01"
_BRIEF = """\
---
id: OBPI-0.1.0-01-thing
parent: ADR-0.1.0-thing
item: 1
lane: Lite
status: Draft
---

# OBPI-0.1.0-01-thing: Thing

## Allowed Paths

- `src/gzkit/thing.py`
"""
_ADR_SLUG = "ADR-0.1.0-thing"
_ADR = """\
---
id: ADR-0.1.0-thing
status: Proposed
semver: 0.1.0
lane: lite
kind: feature
---

# ADR-0.1.0-thing: Thing

## Intent

Do the thing.
"""


class SlugIdForTests(unittest.TestCase):
    """The helper maps a bare id to the resolved file's slug, and nothing else."""

    def test_bare_obpi_and_adr_ids_take_the_slug(self) -> None:
        self.assertEqual(slug_id_for(_OBPI_BARE, _OBPI_SLUG), _OBPI_SLUG)
        self.assertEqual(slug_id_for("ADR-0.1.0", _ADR_SLUG), _ADR_SLUG)

    def test_an_id_that_is_already_the_slug_is_kept(self) -> None:
        self.assertEqual(slug_id_for(_OBPI_SLUG, _OBPI_SLUG), _OBPI_SLUG)

    def test_a_stem_of_a_different_artifact_is_ignored(self) -> None:
        """A prefix-glob hit on ADR-0.1.1x must not rename ADR-0.1.1."""
        self.assertEqual(slug_id_for("ADR-0.1.1", "ADR-0.1.10-other"), "ADR-0.1.1")
        self.assertEqual(slug_id_for("OBPI-0.1.0-01", "OBPI-0.1.0-02-other"), "OBPI-0.1.0-01")

    def test_non_artifact_ids_and_synthetic_stems_pass_through(self) -> None:
        self.assertEqual(slug_id_for("recon-target", "brief"), "recon-target")
        self.assertEqual(slug_id_for(_OBPI_BARE, "brief"), _OBPI_BARE)


class AirlockProducerTests(unittest.TestCase):
    """``airlock_in`` / ``airlock_out`` book the brief's slug for a bare target."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.brief = root / f"{_OBPI_SLUG}.md"
        self.brief.write_text(_BRIEF, encoding="utf-8")
        self.ledger = Ledger(root / "ledger.jsonl")

    def _ids(self, event: str) -> list[str]:
        return [e.id for e in self.ledger.read_all() if e.event == event]

    def test_airlock_in_books_the_slug(self) -> None:
        airlock_enter(_OBPI_BARE, self.brief, reach_fn=lambda _n: [], ledger=self.ledger)
        self.assertEqual(self._ids("airlock_in"), [_OBPI_SLUG])

    def test_airlock_out_books_the_slug(self) -> None:
        airlock_exit(_OBPI_BARE, self.brief, reach_fn=lambda _n: [], ledger=self.ledger)
        self.assertEqual(self._ids("airlock_out"), [_OBPI_SLUG])

    def test_aborted_airlock_out_books_the_slug(self) -> None:
        def _boom(_node: str) -> list[str]:
            raise RuntimeError("reach failed")

        with self.assertRaises(RuntimeError):
            airlock_exit(_OBPI_BARE, self.brief, reach_fn=_boom, ledger=self.ledger)
        self.assertEqual(self._ids("airlock_out"), [_OBPI_SLUG])


class CliProducerTests(unittest.TestCase):
    """``gz obpi lock`` and ``gz adr evaluate`` record the slug for a bare id."""

    def _seed(self) -> Ledger:
        _quick_init()
        adrs = Path(GzkitConfig.load(Path(".gzkit.json")).paths.adrs)
        package = adrs / "pre-release" / _ADR_SLUG
        (package / "obpis").mkdir(parents=True, exist_ok=True)
        (package / f"{_ADR_SLUG}.md").write_text(_ADR, encoding="utf-8")
        (package / "obpis" / f"{_OBPI_SLUG}.md").write_text(_BRIEF, encoding="utf-8")
        return Ledger(Path(".gzkit/ledger.jsonl"))

    def test_lock_claim_and_release_use_the_slug(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            ledger = self._seed()
            claim = runner.invoke(main, ["obpi", "lock", "claim", _OBPI_BARE, "--agent", "a1"])
            self.assertEqual(claim.exit_code, 0, claim.output)
            # A second agent claiming by slug meets the same lock, not a fresh one.
            rival = runner.invoke(main, ["obpi", "lock", "claim", _OBPI_SLUG, "--agent", "a2"])
            self.assertNotEqual(rival.exit_code, 0, rival.output)
            release = runner.invoke(
                main,
                ["obpi", "lock", "release", _OBPI_BARE, "--agent", "a1"]
                + ["--abandon", "tool_failure:test fixture"],
            )
            self.assertEqual(release.exit_code, 0, release.output)
            ids = {e.event: e.id for e in ledger.read_all() if e.event.startswith("obpi_lock_")}
            self.assertEqual(ids.get("obpi_lock_claimed"), _OBPI_SLUG)
            self.assertEqual(ids.get("obpi_lock_released"), _OBPI_SLUG)

    def test_adr_evaluate_records_the_slug(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            ledger = self._seed()
            runner.invoke(main, ["adr", "evaluate", "ADR-0.1.0"])
            evaluation = {"adr-evaluation", "adr_eval_completed"}
            ids = {e.id for e in ledger.read_all() if e.event in evaluation}
            self.assertEqual(ids, {_ADR_SLUG})


class RenamedEvaluationReaderTests(unittest.TestCase):
    """The justify-binding gate sees an evaluation booked under a renamed bare id.

    It matched ``adr-evaluation`` rows by raw id, so a low score recorded under
    ``ADR-0.1.0`` was invisible to a check of ``ADR-0.1.0-thing`` even after the
    ledger renamed one to the other: the gate found no evaluation and passed.
    """

    _REPO = Path(__file__).resolve().parents[2]

    def _gate(self, evaluated_id: str, renames: bool) -> list:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            ledger.append(
                adr_evaluation_event(
                    artifact_id=evaluated_id,
                    artifact_type="ADR",
                    dimensions={"intent": 1.0},
                    scores={"intent": 0.1},
                    weighted_total=1.0,
                    red_team_challenges_fired=[],
                    evaluator_persona="gz-adr-evaluate",
                    timestamp="2026-09-27T00:00:00+00:00",
                )
            )
            if renames:
                ledger.append(artifact_renamed_event("ADR-0.1.0", _ADR_SLUG, "fixture"))
            return validate_evaluation_justify_binding(
                _ADR_SLUG, self._REPO, ledger_path=Path(tmp) / "ledger.jsonl"
            )

    def test_low_score_under_the_renamed_bare_id_fires_the_gate(self) -> None:
        self.assertEqual(len(self._gate("ADR-0.1.0", renames=True)), 1)

    def test_an_evaluation_of_another_adr_does_not(self) -> None:
        """Control: the rename map widens identity to one artifact, not to all."""
        self.assertEqual(self._gate("ADR-0.1.1", renames=True), [])


if __name__ == "__main__":
    unittest.main()
