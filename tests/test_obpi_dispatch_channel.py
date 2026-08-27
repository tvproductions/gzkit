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
    """Build a project root with an active pipeline marker and an empty ledger.

    Returns the PROJECT ROOT, not the plans dir: since GHI #886 the channel's
    evidence is the Layer-2 ledger, so a fixture that could only produce a marker
    would be unable to express the property under test.
    """
    root = Path(tempfile.mkdtemp(prefix="gzkit-dispatch-"))
    plans = root / ".claude" / "plans"
    plans.mkdir(parents=True)
    (root / ".gzkit").mkdir(parents=True)
    (root / ".gzkit" / "ledger.jsonl").touch()
    obpi_id = "OBPI-0.12.0-04"
    payload: dict[str, object] = {"obpi_id": obpi_id, "parent_adr": "ADR-0.12.0"}
    if stage is not None:
        payload["current_stage"] = stage
    payload.update(marker_extra)
    (plans / f".pipeline-active-{obpi_id}.json").write_text(json.dumps(payload), encoding="utf-8")
    return root, obpi_id


def _marker(root: Path, obpi_id: str) -> Path:
    return root / ".claude" / "plans" / f".pipeline-active-{obpi_id}.json"


class TestChannelIsNeverInferred(unittest.TestCase):
    """Credit comes from a recorded dispatch, never from the presence of work."""

    def test_empty_state_reports_the_full_mandated_roster_as_not_dispatched(self) -> None:
        """Silence is the defect, so the roster is emitted even when nothing ran.

        Defaulting to an empty table would make an undispatched Stage 2 look
        identical to a ceremony that has no dispatch mandate.
        """
        root, obpi_id = _plans()
        channel = chan.dispatch_channel(root, obpi_id)
        self.assertEqual(len(channel), len(chan.MANDATED_STAGE2_ROLES))
        for entry in channel:
            self.assertEqual(entry.disposition, chan.DispatchDisposition.NOT_DISPATCHED)

    def test_a_recorded_dispatch_is_credited(self) -> None:
        root, obpi_id = _plans()
        chan.record_dispatch(root, obpi_id, role="Implementer", model="sonnet", task_id=1)
        by_role = {e.role: e for e in chan.dispatch_channel(root, obpi_id)}
        self.assertEqual(by_role["Implementer"].disposition, chan.DispatchDisposition.DISPATCHED)
        self.assertEqual(
            by_role["QualityReviewer"].disposition, chan.DispatchDisposition.NOT_DISPATCHED
        )

    def test_partial_dispatch_is_still_single_driver(self) -> None:
        """Crediting one persona would launder the reviewers that never ran.

        The two reviewers exist to catch what the implementer cannot see in its
        own work; a run missing them is not a reviewed run.
        """
        root, obpi_id = _plans()
        chan.record_dispatch(root, obpi_id, role="Implementer", model="sonnet", task_id=1)
        self.assertTrue(chan.is_single_driver(chan.dispatch_channel(root, obpi_id)))

    def test_full_roster_is_not_single_driver(self) -> None:
        root, obpi_id = _plans()
        for i, role in enumerate(chan.MANDATED_STAGE2_ROLES, start=1):
            chan.record_dispatch(root, obpi_id, role=role, model="sonnet", task_id=i)
        self.assertFalse(chan.is_single_driver(chan.dispatch_channel(root, obpi_id)))


class TestTheWriterIsReachable(unittest.TestCase):
    """The recording path must be callable, or the channel is a permanent negative.

    GHI #845 (corrected): `persist_dispatch_state` writes `marker["dispatch_state"]`
    correctly and had zero production callers. A channel with no way to report
    DISPATCHED is noise the operator learns to ignore.
    """

    def test_record_dispatch_persists_into_the_marker(self) -> None:
        root, obpi_id = _plans()
        chan.record_dispatch(root, obpi_id, role="Implementer", model="sonnet", task_id=1)
        marker = json.loads(_marker(root, obpi_id).read_text(encoding="utf-8"))
        self.assertEqual(len(marker["dispatch_state"]), 1)
        self.assertEqual(marker["dispatch_state"][0]["role"], "Implementer")

    def test_recording_is_additive_not_replacing(self) -> None:
        root, obpi_id = _plans()
        chan.record_dispatch(root, obpi_id, role="Implementer", model="sonnet", task_id=1)
        chan.record_dispatch(root, obpi_id, role="SpecReviewer", model="opus", task_id=2)
        marker = json.loads(_marker(root, obpi_id).read_text(encoding="utf-8"))
        self.assertEqual(len(marker["dispatch_state"]), 2)


