"""`gz check` scope membership is declared in config, not hard-coded (GHI #950).

The roster of steps a scope drops lived as a module-level frozenset, which made
"what does the push gate actually run" a code question. These tests pin the
three properties that make the declaration trustworthy: it is READ rather than
restated, its polarity is conservative (unknown scope drops nothing), and a
partial scope can never record the fingerprint the pre-push gate reuses.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.commands.quality import (
    _build_check_steps,
    _scope_records_verified,
    _scope_skips,
    _select_check_steps,
)
from gzkit.traceability import covers

_CONFIG = Path(__file__).resolve().parents[2] / "data" / "check_step_scopes.json"


class TestScopeDeclarationIsRead(unittest.TestCase):
    """The runner reads the declaration; it does not restate it."""

    @covers("REQ-0.0.68-01-01")
    def test_prepush_scope_drops_exactly_what_the_config_declares(self) -> None:
        scopes = json.loads(_CONFIG.read_text(encoding="utf-8"))["scopes"]
        declared = set(scopes["prepush"]["skips"])
        self.assertEqual(
            _scope_skips("prepush"),
            declared,
            "the runner must read the declaration, not carry a second copy of it",
        )

    @covers("REQ-0.0.68-01-01")
    def test_behave_is_absent_from_the_prepush_sweep_and_present_in_the_full_one(self) -> None:
        """The change this config exists to make, asserted on the step list itself."""
        full = [name for name, _ in _select_check_steps(fast=False)]
        prepush = [name for name, _ in _select_check_steps(fast=False, prepush=True)]
        self.assertIn("Behave", full, "the full sweep still owes a BDD run")
        self.assertNotIn("Behave", prepush, "the push gate must not pay Behave; CI runs it")
        self.assertIn("Test", prepush, "dropping Behave must not gut the gate")
        self.assertEqual(len(full) - len(prepush), 1, "prepush drops Behave and nothing else")


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
            len(_select_check_steps(fast=False)),
            len(_build_check_steps()),
            "the unnamed full scope drops nothing",
        )


class TestPartialScopesCannotRecordVerification(unittest.TestCase):
    """A scope that drops a step must never satisfy the pre-push reuse cache.

    `record_verified` admits only `scope="full"` because a partial verification
    that can satisfy a gate is the presence-check failure `AGENTS.md` names. That
    guard is only as good as the caller's honesty about its own scope, so the
    declaration carries the claim and this test pins it.
    """

    @covers("REQ-0.0.68-01-01")
    def test_every_scope_that_skips_a_step_declares_it_does_not_record(self) -> None:
        scopes = json.loads(_CONFIG.read_text(encoding="utf-8"))["scopes"]
        for name, entry in scopes.items():
            with self.subTest(scope=name):
                if entry["skips"]:
                    self.assertFalse(
                        entry["records_verified"],
                        f"scope {name!r} drops {entry['skips']} yet claims it may record a "
                        "full-scope pass; that fingerprint would let a partial run satisfy "
                        "the push gate",
                    )
                    self.assertFalse(_scope_records_verified(name))

    @covers("REQ-0.0.68-01-01")
    def test_the_full_scope_records(self) -> None:
        self.assertTrue(
            _scope_records_verified("full"),
            "the full sweep is the only thing that may record a verified fingerprint",
        )


if __name__ == "__main__":
    unittest.main()
