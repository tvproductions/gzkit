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
from unittest.mock import patch

from gzkit import obpi_dispatch_channel as chan
from gzkit.cli.helpers.exit_codes import EXIT_POLICY_BREACH, EXIT_SUCCESS, EXIT_USER_ERROR
from gzkit.commands.obpi_precomplete import CheckResult, obpi_precomplete_cmd
from gzkit.ledger import (
    Ledger,
    LedgerEvent,
    obpi_created_event,
    obpi_receipt_emitted_event,
    pipeline_launched_event,
)
from gzkit.ledger_events import (
    artifact_renamed_event,
    obpi_blocked_on_operator_event,
    obpi_parked_event,
    obpi_unparked_event,
    obpi_withdrawn_event,
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


#: The precomplete checks that judge evidence a bare project root does not hold.
#: They are replaced with a pass that keeps what it was handed; the operator
#: block check and the Stage 2 dispatch check, the two under test, are real.
_REPLACED_PRECOMPLETE_CHECKS = (
    "_check_brief_readiness",
    "_check_scope_audit",
    "_check_reconcile_idempotent",
    "_check_lock_held",
    "_check_arb_receipts_passed",
    "_check_plan_audit_receipt",
    "_check_brief_headings_scoped",
    "_check_behave_req_coverage_scoped",
    "_check_task_envelope_coherence",
    "_check_acceptance_records",
)

#: The replaced checks that read under an OBPI id, as their last argument.
_ID_TAKING_PRECOMPLETE_CHECKS = (
    "_check_lock_held",
    "_check_arb_receipts_passed",
    "_check_plan_audit_receipt",
    "_check_behave_req_coverage_scoped",
    "_check_acceptance_records",
)


class TestPrecompleteNamesTheObpiOnceAtEntry(unittest.TestCase):
    """Every precomplete control reads the same OBPI however its id was spelled.

    ``gz obpi precomplete`` names the OBPI once, at entry, by the resolver the
    launcher uses (operator ruling 2026-10-12, Open Design Question 19: "one
    resolver at command entry"). Every check, the report and the position
    record use the id the ledger holds for it, so the short
    ``OBPI-<semver>-<item>`` form, a renamed id and the full id read the same
    operator block, the same marker and the same dispatch records, whether or
    not a run is in flight. An id the resolver gives to no single OBPI is
    refused before any check runs. Review findings, each a
    defect older than OBPI-0.35.0-15
    in a control Requirement 11 names: the Stage 2 dispatch check looked for
    the marker under the id as typed and passed a short id as "not assessable"
    (fc1-AUX-precomplete-checks-still-run-under-the-typed-id), still did once
    the run was retired
    (fc3-aux-precomplete-dispatch-check-reads-the-typed-id-once-the-run-is-retired),
    and the operator block check read the block under the id as typed
    (fc2-aux-precomplete-operator-block-check-still-reads-the-id-as-typed).
    The final round added three on the same root: a brief whose file name
    extends the id typed, a brief whose frontmatter keeps an id the ledger
    renamed, and a prefix of the launch id longer than its short form.
    These are controls and no acceptance criterion, so no REQ is bound to them.
    The tests of the position record are bound to REQ-0.35.0-15-02, whose
    subject it is.

    The command is run whole. Each control is unchanged for a full id, which
    the full-id assertions below pin, and no weaker for a short one.
    """

    _SHORT = "OBPI-0.12.0-04"
    _FULL = "OBPI-0.12.0-04-dispatch-channel"
    _SIBLING = "OBPI-0.12.0-04-interrogate"
    _ADR = "ADR-0.12.0"

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / ".claude" / "plans").mkdir(parents=True)
        (self.root / ".gzkit").mkdir()
        self.ledger = Ledger(self.root / ".gzkit" / "ledger.jsonl")
        self.ledger.append(obpi_created_event(self._FULL, self._ADR))
        (self.root / "design" / "adr" / self._ADR / "obpis").mkdir(parents=True)
        self._brief(self._FULL)
        _marker(self.root, self._FULL).write_text(
            json.dumps({"obpi_id": self._FULL, "parent_adr": self._ADR, "current_stage": "verify"}),
            encoding="utf-8",
        )

    def _brief(self, name: str, *, carries: str | None = None, status: str = "in_progress") -> None:
        """Write the brief file ``name``, whose frontmatter carries the id ``carries``."""
        briefs = self.root / "design" / "adr" / self._ADR / "obpis"
        (briefs / f"{name}.md").write_text(
            f"---\nid: {carries or name}\nparent: {self._ADR}\nitem: 4\nlane: heavy\n"
            f"status: {status}\n---\n\n# {name}\n",
            encoding="utf-8",
        )

    def _launch_row(self, obpi_id: str) -> LedgerEvent:
        return pipeline_launched_event(
            obpi_id=obpi_id,
            parent_adr=self._ADR,
            lane="heavy",
            nonce="0123456789abcdef0123456789abcdef",
            marker_path=f".claude/plans/.pipeline-active-{obpi_id}.json",
            entry="full",
        )

    def _launch(self) -> None:
        self.ledger.append(self._launch_row(self._FULL))

    def _start_over(self, *rows: LedgerEvent, registered: tuple[LedgerEvent, ...] = ()) -> None:
        """Empty the ledger, register the OBPI on it, then append ``rows``.

        ``registered`` replaces the one row that registers the OBPI under its
        full id, for a ledger that came to that id another way.
        """
        self.ledger.path.write_text("", encoding="utf-8")
        self.ledger = Ledger(self.ledger.path)
        for row in (*(registered or (obpi_created_event(self._FULL, self._ADR),)), *rows):
            self.ledger.append(row)

    def _dispatch_the_roster(self) -> None:
        for task, role in enumerate(chan.MANDATED_STAGE2_ROLES, start=1):
            chan.record_dispatch(self.root, self._FULL, role=role, model="sonnet", task_id=task)

    def _precomplete(self, obpi_id: str) -> dict[str, Any]:
        """Run ``gz obpi precomplete <obpi_id> --json`` on the project.

        Returns its exit code, its report, and the id each replaced id-taking
        check was handed.
        """
        handed: dict[str, str] = {}

        def _replaced(name: str) -> Callable[..., CheckResult]:
            def _check(*args: Any) -> CheckResult:
                if name in _ID_TAKING_PRECOMPLETE_CHECKS:
                    handed[name] = args[-1]
                return CheckResult(name=name, ok=True, message="replaced")

            return _check

        module = "gzkit.commands.obpi_precomplete"
        patches = [
            patch(f"{module}.{name}", new=_replaced(name)) for name in _REPLACED_PRECOMPLETE_CHECKS
        ]
        patches.append(patch(f"{module}.get_project_root", return_value=self.root))
        for each in patches:
            each.start()
            self.addCleanup(each.stop)
        code = EXIT_SUCCESS
        with patch("builtins.print") as printed:
            try:
                obpi_precomplete_cmd(obpi_id=obpi_id, as_json=True)
            except SystemExit as exc:
                code = int(exc.code or 0)
        for each in patches:
            each.stop()
        report = json.loads(printed.call_args[0][0]) if printed.call_args else None
        checks = {check["name"]: check for check in report["checks"]} if report else {}
        return {"exit": code, "report": report, "checks": checks, "handed": handed}

    def _check(self, obpi_id: str) -> dict[str, Any]:
        """Return the Stage 2 dispatch check as the command reported it."""
        return self._precomplete(obpi_id)["checks"]["stage2_dispatch"]

    def test_a_short_id_no_longer_passes_a_run_that_dispatched_nothing(self) -> None:
        """The silent single-driver run the gate refuses is refused by either spelling."""
        self._launch()

        result = self._check(self._SHORT)

        self.assertFalse(result["ok"])
        self.assertIn("NOT DISPATCHED", result["message"])
        self.assertIsNotNone(result["remediation"])
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
                self._start_over(self._launch_row(self._FULL))
                record()

                result = self._check(self._SHORT)

                self.assertTrue(result["ok"])
                self.assertIn(said, result["message"])
                self.assertNotIn("no active pipeline marker", result["message"])
                self.assertEqual(result, self._check(self._FULL))

    def test_a_short_id_reads_the_marker_the_full_id_reads_whatever_the_ledger_holds(self) -> None:
        """No run in flight, or two: the short id still reads what the full id reads.

        The control is the full id, which finds its marker whatever the ledger
        holds and is refused for the dispatch nobody recorded, as it always
        was. The short id once looked for a marker under the id as typed in
        every one of these cases, found none and passed as "not assessable".
        """
        launch = self._launch_row(self._FULL)
        ended = obpi_receipt_emitted_event(
            self._FULL,
            receipt_event="completed",
            attestor="test",
            obpi_completion="attested_completed",
            parent_adr=self._ADR,
        )
        parked = obpi_parked_event(self._FULL, self._ADR, "ADR-pool.dispatch")
        unparked = obpi_unparked_event(self._FULL, self._ADR, "ADR-pool.dispatch")
        ledgers: dict[str, list[LedgerEvent]] = {
            "never launched": [],
            "ended by its receipt": [launch, ended],
            "parked": [launch, parked],
            "withdrawn": [launch, obpi_withdrawn_event(self._FULL, self._ADR, "superseded", "g0")],
            "parked, unparked and not launched again": [launch, parked, unparked],
            "two runs in flight": [launch, self._launch_row(self._SIBLING)],
        }
        for name, rows in ledgers.items():
            with self.subTest(ledger=name):
                self._start_over(*rows)

                by_short = self._check(self._SHORT)
                by_full = self._check(self._FULL)

                self.assertFalse(by_full["ok"])
                self.assertIn("NOT DISPATCHED", by_full["message"])
                self.assertIn(self._FULL, by_full["remediation"])
                self.assertEqual(by_short, by_full)

    def test_an_operator_block_refuses_a_short_id_as_it_refuses_the_full_id(self) -> None:
        """A standing operator block is read under the OBPI's id, not the typing."""
        block = obpi_blocked_on_operator_event(
            self._FULL, self._ADR, "the boundary set needs a ruling", "rule on Question 9"
        )
        for standing, rows in (("no block", []), ("a block standing", [block])):
            self._start_over(self._launch_row(self._FULL), *rows)
            self._dispatch_the_roster()
            by_full = self._precomplete(self._FULL)
            for spelled, given in (("full", self._FULL), ("short", self._SHORT)):
                with self.subTest(block=standing, spelled=spelled):
                    found = self._precomplete(given)

                    blocked = bool(rows)
                    self.assertEqual(found["checks"]["operator_block"]["ok"], not blocked)
                    self.assertEqual(found["report"]["ready"], not blocked)
                    self.assertEqual(found["exit"], EXIT_POLICY_BREACH if blocked else EXIT_SUCCESS)
                    self.assertEqual(found["report"], by_full["report"])
            if rows:
                self.assertIn(
                    "the boundary set needs a ruling",
                    by_full["checks"]["operator_block"]["message"],
                )

    def test_a_full_id_reads_its_own_controls_beside_a_brief_whose_name_extends_it(self) -> None:
        """A second brief named ``<id>-<more>`` lends the id typed none of its controls.

        Review finding
        fin-AUX-precomplete-full-id-beside-a-hyphen-extended-sibling-brief-reads-the-siblings-controls.
        A glob on ``<id>*.md`` sorts ``<id>-<more>.md`` before ``<id>.md``, and
        the checks then ran under the id that brief carries: the standing
        operator block and the unrecorded Stage 2 dispatch of the OBPI typed
        no longer failed the command (Requirement 11). The OBPI is the one the
        ledger names for the id.
        """
        extended = f"{self._FULL}-extended"
        self._brief(extended)
        self.assertLess(f"{extended}.md", f"{self._FULL}.md", "the extending brief sorts first")
        block = obpi_blocked_on_operator_event(
            self._FULL, self._ADR, "the boundary set needs a ruling", "rule on Question 9"
        )
        self._start_over(
            obpi_created_event(extended, self._ADR), self._launch_row(self._FULL), block
        )

        found = self._precomplete(self._FULL)

        self.assertEqual(found["handed"], dict.fromkeys(_ID_TAKING_PRECOMPLETE_CHECKS, self._FULL))
        self.assertEqual(found["report"]["obpi_id"], self._FULL)
        self.assertFalse(found["checks"]["operator_block"]["ok"])
        self.assertIn(
            "the boundary set needs a ruling", found["checks"]["operator_block"]["message"]
        )
        self.assertFalse(found["checks"]["stage2_dispatch"]["ok"])
        self.assertIn("NOT DISPATCHED", found["checks"]["stage2_dispatch"]["message"])
        self.assertEqual(found["exit"], EXIT_POLICY_BREACH)

    def test_a_renamed_id_reads_its_controls_under_the_id_the_ledger_holds(self) -> None:
        """A brief that keeps the id the ledger renamed lends the checks no stale name.

        Review finding
        fin-aux-precomplete-checks-read-under-the-briefs-frontmatter-id-which-can-differ-from-the-ledger-id.
        The ledger renamed the short form to the full id and the brief's
        frontmatter was never rewritten, as for ten ``ADR-0.1.0`` briefs. The
        checks ran under the frontmatter id, where no operator block and no
        dispatch record is filed, so a standing block and an unrecorded
        Stage 2 dispatch stopped failing the command (Requirement 11).
        """
        self._brief(self._FULL, carries=self._SHORT)
        block = obpi_blocked_on_operator_event(
            self._FULL, self._ADR, "the boundary set needs a ruling", "rule on Question 9"
        )
        self._start_over(
            self._launch_row(self._FULL),
            block,
            registered=(
                obpi_created_event(self._SHORT, self._ADR),
                artifact_renamed_event(self._SHORT, self._FULL),
            ),
        )
        for spelled, given in (("full", self._FULL), ("short", self._SHORT)):
            with self.subTest(spelled=spelled):
                found = self._precomplete(given)

                self.assertEqual(
                    found["handed"], dict.fromkeys(_ID_TAKING_PRECOMPLETE_CHECKS, self._FULL)
                )
                self.assertEqual(found["report"]["obpi_id"], self._FULL)
                self.assertFalse(found["checks"]["operator_block"]["ok"])
                self.assertFalse(found["checks"]["stage2_dispatch"]["ok"])
                self.assertIn("NOT DISPATCHED", found["checks"]["stage2_dispatch"]["message"])
                self.assertEqual(found["exit"], EXIT_POLICY_BREACH)

    @covers("REQ-0.35.0-15-02")
    def test_a_prefix_the_resolver_expands_is_checked_and_recorded_under_the_launch_id(
        self,
    ) -> None:
        """A prefix longer than the short form names the run, for the checks and the record.

        Review finding
        fin-REQ02-a-slug-prefix-id-is-accepted-by-precomplete-and-records-nothing.
        A file glob accepted ``<short>-dispatch`` and the recorder, handed the
        id as typed, found no run: the boundary was crossed and never
        recorded. The resolver expands a prefix that ends on a whole word of
        the id, so the command runs and its crossing is on the launch id.
        """
        block = obpi_blocked_on_operator_event(
            self._FULL, self._ADR, "the boundary set needs a ruling", "rule on Question 9"
        )
        self._start_over(self._launch_row(self._FULL), block)

        found = self._precomplete(f"{self._SHORT}-dispatch")

        self.assertEqual(found["handed"], dict.fromkeys(_ID_TAKING_PRECOMPLETE_CHECKS, self._FULL))
        self.assertFalse(found["checks"]["operator_block"]["ok"])
        self.assertFalse(found["checks"]["stage2_dispatch"]["ok"])
        self.assertEqual(found["exit"], EXIT_POLICY_BREACH)
        recorded = self._recorded_positions()
        self.assertEqual([row.id for row in recorded], [self._FULL])
        self.assertEqual(recorded[0].extra["position_label"], "precomplete")

    @covers("REQ-0.35.0-15-02")
    def test_an_id_naming_no_single_obpi_is_refused_before_any_check_or_record(self) -> None:
        """Nothing is checked and nothing is recorded under an id the resolver refuses.

        A prefix that stops inside a word of the id names no OBPI, and a short
        form two live OBPIs share names two. The glob accepted both: the
        first gave the recorder an id naming no run, and the second ran the
        checks against whichever brief sorted first. Each is refused with the
        user-error exit before a check runs, so no boundary is crossed.
        """
        refused: dict[str, tuple[str, tuple[LedgerEvent, ...]]] = {
            "a prefix that stops inside a word": (f"{self._SHORT}-disp", ()),
            "a short form two live OBPIs share": (
                self._SHORT,
                (obpi_created_event(self._SIBLING, self._ADR),),
            ),
        }
        self._brief(self._SIBLING)
        for name, (given, rows) in refused.items():
            with self.subTest(refused=name):
                self._start_over(*rows, self._launch_row(self._FULL))

                found = self._precomplete(given)

                self.assertEqual(found["exit"], EXIT_USER_ERROR)
                self.assertIsNone(found["report"], "no report: nothing was checked")
                self.assertEqual(found["handed"], {})
                self.assertEqual(self._recorded_positions(), [])

    def _recorded_positions(self) -> list[LedgerEvent]:
        return [
            row
            for row in Ledger(self.ledger.path).read_all()
            if row.event == "pipeline_stage_transition"
        ]

    def test_every_check_uses_the_id_the_brief_carries_and_the_run_is_recorded(self) -> None:
        self._launch()

        found = self._precomplete(self._SHORT)

        self.assertEqual(found["report"]["obpi_id"], self._FULL)
        self.assertEqual(found["handed"], dict.fromkeys(_ID_TAKING_PRECOMPLETE_CHECKS, self._FULL))
        recorded = self._recorded_positions()
        self.assertEqual([row.id for row in recorded], [self._FULL])
        self.assertEqual(recorded[0].extra["position_label"], "precomplete")

    @covers("REQ-0.35.0-15-02")
    def test_a_short_id_records_under_the_live_run_when_a_retired_brief_sorts_first(self) -> None:
        """A short id names the live OBPI for the checks and for the position record.

        Review finding
        t3-AUX-precomplete-short-id-follows-the-first-sorted-brief-for-the-position-record.
        Two briefs sit on disk under one short form, and the one that sorts
        first belongs to a retired sibling that was never launched. A glob
        gave a short id the sibling's brief. Handing that brief's id to the
        position record named no run, so the live run's ``precomplete``
        boundary went unrecorded. The resolver drops the withdrawn sibling,
        as the launcher does, so the short id names the live OBPI.

        Amended 2026-10-12 with the ruling on Open Design Question 19: this
        test once asserted that the checks ran under the retired sibling's id
        while the record went to the live run. That split is the defect the
        ruling removes, so the checks are asserted under the live OBPI's id,
        the one the record is filed under.
        """
        retired = "OBPI-0.12.0-04-abandoned-first"
        briefs = self.root / "design" / "adr" / self._ADR / "obpis"
        (briefs / f"{retired}.md").write_text(
            f"---\nid: {retired}\nparent: {self._ADR}\nitem: 4\nlane: heavy\n"
            "status: Abandoned\n---\n\n# Abandoned first\n",
            encoding="utf-8",
        )
        self.assertLess(f"{retired}.md", f"{self._FULL}.md", "the retired brief sorts first")
        self._start_over(
            obpi_withdrawn_event(retired, self._ADR, "superseded", "g0"),
            self._launch_row(self._FULL),
        )

        found = self._precomplete(self._SHORT)

        self.assertEqual(found["handed"], dict.fromkeys(_ID_TAKING_PRECOMPLETE_CHECKS, self._FULL))
        self.assertEqual(found["report"]["obpi_id"], self._FULL)
        recorded = self._recorded_positions()
        self.assertEqual([row.id for row in recorded], [self._FULL])
        self.assertEqual(recorded[0].extra["position_label"], "precomplete")
        marker = json.loads(_marker(self.root, self._FULL).read_text(encoding="utf-8"))
        self.assertEqual(marker["position"]["label"], "precomplete")


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
