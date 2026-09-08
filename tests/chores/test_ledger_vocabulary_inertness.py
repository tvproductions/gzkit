"""The never-fired disclosure is a shrink-ratchet, and the code must say so (GHI #611).

ADR-0.0.73 Boundary Invariant #8 registers `data/ledger_vocabulary_grandfather.json`
as a **monotonic shrink-ratchet** — verbatim, *"a committed baseline the list can
only decrease against"*. The gate's recovery prose then told the reader to
*"RAISE the baseline only when the honest current set is genuinely larger"*, in
the same sentence as the warning that a raise is the laundering the ratchet
refuses. Prose that authorizes the act its own citation forbids is worse than
silence: it hands an agent a sanctioned-looking route to clear its own gate.

The prose is corrected, but prose is not the fence. These tests assert the
BEHAVIOR the invariant names — the re-baseline path refuses to grow, and drains
only downward — because a test that greps the message for the absence of a word
proves the wording and not the ratchet (`.gzkit/rules/tests.md` § The
discriminator).

Two checks deliberately live elsewhere rather than here:

* that the corrected wording stays corrected has **no** unit test, because a
  substring assertion over a production message is the exact shape the
  discriminator routes away — `gz validate --tautological-tests` flagged the
  attempt, correctly;
* that the packaged chore and its `.gzkit` mirror stay byte-identical is already
  `gz validate --distribution`, which walks `src/gzkit/chores` (GHI #783). A
  second, weaker copy here would be the per-consumer duplication this codebase
  keeps paying for.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = (
    _REPO_ROOT
    / "src"
    / "gzkit"
    / "chores"
    / "ledger-vocabulary-inertness"
    / "check_ledger_inertness.py"
)


def _load(script: Path = _SCRIPT) -> Any:
    """Import the chore script by path — its directory is not an importable package."""
    spec = importlib.util.spec_from_file_location("_check_ledger_inertness", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TheBaselineOnlyEverDecreases(unittest.TestCase):
    """`--report --write` re-baselines DOWNWARD or refuses; it never absorbs growth."""

    def setUp(self) -> None:
        self.chore = _load()

    def _root(self, *, declared: list[str], fired: list[str], baseline: list[str]) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / "pyproject.toml").write_text("", encoding="utf-8")
        schema = root / "src" / "gzkit" / "schemas" / "ledger.json"
        schema.parent.mkdir(parents=True, exist_ok=True)
        schema.write_text(
            json.dumps({"events": {name: {"required": [], "properties": {}} for name in declared}}),
            encoding="utf-8",
        )
        ledger = root / ".gzkit" / "ledger.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(
            "".join(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": name,
                        "id": "x",
                        "ts": "2026-01-01T00:00:00+00:00",
                    }
                )
                + "\n"
                for name in fired
            ),
            encoding="utf-8",
        )
        target = root / self.chore._BASELINE_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps({"schema_version": 1, "rationale": "test", "never_fired": baseline}) + "\n",
            encoding="utf-8",
        )
        return root

    def _baseline(self, root: Path) -> list[str]:
        payload = json.loads((root / self.chore._BASELINE_REL).read_text(encoding="utf-8"))
        return payload["never_fired"]

    def test_a_drained_type_shrinks_the_baseline(self) -> None:
        """The one sanctioned direction: a producer appeared, so the list falls."""
        root = self._root(declared=["a", "b"], fired=["a"], baseline=["a", "b"])
        self.assertEqual(self.chore.report(root, write=True), 0)
        self.assertEqual(self._baseline(root), ["b"])

    def test_a_grown_never_fired_set_refuses_to_re_baseline(self) -> None:
        """A re-run must never absorb a newly undisclosed type into the baseline."""
        root = self._root(declared=["a", "b", "c"], fired=[], baseline=["a", "b"])
        self.assertEqual(self.chore.report(root, write=True), 3)
        self.assertEqual(
            self._baseline(root),
            ["a", "b"],
            "the re-baseline path absorbed a grown never-fired set; the ratchet is "
            "shrink-only (ADR-0.0.73 BI #8)",
        )

    def test_an_undisclosed_type_fails_the_gate_closed(self) -> None:
        root = self._root(declared=["a", "b", "c"], fired=[], baseline=["a", "b"])
        self.assertEqual(self.chore.enforce(root), 3)

    def test_a_fully_disclosed_set_passes(self) -> None:
        """Guard: the gate must be satisfiable, or the refusals prove nothing."""
        root = self._root(declared=["a", "b"], fired=[], baseline=["a", "b"])
        self.assertEqual(self.chore.enforce(root), 0)

    def test_real_isolated_producer_satisfies_gate_without_changing_live_counts(self) -> None:
        self.chore = _load(
            _REPO_ROOT / ".gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py"
        )
        root = self._root(declared=["acceptance_recorded"], fired=[], baseline=[])
        ledger = root / ".gzkit/ledger.jsonl"
        before = ledger.read_bytes()
        self.assertEqual(self.chore.enforce(root), 0)
        self.assertEqual(ledger.read_bytes(), before)
        self.assertEqual(self.chore.never_fired(root), ["acceptance_recorded"])
        self.assertEqual(self._baseline(root), [])
        self.assertEqual(self.chore.report(root, write=True), 3)
        self.assertEqual(self._baseline(root), [])

    def test_current_failed_execution_blocks_despite_previous_report(self) -> None:
        self.chore = _load(
            _REPO_ROOT / ".gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py"
        )
        root = self._root(declared=["acceptance_recorded"], fired=[], baseline=[])
        ledger = root / ".gzkit/ledger.jsonl"
        before = ledger.read_bytes()
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(self.chore.enforce(root), 0)
        (root / "previous-producer-report.json").write_text(output.getvalue(), encoding="utf-8")
        with patch("gzkit.acceptance_store.initialize", return_value=None):
            self.assertEqual(self.chore.enforce(root), 3)
        self.assertEqual(ledger.read_bytes(), before)
        self.assertEqual(self._baseline(root), [])

    def test_live_or_disclosed_types_do_not_trigger_isolated_execution(self) -> None:
        self.chore = _load(
            _REPO_ROOT / ".gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py"
        )
        for fired, baseline in ((["acceptance_recorded"], []), ([], ["acceptance_recorded"])):
            with self.subTest(fired=fired, baseline=baseline):
                root = self._root(declared=["acceptance_recorded"], fired=fired, baseline=baseline)
                with patch("gzkit.acceptance_store.initialize") as producer:
                    self.assertEqual(self.chore.enforce(root), 0)
                producer.assert_not_called()

    def test_verified_producer_cannot_cover_another_undisclosed_event(self) -> None:
        self.chore = _load(
            _REPO_ROOT / ".gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py"
        )
        root = self._root(
            declared=["acceptance_recorded", "unregistered_event"], fired=[], baseline=[]
        )
        self.assertEqual(self.chore.enforce(root), 3)
        self.assertEqual(self.chore.fired_events(root), {})
        self.assertEqual(self._baseline(root), [])


if __name__ == "__main__":
    unittest.main()