class TestDegradedModeKeepsTheGateCompliable(unittest.TestCase):
    """A gate with no compliant path for a dispatch-less session gets worked around.

    GHI #770 recorded exactly this: a session whose standing instruction forbade
    subagents had no way to comply and no way to declare that it had not.
    """

    def test_declaring_single_driver_is_recorded_and_visible(self) -> None:
        root, obpi_id = _plans()
        chan.declare_single_driver(root, obpi_id, reason="harness forbids subagents")
        self.assertTrue(chan.single_driver_declaration(root, obpi_id))
        rendered = chan.render_dispatch_channel(
            chan.dispatch_channel(root, obpi_id),
            declaration=chan.single_driver_declaration(root, obpi_id),
        )
        self.assertIn("SINGLE-DRIVER DECLARED", rendered)
        self.assertIn("harness forbids subagents", rendered)

    def test_undeclared_and_undispatched_renders_the_bare_verdict(self) -> None:
        root, obpi_id = _plans()
        rendered = chan.render_dispatch_channel(chan.dispatch_channel(root, obpi_id))
        self.assertIn("SINGLE-DRIVER", rendered)
        self.assertIn("NOT DISPATCHED", rendered)
        self.assertNotIn("SINGLE-DRIVER DECLARED", rendered)


class TestPrecompleteSurfacesTheChannel(unittest.TestCase):
    """Stage 5 is the operator's decision point, so the channel must appear there."""

    def _check(self, root: Path, obpi_id: str) -> object:
        from gzkit.commands.obpi_precomplete import _check_stage2_dispatch

        return _check_stage2_dispatch(root, obpi_id)

    def test_blocks_when_pipeline_ran_with_no_dispatch_and_no_declaration(self) -> None:
        """The OBPI-0.35.0-09 condition: marker present, Stage 2 run inline."""
        root, obpi_id = _plans("verify")
        result = self._check(root, obpi_id)
        self.assertFalse(result.ok)
        self.assertIn("NOT DISPATCHED", result.message)
        self.assertIsNotNone(result.remediation)

    def test_passes_when_the_full_roster_was_dispatched(self) -> None:
        root, obpi_id = _plans("verify")
        for i, role in enumerate(chan.MANDATED_STAGE2_ROLES, start=1):
            chan.record_dispatch(root, obpi_id, role=role, model="sonnet", task_id=i)
        self.assertTrue(self._check(root, obpi_id).ok)

    def test_passes_but_discloses_when_single_driver_is_declared(self) -> None:
        """Declared is permitted; silent is not. That is the whole distinction."""
        root, obpi_id = _plans("verify")
        chan.declare_single_driver(root, obpi_id, reason="cron run, no Agent tool")
        result = self._check(root, obpi_id)
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


