"""Tests for the Stage-2 dispatch channel (GHI #845).

Derived from the GHI's semantics: an undispatched Stage 2 must be VISIBLE in an
artifact, credit must come only from a recorded dispatch, and the gate must stay
compliable so it is obeyed rather than worked around.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit import obpi_dispatch_channel as chan


def _plans(stage: str | None = "implement", **marker_extra: object) -> tuple[Path, str]:
    root = Path(tempfile.mkdtemp(prefix="gzkit-dispatch-"))
    plans = root / ".claude" / "plans"
    plans.mkdir(parents=True)
    obpi_id = "OBPI-0.12.0-04"
    payload: dict[str, object] = {"obpi_id": obpi_id}
    if stage is not None:
        payload["current_stage"] = stage
    payload.update(marker_extra)
    (plans / f".pipeline-active-{obpi_id}.json").write_text(json.dumps(payload), encoding="utf-8")
    return plans, obpi_id


class TestChannelIsNeverInferred(unittest.TestCase):
    """Credit comes from a recorded dispatch, never from the presence of work."""

    def test_empty_state_reports_the_full_mandated_roster_as_not_dispatched(self) -> None:
        """Silence is the defect, so the roster is emitted even when nothing ran.

        Defaulting to an empty table would make an undispatched Stage 2 look
        identical to a ceremony that has no dispatch mandate.
        """
        plans, obpi_id = _plans()
        channel = chan.dispatch_channel(plans, obpi_id)
        self.assertEqual(len(channel), len(chan.MANDATED_STAGE2_ROLES))
        for entry in channel:
            self.assertEqual(entry.disposition, chan.DispatchDisposition.NOT_DISPATCHED)

    def test_a_recorded_dispatch_is_credited(self) -> None:
        plans, obpi_id = _plans()
        chan.record_dispatch(plans, obpi_id, role="Implementer", model="sonnet", task_id=1)
        by_role = {e.role: e for e in chan.dispatch_channel(plans, obpi_id)}
        self.assertEqual(by_role["Implementer"].disposition, chan.DispatchDisposition.DISPATCHED)
        self.assertEqual(
            by_role["QualityReviewer"].disposition, chan.DispatchDisposition.NOT_DISPATCHED
        )

    def test_partial_dispatch_is_still_single_driver(self) -> None:
        """Crediting one persona would launder the reviewers that never ran.

        The two reviewers exist to catch what the implementer cannot see in its
        own work; a run missing them is not a reviewed run.
        """
        plans, obpi_id = _plans()
        chan.record_dispatch(plans, obpi_id, role="Implementer", model="sonnet", task_id=1)
        self.assertTrue(chan.is_single_driver(chan.dispatch_channel(plans, obpi_id)))

    def test_full_roster_is_not_single_driver(self) -> None:
        plans, obpi_id = _plans()
        for i, role in enumerate(chan.MANDATED_STAGE2_ROLES, start=1):
            chan.record_dispatch(plans, obpi_id, role=role, model="sonnet", task_id=i)
        self.assertFalse(chan.is_single_driver(chan.dispatch_channel(plans, obpi_id)))


class TestTheWriterIsReachable(unittest.TestCase):
    """The recording path must be callable, or the channel is a permanent negative.

    GHI #845 (corrected): `persist_dispatch_state` writes `marker["dispatch_state"]`
    correctly and had zero production callers. A channel with no way to report
    DISPATCHED is noise the operator learns to ignore.
    """

    def test_record_dispatch_persists_into_the_marker(self) -> None:
        plans, obpi_id = _plans()
        chan.record_dispatch(plans, obpi_id, role="Implementer", model="sonnet", task_id=1)
        marker = json.loads(
            (plans / f".pipeline-active-{obpi_id}.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(marker["dispatch_state"]), 1)
        self.assertEqual(marker["dispatch_state"][0]["role"], "Implementer")

    def test_recording_is_additive_not_replacing(self) -> None:
        plans, obpi_id = _plans()
        chan.record_dispatch(plans, obpi_id, role="Implementer", model="sonnet", task_id=1)
        chan.record_dispatch(plans, obpi_id, role="SpecReviewer", model="opus", task_id=2)
        marker = json.loads(
            (plans / f".pipeline-active-{obpi_id}.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(marker["dispatch_state"]), 2)


class TestDegradedModeKeepsTheGateCompliable(unittest.TestCase):
    """A gate with no compliant path for a dispatch-less session gets worked around.

    GHI #770 recorded exactly this: a session whose standing instruction forbade
    subagents had no way to comply and no way to declare that it had not.
    """

    def test_declaring_single_driver_is_recorded_and_visible(self) -> None:
        plans, obpi_id = _plans()
        chan.declare_single_driver(plans, obpi_id, reason="harness forbids subagents")
        self.assertTrue(chan.single_driver_declaration(plans, obpi_id))
        rendered = chan.render_dispatch_channel(
            chan.dispatch_channel(plans, obpi_id),
            declaration=chan.single_driver_declaration(plans, obpi_id),
        )
        self.assertIn("SINGLE-DRIVER DECLARED", rendered)
        self.assertIn("harness forbids subagents", rendered)

    def test_undeclared_and_undispatched_renders_the_bare_verdict(self) -> None:
        plans, obpi_id = _plans()
        rendered = chan.render_dispatch_channel(chan.dispatch_channel(plans, obpi_id))
        self.assertIn("SINGLE-DRIVER", rendered)
        self.assertIn("NOT DISPATCHED", rendered)
        self.assertNotIn("SINGLE-DRIVER DECLARED", rendered)


class TestPrecompleteSurfacesTheChannel(unittest.TestCase):
    """Stage 5 is the operator's decision point, so the channel must appear there."""

    def _check(self, plans: Path, obpi_id: str) -> object:
        from gzkit.commands.obpi_precomplete import _check_stage2_dispatch

        return _check_stage2_dispatch(plans.parent.parent, obpi_id)

    def test_blocks_when_pipeline_ran_with_no_dispatch_and_no_declaration(self) -> None:
        """The OBPI-0.35.0-09 condition: marker present, Stage 2 run inline."""
        plans, obpi_id = _plans("verify")
        result = self._check(plans, obpi_id)
        self.assertFalse(result.ok)
        self.assertIn("NOT DISPATCHED", result.message)
        self.assertIsNotNone(result.remediation)

    def test_passes_when_the_full_roster_was_dispatched(self) -> None:
        plans, obpi_id = _plans("verify")
        for i, role in enumerate(chan.MANDATED_STAGE2_ROLES, start=1):
            chan.record_dispatch(plans, obpi_id, role=role, model="sonnet", task_id=i)
        self.assertTrue(self._check(plans, obpi_id).ok)

    def test_passes_but_discloses_when_single_driver_is_declared(self) -> None:
        """Declared is permitted; silent is not. That is the whole distinction."""
        plans, obpi_id = _plans("verify")
        chan.declare_single_driver(plans, obpi_id, reason="cron run, no Agent tool")
        result = self._check(plans, obpi_id)
        self.assertTrue(result.ok)
        self.assertIn("SINGLE-DRIVER DECLARED", result.message)

    def test_reports_absence_rather_than_passing_silently_with_no_marker(self) -> None:
        """No marker is a different gate's business, but it must still be SAID.

        Reporting nothing here would make 'no pipeline ran' and 'the pipeline
        dispatched correctly' render identically, which is the byte-indistinguishable
        failure this whole channel exists to end.
        """
        root = Path(tempfile.mkdtemp(prefix="gzkit-dispatch-"))
        (root / ".claude" / "plans").mkdir(parents=True)
        from gzkit.commands.obpi_precomplete import _check_stage2_dispatch

        result = _check_stage2_dispatch(root, "OBPI-0.12.0-04")
        self.assertIn("no active pipeline marker", result.message)


if __name__ == "__main__":
    unittest.main()
