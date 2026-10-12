"""Tests for the Stage-2 dispatch channel (GHI #845).

Derived from the GHI's semantics: an undispatched Stage 2 must be VISIBLE in an
artifact, credit must come only from a recorded dispatch, and the gate must stay
compliable so it is obeyed rather than worked around.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import Any

from gzkit import obpi_dispatch_channel as chan
from gzkit.ledger import (
    Ledger,
    LedgerEvent,
    obpi_receipt_emitted_event,
    pipeline_launched_event,
)
from gzkit.pipeline_runtime import (
    RunCrossing,
    advance_pipeline_markers,
    pipeline_marker_payload,
    record_position,
    write_pipeline_markers,
)
from gzkit.traceability import covers


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


class TestPrecompleteNamesTheRunForItsDispatchCheck(unittest.TestCase):
    """The Stage 2 dispatch control finds the run however the OBPI was spelled.

    Review finding fc1-AUX-precomplete-checks-still-run-under-the-typed-id, a
    defect older than OBPI-0.35.0-15: the check decided whether a pipeline ran
    by looking for the marker file under the id as typed. The launcher names
    the marker by the full slug, so the short ``OBPI-<semver>-<item>`` form
    found no file and the check passed as "not assessable" while a run was in
    flight. The check now names the run as its position is recorded: by the id
    the launch in flight carries. This is the control of Requirement 11 and no
    acceptance criterion of OBPI-0.35.0-15, so no REQ is bound here.
    """

    _SHORT = "OBPI-0.12.0-04"
    _FULL = "OBPI-0.12.0-04-dispatch-channel"
    _SIBLING = "OBPI-0.12.0-04-interrogate"

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / ".claude" / "plans").mkdir(parents=True)
        (self.root / ".gzkit").mkdir()
        self.ledger = Ledger(self.root / ".gzkit" / "ledger.jsonl")
        _marker(self.root, self._FULL).write_text(
            json.dumps(
                {"obpi_id": self._FULL, "parent_adr": "ADR-0.12.0", "current_stage": "verify"}
            ),
            encoding="utf-8",
        )

    def _launch_row(self, obpi_id: str) -> LedgerEvent:
        return pipeline_launched_event(
            obpi_id=obpi_id,
            parent_adr="ADR-0.12.0",
            lane="heavy",
            nonce="0123456789abcdef0123456789abcdef",
            marker_path=f".claude/plans/.pipeline-active-{obpi_id}.json",
            entry="full",
        )

    def _launch(self) -> None:
        self.ledger.append(self._launch_row(self._FULL))

    def _dispatch_the_roster(self) -> None:
        for task, role in enumerate(chan.MANDATED_STAGE2_ROLES, start=1):
            chan.record_dispatch(self.root, self._FULL, role=role, model="sonnet", task_id=task)

    def _check(self, obpi_id: str) -> Any:
        from gzkit.commands.obpi_precomplete import _check_stage2_dispatch

        return _check_stage2_dispatch(self.root, obpi_id)

    def test_a_short_id_no_longer_passes_a_run_that_dispatched_nothing(self) -> None:
        """The silent single-driver run the gate refuses is refused by either spelling."""
        self._launch()

        result = self._check(self._SHORT)

        self.assertFalse(result.ok)
        self.assertIn("NOT DISPATCHED", result.message)
        self.assertIsNotNone(result.remediation)
        self.assertEqual(result, self._check(self._FULL))

    def test_a_short_id_reads_what_the_run_recorded(self) -> None:
        """A dispatched roster and a declared single driver pass, and say which they are."""
        recorded: dict[str, Callable[[], None]] = {
            "DISPATCHED": self._dispatch_the_roster,
            "SINGLE-DRIVER DECLARED": lambda: chan.declare_single_driver(
                self.root, self._FULL, reason="cron run, no Agent tool"
            ),
        }
        for said, record in recorded.items():
            with self.subTest(recorded=said):
                self.ledger.path.write_text("", encoding="utf-8")
                self.ledger = Ledger(self.ledger.path)
                self._launch()
                record()

                result = self._check(self._SHORT)

                self.assertTrue(result.ok)
                self.assertIn(said, result.message)
                self.assertNotIn("no active pipeline marker", result.message)
                self.assertEqual(result, self._check(self._FULL))

    def test_with_no_one_run_in_flight_the_check_reads_as_it_always_did(self) -> None:
        """The control: nothing changes for a full id, or when the id names no one run.

        Never launched, ended by its receipt, or two runs in flight under the
        one short form: the short id names no run, so the check looks for the
        marker under the id as typed, as before. The full id finds its marker
        whatever the ledger holds, as before.
        """
        ended = obpi_receipt_emitted_event(
            self._FULL,
            receipt_event="completed",
            attestor="test",
            obpi_completion="attested_completed",
            parent_adr="ADR-0.12.0",
        )
        launch = self._launch_row(self._FULL)
        ledgers: dict[str, list[LedgerEvent]] = {
            "never launched": [],
            "ended by its receipt": [launch, ended],
            "two runs in flight": [launch, self._launch_row(self._SIBLING)],
        }
        for name, rows in ledgers.items():
            with self.subTest(ledger=name):
                self.ledger.path.write_text("", encoding="utf-8")
                self.ledger = Ledger(self.ledger.path)
                for row in rows:
                    self.ledger.append(row)

                by_short = self._check(self._SHORT)
                by_full = self._check(self._FULL)

                self.assertTrue(by_short.ok)
                self.assertIn("no active pipeline marker", by_short.message)
                self.assertFalse(by_full.ok)
                self.assertIn("NOT DISPATCHED", by_full.message)
                self.assertIn(self._FULL, by_full.remediation)


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


class TestBothMarkerFilesAgreeAfterADispatch(unittest.TestCase):
    """The legacy marker never falls behind the per-OBPI marker (OBPI-0.35.0-15).

    A launch writes one payload to both files and ``OBPI-0.13.0-02`` Requirement 4
    has them stay that way. They diverged after the first dispatch, because the
    dispatch record and the single-driver declaration were written to the
    per-OBPI file alone, so a reader of the legacy marker saw a run with no
    dispatch at all.
    """

    _OBPI = "OBPI-0.12.0-04"

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.plans = self.root / ".claude" / "plans"
        (self.root / ".gzkit").mkdir(parents=True)
        (self.root / ".gzkit" / "ledger.jsonl").touch()
        payload = pipeline_marker_payload(self._OBPI, "ADR-0.12.0", "heavy", None, "pass")
        self.per_obpi, self.legacy = write_pipeline_markers(self.plans, payload)

    @staticmethod
    def _read(path: Path) -> dict[str, object]:
        return json.loads(path.read_text(encoding="utf-8"))

    @covers("REQ-0.35.0-15-07")
    def test_a_recorded_dispatch_reaches_both_marker_files(self) -> None:
        chan.record_dispatch(self.root, self._OBPI, role="Implementer", model="sonnet", task_id=1)

        dispatched = self._read(self.legacy).get("dispatch_state")
        self.assertIsInstance(dispatched, list)
        assert isinstance(dispatched, list)
        self.assertEqual([record["role"] for record in dispatched], ["Implementer"])
        self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())

    @covers("REQ-0.35.0-15-07")
    def test_a_single_driver_declaration_reaches_both_marker_files(self) -> None:
        chan.declare_single_driver(self.root, self._OBPI, reason="harness forbids subagents")

        declaration = self._read(self.legacy).get("single_driver_declaration")
        self.assertIsInstance(declaration, dict)
        assert isinstance(declaration, dict)
        self.assertEqual(declaration["reason"], "harness forbids subagents")
        self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())

    @covers("REQ-0.35.0-15-07")
    def test_a_dispatch_after_an_advance_keeps_the_stage_and_position(self) -> None:
        """A dispatch adds its record and moves nothing else the advance wrote."""
        position = {"kind": "phase", "label": "verification", "boundary": "gz obpi pipeline"}
        advance_pipeline_markers(
            self.plans,
            self._OBPI,
            stage="verify",
            position=position,
            updated_at="2026-10-11T10:30:00.250000+00:00",
            blockers=[],
            requires_human_attestation=True,
        )
        advanced = self._read(self.per_obpi)

        chan.record_dispatch(self.root, self._OBPI, role="SpecReviewer", model="opus", task_id=1)

        for marker_path in (self.per_obpi, self.legacy):
            marker = self._read(marker_path)
            self.assertEqual(marker["current_stage"], "verify")
            self.assertEqual(marker["position"], position)
            self.assertEqual(marker["updated_at"], advanced["updated_at"])
            self.assertIn("dispatch_state", marker)
        self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())

    def test_a_declaration_leaves_another_obpis_legacy_marker_alone(self) -> None:
        self.legacy.write_text(json.dumps({"obpi_id": "OBPI-0.12.0-99"}), encoding="utf-8")
        foreign = self.legacy.read_bytes()

        chan.declare_single_driver(self.root, self._OBPI, reason="harness forbids subagents")

        self.assertIn("single_driver_declaration", self._read(self.per_obpi))
        self.assertEqual(self.legacy.read_bytes(), foreign)

    def _dispatch_parents(self) -> list[object]:
        """Return the parent ADR each recorded dispatch names on the ledger."""
        ledger = (self.root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
        rows = [json.loads(line) for line in ledger.splitlines() if line.strip()]
        return [row.get("parent") for row in rows if row["event"] == "stage2_dispatch_recorded"]

    def test_a_dispatch_after_the_per_obpi_marker_is_gone_keeps_the_earlier_records(self) -> None:
        """The cache is read from the file it is written to: the legacy marker as fallback.

        Read from the per-OBPI file alone the earlier records were not seen, and
        the write that followed replaced them in the legacy marker with one
        record. The parent ADR on the ledger row comes from the same read.
        """
        chan.record_dispatch(self.root, self._OBPI, role="Implementer", model="sonnet", task_id=1)
        self.per_obpi.unlink()

        chan.record_dispatch(self.root, self._OBPI, role="SpecReviewer", model="opus", task_id=1)

        dispatched = self._read(self.legacy).get("dispatch_state")
        assert isinstance(dispatched, list)
        self.assertEqual([record["role"] for record in dispatched], ["Implementer", "SpecReviewer"])
        self.assertEqual(self._dispatch_parents(), ["ADR-0.12.0", "ADR-0.12.0"])
        self.assertFalse(self.per_obpi.exists())

    def test_an_unreadable_per_obpi_marker_costs_the_legacy_marker_nothing(self) -> None:
        """A per-OBPI file that is not this run's marker reads as absent.

        The declaration then lands on the legacy marker beside what it already
        carried. Read on its own terms, an empty object became the payload
        written over the legacy marker, and the run lost its marker.
        """
        corruptions = (
            ("truncated JSON", b'{"obpi_id": '),
            ("JSON that is not an object", b"[]"),
            ("an object naming no OBPI", b"{}"),
            ("bytes that are not UTF-8", b"\xff\xfe{}"),
        )
        for name, content in corruptions:
            with self.subTest(per_obpi=name):
                payload = pipeline_marker_payload(self._OBPI, "ADR-0.12.0", "heavy", None, "pass")
                write_pipeline_markers(self.plans, payload)
                chan.record_dispatch(
                    self.root, self._OBPI, role="Implementer", model="sonnet", task_id=1
                )
                before = self._read(self.legacy)
                self.per_obpi.write_bytes(content)

                chan.declare_single_driver(self.root, self._OBPI, reason="no subagents here")

                after = self._read(self.legacy)
                declaration = after.pop("single_driver_declaration", None)
                assert isinstance(declaration, dict)
                self.assertEqual(declaration["reason"], "no subagents here")
                self.assertEqual(after, before)
                self.assertEqual(self.per_obpi.read_bytes(), content)


if __name__ == "__main__":
    unittest.main()


class TestADispatchRecordsTheTaskAndCreditStaysOnTheLedger(unittest.TestCase):
    """OBPI-0.35.0-15: a dispatch marks a Stage 2 task; its credit is unchanged.

    A position is never gate evidence (Requirement 12). The dispatch appends its
    own ``stage2_dispatch_recorded`` row, which is what credit reads, and one
    ``pipeline_stage_transition`` row, which is what the position reads. Neither
    stands in for the other.
    """

    def setUp(self) -> None:
        self.root, self.obpi_id = _plans()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.ledger = Ledger(self.root / ".gzkit" / "ledger.jsonl")

    def _launch(self) -> None:
        self.ledger.append(
            pipeline_launched_event(
                obpi_id=self.obpi_id,
                parent_adr="ADR-0.12.0",
                lane="heavy",
                nonce="0123456789abcdef0123456789abcdef",
                marker_path=f".claude/plans/.pipeline-active-{self.obpi_id}.json",
                entry="full",
            )
        )

    def _crossings(self) -> list[dict]:
        return [
            row.extra
            for row in Ledger(self.ledger.path).read_all()
            if row.event == "pipeline_stage_transition" and row.id == self.obpi_id
        ]

    def _credited(self) -> set[str]:
        return {
            entry.role
            for entry in chan.dispatch_channel(self.root, self.obpi_id)
            if entry.disposition is chan.DispatchDisposition.DISPATCHED
        }

    def test_a_dispatch_in_a_run_in_flight_names_the_task_it_dispatched(self) -> None:
        self._launch()

        chan.record_dispatch(self.root, self.obpi_id, role="Implementer", model="sonnet", task_id=3)

        (crossing,) = self._crossings()
        self.assertEqual(crossing["stage"], "implement")
        self.assertEqual(crossing["position_kind"], "task")
        self.assertEqual(crossing["position_label"], "task 3")
        marker = json.loads(_marker(self.root, self.obpi_id).read_text(encoding="utf-8"))
        self.assertEqual(marker["current_stage"], "implement")
        self.assertEqual(marker["position"]["label"], "task 3")
        self.assertEqual(len(marker["dispatch_state"]), 1)

    @covers("REQ-0.35.0-15-02")
    def test_a_dispatch_with_no_run_in_flight_records_no_position(self) -> None:
        chan.record_dispatch(self.root, self.obpi_id, role="Implementer", model="sonnet", task_id=1)

        self.assertEqual(self._crossings(), [])
        self.assertEqual(self._credited(), {"Implementer"})

    def test_dispatch_credit_reads_the_ledger_whatever_the_position_says(self) -> None:
        """A recorded position grants no credit, and losing the marker costs none."""
        self._launch()
        record_position(
            self.ledger,
            self.root / ".claude" / "plans",
            self.obpi_id,
            RunCrossing(boundary="dispatch", task="task 1"),
        )
        self.assertEqual(len(self._crossings()), 1)
        self.assertEqual(self._credited(), set(), "a position is not a dispatch record")

        chan.record_dispatch(self.root, self.obpi_id, role="Implementer", model="sonnet", task_id=1)
        _marker(self.root, self.obpi_id).unlink()

        self.assertEqual(self._credited(), {"Implementer"})
