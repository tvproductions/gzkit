"""`gz check` scope membership is declared in config, not hard-coded (GHI #950).

The roster of steps a scope drops lived as a module-level frozenset, which made
"what does the push gate actually run" a code question. These tests pin the
properties that make the declaration trustworthy: it is READ rather than
restated, its polarity is conservative (unknown scope drops nothing), a scope
narrower than the per-change gate can never record the fingerprint that gate
reuses, and the default scope is the per-change gate — `Behave` is heavy-lane
and CI scope, reached only through `--full` (GHI #1088). Since GHI #1191 the
per-change gate also drops the whole unit tier and runs the tests the change
touches in its place.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.commands.quality import (
    _build_check_steps,
    _load_check_step_scopes,
    _scope_records_verified,
    _scope_skips,
    _select_check_steps,
)
from gzkit.traceability import covers

_CONFIG = Path(__file__).resolve().parents[2] / "data" / "check_step_scopes.json"


class TestScopeDeclarationIsRead(unittest.TestCase):
    """The runner reads the declaration; it does not restate it."""

    @covers("REQ-0.0.68-01-01")
    def test_the_change_scope_drops_exactly_what_the_config_declares(self) -> None:
        scopes = json.loads(_CONFIG.read_text(encoding="utf-8"))["scopes"]
        declared = set(scopes["change"]["skips"])
        self.assertEqual(
            _scope_skips("change"),
            declared,
            "the runner must read the declaration, not carry a second copy of it",
        )

    @covers("REQ-0.0.68-01-01")
    def test_the_change_sweep_is_the_full_one_minus_exactly_the_declared_skips(self) -> None:
        """The change this config exists to make, asserted on the step list itself.

        The count is derived from the declaration rather than written here: a
        hard-coded difference would have to be edited every time a scope entry
        changes, which is the second copy this file exists to remove.
        """
        full = [name for name, _ in _select_check_steps("full")]
        change = [name for name, _ in _select_check_steps("change")]
        declared = _scope_skips("change")

        self.assertEqual(
            set(full) - set(change), set(declared), "change drops exactly the declared steps"
        )
        self.assertEqual(
            set(change) - set(full),
            {"Test (changed)"},
            "the only step the gate adds is the changed-test run that stands in for Test",
        )
        for step in declared:
            self.assertIn(step, full, f"{step} must still run in the full sweep")
        self.assertIn("Lint", change)
        self.assertIn("Typecheck", change)
        self.assertIn("Smoke tier", change)


class TestScopePolarityIsConservative(unittest.TestCase):
    """An unreadable or unknown scope runs MORE, never less."""

    @covers("REQ-0.0.68-01-01")
    def test_an_undeclared_scope_drops_nothing(self) -> None:
        """Absence of policy must not be read as permission to skip.

        The inverse polarity — unknown scope means "skip everything not listed" —
        would turn a typo in a scope name into a silently empty gate.
        """
        self.assertEqual(_scope_skips("no-such-scope"), frozenset())
        self.assertEqual(
            len(_select_check_steps("full")),
            len(_build_check_steps()),
            "the full scope drops nothing",
        )


class TestOnlyScopesCoveringTheGateRecord(unittest.TestCase):
    """A scope narrower than the per-change gate must never satisfy its reuse cache.

    The pre-push gate runs the `change` scope, so a fingerprint may stand in for it
    only when the run that minted it dropped nothing the gate would have run. A
    scope whose skips exceed the gate's is a partial verification, and a partial
    verification that can satisfy a gate is the presence-check failure
    `AGENTS.md` names.
    """

    def test_every_recording_scope_covers_the_per_change_gate(self) -> None:
        gate_skips = _scope_skips("change")
        for name in _load_check_step_scopes():
            with self.subTest(scope=name):
                if _scope_records_verified(name):
                    self.assertLessEqual(
                        _scope_skips(name),
                        gate_skips,
                        f"scope {name!r} records a fingerprint yet drops "
                        f"{_scope_skips(name) - gate_skips}, which the per-change gate runs",
                    )

    def test_a_scope_declared_not_to_record_does_not(self) -> None:
        from unittest import mock  # noqa: PLC0415

        narrow = {"narrow": {"skips": ["Lint"], "records_verified": False}}
        with mock.patch("gzkit.commands.quality._load_check_step_scopes", return_value=narrow):
            self.assertFalse(_scope_records_verified("narrow"))

    def test_the_change_and_full_scopes_record(self) -> None:
        self.assertTrue(_scope_records_verified("change"))
        self.assertTrue(_scope_records_verified("full"))

    def test_without_a_declaration_the_default_still_records(self) -> None:
        """An adopter project ships no scope file, so its default drops nothing.

        A scope that drops nothing ran the full sweep, so refusing to record it
        would silently disable the pre-push reuse in every adopter repository.
        It also keeps the whole unit tier: the changed-test run stands in only
        where `Test` is declared dropped.
        """
        from unittest import mock  # noqa: PLC0415

        with mock.patch("gzkit.commands.quality._load_check_step_scopes", return_value={}):
            self.assertEqual(_scope_skips("change"), frozenset())
            self.assertTrue(_scope_records_verified("change"))
            names = [name for name, _ in _select_check_steps("change")]
            self.assertIn("Test", names)
            self.assertNotIn("Test (changed)", names)


class TestTheDefaultIsThePerChangeGate(unittest.TestCase):
    """Plain `gz check` is the per-change gate; the full tier needs `--full`.

    `Behave` left the gate under GHI #1088. The whole unit tier left it under
    GHI #1191 (operator ruling 2026-10-11): the gate runs the tests the change
    touches, and `--full` runs the tier in CI, at release and as a chore.
    """

    def test_the_change_scope_drops_behave_and_the_whole_unit_tier(self) -> None:
        change = [name for name, _ in _select_check_steps("change")]
        self.assertNotIn("Behave", change)
        self.assertNotIn("Test", change)
        self.assertIn("Test (changed)", change)

    def test_the_full_scope_runs_behave_and_the_whole_unit_tier(self) -> None:
        full = [name for name, _ in _select_check_steps("full")]
        self.assertIn("Behave", full)
        self.assertIn("Test", full)
        self.assertNotIn("Test (changed)", full)

    def test_plain_gz_check_selects_the_change_scope(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        args = _build_parser().parse_args(["check"])
        self.assertFalse(args.full)

    def test_full_flag_selects_the_full_scope(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        self.assertTrue(_build_parser().parse_args(["check", "--full"]).full)

    def test_the_retired_fast_flag_is_a_usage_error(self) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        with self.assertRaises(SystemExit) as raised:
            _build_parser().parse_args(["check", "--fast"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