class TestCreditOutlivesTheMarker(unittest.TestCase):
    """Stage-2 dispatch credit is Layer-2 evidence, not a pipeline-marker key (GHI #886).

    The marker is Layer 3 (``docs/governance/state-doctrine.md``; ``AGENTS.md``
    § Architectural Boundaries #6), and ``ADR-0.0.9`` Rule 5 states the
    consequence in as many words: *"Layer 3 artifacts cannot block gates. Only
    L1 (canon) and L2 (events) can be gate evidence."*

    Measured on ``OBPI-0.35.0-02``, 2026-08-26: the mandated two-stage review DID
    run and recorded 3/3 for both tasks, and the credit was destroyed by
    ``gz obpi pipeline --clear-stale`` — a SANCTIONED recovery path, not misuse.
    A compliant run became indistinguishable from a non-compliant one, with no
    way back except a prose declaration asserting the lost fact.
    """

    def _clear_stale(self, root: Path, obpi_id: str) -> None:
        """Reproduce what the sanctioned clear-stale recovery does to the marker."""
        _marker(root, obpi_id).unlink()

    def test_dispatch_credit_survives_clearing_the_marker(self) -> None:
        root, obpi_id = _plans()
        for i, role in enumerate(chan.MANDATED_STAGE2_ROLES, start=1):
            chan.record_dispatch(root, obpi_id, role=role, model="sonnet", task_id=i)
        self._clear_stale(root, obpi_id)
        self.assertFalse(chan.is_single_driver(chan.dispatch_channel(root, obpi_id)))

    def test_single_driver_declaration_survives_clearing_the_marker(self) -> None:
        """The declaration is the RECOVERY artifact; losing it re-opens the stall.

        Covering only dispatch records would leave the gate half-durable: a
        clear-stale would still convert a knowingly-declared single-driver run
        back into a silent one, which is exactly what this gate refuses.
        """
        root, obpi_id = _plans()
        chan.declare_single_driver(root, obpi_id, reason="harness forbids subagents")
        self._clear_stale(root, obpi_id)
        declaration = chan.single_driver_declaration(root, obpi_id)
        self.assertIsNotNone(declaration)
        self.assertEqual(declaration["reason"], "harness forbids subagents")

    def test_a_hand_written_marker_key_grants_no_dispatch_credit(self) -> None:
        """Layer 3 is not gate evidence, so writing the key must not buy the verdict.

        This is the same forgery surface GHI #412 closed for the marker's nonce:
        any process with write access could otherwise satisfy the gate by editing
        a JSON file no ceremony produced.
        """
        root, obpi_id = _plans()
        marker = json.loads(_marker(root, obpi_id).read_text(encoding="utf-8"))
        marker["dispatch_state"] = [
            {
                "task_id": 1,
                "role": role,
                "agent_file": "",
                "model": "sonnet",
                "isolation": "inline",
                "background": False,
                "dispatched_at": "2026-08-27T00:00:00Z",
                "status": "done",
                "persona_loaded": None,
                "completed_at": None,
                "result": None,
            }
            for role in chan.MANDATED_STAGE2_ROLES
        ]
        _marker(root, obpi_id).write_text(json.dumps(marker), encoding="utf-8")
        self.assertTrue(chan.is_single_driver(chan.dispatch_channel(root, obpi_id)))

    def test_a_hand_written_declaration_key_does_not_satisfy_the_gate(self) -> None:
        root, obpi_id = _plans()
        marker = json.loads(_marker(root, obpi_id).read_text(encoding="utf-8"))
        marker["single_driver_declaration"] = {"reason": "forged", "declared_at": "2026-08-27"}
        _marker(root, obpi_id).write_text(json.dumps(marker), encoding="utf-8")
        self.assertIsNone(chan.single_driver_declaration(root, obpi_id))

    def test_credit_does_not_leak_from_another_obpi(self) -> None:
        """The ledger is project-wide, so the id filter is what keeps credit honest.

        Without it every OBPI would inherit every other OBPI's dispatch records
        forever — "credit is never inferred" collapsing into "credit is inferred
        from any dispatch anyone ever made". Found by a mutation sweep: dropping
        `event.id == obpi_id` left the whole suite green.
        """
        root, obpi_id = _plans()
        other = "OBPI-0.12.0-99"
        (root / ".claude" / "plans" / f".pipeline-active-{other}.json").write_text(
            json.dumps({"obpi_id": other, "parent_adr": "ADR-0.12.0"}), encoding="utf-8"
        )
        for i, role in enumerate(chan.MANDATED_STAGE2_ROLES, start=1):
            chan.record_dispatch(root, other, role=role, model="sonnet", task_id=i)
        chan.declare_single_driver(root, other, reason="the other OBPI could not dispatch")

        self.assertTrue(chan.is_single_driver(chan.dispatch_channel(root, obpi_id)))
        self.assertIsNone(chan.single_driver_declaration(root, obpi_id))

    def test_the_gate_still_passes_after_clear_stale_and_relaunch(self) -> None:
        """The incident, end to end: dispatch, lose the marker, relaunch, complete.

        Before this fix the relaunched marker carried no ``dispatch_state`` and
        ``gz obpi precomplete`` reported 0 of 3 mandated roles against a run that
        had recorded 3/3.
        """
        from gzkit.commands.obpi_precomplete import _check_stage2_dispatch

        root, obpi_id = _plans("verify")
        for i, role in enumerate(chan.MANDATED_STAGE2_ROLES, start=1):
            chan.record_dispatch(root, obpi_id, role=role, model="sonnet", task_id=i)
        self._clear_stale(root, obpi_id)
        _plans_dir = root / ".claude" / "plans"
        (_plans_dir / f".pipeline-active-{obpi_id}.json").write_text(
            json.dumps({"obpi_id": obpi_id, "parent_adr": "ADR-0.12.0", "current_stage": "verify"}),
            encoding="utf-8",
        )
        result = _check_stage2_dispatch(root, obpi_id)
        self.assertTrue(result.ok)
        self.assertIn("DISPATCHED", result.message)


if __name__ == "__main__":
    unittest.main()
