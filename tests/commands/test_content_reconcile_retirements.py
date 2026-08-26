"""gz content reconcile-retirements tests — Layer-2 repair for orphaned tombstones.

GHI #885 arm 2 (hand-appended tombstones), GHI #878 option (a) (partial writes).

These tests pin the semantics that make the repair honest: the verb records that
a tombstone was FOUND unwitnessed, and never that the governed retirement ran.
``test_repair_does_not_emit_a_governed_retirement_event`` is the load-bearing
one — emitting ``corpus_entry_retired`` here would be a fabricated receipt under
``AGENTS.md`` § Attestation, and it would also satisfy the witness gate, so
nothing downstream would catch the substitution.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.content.corpus_store import append_entry
from gzkit.content.models.corpus import CorpusEntry
from gzkit.governance.trust_audits import validate_corpus_retirement_witness
from tests.commands.common import CliRunner

_LEDGER = Path(".gzkit") / "ledger.jsonl"


def _entry(entry_id: str, *, retires: str | None = None, origin: str = "test") -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="attestation",
        tier="invariant",
        classification="Judgment",
        text=f"doctrine text for {entry_id}",
        origin=origin,
        ts="2026-01-01T00:00:00+00:00",
        retires=retires,
    )


def _events() -> list[dict]:
    if not _LEDGER.exists():
        return []
    return [json.loads(line) for line in _LEDGER.read_text(encoding="utf-8").splitlines() if line]


class TestReconcileRetirements(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    def _seed_orphan(self, name: str = "a", origin: str = "GHI #862; hand-appended") -> None:
        """Seed one live entry plus a hand-written tombstone with no ledger witness."""
        root = Path()
        append_entry(root, "AGENTS.md", _entry(f"corpus-{name}"))
        append_entry(
            root,
            "AGENTS.md",
            _entry(f"corpus-tomb-{name}", retires=f"corpus-{name}", origin=origin),
        )

    def test_reconciling_clears_the_witness_gate(self) -> None:
        """After repair the detection gate reports the surface clean."""
        with self._runner.isolated_filesystem():
            self._seed_orphan()
            self.assertEqual(len(validate_corpus_retirement_witness(Path())), 1)

            self._runner.invoke(main, ["content", "reconcile-retirements", "AGENTS.md"])

            self.assertEqual(validate_corpus_retirement_witness(Path()), [])

    def test_repair_does_not_emit_a_governed_retirement_event(self) -> None:
        """The repair must NOT claim `gz content retire` ran (AGENTS.md § Attestation).

        A backfilled `corpus_entry_retired` would clear the same gate while
        retroactively witnessing a procedure nobody performed. The distinction
        between the two event types is the only thing that lets a later auditor
        tell a governed retirement from a reconciled one.
        """
        with self._runner.isolated_filesystem():
            self._seed_orphan()

            self._runner.invoke(main, ["content", "reconcile-retirements", "AGENTS.md"])

            kinds = [e.get("event") for e in _events()]
            self.assertIn("corpus_retirement_reconciled", kinds)
            self.assertNotIn(
                "corpus_entry_retired",
                kinds,
                "reconciliation must never emit the governed-retirement type — that "
                "is a fabricated receipt for a procedure that never ran",
            )

    def test_event_names_the_retired_subject_and_keeps_the_forensic_origin(self) -> None:
        """The event binds to the retired id and preserves the row's origin prose."""
        with self._runner.isolated_filesystem():
            self._seed_orphan(origin="GHI #862; operator ruling 2026-08-22")

            self._runner.invoke(main, ["content", "reconcile-retirements", "AGENTS.md"])

            [event] = [e for e in _events() if e.get("event") == "corpus_retirement_reconciled"]
            self.assertEqual(event["retired_entry_id"], "corpus-a")
            self.assertEqual(event["retraction_entry_id"], "corpus-tomb-a")
            self.assertEqual(event["surface"], "AGENTS.md")
            self.assertEqual(
                event["origin"],
                "GHI #862; operator ruling 2026-08-22",
                "the row's origin is the only surviving forensic difference between a "
                "governed and a hand-written tombstone; the repair must carry it forward",
            )

    def test_is_idempotent(self) -> None:
        """A second run over a reconciled surface writes nothing."""
        with self._runner.isolated_filesystem():
            self._seed_orphan()
            self._runner.invoke(main, ["content", "reconcile-retirements", "AGENTS.md"])
            after_first = len(_events())

            self._runner.invoke(main, ["content", "reconcile-retirements", "AGENTS.md"])

            self.assertEqual(len(_events()), after_first)

    def test_dry_run_writes_nothing(self) -> None:
        """--dry-run reports the work and leaves Layer 2 untouched."""
        with self._runner.isolated_filesystem():
            self._seed_orphan()

            result = self._runner.invoke(
                main, ["content", "reconcile-retirements", "AGENTS.md", "--dry-run"]
            )

            self.assertIn("corpus-a", result.output)
            self.assertEqual(_events(), [])
            self.assertEqual(len(validate_corpus_retirement_witness(Path())), 1)

    def test_each_orphan_gets_its_own_event(self) -> None:
        """Repair is per-subject, so a partially-witnessed surface converges."""
        with self._runner.isolated_filesystem():
            for name in ("a", "b", "c"):
                self._seed_orphan(name)

            self._runner.invoke(main, ["content", "reconcile-retirements", "AGENTS.md"])

            reconciled = [e for e in _events() if e.get("event") == "corpus_retirement_reconciled"]
            self.assertEqual(
                {e["retired_entry_id"] for e in reconciled},
                {"corpus-a", "corpus-b", "corpus-c"},
            )

    def test_unknown_surface_exits_nonzero(self) -> None:
        """A surface with no corpus store is a user error, not a silent no-op."""
        with self._runner.isolated_filesystem():
            result = self._runner.invoke(main, ["content", "reconcile-retirements", "NOPE.md"])

            self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
