"""BEHAVIOR REQs cannot be accepted-uncovered at the completion layer (GHI #537).

Assertions derive from ADR-0.0.59's closed proof-channel mapping — BEHAVIOR's only
proof channel is a `@covers`-decorated test — not from a run of the implementation.

The layer this closes: `.gzkit/rules/tests.md` § REQ Scope Discipline *declared* the
mapping, `gz validate --req-kind-discipline` enforced it at brief-authoring time, and
nothing enforced it at completion time. A brief could tag a REQ `[behavior]` and then
close it through the SUPPORT-shaped `--accept-uncovered` channel.

Note the asymmetry this test suite pins: because `_enforce_req_coverage_gate` already
filters SUPPORT and STRUCTURAL-FENCE REQs out *before* collecting gaps, the only REQs
that can ever reach the waiver path are BEHAVIOR ones. Refusing them is therefore a
refusal of every REQ the path can see.
"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from gzkit.commands.obpi_complete import _apply_uncovered_waivers


def _waive(**overrides: object):
    kwargs: dict[str, object] = {
        "gaps": ["REQ-1.2.3-01-01"],
        "accept_uncovered": ["REQ-1.2.3-01-01"],
        "accept_uncovered_reason": ["documentation-only; no test surface"],
        "req_kinds": {"REQ-1.2.3-01-01": "BEHAVIOR"},
        "fail_closed": True,
        "obpi_id": "OBPI-1.2.3-01",
        "parent_adr": "ADR-1.2.3",
        "attestor": "g0",
        "attestor_present": True,
        "project_root": Path("."),
        "as_json": False,
        "ledger": None,
    }
    kwargs.update(overrides)
    return _apply_uncovered_waivers(**kwargs)


class TestBehaviorReqCannotBeWaived(unittest.TestCase):
    def test_tagged_behavior_req_is_refused(self) -> None:
        """BEHAVIOR's only proof channel is a @covers test; a reason cannot substitute."""
        with self.assertRaises(SystemExit) as ctx, redirect_stdout(io.StringIO()):
            _waive()
        self.assertEqual(ctx.exception.code, 3)

    def test_untagged_req_defaults_to_behavior_and_is_refused(self) -> None:
        """Omitting the [kind] tag must not become the bypass that unlocks the waiver."""
        with self.assertRaises(SystemExit) as ctx, redirect_stdout(io.StringIO()):
            _waive(req_kinds={})
        self.assertEqual(ctx.exception.code, 3)

    def test_refusal_names_the_req_the_kind_and_the_proof_channel(self) -> None:
        """Guardrail prose: what failed, why it is forbidden, the governed next step."""
        buffer = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stdout(buffer), redirect_stderr(buffer):
            _waive()
        message = buffer.getvalue()
        self.assertIn("REQ-1.2.3-01-01", message)
        self.assertIn("BEHAVIOR", message)
        self.assertIn("@covers", message)

    def test_refusal_fires_on_the_lite_lane_too(self) -> None:
        """The prohibition is a proof-channel rule, not a lane policy.

        The lite lane's coverage gate is warn-only, but an operator who explicitly asks
        to waive a BEHAVIOR REQ is asking for the forbidden thing on any lane.
        """
        with self.assertRaises(SystemExit) as ctx, redirect_stdout(io.StringIO()):
            _waive(fail_closed=False)
        self.assertEqual(ctx.exception.code, 3)

    def test_no_ledger_event_is_emitted_when_the_waiver_is_refused(self) -> None:
        """A refused waiver must leave no `obpi_completion_uncovered_accept` trace."""
        ledger = mock.MagicMock()
        with self.assertRaises(SystemExit), redirect_stdout(io.StringIO()):
            _waive(ledger=ledger)
        ledger.append.assert_not_called()


class TestNonWaiverPathsAreUnchanged(unittest.TestCase):
    """The refusal must not fire when no BEHAVIOR REQ is actually being waived."""

    def test_accepting_a_req_that_is_not_a_gap_is_a_no_op(self) -> None:
        """Naming a REQ that already has a covering test waives nothing."""
        remaining = _waive(gaps=[], accept_uncovered=["REQ-1.2.3-01-01"])
        self.assertEqual(remaining, [])

    def test_gaps_pass_through_untouched_when_nothing_is_accepted(self) -> None:
        remaining = _waive(gaps=["REQ-1.2.3-01-01"], accept_uncovered=[])
        self.assertEqual(remaining, ["REQ-1.2.3-01-01"])

    def test_a_support_req_reaching_the_path_is_still_waivable(self) -> None:
        """Defensive: if the upstream kind filter ever moves, SUPPORT stays waivable.

        SUPPORT's proof channel is a ledger event plus a structural validator, so an
        uncovered SUPPORT REQ is not an unproven claim. This cannot be reached today —
        `_enforce_req_coverage_gate` filters it out first — and the assertion exists so
        that a future refactor which surfaces it does not silently refuse it.
        """
        ledger = mock.MagicMock()
        remaining = _waive(
            req_kinds={"REQ-1.2.3-01-01": "SUPPORT"},
            ledger=ledger,
            fail_closed=False,
        )
        self.assertEqual(remaining, [])
        ledger.append.assert_called_once()


if __name__ == "__main__":
    unittest.main()
