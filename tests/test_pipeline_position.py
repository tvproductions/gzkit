"""Tests for the position a pipeline run has reached (OBPI-0.35.0-15, GHI #1172).

A pipeline marker used to record the stage the LAUNCH named, so a full launch
read ``implement`` for the whole run. These tests are derived from the brief's
acceptance criteria for the two controls of that repair: a launch with nothing
after it reads as it always did (REQ-0.35.0-15-04), and a marker advanced past
``implement`` keeps every reader working with both marker files identical
(REQ-0.35.0-15-07).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable, Iterator
from contextlib import ExitStack, contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from gzkit import obpi_dispatch_channel as chan
from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    LedgerEvent,
    adr_created_event,
    artifact_renamed_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
    pipeline_launched_event,
    pipeline_stage_transition_event,
)
from gzkit.ledger_events import (
    brief_reconciled_event,
    obpi_parked_event,
    obpi_superseded_event,
    obpi_unparked_event,
    obpi_withdrawn_event,
)
from gzkit.pipeline_runtime import (
    BLOCKER_SUMMARY_WIDTH,
    RULED_BOUNDARIES,
    STAGE_POSITION_KIND,
    STALE_MARKER_HOURS,
    PipelinePosition,
    RunCrossing,
    advance_pipeline_markers,
    clear_stale_pipeline_markers,
    find_stale_pipeline_markers,
    in_flight_launch_id,
    load_dispatch_state,
    load_obpi_pipeline_marker,
    marker_position,
    pipeline_command,
    pipeline_completion_reminder_message,
    pipeline_concurrency_blockers,
    pipeline_marker_paths,
    pipeline_marker_payload,
    pipeline_resume_command,
    pipeline_stage_output,
    purge_orphaned_active_markers,
    rebuild_marker,
    record_position,
    replay_pipeline_position,
    restore_pipeline_marker_twin,
    runs_in_flight,
    write_pipeline_markers,
)
from gzkit.pipeline_stage_fence import (
    CANONICAL_STAGES,
    marker_stage,
    refuses_production_commit,
    refuses_production_write,
)
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init

_OBPI = "OBPI-0.99.0-01-run-position-demo"
#: The same OBPI by the leading ``OBPI-<semver>-<item>`` of its id.
_SHORT_OBPI = "OBPI-0.99.0-01"
#: A second OBPI under the same short form: a reused semver leaves one behind.
_SIBLING_OBPI = "OBPI-0.99.0-01-interrogate"
_OTHER_OBPI = "OBPI-0.99.0-02-another-run"
_ADR = "ADR-0.99.0-run-position-demo"
_NONCE = "0123456789abcdef0123456789abcdef"
_BOUNDARY = "gz obpi pipeline"
_SRC = "src/gzkit/example.py"

_LAUNCHED_AT = "2026-10-11T09:00:00+00:00"
_CROSSED_AT = "2026-10-11T10:30:00.250000+00:00"
_CROSSED_LATER_AT = "2026-10-11T11:45:00.500000+00:00"

#: One recorded boundary per stage past ``implement``, with what the fence
#: doctrine says of that stage: authoring production code is refused once a run
#: leaves Stage 2, while committing it is refused everywhere but ``sync``, the
#: pipeline's own commit stage (``pipeline_stage_fence`` module docstring).
_CROSSINGS: tuple[tuple[str, str, str, bool, bool], ...] = (
    ("verify", "phase", "verification-passed", True, True),
    ("ceremony", "round", "present-evidence", True, True),
    ("sync", "step", "precomplete", True, False),
)

#: What an advance must not touch (OBPI-0.35.0-15 Requirement 8).
_PRESERVED_KEYS = (
    "nonce",
    "started_at",
    "entry",
    "receipt_state",
    "dispatch_state",
    "single_driver_declaration",
)

_STAGE_OUTPUT_FIELDS = ("blockers", "required_human_action", "next_command", "resume_point")

#: What a ceremony launch asks of the operator before completion accounting.
_CEREMONY_HUMAN_ACTION = (
    "Present evidence and obtain explicit human attestation before completion accounting."
)

#: The launch values as they are today (REQ-0.35.0-15-04), by ``--from`` value:
#: ``entry``, ``current_stage``, ``resume_point`` and ``required_human_action``.
#: ``None`` is the full launch. No launch writes a blocker.
_LAUNCH_VALUES: dict[str | None, tuple[str, str, str | None, str | None]] = {
    None: ("full", "implement", "verify", None),
    "verify": ("verify", "verify", "ceremony", None),
    "ceremony": ("ceremony", "ceremony", "sync", _CEREMONY_HUMAN_ACTION),
    "sync": ("sync", "sync", None, None),
}

_CLI_OBPI = "OBPI-0.13.0-01-runtime-command-contract"
#: The same OBPI as an operator types it: the commands' own help gives this form.
_CLI_SHORT_OBPI = "OBPI-0.13.0-01"
#: A second ledger-graph key under that short form: created, parked, never launched.
_CLI_SIBLING_OBPI = "OBPI-0.13.0-01-interrogate"
#: A prefix of the launch id longer than its short form, ending on a whole word.
_CLI_SLUG_PREFIX = "OBPI-0.13.0-01-runtime"
#: What the ledger renames the launched OBPI to in the rename tests.
_CLI_RENAMED_OBPI = "OBPI-0.13.0-01-runtime-command-surface"
_CLI_ADR = "ADR-0.13.0-obpi-pipeline-runtime-surface"
#: The acceptance criteria of a seeded brief that has any: one TASK each at launch.
_CLI_REQS = ("REQ-0.13.0-01-01", "REQ-0.13.0-01-02")

#: The ledger row that retires an OBPI with no receipt, by how it was retired
#: (operator ruling 2026-10-11, Open Design Question 12: retirement ends a run;
#: operator ruling 2026-10-12, Open Design Question 16: "supersede ends a run").
#: Each row carries the retired OBPI's own id, as the command that writes it does.
_RETIREMENTS: dict[str, Callable[[str, str], LedgerEvent]] = {
    "parked": lambda obpi_id, adr: obpi_parked_event(obpi_id, adr, "ADR-pool.interrogate"),
    "withdrawn": lambda obpi_id, adr: obpi_withdrawn_event(obpi_id, adr, "superseded", "g0"),
    "superseded": lambda obpi_id, adr: obpi_superseded_event(
        obpi_id, adr, _OTHER_OBPI, "replaced by its successor", "g0"
    ),
}


def seed_launchable_obpi(*, with_reqs: bool = False) -> tuple[Path, Path]:
    """Seed the working directory so ``gz obpi pipeline`` can launch ``_CLI_OBPI``.

    Call inside ``CliRunner().isolated_filesystem()``: a heavy-lane project, the
    parent ADR, a Draft brief and the ledger rows the launcher requires. Returns
    the per-OBPI and legacy marker paths the launch will write.

    ``with_reqs`` gives the brief ``_CLI_REQS`` as acceptance criteria, so a
    full launch auto-starts one TASK for each of them.
    """
    criteria = ""
    if with_reqs:
        lines = "\n".join(
            f"- [ ] {req} [BEHAVIOR]: Given a launch, the marker reads as launched."
            for req in _CLI_REQS
        )
        criteria = f"\n## Acceptance Criteria\n\n{lines}\n"
    _quick_init("heavy")
    config = GzkitConfig.load(Path(".gzkit.json"))
    adr_dir = Path(config.paths.adrs) / "pre-release" / _CLI_ADR
    (adr_dir / "obpis").mkdir(parents=True, exist_ok=True)
    (adr_dir / f"{_CLI_ADR}.md").write_text(
        f"---\nid: {_CLI_ADR}\nstatus: Proposed\nsemver: 0.13.0\nlane: heavy\n"
        "parent: PRD-GZKIT-1.0.0\ndate: 2026-03-13\n---\n\n"
        f"# {_CLI_ADR}: Demo Pipeline ADR\n",
        encoding="utf-8",
    )
    (adr_dir / "obpis" / f"{_CLI_OBPI}.md").write_text(
        f"---\nid: {_CLI_OBPI}\nparent: {_CLI_ADR}\nitem: 1\nlane: Heavy\n"
        "status: Draft\n---\n\n"
        f"# {_CLI_OBPI}: Runtime Command Contract\n\n**Brief Status:** Draft\n\n"
        "## Verification\n\n```bash\nuv run gz validate --documents\n```\n" + criteria,
        encoding="utf-8",
    )
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(adr_created_event(_CLI_ADR, "PRD-GZKIT-1.0.0", "heavy"))
    ledger.append(obpi_created_event(_CLI_OBPI, _CLI_ADR))
    ledger.append(
        brief_reconciled_event(
            _CLI_OBPI,
            has_drift=False,
            allowlist_delta_count=0,
            discovery_delta_count=0,
            verification_delta_count=0,
            req_count_delta=0,
            citation_delta_count=0,
        )
    )
    return pipeline_marker_paths(Path.cwd() / ".claude" / "plans", _CLI_OBPI)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def _all_of(*patches: Any) -> Iterator[None]:
    """Hold every given patch for the length of one ``with`` block."""
    with ExitStack() as stack:
        for each in patches:
            stack.enter_context(each)
        yield


#: The arguments ``gz obpi complete`` needs to reach its transaction.
COMPLETE_ARGS: tuple[str, ...] = (
    *("obpi", "complete", _CLI_OBPI, "--attestor", "g0"),
    *("--attestation-text", "attest completed"),
    *("--implementation-summary", "- Files: src/gzkit/example.py"),
    *("--key-proof", "the covering tests pass"),
)


@contextmanager
def verification_replaced(
    *,
    failing: bool = False,
    detail: str = "exit 1",
    at_dispatch: Callable[[], None] | None = None,
) -> Iterator[list[str]]:
    """Let ``gz obpi pipeline --from=verify`` or ``--from=ceremony`` run in a seeded project.

    The stage runners are real. Their Stage 2 acceptance check and the dispatch
    of the verification commands are replaced, so no verification command
    runs: each reports a pass, or the first reports a failure with ``detail``
    as its output. ``at_dispatch`` is called at the moment the commands would
    run. Yields the blockers a failed verification finds, as the console
    prints them; the list is filled when the runner dispatches.
    """
    blockers: list[str] = []

    def _dispatch(commands: list[str], _runner: object) -> list[tuple[str, bool, str]]:
        if at_dispatch is not None:
            at_dispatch()
        results = [(command, True, "pass") for command in commands]
        if failing:
            results[0] = (commands[0], False, detail)
            blockers.append(f"{commands[0]}: {detail}")
        return results

    with (
        patch("gzkit.commands.obpi_stages.acceptance_blockers", new=lambda *_a, **_k: []),
        patch("gzkit.commands.obpi_stages._dispatch_verification_commands", new=_dispatch),
    ):
        yield blockers


def precomplete_checks_replaced(found: list[Any] | None = None) -> Any:
    """Replace the checks ``gz obpi precomplete`` runs with ``found``."""
    return patch("gzkit.commands.obpi_precomplete._run_all_checks", return_value=found or [])


def completion_gates_replaced(*, failing_write: bool = False) -> Any:
    """Let ``gz obpi complete`` reach its transaction in a seeded project.

    The completion gates judge evidence a seeded project does not hold, so
    each is replaced; the transaction, the ledger and the marker are real.
    ``failing_write`` makes the ledger write inside the transaction fail, so
    the completion rolls back and exits 2.
    """
    module = "gzkit.commands.obpi_complete"
    replaced = [
        patch(f"{module}.{gate}", return_value=None)
        for gate in (
            "_enforce_reconcile_receipt_gate",
            "_enforce_scope_gate",
            "_enforce_security_review_gate",
            "_enforce_attestation_receipt_gate",
            "_enforce_req_coverage_gate",
            "_enforce_task_envelope_gate",
            "_current_adversarial_event",
            "_surrender_lock_at_completion",
        )
    ]
    replaced.append(patch(f"{module}.build_scope_audit", return_value=Mock()))
    replaced.append(patch(f"{module}._validate_would_be_content", return_value=[]))
    replaced.append(
        patch(
            f"{module}.enrich_completed_receipt_evidence",
            side_effect=lambda **given: (given["base_evidence"], None),
        )
    )
    if failing_write:
        replaced.append(patch(f"{module}._append_stamped", side_effect=OSError("disk full")))
    return _all_of(*replaced)


def write_stage4_packet(name: str) -> str:
    """Write a Step-4a packet named as the pipeline skill names it; return its path."""
    packet = Path(".gzkit") / "evidence" / f"{name}.stage4a.md"
    packet.parent.mkdir(parents=True, exist_ok=True)
    packet.write_text("# Step-4a packet\n", encoding="utf-8")
    return packet.as_posix()


def write_review_receipt() -> str:
    """Write an ARB receipt a review import can resolve; return its run id."""
    run_id = "arb-step-specreview-0123456789abcdef"
    receipts = Path("receipts")
    receipts.mkdir(exist_ok=True)
    (receipts / f"{run_id}.json").write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
    return run_id


def stage4_work_replaced(*, review_stage: str = "adversarial") -> Any:
    """Replace what the three Stage 4 commands compute, keeping what they record.

    ``review_stage`` is the stage the imported review carries.
    """
    packet = Mock(blockers=[], review_blockers=[])
    packet.model_dump_json.return_value = "{}"
    verdict = Mock(verified=True)
    verdict.model_dump_json.return_value = "{}"
    review = Mock(stage=review_stage)
    review.model_dump.return_value = {}
    receipts = Path("receipts").resolve()
    return _all_of(
        patch(
            "gzkit.commands.obpi_present_evidence.generate_evidence_packet",
            return_value=packet,
        ),
        patch(
            "gzkit.commands.obpi_present_evidence.write_packet",
            side_effect=lambda root, _packet: root / ".gzkit" / "evidence" / "packet.json",
        ),
        patch("gzkit.commands.obpi_verify_packet.verify_packet", return_value=verdict),
        patch("gzkit.commands.obpi_acceptance.record_review", return_value=review),
        patch("gzkit.commands.obpi_acceptance.record_human_review", return_value=review),
        patch("gzkit.commands.obpi_acceptance.receipts_root", return_value=receipts),
    )


class _RunFixture(unittest.TestCase):
    """A project root holding a launched run's two marker files and its ledger."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.plans = self.root / ".claude" / "plans"
        self.plans.mkdir(parents=True)
        (self.root / ".gzkit").mkdir()
        (self.root / ".gzkit" / "ledger.jsonl").touch()
        self.per_obpi, self.legacy = pipeline_marker_paths(self.plans, _OBPI)

    def _launch(self, start_from: str | None = None) -> dict[str, Any]:
        """Write both markers exactly as the launcher does, and return the payload."""
        payload = pipeline_marker_payload(
            _OBPI,
            _ADR,
            "heavy",
            start_from,
            "pass",
            requires_human_attestation=True,
            nonce=_NONCE,
        )
        write_pipeline_markers(self.plans, payload)
        return payload

    def _advance(
        self,
        stage: str,
        kind: str,
        label: str,
        *,
        blockers: list[str] | None = None,
        updated_at: str = _CROSSED_AT,
    ) -> dict[str, Any] | None:
        return advance_pipeline_markers(
            self.plans,
            _OBPI,
            stage=stage,
            position={"kind": kind, "label": label, "boundary": _BOUNDARY},
            updated_at=updated_at,
            blockers=blockers or [],
            requires_human_attestation=True,
        )


class TestTheTwinRestoreReadsBeforeItCreates(_RunFixture):
    """A restore that cannot read its source leaves no marker file behind.

    Review finding fin-specB-twin-restore-creates-its-target-before-reading-its-source.
    ``gz state --repair`` restores the one missing marker file of a run as a
    copy of its twin. The target was created before the source was read, so a
    read that failed left an empty file where a marker is expected: unreadable
    as a marker, and in the way of the next restore. This is a property of a
    writer and no acceptance criterion, so no REQ is bound to it.
    """

    def test_a_source_that_cannot_be_read_leaves_no_target_behind(self) -> None:
        for lost in ("legacy", "per_obpi"):
            with self.subTest(missing=lost):
                self._launch()
                missing = getattr(self, lost)
                source = self.per_obpi if missing == self.legacy else self.legacy
                missing.unlink()

                with (
                    patch.object(Path, "read_bytes", side_effect=OSError("unreadable")),
                    self.assertRaises(OSError),
                ):
                    restore_pipeline_marker_twin(self.plans, _OBPI)

                self.assertFalse(missing.exists(), "a failed read creates nothing")
                self.assertEqual(
                    restore_pipeline_marker_twin(self.plans, _OBPI),
                    (missing, source),
                    "and the restore still succeeds once the source reads",
                )
                self.assertEqual(missing.read_bytes(), source.read_bytes())


class TestAnAdvancedMarkerKeepsEveryReaderWorking(_RunFixture):
    """REQ-0.35.0-15-07: the readers act on the stage reached, and nothing is lost."""

    @covers("REQ-0.35.0-15-07")
    def test_the_fence_decides_on_the_stage_the_run_has_reached(self) -> None:
        """Both marker files hand the fence the stage reached, never the launch stage.

        A full launch read ``implement`` for the whole run, so the post-Stage-2
        fence never armed. After an advance the fence must refuse a production
        write at every later stage, and refuse a production commit everywhere
        but ``sync``.
        """
        for stage, kind, label, write_refused, commit_refused in _CROSSINGS:
            with self.subTest(stage=stage):
                self._launch()
                self._advance(stage, kind, label)
                for marker_path in (self.per_obpi, self.legacy):
                    reached = marker_stage(marker_path)
                    self.assertEqual(reached, stage)
                    self.assertEqual(refuses_production_write(reached, _SRC), write_refused)
                    self.assertEqual(refuses_production_commit(reached, _SRC), commit_refused)

    @covers("REQ-0.35.0-15-07")
    def test_a_position_inside_a_stage_is_never_written_as_a_stage(self) -> None:
        """The position rides its own key; ``current_stage`` stays canonical.

        Requirement 3: the fence and the marker authenticity check both refuse a
        stage outside the canonical set, so a position written as a stage would
        trip both. An advance that names a non-canonical stage is refused and
        leaves the markers as they were.
        """
        for stage, kind, label, _write, _commit in _CROSSINGS:
            with self.subTest(stage=stage):
                self._launch()
                self._advance(stage, kind, label)
                for marker_path in (self.per_obpi, self.legacy):
                    marker = _read(marker_path)
                    self.assertIn(marker["current_stage"], CANONICAL_STAGES)
                    self.assertEqual(
                        marker.get("position"),
                        {"kind": kind, "label": label, "boundary": _BOUNDARY},
                    )

        self._launch()
        before = (self.per_obpi.read_bytes(), self.legacy.read_bytes())
        with self.assertRaises(ValueError):
            self._advance("task 2", "task", "task 2")
        self.assertEqual((self.per_obpi.read_bytes(), self.legacy.read_bytes()), before)

    @covers("REQ-0.35.0-15-07")
    def test_resume_command_and_reminder_agree_with_the_recorded_stage(self) -> None:
        """The stage-output fields are the recorded stage's, not the launch's.

        Requirement 9: at stage level they are what ``pipeline_stage_output``
        returns for that stage, so the expectation is derived from it and no
        command line is pinned here (OBPI-0.35.0-16 re-derives ``next_command``).
        """
        for stage, kind, label, _write, _commit in _CROSSINGS:
            with self.subTest(stage=stage):
                launch = self._launch()
                self._advance(stage, kind, label)
                marker = _read(self.per_obpi)
                expected = pipeline_stage_output(_OBPI, stage, requires_human_attestation=True)

                for field in _STAGE_OUTPUT_FIELDS:
                    self.assertEqual(marker[field], expected[field], field)
                self.assertEqual(pipeline_resume_command(marker), expected["next_command"])

                # output-contract: the reminder's stage line and command are what a reader sees
                reminder = pipeline_completion_reminder_message(marker, brief_status="In Progress")
                assert reminder is not None
                self.assertIn(f"Current stage: {stage}", reminder)
                self.assertIn(expected["next_command"], reminder)
                self.assertNotIn(launch["next_command"], reminder)

    @covers("REQ-0.35.0-15-07")
    def test_a_failed_verification_keeps_its_blockers_and_resumes_at_verify(self) -> None:
        """A run launched in full that fails Stage 3 reads ``verify`` with its blockers."""
        blockers = ["uv run gz test: exit 1"]
        self._launch()
        self._advance("verify", "phase", "verification-failed", blockers=blockers)
        marker = _read(self.per_obpi)

        self.assertEqual(marker["current_stage"], "verify")
        self.assertEqual(marker["blockers"], blockers)
        self.assertEqual(marker["resume_point"], "verify")
        self.assertEqual(pipeline_resume_command(marker), pipeline_command(_OBPI, "verify"))
        # output-contract: the reminder lists the blockers a reader must clear
        reminder = pipeline_completion_reminder_message(marker, brief_status="In Progress")
        assert reminder is not None
        self.assertIn("Current stage: verify", reminder)
        self.assertIn(blockers[0], reminder)

    @covers("REQ-0.35.0-15-07")
    def test_dispatch_state_is_still_read_from_an_advanced_marker(self) -> None:
        self._launch()
        chan.record_dispatch(self.root, _OBPI, role="Implementer", model="sonnet", task_id=1)
        before = load_dispatch_state(self.plans, _OBPI)
        self.assertEqual(len(before), 1)

        self._advance("verify", "phase", "verification")

        self.assertEqual(_read(self.per_obpi)["current_stage"], "verify")
        self.assertEqual(load_dispatch_state(self.plans, _OBPI), before)

    @covers("REQ-0.35.0-15-07")
    def test_an_advance_discards_nothing_the_marker_already_carried(self) -> None:
        """Requirement 8: six keys survive an advance unchanged, in both files."""
        self._launch()
        chan.record_dispatch(self.root, _OBPI, role="Implementer", model="sonnet", task_id=1)
        chan.declare_single_driver(self.root, _OBPI, reason="harness forbids subagents")
        before = _read(self.per_obpi)
        for key in _PRESERVED_KEYS:
            self.assertIn(key, before, f"fixture must carry {key} for the control to bind")

        self._advance("ceremony", "round", "verify-packet")

        for marker_path in (self.per_obpi, self.legacy):
            after = _read(marker_path)
            self.assertEqual(after["current_stage"], "ceremony")
            self.assertEqual(after["updated_at"], _CROSSED_AT)
            for key in _PRESERVED_KEYS:
                self.assertEqual(after[key], before[key], key)

    @covers("REQ-0.35.0-15-07")
    def test_both_marker_files_hold_the_same_bytes_after_an_advance(self) -> None:
        for stage, kind, label, _write, _commit in _CROSSINGS:
            with self.subTest(stage=stage):
                self._launch()
                self._advance(stage, kind, label)
                self.assertEqual(_read(self.per_obpi)["current_stage"], stage)
                self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())

    def test_an_advance_leaves_another_obpis_legacy_marker_alone(self) -> None:
        """A legacy marker naming another OBPI is that run's, and is skipped."""
        self._launch()
        self.legacy.write_text(
            json.dumps({"obpi_id": _OTHER_OBPI, "current_stage": "implement"}) + "\n",
            encoding="utf-8",
        )
        foreign = self.legacy.read_bytes()

        self._advance("verify", "phase", "verification")

        self.assertEqual(_read(self.per_obpi)["current_stage"], "verify")
        self.assertEqual(self.legacy.read_bytes(), foreign)

    def test_an_advance_falls_back_to_the_legacy_marker_and_creates_no_file(self) -> None:
        """Only ``gz state --repair`` rebuilds a missing marker (Requirement 18)."""
        self._launch()
        self.per_obpi.unlink()

        self._advance("verify", "phase", "verification")

        self.assertEqual(_read(self.legacy)["current_stage"], "verify")
        self.assertFalse(self.per_obpi.exists())

    def test_an_advance_writes_nothing_when_no_marker_exists(self) -> None:
        self.assertIsNone(self._advance("verify", "phase", "verification"))
        self.assertFalse(self.per_obpi.exists())
        self.assertFalse(self.legacy.exists())

    def test_an_advance_refuses_a_position_that_is_not_kind_label_and_boundary(self) -> None:
        """A position is exactly a non-empty kind, label and boundary, or nothing is written.

        The marker module takes the position as plain data and never imports
        the model that validates it, so it checks the shape itself: a marker
        must not carry a position a replay of the ledger could never produce.
        """
        sound = {"kind": "phase", "label": "verification", "boundary": _BOUNDARY}
        malformed: dict[str, dict[str, Any]] = {
            f"no {key}": {k: v for k, v in sound.items() if k != key} for key in sound
        }
        malformed.update({f"empty {key}": {**sound, key: ""} for key in sound})
        malformed["an extra key"] = {**sound, "ordinal": "2"}
        malformed["a label that is not text"] = {**sound, "label": 2}
        self._launch()
        before = (self.per_obpi.read_bytes(), self.legacy.read_bytes())

        for name, position in malformed.items():
            with self.subTest(position=name):
                with self.assertRaises(ValueError):
                    advance_pipeline_markers(
                        self.plans,
                        _OBPI,
                        stage="verify",
                        position=position,
                        updated_at=_CROSSED_AT,
                        blockers=[],
                        requires_human_attestation=True,
                    )
                self.assertEqual((self.per_obpi.read_bytes(), self.legacy.read_bytes()), before)


class _RecordingFixture(_RunFixture):
    """A launched run whose boundaries are recorded through ``record_position``."""

    def setUp(self) -> None:
        super().setUp()
        self.ledger = Ledger(self.root / ".gzkit" / "ledger.jsonl")

    def _launch_on_ledger(self, start_from: str | None = None, *, obpi_id: str = _OBPI) -> None:
        """Write the markers and append the launch, as ``gz obpi pipeline`` does."""
        payload = self._launch(start_from)
        self.ledger.append(
            pipeline_launched_event(
                obpi_id=obpi_id,
                parent_adr=_ADR,
                lane="heavy",
                nonce=_NONCE,
                marker_path=f".claude/plans/.pipeline-active-{obpi_id}.json",
                entry=str(payload["entry"]),
            )
        )

    def _complete_on_ledger(self, *, obpi_id: str = _OBPI) -> None:
        self.ledger.append(
            obpi_receipt_emitted_event(
                obpi_id,
                receipt_event="completed",
                attestor="test",
                obpi_completion="attested_completed",
                parent_adr=_ADR,
            )
        )

    def _validate_on_ledger(self, *, obpi_id: str = _OBPI) -> None:
        """Append a receipt that is not a completion: a ``validated`` one."""
        self.ledger.append(
            obpi_receipt_emitted_event(
                obpi_id, receipt_event="validated", attestor="test", parent_adr=_ADR
            )
        )

    def _retire_on_ledger(self, how: str, *, obpi_id: str = _OBPI) -> None:
        """Append the row that retires ``obpi_id``: a key of ``_RETIREMENTS``."""
        self.ledger.append(_RETIREMENTS[how](obpi_id, _ADR))

    def _empty_the_ledger(self) -> None:
        self.ledger.path.write_text("", encoding="utf-8")
        self.ledger = Ledger(self.ledger.path)

    def _record(
        self,
        boundary: str = "verification",
        *,
        task: str | None = None,
        blockers: list[str] | None = None,
        obpi_id: str = _OBPI,
    ) -> Any:
        """Record a crossing of a ruled boundary, as the command that marks it does.

        ``obpi_id`` is the id the command hands the recorder, however it came by it.
        """
        return record_position(
            self.ledger,
            self.plans,
            obpi_id,
            RunCrossing(boundary=boundary, task=task, blockers=blockers or []),
        )

    def _crossings(self) -> list[LedgerEvent]:
        """Read the transition rows from disk, as a process that did not write them."""
        return [
            row
            for row in Ledger(self.ledger.path).read_all()
            if row.event == "pipeline_stage_transition"
        ]

    def _markers(self) -> tuple[bytes, bytes]:
        return self.per_obpi.read_bytes(), self.legacy.read_bytes()


class TestRecordPositionWritesTheLedgerThenTheMarker(_RecordingFixture):
    """Requirement 18: one event per boundary, the ledger first and the marker second."""

    def test_a_boundary_appends_one_event_and_both_markers_take_its_time(self) -> None:
        self._launch_on_ledger()

        self._record("verification")

        crossings = self._crossings()
        self.assertEqual(len(crossings), 1)
        (crossing,) = crossings
        self.assertEqual(crossing.id, _OBPI)
        self.assertEqual(crossing.parent, _ADR)
        self.assertEqual(crossing.extra["stage"], "verify")
        self.assertEqual(crossing.extra["position_kind"], "phase")
        self.assertEqual(crossing.extra["position_label"], "verification")
        self.assertEqual(crossing.extra["boundary"], _BOUNDARY)
        for marker_path in (self.per_obpi, self.legacy):
            marker = _read(marker_path)
            self.assertEqual(marker["current_stage"], "verify")
            self.assertEqual(
                marker["position"],
                {"kind": "phase", "label": "verification", "boundary": _BOUNDARY},
            )
            self.assertEqual(marker["updated_at"], crossing.ts)
        self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())

    def test_the_event_is_on_the_ledger_before_the_marker_is_written(self) -> None:
        """The order ``record_dispatch`` uses: a marker never holds what the ledger lacks."""
        self._launch_on_ledger()
        on_ledger_at_marker_write: list[int] = []

        def _spy(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
            on_ledger_at_marker_write.append(len(self._crossings()))
            return advance_pipeline_markers(*args, **kwargs)

        with patch("gzkit.pipeline_position.advance_pipeline_markers", side_effect=_spy):
            self._record("present-evidence")

        self.assertEqual(on_ledger_at_marker_write, [1])
        self.assertEqual(_read(self.per_obpi)["current_stage"], "ceremony")

    @covers("REQ-0.35.0-15-02")
    def test_nothing_is_recorded_unless_the_ledger_shows_a_run_in_flight(self) -> None:
        """A marker on disk is not a run: in flight is read from the ledger alone.

        A run is in flight from its latest ``pipeline_launched`` until an
        ``obpi_receipt_emitted``, an ``obpi_parked`` or an ``obpi_withdrawn``
        for that id follows it. With no launch, with a receipt or a retirement
        after the launch, or with only another OBPI's launch, a boundary
        appends nothing and leaves the markers as they were.
        """
        cases = {
            "never launched": lambda: self._launch(),
            "completed after its launch": lambda: (
                self._launch_on_ledger(),
                self._complete_on_ledger(),
            ),
            "parked after its launch": lambda: (
                self._launch_on_ledger(),
                self._retire_on_ledger("parked"),
            ),
            "withdrawn after its launch": lambda: (
                self._launch_on_ledger(),
                self._retire_on_ledger("withdrawn"),
            ),
            "only another OBPI launched": lambda: self._launch_on_ledger(obpi_id=_OTHER_OBPI),
        }
        for name, arrange in cases.items():
            with self.subTest(run=name):
                self.ledger.path.write_text("", encoding="utf-8")
                self.ledger = Ledger(self.ledger.path)
                arrange()
                before = (self.per_obpi.read_bytes(), self.legacy.read_bytes())

                recorded = self._record("verification")

                self.assertIsNone(recorded)
                self.assertEqual(self._crossings(), [])
                self.assertEqual((self.per_obpi.read_bytes(), self.legacy.read_bytes()), before)

    def test_a_relaunch_after_a_receipt_is_a_run_in_flight_again(self) -> None:
        self._launch_on_ledger()
        self._complete_on_ledger()
        self._launch_on_ledger("verify")

        self._record("verification-passed")

        self.assertEqual(len(self._crossings()), 1)
        self.assertEqual(_read(self.per_obpi)["position"]["label"], "verification-passed")

    @covers("REQ-0.35.0-15-02")
    def test_a_receipt_that_is_not_a_completion_leaves_the_run_in_flight(self) -> None:
        """Only the completion receipt ends a run (Open Design Question 8).

        ``obpi_receipt_emitted`` also carries a ``validated`` receipt, which
        completes nothing. A boundary crossed after one is still recorded; the
        completion receipt then ends the run as before.
        """
        self._launch_on_ledger()
        self._validate_on_ledger()

        recorded = self._record("verification")

        self.assertIsNotNone(recorded)
        self.assertEqual([row.extra["stage"] for row in self._crossings()], ["verify"])
        self.assertEqual(_read(self.per_obpi)["current_stage"], "verify")

        self._complete_on_ledger()

        self.assertIsNone(self._record("verification-passed"))
        self.assertEqual(len(self._crossings()), 1)

    @covers("REQ-0.35.0-15-02")
    def test_an_unparked_obpi_has_no_run_until_it_is_launched_again(self) -> None:
        """Unpark starts no run: "a later launch starts a new run" (Question 12).

        The park ended the run. Unparking releases the OBPI for work and
        resumes nothing, so a boundary crossed before the next launch is
        recorded nowhere, by the launch id or by its short form.
        """
        self._launch_on_ledger()
        self._retire_on_ledger("parked")
        self.ledger.append(obpi_unparked_event(_OBPI, _ADR, "ADR-pool.interrogate"))
        before = self._markers()

        for given in (_OBPI, _SHORT_OBPI):
            with self.subTest(given=given):
                self.assertIsNone(self._record("verification", obpi_id=given))
                self.assertIsNone(in_flight_launch_id(Ledger(self.ledger.path).read_all(), given))
        self.assertEqual(self._crossings(), [])
        self.assertEqual(self._markers(), before)

        self._launch_on_ledger("verify")

        self.assertIsNotNone(self._record("verification-passed"))
        self.assertEqual(len(self._crossings()), 1)

    def test_a_deleted_marker_does_not_drop_the_crossing(self) -> None:
        """The ledger keeps the crossing; only ``gz state --repair`` rebuilds a marker."""
        self._launch_on_ledger()
        self.per_obpi.unlink()
        self.legacy.unlink()

        self._record("verification")

        self.assertEqual(len(self._crossings()), 1)
        self.assertFalse(self.per_obpi.exists())
        self.assertFalse(self.legacy.exists())
        replay = replay_pipeline_position(Ledger(self.ledger.path).read_all(), _OBPI)
        assert replay is not None
        self.assertEqual(replay.stage, "verify")

    def test_a_marker_write_failure_warns_and_never_raises(self) -> None:
        """A position is never gate evidence (Requirement 12): the command goes on."""
        self._launch_on_ledger()
        before = self.per_obpi.read_bytes()

        with (
            patch(
                "gzkit.pipeline_position.advance_pipeline_markers",
                side_effect=PermissionError("marker is read-only"),
            ),
            self.assertLogs("gzkit.pipeline_position", level="WARNING") as logged,
        ):
            self._record("verification")

        self.assertEqual(len(self._crossings()), 1)
        self.assertEqual(self.per_obpi.read_bytes(), before)
        self.assertEqual(len(logged.records), 1)
        self.assertIn(_OBPI, logged.records[0].getMessage())

    def test_a_ledger_failure_while_recording_warns_and_returns_nothing(self) -> None:
        """An I/O failure reading or appending never reaches the command (Requirement 12).

        A position is never gate evidence, so the command that marked the
        boundary keeps its own outcome. Nothing reaches the marker, because a
        marker never holds a position the ledger lacks.
        """
        failing = {
            "the append": patch.object(self.ledger, "append", side_effect=OSError("disk full")),
            "the read": patch.object(self.ledger, "read_all", side_effect=OSError("unreadable")),
        }
        for name, failure in failing.items():
            with self.subTest(failing=name):
                self._launch_on_ledger()
                before = (self.per_obpi.read_bytes(), self.legacy.read_bytes())

                with (
                    failure,
                    self.assertLogs("gzkit.pipeline_position", level="WARNING") as logged,
                ):
                    try:
                        recorded = self._record("verification")
                    except OSError as exc:
                        self.fail(f"the record failed the command that hosts it: {exc}")

                self.assertIsNone(recorded)
                self.assertEqual(self._crossings(), [])
                self.assertEqual((self.per_obpi.read_bytes(), self.legacy.read_bytes()), before)
                self.assertIn(_OBPI, logged.records[0].getMessage())

    def test_a_failure_that_is_not_io_still_raises(self) -> None:
        """Only I/O is contained: a defect in the record is not hidden as a warning."""
        self._launch_on_ledger()

        with (
            patch.object(self.ledger, "append", side_effect=ValueError("not a ledger row")),
            self.assertRaises(ValueError),
        ):
            self._record("verification")

    def test_a_blocker_is_written_whole_up_to_the_bound_and_cut_beyond_it(self) -> None:
        """One event never carries more of a blocker than the bound allows.

        A blocker within the bound is the event's blocker unchanged. One
        character more and it is cut to one line of exactly the bound, which
        keeps how it began and says how long it was.
        """
        at_bound = "uv run gz test: " + "x" * (BLOCKER_SUMMARY_WIDTH - 16)
        beyond = at_bound + "y"
        self._launch_on_ledger("verify")

        self._record("verification-failed", blockers=[at_bound, beyond])

        whole, cut = self._crossings()[-1].extra["blockers"]
        self.assertEqual(whole, at_bound)
        self.assertEqual(len(cut), BLOCKER_SUMMARY_WIDTH)
        self.assertTrue(cut.startswith("uv run gz test: xxx"))
        self.assertIn(str(len(beyond)), cut)
        self.assertEqual(_read(self.per_obpi)["blockers"], [whole, cut])

    def test_a_failed_verification_carries_its_blockers_to_both_files(self) -> None:
        blockers = ["uv run gz test: exit 1"]
        self._launch_on_ledger("verify")

        self._record("verification-failed", blockers=blockers)

        (crossing,) = self._crossings()
        self.assertEqual(crossing.extra["blockers"], blockers)
        for marker_path in (self.per_obpi, self.legacy):
            marker = _read(marker_path)
            self.assertEqual(marker["blockers"], blockers)
            self.assertEqual(marker["resume_point"], "verify")

    def test_a_malformed_crossing_is_refused_before_the_ledger_is_written(self) -> None:
        """A boundary outside the ruled set, or a task where none belongs, is never recorded.

        A command names its boundary and nothing else, so it cannot record a
        stage of its own choosing: a stage name is not a boundary. A boundary
        that names a task needs one, and no other boundary takes one.
        """
        self._launch_on_ledger()
        before = (self.per_obpi.read_bytes(), self.legacy.read_bytes())
        malformed: tuple[tuple[str, str | None], ...] = (
            ("sync", None),
            ("gz obpi precomplete", None),
            ("task-start", None),
            ("task-complete", ""),
            ("precomplete", "TASK-0.99.0-01-01-01"),
        )

        for boundary, task in malformed:
            with self.subTest(boundary=boundary, task=task):
                with self.assertRaises(ValueError):
                    self._record(boundary, task=task)
                self.assertEqual(self._crossings(), [])
                self.assertEqual((self.per_obpi.read_bytes(), self.legacy.read_bytes()), before)

    def test_every_ruled_boundary_moves_the_stage_or_records_in_place_as_ruled(self) -> None:
        """Requirement 2 (a) and (b), for every boundary at every stage a run can be in.

        The expectation is written here from the ruling, not read from the
        table: six boundaries begin a stage's work and move the run to it; the
        other eight record inside the stage the launch reached. The kind is
        always the kind of the stage recorded.
        """
        moves_to = {
            "dispatch": "implement",
            "task-start": "implement",
            "verification": "verify",
            "ceremony": "ceremony",
            "present-evidence": "ceremony",
            "complete": "sync",
        }
        in_place = {
            "task-complete",
            "task-block",
            "task-escalate",
            "verification-passed",
            "verification-failed",
            "precomplete",
            "verify-packet",
            "acceptance-review",
        }
        names_task = {"dispatch", "task-start", "task-complete", "task-block", "task-escalate"}
        kind_of = {"implement": "task", "verify": "phase", "ceremony": "round", "sync": "step"}
        self.assertEqual(set(RULED_BOUNDARIES), set(moves_to) | in_place)
        self.assertEqual(tuple(STAGE_POSITION_KIND), CANONICAL_STAGES)

        for start_from, (_entry, launched_at, _resume, _action) in _LAUNCH_VALUES.items():
            for boundary in sorted(RULED_BOUNDARIES):
                with self.subTest(launched_at=launched_at, boundary=boundary):
                    self.ledger.path.write_text("", encoding="utf-8")
                    self.ledger = Ledger(self.ledger.path)
                    self._launch_on_ledger(start_from)
                    task = "TASK-0.99.0-01-01-01" if boundary in names_task else None

                    self._record(boundary, task=task)

                    (crossing,) = self._crossings()
                    stage = moves_to.get(boundary, launched_at)
                    self.assertEqual(crossing.extra["stage"], stage)
                    self.assertEqual(crossing.extra["position_kind"], kind_of[stage])
                    self.assertEqual(crossing.extra["position_label"], task or boundary)
                    self.assertEqual(_read(self.per_obpi)["current_stage"], stage)
                    self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())

    def test_an_in_place_boundary_reads_the_stage_from_the_ledger_not_the_marker(self) -> None:
        """A marker is never what the decision rests on (Requirement 12).

        The ledger says the run has reached ``ceremony``. The marker is then
        made to say ``implement``, as a stale or hand-edited file would. A
        check recorded now lands inside ``ceremony``, and the marker is brought
        back to what the ledger says.
        """
        self._launch_on_ledger()
        self._record("ceremony")
        stale = _read(self.per_obpi)
        stale["current_stage"] = "implement"
        write_pipeline_markers(self.plans, stale)

        self._record("precomplete")

        self.assertEqual(self._crossings()[-1].extra["stage"], "ceremony")
        for marker_path in (self.per_obpi, self.legacy):
            self.assertEqual(_read(marker_path)["current_stage"], "ceremony")
            self.assertEqual(_read(marker_path)["position"]["kind"], "round")


class TestOnlyAVerificationResultOrNewWorkSettlesBlockers(_RecordingFixture):
    """A check never erases a failed verification (Requirement 9).

    Review finding fc1-aux-in-place-record-after-failed-verification-drops-blockers:
    a check recorded after a failed verification wrote no blockers, the replay
    keeps the last crossing's blockers, and the marker of a run whose
    verification had failed then read no blockers and a resume point of
    ``ceremony``. The ruling, written here and not read from the table: a
    verification result sets the run's blockers to its own; a boundary that
    begins work clears them; every other boundary carries them forward.
    """

    _FOUND = ("uv run gz test: exit 1", "uv run gz lint: exit 1")
    _TASK = "TASK-0.99.0-01-01-01"
    _CARRIES = (
        "precomplete",
        "verify-packet",
        "acceptance-review",
        "task-complete",
        "task-block",
        "task-escalate",
    )
    _BEGINS_WORK = (
        "dispatch",
        "task-start",
        "verification",
        "ceremony",
        "present-evidence",
        "complete",
    )
    _RESULTS = ("verification-passed", "verification-failed")
    _NAMES_TASK = ("dispatch", "task-start", "task-complete", "task-block", "task-escalate")

    def _task(self, boundary: str) -> str | None:
        return self._TASK if boundary in self._NAMES_TASK else None

    def _stage_output(self, marker_path: Path) -> dict[str, Any]:
        marker = _read(marker_path)
        return {field: marker[field] for field in _STAGE_OUTPUT_FIELDS}

    def _fail_a_verification(self) -> dict[str, Any]:
        """Launch a run and fail its verification; return what the failure left to read."""
        self.ledger.path.write_text("", encoding="utf-8")
        self.ledger = Ledger(self.ledger.path)
        self._launch_on_ledger()
        self._record("verification")
        self._record("verification-failed", blockers=list(self._FOUND))
        as_failed = self._stage_output(self.per_obpi)
        self.assertEqual(
            (as_failed["blockers"], as_failed["resume_point"]), (list(self._FOUND), "verify")
        )
        return as_failed

    def test_the_three_kinds_are_the_whole_ruled_set(self) -> None:
        self.assertEqual(
            set(RULED_BOUNDARIES), {*self._CARRIES, *self._BEGINS_WORK, *self._RESULTS}
        )

    def test_a_check_or_a_bookkeeping_event_carries_the_failure_forward(self) -> None:
        """The event, the replay and both markers still say what the verification found."""
        for boundary in self._CARRIES:
            with self.subTest(boundary=boundary):
                as_failed = self._fail_a_verification()

                reached = self._record(boundary, task=self._task(boundary))

                for marker_path in (self.per_obpi, self.legacy):
                    self.assertEqual(self._stage_output(marker_path), as_failed)
                    self.assertEqual(
                        _read(marker_path)["position"]["label"], self._task(boundary) or boundary
                    )
                self.assertEqual(reached.blockers, list(self._FOUND))
                self.assertEqual(self._crossings()[-1].extra.get("blockers"), list(self._FOUND))

    def test_checks_run_one_after_another_still_carry_the_failure(self) -> None:
        as_failed = self._fail_a_verification()

        for boundary in self._CARRIES:
            self._record(boundary, task=self._task(boundary))

        self.assertEqual(self._stage_output(self.per_obpi), as_failed)
        self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())
        replay = replay_pipeline_position(Ledger(self.ledger.path).read_all(), _OBPI)
        assert replay is not None
        self.assertEqual(replay.blockers, list(self._FOUND))

    def test_a_boundary_that_begins_work_clears_the_failure(self) -> None:
        """New work answers the failure: nothing is carried into the stage it enters."""
        for boundary in self._BEGINS_WORK:
            with self.subTest(boundary=boundary):
                self._fail_a_verification()

                reached = self._record(boundary, task=self._task(boundary))

                self.assertEqual(reached.blockers, [])
                self.assertFalse(self._crossings()[-1].extra.get("blockers"))
                for marker_path in (self.per_obpi, self.legacy):
                    self.assertEqual(_read(marker_path)["blockers"], [])

    def test_a_verification_result_sets_the_blockers_to_its_own(self) -> None:
        """A later failure replaces what was found, a pass leaves nothing; neither adds."""
        later = ["uv run gz typecheck: exit 1"]
        results: tuple[tuple[str, list[str]], ...] = (
            ("verification-failed", later),
            ("verification-passed", []),
        )
        for boundary, own in results:
            with self.subTest(boundary=boundary):
                self._fail_a_verification()
                self._record("precomplete")

                reached = self._record(boundary, blockers=own)

                self.assertEqual(reached.blockers, own)
                for marker_path in (self.per_obpi, self.legacy):
                    self.assertEqual(_read(marker_path)["blockers"], own)

    def test_a_crossing_that_settles_no_blockers_is_refused_when_it_names_some(self) -> None:
        """Only a verification result names blockers; any other crossing that does is malformed.

        Dropping them would lose what the caller found without a word, and
        writing them would let a check overwrite a verification's result.
        """
        self._launch_on_ledger()
        before = self._markers()

        for boundary in (*self._CARRIES, *self._BEGINS_WORK):
            with self.subTest(boundary=boundary):
                with self.assertRaises(ValueError):
                    self._record(boundary, task=self._task(boundary), blockers=["a finding"])
                self.assertEqual(self._crossings(), [])
                self.assertEqual(self._markers(), before)


class TestTheRecorderFindsTheRunItself(_RecordingFixture):
    """REQ-0.35.0-15-02: the run is matched where every producer passes, in the recorder.

    A producer hands over the id it holds. The launch row carries the id the
    launcher resolved, and the two differ whenever a command was given, or
    derived, the short ``OBPI-<semver>-<item>`` form. Resolving it in each
    caller left a caller out twice (review findings
    QR2-REQ02-noncanonical-id-records-nothing and
    fc1-REQ02-task-start-resolves-its-obpi-id-unlike-the-launcher), so the rule
    is the recorder's: among the runs in flight, the one whose id is the id
    given, or else the one whose short form is.
    """

    @covers("REQ-0.35.0-15-02")
    def test_the_launch_id_and_its_short_form_both_name_the_run(self) -> None:
        """Either spelling records one event, under the id the launch carries."""
        for name, given in (("the launch id", _OBPI), ("its short form", _SHORT_OBPI)):
            with self.subTest(given=name):
                self.ledger.path.write_text("", encoding="utf-8")
                self.ledger = Ledger(self.ledger.path)
                self._launch_on_ledger()

                reached = self._record("verification", obpi_id=given)

                crossings = self._crossings()
                self.assertEqual(len(crossings), 1, "the boundary is recorded")
                (crossing,) = crossings
                self.assertEqual((crossing.id, crossing.parent), (_OBPI, _ADR))
                self.assertIsNotNone(reached)
                self.assertEqual(reached.stage, "verify")
                for marker_path in (self.per_obpi, self.legacy):
                    marker = _read(marker_path)
                    self.assertEqual(marker["current_stage"], "verify")
                    self.assertEqual(marker["position"]["label"], "verification")
                    self.assertEqual(marker["updated_at"], crossing.ts)

    @covers("REQ-0.35.0-15-02")
    def test_a_short_form_names_the_run_in_flight_when_its_sibling_has_ended(self) -> None:
        """Only a run in flight is a candidate: a finished sibling is no ambiguity."""
        self._launch_on_ledger(obpi_id=_SIBLING_OBPI)
        self._complete_on_ledger(obpi_id=_SIBLING_OBPI)
        self._launch_on_ledger()

        self._record("verification", obpi_id=_SHORT_OBPI)

        self.assertEqual([row.id for row in self._crossings()], [_OBPI])
        self.assertEqual(_read(self.per_obpi)["current_stage"], "verify")

    def _assert_a_retired_siblings_launch_is_no_second_run(self, how: str) -> None:
        """A sibling launched, never receipted and then retired leaves one run in flight.

        Review finding
        fc2-REQ02-a-retired-siblings-unreceipted-launch-is-still-a-run-in-flight,
        first half. No command writes a receipt for an OBPI that is parked or
        withdrawn, so its launch stayed a run in flight for good, and a
        producer holding the short form then saw two runs and recorded
        nothing. The retirement ends the sibling's run, whichever of the two
        was launched first, and it ends no run but the sibling's.
        """
        orders: dict[str, Callable[[], object]] = {
            "the sibling launched and retired first": lambda: (
                self._launch_on_ledger(obpi_id=_SIBLING_OBPI),
                self._retire_on_ledger(how, obpi_id=_SIBLING_OBPI),
                self._launch_on_ledger(),
            ),
            "the sibling retired after the live launch": lambda: (
                self._launch_on_ledger(obpi_id=_SIBLING_OBPI),
                self._launch_on_ledger(),
                self._retire_on_ledger(how, obpi_id=_SIBLING_OBPI),
            ),
        }
        for order, arrange in orders.items():
            with self.subTest(order=order):
                self._empty_the_ledger()
                arrange()

                with self.assertNoLogs("gzkit.pipeline_position", level="WARNING"):
                    reached = self._record("verification", obpi_id=_SHORT_OBPI)

                self.assertEqual(
                    [row.id for row in self._crossings()], [_OBPI], "recorded under the live run"
                )
                self.assertIsNotNone(reached)
                for marker_path in (self.per_obpi, self.legacy):
                    self.assertEqual(_read(marker_path)["current_stage"], "verify")

    @covers("REQ-0.35.0-15-02")
    def test_a_withdrawn_sibling_that_was_launched_is_no_second_run(self) -> None:
        """A short-form producer records under the live run, and nothing warns."""
        self._assert_a_retired_siblings_launch_is_no_second_run("withdrawn")

    @covers("REQ-0.35.0-15-02")
    def test_a_parked_sibling_that_was_launched_is_no_second_run(self) -> None:
        """Parking ends a run as withdrawal does: one run in flight, no warning."""
        self._assert_a_retired_siblings_launch_is_no_second_run("parked")

    @covers("REQ-0.35.0-15-02")
    def test_a_superseded_sibling_that_was_launched_is_no_second_run(self) -> None:
        """A supersede ends a run (Open Design Question 16): one run in flight, no warning.

        No command writes a receipt for a superseded OBPI either, so its
        launch stayed a run in flight for good and the short form named two.
        """
        self._assert_a_retired_siblings_launch_is_no_second_run("superseded")

    @covers("REQ-0.35.0-15-02")
    def test_a_parked_obpi_launched_again_is_in_flight_again(self) -> None:
        """Parking ends the run, and a later launch starts a new one.

        Operator ruling 2026-10-11 (Open Design Question 12): retirement ends
        a run. Park is the reversible retirement, so the OBPI can be launched
        again, and the run in flight is then that launch's.
        """
        self._launch_on_ledger()
        self._record("verification")
        self._retire_on_ledger("parked")

        self.assertIsNone(self._record("verification-passed", obpi_id=_SHORT_OBPI))
        self.assertEqual(len(self._crossings()), 1, "a parked OBPI has no run in flight")

        self._launch_on_ledger("verify")
        reached = self._record("verification-passed", obpi_id=_SHORT_OBPI)

        self.assertEqual([row.id for row in self._crossings()], [_OBPI, _OBPI])
        self.assertIsNotNone(reached)
        self.assertEqual(_read(self.per_obpi)["position"]["label"], "verification-passed")

    @covers("REQ-0.35.0-15-02")
    def test_a_superseded_obpis_own_id_names_no_run(self) -> None:
        """Neither the launch id nor its short form names a run once it is superseded.

        Open Design Question 16: "supersede ends a run". The recorder then
        records nothing for either spelling, warns of nothing, and leaves the
        ledger and both marker files as they were.
        """
        self._launch_on_ledger()
        self._record("verification")
        self._retire_on_ledger("superseded")
        rows = list(Ledger(self.ledger.path).read_all())
        before = self._markers()

        for name, given in (("the launch id", _OBPI), ("its short form", _SHORT_OBPI)):
            with self.subTest(given=name):
                self.assertIsNone(in_flight_launch_id(rows, given))
                with self.assertNoLogs("gzkit.pipeline_position", level="WARNING"):
                    recorded = self._record("verification-passed", obpi_id=given)

                self.assertIsNone(recorded)
                self.assertEqual(len(self._crossings()), 1, "nothing after the supersede")
                self.assertEqual(self._markers(), before)

    @covers("REQ-0.35.0-15-02")
    def test_a_superseded_obpi_launched_again_is_in_flight_again(self) -> None:
        """A supersede ends the run it finds; a launch after it starts a new one.

        The rule is the ledger's order and nothing else (Open Design Questions
        12 and 16): the run in flight is the latest launch with no row after
        it that ends a run. Whether a superseded OBPI may be launched is the
        launcher's to decide, not the recorder's.
        """
        self._launch_on_ledger()
        self._retire_on_ledger("superseded")
        self._launch_on_ledger("verify")
        rows = list(Ledger(self.ledger.path).read_all())

        for name, given in (("the launch id", _OBPI), ("its short form", _SHORT_OBPI)):
            with self.subTest(given=name):
                self.assertEqual(in_flight_launch_id(rows, given), _OBPI)
        reached = self._record("verification-passed", obpi_id=_SHORT_OBPI)

        self.assertIsNotNone(reached)
        self.assertEqual([row.id for row in self._crossings()], [_OBPI])
        self.assertEqual(_read(self.per_obpi)["position"]["label"], "verification-passed")

    @covers("REQ-0.35.0-15-02")
    def test_the_short_form_is_the_whole_item_number_whatever_its_width(self) -> None:
        """Item 10 never names item 100, and a one-digit item has a short form.

        Review finding
        fc2-AUX-short-form-is-two-digits-in-the-recorder-and-any-digits-in-the-id-grammar.
        The id grammar gives an item any number of digits. A short form cut
        at two of them let item 10's short id name item 100's run, an
        unrelated OBPI, while item 100's own short id and every one-digit
        item's named nothing.
        """
        wide, narrow = "OBPI-0.99.0-100-wide-item", "OBPI-0.99.0-7-narrow-item"
        self._launch_on_ledger(obpi_id=wide)
        self._launch_on_ledger(obpi_id=narrow)

        for stranger in ("OBPI-0.99.0-10", "OBPI-0.99.0-1", "OBPI-0.99.0-1000", "OBPI-0.99.0-70"):
            with self.subTest(given=stranger):
                with self.assertNoLogs("gzkit.pipeline_position", level="WARNING"):
                    recorded = self._record("verification", obpi_id=stranger)

                self.assertIsNone(recorded, "another item's short form names no run")
        self.assertEqual(self._crossings(), [])

        for given, launch_id in (("OBPI-0.99.0-100", wide), ("OBPI-0.99.0-7", narrow)):
            with self.subTest(given=given):
                reached = self._record("verification", obpi_id=given)

                self.assertIsNotNone(reached, "an item's own short form names its run")
                self.assertEqual(self._crossings()[-1].id, launch_id)
        self.assertEqual([row.id for row in self._crossings()], [wide, narrow])

    @covers("REQ-0.35.0-15-02")
    def test_two_runs_in_flight_sharing_a_short_form_record_nothing_and_warn_once(self) -> None:
        """A short form that names two runs names neither, and says so.

        Guessing would file a crossing under the wrong run, and silence would
        be the defect again: a ruled boundary unrecorded with nothing to show
        for it. One warning names both runs. Each run's own id still names it.
        """
        self._launch_on_ledger()
        self._launch_on_ledger(obpi_id=_SIBLING_OBPI)
        before = self._markers()

        with self.assertLogs("gzkit.pipeline_position", level="WARNING") as logged:
            recorded = self._record("verification", obpi_id=_SHORT_OBPI)

        self.assertIsNone(recorded)
        self.assertEqual(self._crossings(), [])
        self.assertEqual(self._markers(), before)
        self.assertEqual(len(logged.records), 1)
        message = logged.records[0].getMessage()
        self.assertIn(_OBPI, message)
        self.assertIn(_SIBLING_OBPI, message)

        for own_id in (_SIBLING_OBPI, _OBPI):
            with self.subTest(given=own_id):
                self._record("verification", obpi_id=own_id)

                self.assertEqual(self._crossings()[-1].id, own_id)
        self.assertEqual(len(self._crossings()), 2)

    @covers("REQ-0.35.0-15-02")
    def test_an_id_that_is_neither_the_launch_id_nor_its_short_form_names_no_run(self) -> None:
        """Another OBPI, a shorter prefix and a longer one each record nothing, silently.

        The short form is the whole of ``OBPI-<semver>-<item>`` and nothing
        looser: a prefix match would let ``OBPI-0.99.0-0`` or the ADR's semver
        name a run, and a longer prefix of the slug is not an id anyone holds.
        """
        self._launch_on_ledger()
        before = self._markers()
        strangers = (
            _OTHER_OBPI,
            "OBPI-0.99.0-02",
            "OBPI-0.99.0-0",
            "OBPI-0.99.0",
            f"{_SHORT_OBPI}-run",
            f"{_OBPI}-again",
            _SIBLING_OBPI,
            "",
        )

        for given in strangers:
            with self.subTest(given=given):
                with self.assertNoLogs("gzkit.pipeline_position", level="WARNING"):
                    recorded = self._record("verification", obpi_id=given)

                self.assertIsNone(recorded)
                self.assertEqual(self._crossings(), [])
                self.assertEqual(self._markers(), before)


class TestThePositionModuleImportsOnItsOwn(unittest.TestCase):
    """A hook or script may import the runtime before any other gzkit module."""

    def test_the_module_is_importable_first_in_a_fresh_interpreter(self) -> None:
        """The recorder names a ledger event, and must not import it through a cycle.

        ``gzkit.ledger_events`` imports ``gzkit.ledger``, which imports it back,
        so importing the events module first fails. A suite never sees that:
        some earlier test has always loaded the ledger. Only a fresh
        interpreter does, which is what a hook is.
        """
        for module in ("gzkit.pipeline_position", "gzkit.pipeline_runtime"):
            with self.subTest(module=module):
                result = subprocess.run(
                    [sys.executable, "-c", f"import {module}"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr[-600:])


class _LaunchableThroughTheCli(unittest.TestCase):
    """An isolated project whose run is driven through the real ``gz`` commands.

    Every reading is taken from disk, as a process that did not perform the run
    takes it: the ledger rows and the two marker files.
    """

    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        self.per_obpi, self.legacy = seed_launchable_obpi(with_reqs=True)

    def _gz(self, *args: str, exit_code: int = 0) -> str:
        """Run one ``gz`` command, assert its exit code and return what it printed."""
        result = self.runner.invoke(main, list(args))
        self.assertEqual(result.exit_code, exit_code, result.output)
        return result.output

    def _rows(self, event: str) -> list[LedgerEvent]:
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        return [row for row in ledger.read_all() if row.event == event]

    def _crossings(self) -> list[LedgerEvent]:
        return [row for row in self._rows("pipeline_stage_transition") if row.id == _CLI_OBPI]

    def _assert_crossed(
        self, before: int, *, stage: str, kind: str, label: str, boundary: str
    ) -> LedgerEvent:
        """One event was appended, and both marker files name what it recorded."""
        crossings = self._crossings()
        self.assertEqual(len(crossings), before + 1, "exactly one event for one boundary")
        crossing = crossings[-1]
        recorded = crossing.extra
        self.assertEqual(
            (
                recorded["stage"],
                recorded["position_kind"],
                recorded["position_label"],
                recorded["boundary"],
            ),
            (stage, kind, label, boundary),
        )
        self._assert_markers_read(crossing)
        return crossing

    def _verify(
        self,
        *,
        failing: bool = False,
        at_dispatch: Callable[[], None] | None = None,
        detail: str = "exit 1",
    ) -> list[str]:
        """Enter Stage 3 through ``gz obpi pipeline --from=verify``.

        Returns the blockers a failed verification finds, as the console prints
        them; what the run printed is kept in ``self.printed``.
        """
        with verification_replaced(
            failing=failing, detail=detail, at_dispatch=at_dispatch
        ) as blockers:
            self.printed = self._gz(
                "obpi", "pipeline", _CLI_OBPI, "--from=verify", exit_code=1 if failing else 0
            )
        return blockers

    def _precomplete(
        self,
        *,
        exit_code: int = 0,
        found: list[Any] | None = None,
        obpi_id: str = _CLI_OBPI,
    ) -> None:
        """Run ``gz obpi precomplete`` with its checks replaced by ``found``."""
        with precomplete_checks_replaced(found):
            self._gz("obpi", "precomplete", obpi_id, "--json", exit_code=exit_code)

    def _complete(self, *, failing_write: bool = False, obpi_id: str = _CLI_OBPI) -> None:
        """Run ``gz obpi complete`` to its transaction, with every gate replaced."""
        args = tuple(obpi_id if arg == _CLI_OBPI else arg for arg in COMPLETE_ARGS)
        with completion_gates_replaced(failing_write=failing_write):
            self._gz(*args, exit_code=2 if failing_write else 0)

    def _assert_markers_read(self, crossing: LedgerEvent) -> None:
        """Both files carry the crossing's stage, position and time, byte for byte alike.

        ``updated_at`` is the event's own ``ts``, which the ledger fixes when it
        appends the row, so the marker can only have been written after it.
        """
        recorded = crossing.extra
        for marker_path in (self.per_obpi, self.legacy):
            marker = _read(marker_path)
            self.assertEqual(marker["current_stage"], recorded["stage"])
            self.assertEqual(
                marker["position"],
                {
                    "kind": recorded["position_kind"],
                    "label": recorded["position_label"],
                    "boundary": recorded["boundary"],
                },
            )
            self.assertEqual(marker["updated_at"], crossing.ts)
        self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())


class TestEachBoundaryNamesThePositionInsideItsStage(_LaunchableThroughTheCli):
    """REQ-0.35.0-15-02: the task, phase, round or step reached is on the marker."""

    @covers("REQ-0.35.0-15-02")
    def test_each_stage_2_boundary_names_the_task_reached(self) -> None:
        """A dispatch and each ``gz task`` event record the Stage 2 task they mark.

        The launch auto-starts one TASK per REQ and records no position
        (REQ-0.35.0-15-04). Every later boundary appends exactly one event and
        the marker names its task: the dispatched task by its index, a TASK
        event by its TASK id.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        first_task = self._rows("task_started")[0].extra["task_id"]
        self.assertEqual(self._crossings(), [], "a bare launch records no position")
        self._gz("task", "start", "--req", _CLI_REQS[0], "--seq", "next")
        subdivided = self._rows("task_started")[-1].extra["task_id"]
        self.assertNotEqual(subdivided, first_task)
        self._assert_crossed(
            0, stage="implement", kind="task", label=subdivided, boundary="gz task start"
        )

        boundaries: tuple[tuple[tuple[str, ...], str, str], ...] = (
            (
                ("obpi", "dispatch", _CLI_OBPI, "--role", "Implementer", "--model", "sonnet")
                + ("--task", "2"),
                "task 2",
                "gz obpi dispatch",
            ),
            (("task", "complete", first_task), first_task, "gz task complete"),
            (("task", "block", subdivided, "--reason", "waits"), subdivided, "gz task block"),
            (("task", "start", subdivided), subdivided, "gz task start"),
            (
                ("task", "escalate", subdivided, "--reason", "needs a ruling"),
                subdivided,
                "gz task escalate",
            ),
        )
        for args, label, boundary in boundaries:
            with self.subTest(boundary=boundary, label=label):
                before = len(self._crossings())

                self._gz(*args)

                self._assert_crossed(
                    before, stage="implement", kind="task", label=label, boundary=boundary
                )

    @covers("REQ-0.35.0-15-02")
    def test_verification_names_its_phase_at_start_on_failure_and_on_pass(self) -> None:
        """Stage 3 records its start, then a failure with its blockers, or a pass.

        A passed verification chains straight into the ceremony, so the last
        crossing of that run is the Stage 4 round it entered.
        """
        boundary = "gz obpi pipeline"
        self._gz("obpi", "pipeline", _CLI_OBPI)
        at_start: dict[str, Any] = {}

        def _read_at_start() -> None:
            at_start["crossings"] = self._crossings()
            at_start["markers"] = [_read(self.per_obpi), _read(self.legacy)]

        blockers = self._verify(failing=True, at_dispatch=_read_at_start)

        self.assertEqual(len(at_start["crossings"]), 1, "one event when verification starts")
        started = at_start["crossings"][0].extra
        self.assertEqual(
            (started["stage"], started["position_kind"], started["position_label"]),
            ("verify", "phase", "verification"),
        )
        for marker in at_start["markers"]:
            self.assertEqual(marker["current_stage"], "verify")
            self.assertEqual(
                marker["position"],
                {"kind": "phase", "label": "verification", "boundary": boundary},
            )
        failed = self._assert_crossed(
            1, stage="verify", kind="phase", label="verification-failed", boundary=boundary
        )
        self.assertEqual(failed.extra["blockers"], blockers)
        self.assertEqual(_read(self.per_obpi)["blockers"], blockers)

        before = len(self._crossings())
        self._verify()

        passed = self._crossings()[before:]
        self.assertEqual(
            [(row.extra["stage"], row.extra["position_label"]) for row in passed],
            [
                ("verify", "verification"),
                ("verify", "verification-passed"),
                ("ceremony", "ceremony"),
            ],
        )
        self._assert_markers_read(passed[-1])
        self.assertEqual(_read(self.per_obpi)["blockers"], [])

    def test_a_failed_verification_writes_a_bounded_summary_of_its_output(self) -> None:
        """The ledger gets a summary of each blocker; the console keeps the output.

        The failing command here prints several kilobytes, as a failed test run
        does. The verify runner hands the whole output over as the blocker.
        The transition event holds at most the bound for it, on one line,
        beginning with the command that failed; the output itself is printed
        to the operator in full and is not on the ledger.
        """
        output = "\n".join(f"FAIL: test_case_{n} (AssertionError: {n} != 0)" for n in range(200))
        self.assertGreater(len(output), 8000)
        self._gz("obpi", "pipeline", _CLI_OBPI)

        (blocker,) = self._verify(failing=True, detail=output)

        failed = self._crossings()[-1]
        self.assertEqual(failed.extra["position_label"], "verification-failed")
        (summary,) = failed.extra["blockers"]
        self.assertLessEqual(len(summary), BLOCKER_SUMMARY_WIDTH)
        self.assertNotIn("\n", summary)
        self.assertTrue(summary.startswith(blocker[:60].split("\n")[0]))
        self.assertNotIn("test_case_199", json.dumps(failed.extra))
        self.assertIn("test_case_199", self.printed)
        self.assertEqual(_read(self.per_obpi)["blockers"], [summary])
        self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())

    @covers("REQ-0.35.0-15-02")
    def test_entering_the_ceremony_names_the_round_reached(self) -> None:
        self._gz("obpi", "pipeline", _CLI_OBPI)

        with patch("gzkit.commands.obpi_stages.acceptance_blockers", new=lambda *_a, **_k: []):
            self._gz("obpi", "pipeline", _CLI_OBPI, "--from=ceremony")

        self._assert_crossed(
            0, stage="ceremony", kind="round", label="ceremony", boundary="gz obpi pipeline"
        )

    @covers("REQ-0.35.0-15-02")
    def test_each_stage_4_boundary_names_the_round_reached(self) -> None:
        """Evidence presentation, packet verification and Stage 4 review imports mark a round.

        The work each command does is replaced, so what is exercised is the
        boundary it marks: one event, and the round named on both marker files.
        The packet names its OBPI by the path the pipeline skill prescribes.
        The review imported here is adversarial; a human review always is a
        Stage 4 round.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        rounds: tuple[tuple[tuple[str, ...], str, str], ...] = (
            (
                ("obpi", "present-evidence", _CLI_OBPI, "--json"),
                "present-evidence",
                "gz obpi present-evidence",
            ),
            (
                ("obpi", "verify-packet", write_stage4_packet(_CLI_OBPI), "--json"),
                "verify-packet",
                "gz obpi verify-packet",
            ),
            (
                ("obpi", "acceptance", _CLI_OBPI, "review", "--receipt", write_review_receipt()),
                "acceptance-review",
                "gz obpi acceptance",
            ),
            (
                ("obpi", "acceptance", _CLI_OBPI, "human-review", "--attestor", "g0")
                + ("--ruling", "accepted as shown"),
                "acceptance-review",
                "gz obpi acceptance",
            ),
        )
        for args, label, boundary in rounds:
            with self.subTest(boundary=boundary, action=args[1:4]):
                before = len(self._crossings())

                with stage4_work_replaced():
                    self._gz(*args)

                self._assert_crossed(
                    before, stage="ceremony", kind="round", label=label, boundary=boundary
                )

    @covers("REQ-0.35.0-15-02")
    def test_precomplete_records_inside_the_stage_reached_and_never_moves_it(self) -> None:
        """``gz obpi precomplete`` is a check: it names itself inside the stage reached.

        Operator ruling 2026-10-11 (Open Design Question 9, which supersedes
        both Question 5 rulings): only a command that begins a stage's work
        moves the stage. Precomplete runs as the verify runner's last command
        and again as Stage 5 Step 0, and wherever it runs it records the kind
        of the stage the ledger says the run has reached, with its own name as
        the label. A run reaches ``sync`` at ``gz obpi complete`` and never at
        a check. The checks are replaced, and a breach records the same
        position and still exits 3.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        breach = Mock(ok=False)
        breach.model_dump.return_value = {"name": "lock_held", "ok": False}
        stages: tuple[tuple[str, str, Callable[[], object]], ...] = (
            ("implement", "task", lambda: None),
            ("verify", "phase", lambda: self._verify(failing=True)),
            ("ceremony", "round", self._verify),
            ("sync", "step", lambda: self._complete(failing_write=True)),
        )
        for stage, kind, reach in stages:
            reach()
            self.assertEqual(_read(self.per_obpi)["current_stage"], stage)
            for found, exit_code in (([], 0), ([breach], 3)):
                with self.subTest(run_at=stage, exit_code=exit_code):
                    before = len(self._crossings())

                    self._precomplete(found=found, exit_code=exit_code)

                    self._assert_crossed(
                        before,
                        stage=stage,
                        kind=kind,
                        label="precomplete",
                        boundary="gz obpi precomplete",
                    )

    @covers("REQ-0.35.0-15-02")
    def test_a_stage_3_run_never_reads_sync_before_the_ceremony(self) -> None:
        """The verify runner's own precomplete records in place: a Stage 3 phase.

        The precomplete command runs here at the moment the runner would run its
        verification commands, of which it is the last. The ledger then holds
        the run's crossings in order, and none names ``sync``.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)

        self._verify(at_dispatch=self._precomplete)

        self.assertEqual(
            [(row.extra["stage"], row.extra["position_label"]) for row in self._crossings()],
            [
                ("verify", "verification"),
                ("verify", "precomplete"),
                ("verify", "verification-passed"),
                ("ceremony", "ceremony"),
            ],
        )

    @covers("REQ-0.35.0-15-02")
    def test_complete_names_its_step_before_the_receipt_ends_the_run(self) -> None:
        """``gz obpi complete`` records its step as its transaction starts.

        Operator ruling 2026-10-11 (Open Design Question 8): the receipt ends
        the run, so the step is on the ledger before the receipt row, and no
        boundary crossed after the receipt records anything.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)

        self._complete()

        self.assertEqual(len(self._rows("obpi_receipt_emitted")), 1, "the completion landed")
        self._assert_crossed(
            0, stage="sync", kind="step", label="complete", boundary="gz obpi complete"
        )
        in_order = [
            row.event
            for row in Ledger(Path(".gzkit/ledger.jsonl")).read_all()
            if row.id == _CLI_OBPI
        ]
        self.assertLess(
            in_order.index("pipeline_stage_transition"), in_order.index("obpi_receipt_emitted")
        )

        self._precomplete()
        self._gz("task", "start", "--req", _CLI_REQS[0], "--seq", "next")
        self.assertEqual(len(self._crossings()), 1, "nothing records after the receipt")

    def test_a_completion_that_fails_its_write_still_leaves_the_step_it_reached(self) -> None:
        """The record says the run reached the step, not that completion succeeded."""
        self._gz("obpi", "pipeline", _CLI_OBPI)

        self._complete(failing_write=True)

        self.assertEqual(self._rows("obpi_receipt_emitted"), [])
        self._assert_crossed(
            0, stage="sync", kind="step", label="complete", boundary="gz obpi complete"
        )

    @covers("REQ-0.35.0-15-02")
    def test_only_a_stage_4_review_import_records_and_it_never_moves_the_stage(self) -> None:
        """A spec or quality import records nothing; an adversarial one records in place.

        Operator rulings 2026-10-11. Question 7: the imported review carries
        its own stage, and only an adversarial or human review is recorded.
        Question 9: a review import is a check, so it names itself inside the
        stage the run has reached. A run in Stage 2 therefore stays at
        ``implement`` through every import, and the post-Stage-2 fence is not
        armed by one.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        receipt = write_review_receipt()
        as_launched = (self.per_obpi.read_bytes(), self.legacy.read_bytes())

        for review_stage in ("spec", "quality"):
            with self.subTest(review_stage=review_stage):
                with stage4_work_replaced(review_stage=review_stage):
                    self._gz("obpi", "acceptance", _CLI_OBPI, "review", "--receipt", receipt)

                self.assertEqual(self._crossings(), [])
                self.assertEqual(
                    (self.per_obpi.read_bytes(), self.legacy.read_bytes()), as_launched
                )

        imports: tuple[tuple[str, ...], ...] = (
            ("review", "--receipt", receipt),
            ("human-review", "--attestor", "g0", "--ruling", "accepted as shown"),
        )
        for action in imports:
            with self.subTest(action=action[0]):
                before = len(self._crossings())

                with stage4_work_replaced(review_stage="adversarial"):
                    self._gz("obpi", "acceptance", _CLI_OBPI, *action)

                self._assert_crossed(
                    before,
                    stage="implement",
                    kind="task",
                    label="acceptance-review",
                    boundary="gz obpi acceptance",
                )

    @covers("REQ-0.35.0-15-02")
    def test_a_refused_review_import_and_an_unnamed_packet_mark_no_round(self) -> None:
        """Only a successful import is a round, and only a packet that names the run."""
        self._gz("obpi", "pipeline", _CLI_OBPI)
        receipt = write_review_receipt()
        stray_packet = write_stage4_packet("notes")

        with (
            stage4_work_replaced(),
            patch(
                "gzkit.commands.obpi_acceptance.record_review",
                side_effect=ValueError("receipt cites no current proof"),
            ),
        ):
            self._gz("obpi", "acceptance", _CLI_OBPI, "review", "--receipt", receipt, exit_code=3)
            self._gz("obpi", "verify-packet", stray_packet, "--json")

        self.assertEqual(self._crossings(), [])
        self.assertNotIn("position", _read(self.per_obpi))

    @covers("REQ-0.35.0-15-02")
    def test_a_bookkeeping_task_event_stays_in_the_stage_reached(self) -> None:
        """``gz task complete``, ``block`` and ``escalate`` never return a run to Stage 2.

        Operator ruling 2026-10-11 (Open Design Question 9): each records the
        TASK it marks inside the stage the run has reached, as that stage's
        kind. Only work that starts, ``gz task start`` and ``gz obpi
        dispatch``, re-enters ``implement``; that is the recorded re-entry a
        repair needs, and a bookkeeping event is not one.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        self._gz("task", "start", "--req", _CLI_REQS[0], "--seq", "next")
        first, second, third = (row.extra["task_id"] for row in self._rows("task_started"))
        self._verify()
        self.assertEqual(_read(self.per_obpi)["current_stage"], "ceremony")

        bookkeeping: tuple[tuple[tuple[str, ...], str, str], ...] = (
            (("task", "complete", first), first, "gz task complete"),
            (("task", "block", second, "--reason", "waits"), second, "gz task block"),
            (("task", "escalate", third, "--reason", "needs a ruling"), third, "gz task escalate"),
        )
        for args, label, boundary in bookkeeping:
            with self.subTest(boundary=boundary):
                before = len(self._crossings())

                self._gz(*args)

                self._assert_crossed(
                    before, stage="ceremony", kind="round", label=label, boundary=boundary
                )

        dispatch = ("obpi", "dispatch", _CLI_OBPI, "--role", "Implementer", "--model", "sonnet")
        starting: tuple[tuple[tuple[str, ...], str, str], ...] = (
            (("task", "start", second), second, "gz task start"),
            ((*dispatch, "--task", "2"), "task 2", "gz obpi dispatch"),
        )
        for args, label, boundary in starting:
            with self.subTest(boundary=boundary):
                self._verify()
                self.assertEqual(_read(self.per_obpi)["current_stage"], "ceremony")
                before = len(self._crossings())

                self._gz(*args)

                self._assert_crossed(
                    before, stage="implement", kind="task", label=label, boundary=boundary
                )

    @covers("REQ-0.35.0-15-02")
    def test_a_verification_result_is_recorded_inside_the_stage_the_run_is_in(self) -> None:
        """A pass or a fail is a result, not the start of work, and moves no stage.

        A repair started while verification runs re-enters ``implement``
        through ``gz task start``. The failure recorded after it names itself
        inside that stage: it does not return the run to ``verify`` and re-arm
        the fence against the repair that has just begun.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)

        self._verify(
            failing=True,
            at_dispatch=lambda: self._gz("task", "start", "--req", _CLI_REQS[0], "--seq", "next"),
        )

        repair = self._rows("task_started")[-1].extra["task_id"]
        self.assertEqual(
            [
                (row.extra["stage"], row.extra["position_kind"], row.extra["position_label"])
                for row in self._crossings()
            ],
            [
                ("verify", "phase", "verification"),
                ("implement", "task", repair),
                ("implement", "task", "verification-failed"),
            ],
        )
        self._assert_markers_read(self._crossings()[-1])

    @covers("REQ-0.35.0-15-02")
    def test_a_task_event_with_no_run_in_flight_records_no_position(self) -> None:
        """``gz task`` works outside a pipeline run, and then it marks no boundary."""
        self._gz("task", "start", "--req", _CLI_REQS[0], "--seq", "next")

        self.assertEqual(len(self._rows("task_started")), 1)
        self.assertEqual(self._crossings(), [])
        self.assertFalse(self.per_obpi.exists())
        self.assertFalse(self.legacy.exists())


class TestABoundaryIsRecordedUnderTheIdTheLaunchCarries(_LaunchableThroughTheCli):
    """REQ-0.35.0-15-02: a boundary is readable however its command spelled the OBPI."""

    @covers("REQ-0.35.0-15-02")
    def test_each_id_taking_producer_records_a_short_id_under_the_launch_id(self) -> None:
        """The short form an operator types names the run the launch recorded.

        The launch row carries the full slug, and a run is matched by id. A
        command handed ``OBPI-<semver>-<item>`` therefore found no run in
        flight, appended nothing and left the marker at the earlier position
        with no warning (quality review finding
        QR2-REQ02-noncanonical-id-records-nothing). Each command that takes an
        OBPI id is crossed here with the short form; the packet names its OBPI
        by its file name, and a dispatch is recorded through the channel the
        dispatch command calls. ``gz obpi complete`` is last, because its
        receipt ends the run. Every crossing lands on the launch's id. The
        commands that take an OBPI id name it by the launcher's resolver
        (operator ruling 2026-10-12, Open Design Question 19); a dispatch
        reaches the recorder with the id as given, and the recorder finds the
        run. The ``gz task`` verbs take a TASK id and are crossed further on.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        short = _CLI_SHORT_OBPI
        acceptance = ("obpi", "acceptance", short)
        producers: tuple[tuple[str, str, Callable[[], object]], ...] = (
            ("gz obpi precomplete", "precomplete", lambda: self._precomplete(obpi_id=short)),
            (
                "gz obpi present-evidence",
                "present-evidence",
                lambda: self._gz("obpi", "present-evidence", short, "--json"),
            ),
            (
                "gz obpi verify-packet",
                "verify-packet",
                lambda: self._gz("obpi", "verify-packet", write_stage4_packet(short), "--json"),
            ),
            (
                "gz obpi acceptance",
                "acceptance-review",
                lambda: self._gz(*acceptance, "review", "--receipt", write_review_receipt()),
            ),
            (
                "gz obpi acceptance",
                "acceptance-review",
                lambda: self._gz(
                    *acceptance, "human-review", "--attestor", "g0", "--ruling", "accepted"
                ),
            ),
            (
                "gz obpi dispatch",
                "task 2",
                lambda: chan.record_dispatch(
                    Path.cwd(), short, role="Implementer", model="sonnet", task_id=2
                ),
            ),
            ("gz obpi complete", "complete", lambda: self._complete(obpi_id=short)),
        )
        self._assert_each_crossing_lands_on_the_launch_id(producers)

    def _assert_each_crossing_lands_on_the_launch_id(
        self, producers: tuple[tuple[str, str, Callable[[], object]], ...]
    ) -> None:
        """Each ``(boundary, label, cross)`` appends one event, on the launch's id alone."""
        for boundary, label, cross in producers:
            with self.subTest(boundary=boundary, label=label):
                before = len(self._crossings())

                with stage4_work_replaced():
                    cross()

                crossings = self._crossings()
                self.assertEqual(
                    len(crossings), before + 1, "one event on the id the launch carries"
                )
                recorded = crossings[-1].extra
                self.assertEqual(
                    (recorded["position_label"], recorded["boundary"]), (label, boundary)
                )
                self._assert_markers_read(crossings[-1])
        self.assertEqual(
            {row.id for row in self._rows("pipeline_stage_transition")},
            {_CLI_OBPI},
            "no crossing is filed under the id as typed",
        )

    @covers("REQ-0.35.0-15-02")
    def test_a_prefix_longer_than_the_short_form_records_under_the_launch_id(self) -> None:
        """A prefix the launcher's resolver expands names the run for every command.

        Review finding
        fin-REQ02-a-slug-prefix-id-is-accepted-by-precomplete-and-records-nothing.
        ``gz obpi precomplete`` and ``gz obpi present-evidence`` found the
        brief by a file glob on the id as typed, so they accepted a prefix of
        the launch id longer than its short form and handed the recorder an
        id that names no run: the boundary was crossed and never recorded. A
        Step-4a packet named by that prefix and a review imported under it
        went the same way. Each command now names the OBPI by the resolver the
        launcher uses, and each crossing lands on the launch's id.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        prefix = _CLI_SLUG_PREFIX
        self.assertTrue(_CLI_OBPI.startswith(f"{prefix}-"), "a prefix ending on a whole word")
        self.assertNotEqual(prefix, _CLI_SHORT_OBPI, "longer than the short form")
        acceptance = ("obpi", "acceptance", prefix)
        self._assert_each_crossing_lands_on_the_launch_id(
            (
                ("gz obpi precomplete", "precomplete", lambda: self._precomplete(obpi_id=prefix)),
                (
                    "gz obpi present-evidence",
                    "present-evidence",
                    lambda: self._gz("obpi", "present-evidence", prefix, "--json"),
                ),
                (
                    "gz obpi verify-packet",
                    "verify-packet",
                    lambda: self._gz(
                        "obpi", "verify-packet", write_stage4_packet(prefix), "--json"
                    ),
                ),
                (
                    "gz obpi acceptance",
                    "acceptance-review",
                    lambda: self._gz(*acceptance, "review", "--receipt", write_review_receipt()),
                ),
                (
                    "gz obpi acceptance",
                    "acceptance-review",
                    lambda: self._gz(
                        *acceptance, "human-review", "--attestor", "g0", "--ruling", "accepted"
                    ),
                ),
            )
        )

    @covers("REQ-0.35.0-15-02")
    def test_present_evidence_writes_its_packet_for_the_obpi_the_resolver_names(self) -> None:
        """The packet is generated from the resolved brief, under the launch's id."""
        self._gz("obpi", "pipeline", _CLI_OBPI)
        brief = next(Path.cwd().rglob(f"{_CLI_OBPI}.md"))
        for given in (_CLI_SHORT_OBPI, _CLI_SLUG_PREFIX, _CLI_OBPI):
            with self.subTest(given=given), stage4_work_replaced():
                packet = Mock(blockers=[], review_blockers=[])
                packet.model_dump_json.return_value = "{}"
                with patch(
                    "gzkit.commands.obpi_present_evidence.generate_evidence_packet",
                    return_value=packet,
                ) as generate:
                    self._gz("obpi", "present-evidence", given, "--json")

                generate.assert_called_once()
                _root, from_brief, under = generate.call_args.args
                self.assertEqual(under, _CLI_OBPI)
                self.assertEqual(from_brief.resolve(), brief.resolve())

    @covers("REQ-0.35.0-15-02")
    def test_an_id_naming_no_single_obpi_is_refused_and_no_boundary_is_crossed(self) -> None:
        """``precomplete`` and ``present-evidence`` do no work under an id the resolver refuses.

        Two inputs the file glob accepted. A prefix that stops inside a word
        of the id names no OBPI: the commands ran and the recorder found no
        run. A short form two live OBPIs share names two: the commands ran
        against whichever brief sorted first. Each is refused with exit 1
        before a check runs or a packet is generated, so no boundary is
        crossed and none goes unrecorded.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        recorded = len(self._rows("pipeline_stage_transition"))
        for name, given, seed in self._ids_naming_no_single_obpi():
            seed()
            with self.subTest(refused=name, command="gz obpi precomplete"):
                with precomplete_checks_replaced() as checks:
                    self._gz("obpi", "precomplete", given, "--json", exit_code=1)
                checks.assert_not_called()
                self.assertEqual(len(self._rows("pipeline_stage_transition")), recorded)
            with self.subTest(refused=name, command="gz obpi present-evidence"):
                with (
                    patch(
                        "gzkit.commands.obpi_present_evidence.generate_evidence_packet"
                    ) as generate,
                    patch("gzkit.commands.obpi_present_evidence.write_packet") as write,
                ):
                    self._gz("obpi", "present-evidence", given, "--json", exit_code=1)
                generate.assert_not_called()
                write.assert_not_called()
                self.assertEqual(len(self._rows("pipeline_stage_transition")), recorded)

    def _seed_a_live_sibling(self) -> None:
        """Register a second live OBPI under the run's short form, with its brief on disk."""
        brief = next(Path.cwd().rglob(f"{_CLI_OBPI}.md"))
        brief.with_name(f"{_CLI_SIBLING_OBPI}.md").write_text(
            brief.read_text(encoding="utf-8").replace(_CLI_OBPI, _CLI_SIBLING_OBPI),
            encoding="utf-8",
        )
        Ledger(Path(".gzkit/ledger.jsonl")).append(obpi_created_event(_CLI_SIBLING_OBPI, _CLI_ADR))

    def _ids_naming_no_single_obpi(self) -> tuple[tuple[str, str, Callable[[], None]], ...]:
        """Each ``(name, id, seed)``: an id the resolver refuses once ``seed`` has run."""
        return (
            ("a prefix that stops inside a word", f"{_CLI_SHORT_OBPI}-runt", lambda: None),
            ("a short form two live OBPIs share", _CLI_SHORT_OBPI, self._seed_a_live_sibling),
        )

    @contextmanager
    def _review_imports_replaced(self) -> Iterator[tuple[Mock, Mock]]:
        """Replace the store's two review imports; yield them, review then human review."""
        review = Mock(stage="adversarial")
        review.model_dump.return_value = {}
        module = "gzkit.commands.obpi_acceptance"
        with (
            patch(f"{module}.record_review", return_value=review) as imported,
            patch(f"{module}.record_human_review", return_value=review) as ruled,
            patch(f"{module}.receipts_root", return_value=Path("receipts").resolve()),
        ):
            yield imported, ruled

    def _review_actions(self) -> tuple[tuple[str, tuple[str, ...]], ...]:
        """The two actions of ``gz obpi acceptance`` that import a review, with their arguments."""
        return (
            ("review", ("review", "--receipt", write_review_receipt())),
            ("human-review", ("human-review", "--attestor", "g0", "--ruling", "accepted")),
        )

    @covers("REQ-0.35.0-15-02")
    def test_a_review_import_refuses_an_id_naming_no_single_obpi_and_imports_nothing(self) -> None:
        """``review`` and ``human-review`` import nothing under an id the resolver refuses.

        Operator ruling 2026-10-12 on Open Design Question 20. The acceptance
        store finds its brief by a file glob and keys its records by the id as
        typed, so a prefix that stops inside a word of the id could carry the
        whole acceptance sequence: the review was imported, the recorder found
        no run under that id, and the boundary went unrecorded with no
        warning. Each action now names the OBPI by the launcher's resolver
        before anything is read or imported. An id that names no OBPI, or
        two, exits 1 as a user error and not as a blocked acceptance.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        recorded = len(self._rows("pipeline_stage_transition"))
        for name, given, seed in self._ids_naming_no_single_obpi():
            seed()
            for action, args in self._review_actions():
                for as_json in (False, True):
                    with (
                        self.subTest(refused=name, action=action, json=as_json),
                        self._review_imports_replaced() as (imported, ruled),
                    ):
                        printed = self._gz(
                            *("obpi", "acceptance", given, *args),
                            *(("--json",) if as_json else ()),
                            exit_code=1,
                        )

                        imported.assert_not_called()
                        ruled.assert_not_called()
                        self.assertNotIn("Acceptance blocked", printed)
                        if as_json:
                            self.assertIn(given, json.loads(printed)["error"])
                        self.assertEqual(len(self._rows("pipeline_stage_transition")), recorded)

    @covers("REQ-0.35.0-15-02")
    def test_a_review_import_keeps_its_records_under_the_id_typed_and_its_position_on_the_run(
        self,
    ) -> None:
        """The store stays keyed by the id as typed; the position lands on the launch's id.

        A control for the ruling on Question 20: resolving the id at entry
        changes what a review import refuses and the id its boundary is
        recorded under, and nothing about where the acceptance records live.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        for given in (_CLI_OBPI, _CLI_SHORT_OBPI, _CLI_SLUG_PREFIX):
            for action, args in self._review_actions():
                with (
                    self.subTest(given=given, action=action),
                    self._review_imports_replaced() as (imported, ruled),
                ):
                    before = len(self._crossings())

                    self._gz("obpi", "acceptance", given, *args)

                    store = imported if action == "review" else ruled
                    store.assert_called_once()
                    self.assertEqual(store.call_args.args[1], given)
                    self._assert_crossed(
                        before,
                        stage="implement",
                        kind="task",
                        label="acceptance-review",
                        boundary="gz obpi acceptance",
                    )
        self.assertEqual(
            {row.id for row in self._rows("pipeline_stage_transition")},
            {_CLI_OBPI},
            "no crossing is filed under the id as typed",
        )

    def _rename_the_launched_obpi(self) -> None:
        """Append the ledger row that renames the launched OBPI; its brief is left as it is."""
        Ledger(Path(".gzkit/ledger.jsonl")).append(
            artifact_renamed_event(_CLI_OBPI, _CLI_RENAMED_OBPI)
        )

    @covers("REQ-0.35.0-15-02")
    def test_an_obpi_renamed_after_its_launch_records_every_boundary_under_the_launch_id(
        self,
    ) -> None:
        """A rename hides no boundary: each command still records on the launch row's id.

        Review finding
        fin-fc4-REQ02-an-obpi-renamed-after-its-launch-crosses-every-id-taking-boundary-unrecorded.
        The resolver gives every spelling the id the ledger renamed the OBPI
        to, and the recorder once knew the run only by the id its launch row
        carries, so each command crossed its boundary and recorded nothing.
        The old id, the new id and the short form are each crossed here
        through the whole command. ``gz obpi complete`` is last: its receipt
        is written under the new id, and it ends the run launched under the
        old one.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        self._rename_the_launched_obpi()
        for given in (_CLI_RENAMED_OBPI, _CLI_OBPI, _CLI_SHORT_OBPI):
            acceptance = ("obpi", "acceptance", given)
            self._assert_each_crossing_lands_on_the_launch_id(
                (
                    (
                        "gz obpi precomplete",
                        "precomplete",
                        lambda given=given: self._precomplete(obpi_id=given),
                    ),
                    (
                        "gz obpi present-evidence",
                        "present-evidence",
                        lambda given=given: self._gz("obpi", "present-evidence", given, "--json"),
                    ),
                    (
                        "gz obpi acceptance",
                        "acceptance-review",
                        lambda acceptance=acceptance: self._gz(
                            *acceptance, "review", "--receipt", write_review_receipt()
                        ),
                    ),
                    (
                        "gz obpi acceptance",
                        "acceptance-review",
                        lambda acceptance=acceptance: self._gz(
                            *acceptance, "human-review", "--attestor", "g0", "--ruling", "accepted"
                        ),
                    ),
                )
            )
        self._assert_each_crossing_lands_on_the_launch_id(
            (
                (
                    "gz obpi complete",
                    "complete",
                    lambda: self._complete(obpi_id=_CLI_RENAMED_OBPI),
                ),
            )
        )
        rows = list(Ledger(Path(".gzkit/ledger.jsonl")).read_all())
        self.assertEqual(runs_in_flight(rows), [], "the receipt under the new id ended the run")

    @covers("REQ-0.35.0-15-02")
    def test_a_run_launched_under_an_intermediate_name_and_renamed_back_records_every_boundary(
        self,
    ) -> None:
        """A rename that is reversed while the run is in flight hides no boundary.

        Review findings
        fin-fc5A-REQ02-a-rename-back-to-an-earlier-id-leaves-the-resolvers-id-naming-no-run
        and
        fin-fc5A-REQ02-a-rename-reverted-after-the-launch-leaves-the-run-named-by-no-id-the-resolver-returns
        (operator ruling 2026-10-12, Open Design Question 22). The ledger
        renames the OBPI from its first id to the id it is launched under, and
        renames it back while the run is in flight. The resolver then gives
        every spelling the first id. The recorder once read the rename rows by
        a rule of its own, which gave the first id the launch id's name and
        the launch id the first id's, so the id the resolver returns named no
        run and each command crossed its boundary unrecorded. Each command is
        crossed here under the first id, the launch id and the short form, and
        ``gz obpi complete`` last: its receipt, written under the first id,
        ends the run.
        """
        first_id, launch_id = _CLI_RENAMED_OBPI, _CLI_OBPI
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        ledger.append(artifact_renamed_event(first_id, launch_id))
        self._gz("obpi", "pipeline", launch_id)
        self.assertEqual([row.id for row in self._rows("pipeline_launched")], [launch_id])
        ledger.append(artifact_renamed_event(launch_id, first_id))
        rows = list(Ledger(Path(".gzkit/ledger.jsonl")).read_all())
        for given in (first_id, launch_id, _CLI_SHORT_OBPI):
            with self.subTest(named_by=given):
                self.assertEqual(in_flight_launch_id(rows, given), launch_id)
            acceptance = ("obpi", "acceptance", given)
            self._assert_each_crossing_lands_on_the_launch_id(
                (
                    (
                        "gz obpi precomplete",
                        "precomplete",
                        lambda given=given: self._precomplete(obpi_id=given),
                    ),
                    (
                        "gz obpi present-evidence",
                        "present-evidence",
                        lambda given=given: self._gz("obpi", "present-evidence", given, "--json"),
                    ),
                    (
                        "gz obpi acceptance",
                        "acceptance-review",
                        lambda acceptance=acceptance: self._gz(
                            *acceptance, "review", "--receipt", write_review_receipt()
                        ),
                    ),
                    (
                        "gz obpi acceptance",
                        "acceptance-review",
                        lambda acceptance=acceptance: self._gz(
                            *acceptance, "human-review", "--attestor", "g0", "--ruling", "accepted"
                        ),
                    ),
                )
            )
        self._assert_each_crossing_lands_on_the_launch_id(
            (("gz obpi complete", "complete", lambda: self._complete(obpi_id=first_id)),)
        )
        rows = list(Ledger(Path(".gzkit/ledger.jsonl")).read_all())
        self.assertEqual(runs_in_flight(rows), [], "the receipt under the first id ended the run")

    def _seed_a_parked_sibling(self) -> None:
        """Put a second key under the run's short form on the ledger graph.

        The reviewers' counterexample, as the live ledger holds it: an OBPI
        created under the same semver and item, parked when its ADR was
        demoted, and never launched. The ledger is append-only, so its graph
        key stays, and the short form then prefixes two keys.
        """
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        ledger.append(obpi_created_event(_CLI_SIBLING_OBPI, _CLI_ADR))
        ledger.append(obpi_parked_event(_CLI_SIBLING_OBPI, _CLI_ADR, "ADR-pool.interrogate"))

    @covers("REQ-0.35.0-15-02")
    def test_each_task_verb_records_under_the_launch_id_beside_a_parked_sibling(self) -> None:
        """A TASK's first ``gz task start`` reaches the recorder with the short id.

        Review findings fc1-REQ02-task-verbs-resolve-the-obpi-apart-from-the-launcher
        and fc1-REQ02-task-start-resolves-its-obpi-id-unlike-the-launcher. A
        TASK id carries only the semver and the item. With two graph keys
        under that prefix ``gz task start`` cannot pick one, so it files
        ``task_started`` under the short form (its own ruled behaviour, GHI
        #653, asserted here as the precondition) and every later verb on that
        TASK reads the short form back. Each verb is still a ruled boundary of
        the run in flight, and each lands on the id the launch carries.
        """
        self._seed_a_parked_sibling()
        self._gz("obpi", "pipeline", _CLI_OBPI)
        to_complete, to_block, to_escalate = (f"TASK-0.13.0-01-01-{seq:02d}" for seq in (2, 3, 4))
        verbs: tuple[tuple[tuple[str, ...], str, str], ...] = (
            (("task", "start", to_complete), to_complete, "gz task start"),
            (("task", "complete", to_complete), to_complete, "gz task complete"),
            (("task", "start", to_block), to_block, "gz task start"),
            (("task", "block", to_block, "--reason", "waits"), to_block, "gz task block"),
            (("task", "start", to_escalate), to_escalate, "gz task start"),
            (
                ("task", "escalate", to_escalate, "--reason", "needs a ruling"),
                to_escalate,
                "gz task escalate",
            ),
        )
        for args, label, boundary in verbs:
            with self.subTest(boundary=boundary, task=label):
                before = len(self._crossings())

                self._gz(*args)

                self._assert_crossed(
                    before, stage="implement", kind="task", label=label, boundary=boundary
                )

        started_by_hand = {
            row.extra["task_id"]: row.extra["obpi_id"]
            for row in self._rows("task_started")
            if row.extra["task_id"] in (to_complete, to_block, to_escalate)
        }
        self.assertEqual(
            started_by_hand,
            dict.fromkeys((to_complete, to_block, to_escalate), _CLI_SHORT_OBPI),
            "each verb reached the recorder with the short form, or nothing is tested",
        )
        self.assertEqual(
            {row.id for row in self._rows("pipeline_stage_transition")},
            {_CLI_OBPI},
            "no crossing is filed under the short form",
        )

    @covers("REQ-0.35.0-15-02")
    def test_a_task_started_by_req_records_under_the_launch_id_beside_a_sibling_brief(
        self,
    ) -> None:
        """``gz task start --req`` falls back to the short form when two briefs share it.

        That verb tells a phantom graph key from a real OBPI by the brief on
        disk, so the parked sibling alone does not divert it. With the
        sibling's brief also on disk it cannot choose, files ``task_started``
        under the short form, and hands that to the recorder.
        """
        self._seed_a_parked_sibling()
        self._gz("obpi", "pipeline", _CLI_OBPI)
        brief = next(Path.cwd().rglob(f"{_CLI_OBPI}.md"))
        brief.with_name(f"{_CLI_SIBLING_OBPI}.md").write_text(
            brief.read_text(encoding="utf-8").replace(_CLI_OBPI, _CLI_SIBLING_OBPI),
            encoding="utf-8",
        )

        self._gz("task", "start", "--req", _CLI_REQS[0], "--seq", "next")

        started = self._rows("task_started")[-1].extra
        self.assertEqual(started["obpi_id"], _CLI_SHORT_OBPI, "the short form reached the recorder")
        self._assert_crossed(
            0, stage="implement", kind="task", label=started["task_id"], boundary="gz task start"
        )

    def _launch_and_retire_a_sibling(self, how: str) -> None:
        """Launch a sibling OBPI under the run's short form, then retire it unreceipted.

        The sibling's brief declares the same REQs, as a reused semver and
        item do, so its launch auto-starts the TASK ids the live OBPI's launch
        would. Its markers are removed, as clearing a stale run leaves them.
        """
        brief = next(Path.cwd().rglob(f"{_CLI_OBPI}.md"))
        brief.with_name(f"{_CLI_SIBLING_OBPI}.md").write_text(
            brief.read_text(encoding="utf-8").replace(_CLI_OBPI, _CLI_SIBLING_OBPI),
            encoding="utf-8",
        )
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        ledger.append(obpi_created_event(_CLI_SIBLING_OBPI, _CLI_ADR))
        ledger.append(
            brief_reconciled_event(
                _CLI_SIBLING_OBPI,
                has_drift=False,
                allowlist_delta_count=0,
                discovery_delta_count=0,
                verification_delta_count=0,
                req_count_delta=0,
                citation_delta_count=0,
            )
        )
        self._gz("obpi", "pipeline", _CLI_SIBLING_OBPI)
        ledger.append(_RETIREMENTS[how](_CLI_SIBLING_OBPI, _CLI_ADR))
        for marker in pipeline_marker_paths(self.per_obpi.parent, _CLI_SIBLING_OBPI):
            marker.unlink()

    def _assert_task_verbs_record_in_the_live_run_after_a_retired_sibling(self, how: str) -> None:
        """A TASK first started under a retired sibling's slug is marked in the live run.

        Review finding
        fc2-REQ02-a-retired-siblings-unreceipted-launch-is-still-a-run-in-flight,
        second half, on the reviewers' input. The sibling's launch auto-started
        the TASKs under its own slug; the live OBPI's launch starts none of
        them again, because a TASK id is started once whatever OBPI spelling
        its row carries (GHI #653). Every later ``gz task`` verb reads the
        sibling's slug back for its own event, and that event keeps it. The
        recorder is handed the ``OBPI-<semver>-<item>`` the TASK id carries,
        which names the one run in flight: ``complete``, ``block`` and
        ``escalate`` record in place, and a resumed ``start`` re-enters
        ``implement``.
        """
        self._launch_and_retire_a_sibling(how)
        self._gz("obpi", "pipeline", _CLI_OBPI)
        started = {row.extra["task_id"]: row.extra["obpi_id"] for row in self._rows("task_started")}
        first, second = started
        self.assertEqual(
            set(started.values()),
            {_CLI_SIBLING_OBPI},
            "the TASKs were started under the sibling's slug, or nothing is tested",
        )

        verbs: tuple[tuple[tuple[str, ...], str, str, str], ...] = (
            (("task", "complete", first), first, "gz task complete", "ceremony"),
            (("task", "block", second, "--reason", "waits"), second, "gz task block", "ceremony"),
            (("task", "start", second), second, "gz task start", "implement"),
            (
                ("task", "escalate", second, "--reason", "needs a ruling"),
                second,
                "gz task escalate",
                "ceremony",
            ),
        )
        for args, label, boundary, stage in verbs:
            with self.subTest(retired=how, boundary=boundary):
                self._verify()
                self.assertEqual(_read(self.per_obpi)["current_stage"], "ceremony")
                before = len(self._crossings())

                self._gz(*args)

                self._assert_crossed(
                    before,
                    stage=stage,
                    kind=STAGE_POSITION_KIND[stage],
                    label=label,
                    boundary=boundary,
                )

        task_events = [
            row
            for event in ("task_started", "task_completed", "task_blocked", "task_escalated")
            for row in self._rows(event)
        ]
        self.assertEqual(len(task_events), 6, "two launch starts and the four verbs")
        self.assertEqual(
            {row.extra["obpi_id"] for row in task_events},
            {_CLI_SIBLING_OBPI},
            "each verb's own task event keeps the id the TASK was started under",
        )
        self.assertEqual(
            {row.id for row in self._rows("pipeline_stage_transition")},
            {_CLI_OBPI},
            "no crossing is filed under the retired sibling",
        )

    @covers("REQ-0.35.0-15-02")
    def test_task_verbs_on_a_parked_siblings_tasks_record_in_the_live_run(self) -> None:
        """Parked: the reused semver the live ledger shows, with the sibling launched."""
        self._assert_task_verbs_record_in_the_live_run_after_a_retired_sibling("parked")

    @covers("REQ-0.35.0-15-02")
    def test_task_verbs_on_a_withdrawn_siblings_tasks_record_in_the_live_run(self) -> None:
        """Withdrawn: the retirement that is never reversed."""
        self._assert_task_verbs_record_in_the_live_run_after_a_retired_sibling("withdrawn")


class TestACheckNeverErasesAFailedVerification(_LaunchableThroughTheCli):
    """Requirement 9, through the commands: the marker keeps what the failure left."""

    def test_each_check_run_after_a_failure_leaves_its_blockers_and_resume_point(self) -> None:
        """A reader is still told the verification failed, and to resume at ``verify``.

        Review finding fc1-aux-in-place-record-after-failed-verification-drops-blockers.
        After the failure the precondition check, a packet verification, a
        review import and a TASK completion each record their position, and
        the four stage-output fields of both marker files stay as the failure
        left them. The repair that starts next is new work and clears them.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        first = self._rows("task_started")[0].extra["task_id"]
        packet = write_stage4_packet(_CLI_OBPI)
        receipt = write_review_receipt()
        (found,) = self._verify(failing=True)
        as_failed = self._stage_output()
        self.assertEqual((as_failed["blockers"], as_failed["resume_point"]), ([found], "verify"))
        checks: dict[str, Callable[[], object]] = {
            "precomplete": self._precomplete,
            "verify-packet": lambda: self._gz("obpi", "verify-packet", packet, "--json"),
            "acceptance-review": lambda: self._gz(
                "obpi", "acceptance", _CLI_OBPI, "review", "--receipt", receipt
            ),
            first: lambda: self._gz("task", "complete", first),
        }

        for label, run in checks.items():
            with self.subTest(position=label):
                with stage4_work_replaced():
                    run()

                self.assertEqual(_read(self.per_obpi)["position"]["label"], label)
                self.assertEqual(self._stage_output(), as_failed)
                self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())

        self._gz("task", "start", "--req", _CLI_REQS[0], "--seq", "next")

        repair = _read(self.per_obpi)
        self.assertEqual((repair["current_stage"], repair["blockers"]), ("implement", []))

    def _stage_output(self) -> dict[str, Any]:
        marker = _read(self.per_obpi)
        return {field: marker[field] for field in _STAGE_OUTPUT_FIELDS}


class TestNoCheckOrBookkeepingCommandMovesTheFence(_LaunchableThroughTheCli):
    """Requirement 2 (b): what the post-Stage-2 fence decides is moved by no check.

    The fence module is untouched. It reads ``current_stage``, so a command
    that is not the start of a stage's work must leave that value as it found
    it. At each stage a run can be in, every check and bookkeeping command is
    run; each appends its one event, and the fence returns for both marker
    files what it returned before.
    """

    def _fence_verdicts(self) -> list[tuple[str | None, bool, bool]]:
        """Return, per marker file, the stage the fence reads and its two verdicts."""
        verdicts = []
        for marker_path in (self.per_obpi, self.legacy):
            stage = marker_stage(marker_path)
            verdicts.append(
                (
                    stage,
                    refuses_production_write(stage, _SRC),
                    refuses_production_commit(stage, _SRC),
                )
            )
        return verdicts

    def _assert_no_command_moves_the_fence(self, stage: str, reach: Callable[[], object]) -> None:
        self._gz("obpi", "pipeline", _CLI_OBPI)
        self._gz("task", "start", "--req", _CLI_REQS[0], "--seq", "next")
        first, second, third = (row.extra["task_id"] for row in self._rows("task_started"))
        receipt = write_review_receipt()
        packet = write_stage4_packet(_CLI_OBPI)
        breach = Mock(ok=False)
        breach.model_dump.return_value = {"name": "lock_held", "ok": False}
        acceptance = ("obpi", "acceptance", _CLI_OBPI)
        commands: dict[str, Callable[[], object]] = {
            "precomplete": self._precomplete,
            "precomplete, breached": lambda: self._precomplete(found=[breach], exit_code=3),
            "verify-packet": lambda: self._gz("obpi", "verify-packet", packet, "--json"),
            "adversarial review import": lambda: self._gz(
                *acceptance, "review", "--receipt", receipt
            ),
            "human review import": lambda: self._gz(
                *acceptance, "human-review", "--attestor", "g0", "--ruling", "accepted"
            ),
            "task complete": lambda: self._gz("task", "complete", first),
            "task block": lambda: self._gz("task", "block", second, "--reason", "waits"),
            "task escalate": lambda: self._gz("task", "escalate", third, "--reason", "a ruling"),
        }
        reach()
        expected = self._fence_verdicts()
        self.assertEqual({verdict[0] for verdict in expected}, {stage})

        for name, run in commands.items():
            with self.subTest(stage=stage, command=name):
                before = len(self._crossings())

                with stage4_work_replaced():
                    run()

                self.assertEqual(len(self._crossings()), before + 1, "the boundary is recorded")
                self.assertEqual(self._fence_verdicts(), expected)

    @covers("REQ-0.35.0-15-02")
    def test_at_implement_production_writes_stay_admitted(self) -> None:
        self._assert_no_command_moves_the_fence("implement", lambda: None)

    @covers("REQ-0.35.0-15-02")
    def test_at_verify_production_writes_stay_refused(self) -> None:
        self._assert_no_command_moves_the_fence("verify", lambda: self._verify(failing=True))

    @covers("REQ-0.35.0-15-02")
    def test_at_ceremony_production_writes_and_commits_stay_refused(self) -> None:
        self._assert_no_command_moves_the_fence("ceremony", self._verify)

    @covers("REQ-0.35.0-15-02")
    def test_at_sync_production_commits_stay_admitted_and_writes_refused(self) -> None:
        self._assert_no_command_moves_the_fence("sync", lambda: self._complete(failing_write=True))


class TestAPositionThatCannotBeRecordedNeverFailsItsHost(_LaunchableThroughTheCli):
    """Requirement 12: a position is never gate evidence, in either direction.

    The ledger refuses the transition row and nothing else. Each command then
    does what it does with no run in flight: it reports its own result and
    exits with its own code, and the run's position stays where it was.
    """

    @contextmanager
    def _position_writes_fail(self) -> Iterator[None]:
        """Make the ledger refuse a ``pipeline_stage_transition`` row, and only that."""
        append = Ledger.append

        def _append(ledger: Ledger, event: LedgerEvent) -> None:
            if event.event == "pipeline_stage_transition":
                raise OSError("no space left on device")
            append(ledger, event)

        with (
            patch.object(Ledger, "append", autospec=True, side_effect=_append),
            self.assertLogs("gzkit.pipeline_position", level="WARNING"),
        ):
            yield

    def test_precomplete_still_reports_its_checks_and_exits_on_them(self) -> None:
        """The record ran between the checks and their report, so a failure lost the report."""
        self._gz("obpi", "pipeline", _CLI_OBPI)
        breach = Mock(ok=False)
        breach.model_dump.return_value = {"name": "lock_held", "ok": False}

        for found, exit_code, ready in (([], 0, True), ([breach], 3, False)):
            with self.subTest(exit_code=exit_code):
                with (
                    self._position_writes_fail(),
                    patch("gzkit.commands.obpi_precomplete._run_all_checks", return_value=found),
                ):
                    printed = self._gz(
                        "obpi", "precomplete", _CLI_OBPI, "--json", exit_code=exit_code
                    )

                report = json.loads(printed[printed.index("{") :])
                self.assertEqual(report["ready"], ready)
                self.assertEqual(len(report["checks"]), len(found))
                self.assertEqual(self._crossings(), [])

    def test_a_recorded_review_is_not_reported_as_blocked(self) -> None:
        """The review is on record before the position is; its import succeeded.

        The command's ``OSError`` arm printed "Acceptance blocked" and exited 3
        for a review it had already recorded.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        acceptance = ("obpi", "acceptance", _CLI_OBPI)
        imports: tuple[tuple[str, ...], ...] = (
            ("review", "--receipt", write_review_receipt()),
            ("human-review", "--attestor", "g0", "--ruling", "accepted as shown"),
        )
        for action in imports:
            with self.subTest(action=action[0]):
                with stage4_work_replaced(), self._position_writes_fail():
                    printed = self._gz(*acceptance, *action, exit_code=0)

                self.assertNotIn("Acceptance blocked", printed)
                self.assertEqual(self._crossings(), [])

    def test_a_task_verb_still_lands_its_own_event_and_exits_zero(self) -> None:
        self._gz("obpi", "pipeline", _CLI_OBPI)
        first = self._rows("task_started")[0].extra["task_id"]

        with self._position_writes_fail():
            printed = self._gz("task", "complete", first, "--json", exit_code=0)

        self.assertEqual(json.loads(printed[printed.index("{") :])["to_status"], "completed")
        self.assertEqual([row.extra["task_id"] for row in self._rows("task_completed")], [first])
        self.assertEqual(self._crossings(), [])
        self.assertNotIn("position", _read(self.per_obpi))


class TestTheMarkerReportsTheStageTheRunHasReached(_LaunchableThroughTheCli):
    """REQ-0.35.0-15-01: the stage reached, never the stage the launch named."""

    @covers("REQ-0.35.0-15-01")
    def test_a_run_launched_in_full_reads_each_stage_it_crosses_into(self) -> None:
        """Both marker files read ``verify``, ``ceremony`` and ``sync`` as the run crosses.

        GHI #1172: a marker that reports the launch stage for a run that has
        left it is the defect. A failed verification leaves the run in Stage 3;
        a passed one chains into the ceremony, so the run has reached Stage 4;
        the precondition check run from there is a check and leaves it there
        (Open Design Question 9); the completion begins Stage 5, and its
        receipt ends the run. Each reading is later than the launch that wrote
        ``started_at``.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        self.assertEqual(_read(self.per_obpi)["current_stage"], "implement")

        self._verify(failing=True)
        self._assert_reached("verify")

        self._verify()
        self._assert_reached("ceremony")

        self._precomplete()
        self._assert_reached("ceremony")
        self.assertEqual(_read(self.per_obpi)["position"]["label"], "precomplete")

        self._complete()
        self._assert_reached("sync")
        self.assertEqual(_read(self.per_obpi)["position"]["label"], "complete")

    @covers("REQ-0.35.0-15-01")
    def test_an_unbroken_run_reads_ceremony_and_sync_with_no_relaunch(self) -> None:
        """The stage read is the recorder's work, on the marker the full launch wrote.

        Every ``--from`` re-entry rewrites both markers, so a reading taken
        after one could be the relaunch's own. This run is launched once, in
        full, and never re-entered: ``gz obpi present-evidence`` begins Stage 4
        and ``gz obpi complete`` begins Stage 5. At each the marker reads the
        stage reached while ``entry`` is still ``full`` and the nonce and start
        time are the launch's, and the ledger holds the one launch.
        """
        self._gz("obpi", "pipeline", _CLI_OBPI)
        launched = _read(self.per_obpi)
        self.assertEqual((launched["entry"], launched["current_stage"]), ("full", "implement"))

        with stage4_work_replaced():
            self._gz("obpi", "present-evidence", _CLI_OBPI, "--json")
        self._assert_reached("ceremony")
        self._assert_the_launch_still_stands(launched)

        self._complete()
        self._assert_reached("sync")
        self._assert_the_launch_still_stands(launched)

    def _assert_the_launch_still_stands(self, launched: dict[str, Any]) -> None:
        """Both files keep the full launch's identity, and no second launch was recorded."""
        for marker_path in (self.per_obpi, self.legacy):
            marker = _read(marker_path)
            self.assertEqual(marker["entry"], "full")
            self.assertEqual(marker["nonce"], launched["nonce"])
            self.assertEqual(marker["started_at"], launched["started_at"])
        launches = [row for row in self._rows("pipeline_launched") if row.id == _CLI_OBPI]
        self.assertEqual([row.extra["nonce"] for row in launches], [launched["nonce"]])

    def _assert_reached(self, stage: str) -> None:
        """Both files read ``stage``, at a time later than the run started."""
        for marker_path in (self.per_obpi, self.legacy):
            marker = _read(marker_path)
            self.assertEqual(marker["current_stage"], stage)
            self.assertNotEqual(marker["current_stage"], "implement")
            started_at = datetime.fromisoformat(marker["started_at"].replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(marker["updated_at"].replace("Z", "+00:00"))
            self.assertGreater(updated_at, started_at)
        per_obpi, legacy = self._markers()
        self.assertEqual(per_obpi, legacy)

    def _markers(self) -> tuple[bytes, bytes]:
        return self.per_obpi.read_bytes(), self.legacy.read_bytes()


def _launched(entry: str, ts: str, *, obpi_id: str = _OBPI) -> LedgerEvent:
    event = pipeline_launched_event(
        obpi_id=obpi_id,
        parent_adr=_ADR,
        lane="heavy",
        nonce=_NONCE,
        marker_path=f".claude/plans/.pipeline-active-{obpi_id}.json",
        entry=entry,
    )
    return event.model_copy(update={"ts": ts})


def _crossed(
    stage: str,
    kind: str,
    label: str,
    ts: str,
    *,
    blockers: list[str] | None = None,
    obpi_id: str = _OBPI,
) -> LedgerEvent:
    event = pipeline_stage_transition_event(
        obpi_id=obpi_id,
        parent_adr=_ADR,
        stage=stage,
        position_kind=kind,
        position_label=label,
        boundary=_BOUNDARY,
        blockers=blockers,
    )
    return event.model_copy(update={"ts": ts})


#: What a ``pipeline_stage_transition`` row must carry to be a crossing.
_REQUIRED_CROSSING_FIELDS = ("stage", "position_kind", "position_label", "boundary")


def _malformed_crossings() -> list[tuple[str, LedgerEvent]]:
    """Return rows of the transition type that each fail to record a crossing.

    Each is a sound later crossing with one required field removed or emptied,
    plus one whose stage is a position inside a stage and not a canonical stage.
    """
    sound = _crossed("ceremony", "round", "present-evidence", _CROSSED_LATER_AT)
    rows: list[tuple[str, LedgerEvent]] = []
    for field in _REQUIRED_CROSSING_FIELDS:
        without = {key: value for key, value in sound.extra.items() if key != field}
        rows.append((f"no {field}", sound.model_copy(update={"extra": without})))
        emptied = {**sound.extra, field: ""}
        rows.append((f"empty {field}", sound.model_copy(update={"extra": emptied})))
    as_stage = {**sound.extra, "stage": "task 2"}
    rows.append(("a position as the stage", sound.model_copy(update={"extra": as_stage})))
    return rows


class TestALaunchWithNothingAfterItReportsNoPosition(unittest.TestCase):
    """REQ-0.35.0-15-04: the launch reads as it does today, for every entry."""

    @covers("REQ-0.35.0-15-04")
    def test_a_bare_launch_reads_its_launch_values_and_no_position(self) -> None:
        """The control of the repair: a launch that crossed nothing reads as it always has.

        A real ``gz obpi pipeline`` launch, read at the moment of entry: the
        stage runners are replaced by the capture, so both marker files hold
        what the LAUNCH wrote. ``entry``, ``current_stage``, ``blockers``,
        ``required_human_action`` and ``resume_point`` are today's literal
        values, and neither the markers nor the ledger replay names a position.
        ``next_command`` is not asserted (OBPI-0.35.0-16 re-derives it).
        """
        for start_from, launch_values in _LAUNCH_VALUES.items():
            with self.subTest(entry=launch_values[0]):
                at_entry = self._launch_and_read_at_entry(start_from)

                self._assert_reads_as_launched(at_entry, start_from)

    @covers("REQ-0.35.0-15-04")
    def test_a_full_launch_that_auto_starts_tasks_still_reports_no_position(self) -> None:
        """A launch that starts a TASK for each REQ of its brief has crossed nothing.

        The brief of the other launches carries no acceptance criteria, so they
        start no TASK. This one does, and its ``task_started`` rows follow the
        launch on the ledger. They are the launch's own bookkeeping and no
        boundary: the run still reads as launched, with no position.
        """
        at_entry = self._launch_and_read_at_entry(None, with_reqs=True)

        started = [
            row.extra.get("task_id")
            for row in at_entry["events"]
            if row.event == "task_started" and row.extra.get("obpi_id") == _CLI_OBPI
        ]
        self.assertEqual(len(started), len(_CLI_REQS), "one TASK per REQ, or nothing is tested")
        crossings = [row for row in at_entry["events"] if row.event == "pipeline_stage_transition"]
        self.assertEqual(crossings, [])
        self._assert_reads_as_launched(at_entry, None)

    def _launch_and_read_at_entry(
        self, start_from: str | None, *, with_reqs: bool = False
    ) -> dict[str, Any]:
        """Launch through the CLI; return both markers, the ledger and its replay at entry."""
        evidence = json.dumps({"value_narrative": "test", "key_proof": "proof"})
        at_entry: dict[str, Any] = {}
        runner = CliRunner()
        with runner.isolated_filesystem():
            marker_paths = seed_launchable_obpi(with_reqs=with_reqs)

            def _capture_at_entry(**_stage_kwargs: object) -> None:
                events = list(Ledger(Path(".gzkit/ledger.jsonl")).read_all())
                at_entry["markers"] = [_read(path) for path in marker_paths]
                at_entry["events"] = events
                at_entry["replay"] = replay_pipeline_position(events, _CLI_OBPI)

            args = ["obpi", "pipeline", _CLI_OBPI]
            if start_from is not None:
                args.append(f"--from={start_from}")
            if start_from == "sync":
                args += ["--attestor", "human:tester", "--evidence-json", evidence]
            with patch.multiple(
                "gzkit.commands.obpi_cmd",
                _run_pipeline_verify_stage=_capture_at_entry,
                _run_pipeline_ceremony_stage=_capture_at_entry,
                _run_pipeline_sync_stage=_capture_at_entry,
            ):
                result = runner.invoke(main, args)
            if start_from is None:
                _capture_at_entry()

        self.assertEqual(result.exit_code, 0, result.output)
        return at_entry

    def _assert_reads_as_launched(self, at_entry: dict[str, Any], start_from: str | None) -> None:
        """Both markers hold the launch values of ``start_from``; nothing names a position."""
        entry, stage, resume_point, human_action = _LAUNCH_VALUES[start_from]
        per_obpi, legacy = at_entry["markers"]
        self.assertEqual(per_obpi, legacy)
        for marker in (per_obpi, legacy):
            self.assertEqual(marker["entry"], entry)
            self.assertEqual(marker["current_stage"], stage)
            self.assertEqual(marker["blockers"], [])
            self.assertEqual(marker["required_human_action"], human_action)
            self.assertEqual(marker["resume_point"], resume_point)
            self.assertNotIn("position", marker)

        replay = at_entry["replay"]
        self.assertIsNotNone(replay, "the launch is on the ledger to be replayed")
        self.assertEqual(replay.stage, stage)
        self.assertIsNone(replay.position)
        self.assertEqual(replay.blockers, [])


class TestReplayReadsTheRunPositionFromTheLedger(unittest.TestCase):
    """The pure replay ``gz state --repair`` rebuilds a deleted marker from."""

    def test_a_launch_alone_replays_to_its_launch_stage_and_time(self) -> None:
        for entry, stage, _resume_point, _human_action in _LAUNCH_VALUES.values():
            with self.subTest(entry=entry):
                replay = replay_pipeline_position([_launched(entry, _LAUNCHED_AT)], _OBPI)

                assert replay is not None
                self.assertEqual(replay.stage, stage)
                self.assertIsNone(replay.position)
                self.assertEqual(replay.blockers, [])
                self.assertEqual(replay.updated_at, _LAUNCHED_AT)

    def test_the_last_crossing_after_the_launch_is_the_position(self) -> None:
        events = [
            _launched("full", _LAUNCHED_AT),
            _crossed("implement", "task", "task 1", _CROSSED_AT),
            _crossed("verify", "phase", "verification", _CROSSED_LATER_AT),
        ]

        replay = replay_pipeline_position(events, _OBPI)

        assert replay is not None
        self.assertEqual(replay.stage, "verify")
        self.assertEqual(
            replay.position,
            PipelinePosition(kind="phase", label="verification", boundary=_BOUNDARY),
        )
        self.assertEqual(replay.updated_at, _CROSSED_LATER_AT)

    def test_blockers_are_those_of_the_last_crossing_only(self) -> None:
        failed = _crossed(
            "verify", "phase", "verification-failed", _CROSSED_AT, blockers=["gz test: exit 1"]
        )
        launch = _launched("full", _LAUNCHED_AT)

        blocked = replay_pipeline_position([launch, failed], _OBPI)
        cleared = replay_pipeline_position(
            [launch, failed, _crossed("verify", "phase", "verification-passed", _CROSSED_LATER_AT)],
            _OBPI,
        )

        assert blocked is not None and cleared is not None
        self.assertEqual(blocked.blockers, ["gz test: exit 1"])
        self.assertEqual(cleared.blockers, [])

    def test_only_crossings_after_the_latest_launch_count(self) -> None:
        """A relaunch starts a new run; the earlier run's crossings are not its position."""
        events = [
            _launched("full", _LAUNCHED_AT),
            _crossed("verify", "phase", "verification", _CROSSED_AT),
            _launched("ceremony", _CROSSED_LATER_AT),
        ]

        replay = replay_pipeline_position(events, _OBPI)

        assert replay is not None
        self.assertEqual(replay.stage, "ceremony")
        self.assertIsNone(replay.position)
        self.assertEqual(replay.updated_at, _CROSSED_LATER_AT)

    def test_another_obpis_events_are_not_this_runs_position(self) -> None:
        events = [
            _launched("full", _LAUNCHED_AT),
            _launched("sync", _CROSSED_AT, obpi_id=_OTHER_OBPI),
            _crossed("sync", "step", "complete", _CROSSED_LATER_AT, obpi_id=_OTHER_OBPI),
        ]

        replay = replay_pipeline_position(events, _OBPI)

        assert replay is not None
        self.assertEqual(replay.stage, "implement")
        self.assertIsNone(replay.position)
        self.assertEqual(replay.updated_at, _LAUNCHED_AT)

    def test_a_run_that_was_never_launched_has_no_position(self) -> None:
        """A position with no Layer-2 source is not invented (Requirement 4)."""
        events = [_crossed("verify", "phase", "verification", _CROSSED_AT)]

        self.assertIsNone(replay_pipeline_position(events, _OBPI))
        self.assertIsNone(replay_pipeline_position([], _OBPI))

    def test_a_transition_row_lacking_a_required_field_is_not_a_crossing(self) -> None:
        """The replay invents nothing: a malformed row names no stage and no position.

        Every field the event type requires must be on the row, and its stage
        must be canonical. A row that fails is skipped, so the run reads as it
        did before that row: at its last sound crossing, or at its launch. A
        default in place of the missing field would be a position with no
        Layer-2 source (Requirement 4), and a rebuild would write it back.
        """
        launch = _launched("full", _LAUNCHED_AT)
        sound = _crossed("verify", "phase", "verification", _CROSSED_AT)
        at_launch = replay_pipeline_position([launch], _OBPI)
        at_crossing = replay_pipeline_position([launch, sound], _OBPI)
        assert at_launch is not None and at_crossing is not None
        self.assertEqual(at_crossing.stage, "verify")

        for name, malformed in _malformed_crossings():
            with self.subTest(row=name):
                self.assertEqual(replay_pipeline_position([launch, malformed], _OBPI), at_launch)
                self.assertEqual(
                    replay_pipeline_position([launch, sound, malformed], _OBPI), at_crossing
                )


def _receipted(ts: str, *, obpi_id: str = _OBPI, receipt_event: str = "completed") -> LedgerEvent:
    """Return a receipt row; only a ``completed`` one records a completion state."""
    event = obpi_receipt_emitted_event(
        obpi_id,
        receipt_event=receipt_event,
        attestor="test",
        obpi_completion="attested_completed" if receipt_event == "completed" else None,
        parent_adr=_ADR,
    )
    return event.model_copy(update={"ts": ts})


def _retired(how: str, ts: str, *, obpi_id: str = _OBPI) -> LedgerEvent:
    return _RETIREMENTS[how](obpi_id, _ADR).model_copy(update={"ts": ts})


#: What the ledger renames ``_OBPI`` to: the same semver and item, another slug.
_RENAMED_OBPI = "OBPI-0.99.0-01-run-position-renamed"
#: A rename that changes the semver and the item, so the short form changes too.
_MOVED_OBPI = "OBPI-0.98.0-07-run-position-moved"


def _renamed(old_id: str, new_id: str, ts: str = _CROSSED_AT) -> LedgerEvent:
    return artifact_renamed_event(old_id, new_id).model_copy(update={"ts": ts})


class TestARenameNeitherEndsARunNorHidesIt(unittest.TestCase):
    """REQ-0.35.0-15-02: the recorder follows the ledger's renames.

    Review findings
    fin-fc4-REQ02-an-obpi-renamed-after-its-launch-crosses-every-id-taking-boundary-unrecorded
    and fin-fc4A-REQ02-an-obpi-renamed-after-its-launch-records-no-boundary-under-any-spelling
    (operator ruling 2026-10-12, Open Design Question 21). A run is launched
    under one id and the ledger then renames the OBPI. The resolver every
    command names the OBPI by follows renames, so it hands the recorder the
    new id, and the recorder keyed its runs by the launch row's raw id: no
    run, no record, no warning. The in-flight rule and the matching rule
    compare current names. A record is still filed under the launch row's own
    id, the one key the replay, the rebuild and the marker files share.
    """

    @covers("REQ-0.35.0-15-02")
    def test_a_run_renamed_after_its_launch_is_named_by_every_spelling(self) -> None:
        launch = _launched("full", _LAUNCHED_AT)
        later = "OBPI-0.99.0-01-run-position-renamed-again"
        cases: tuple[tuple[str, list[LedgerEvent], str], ...] = (
            ("the old id", [launch, _renamed(_OBPI, _RENAMED_OBPI)], _OBPI),
            ("the new id", [launch, _renamed(_OBPI, _RENAMED_OBPI)], _RENAMED_OBPI),
            ("the short form", [launch, _renamed(_OBPI, _RENAMED_OBPI)], _SHORT_OBPI),
            (
                "the end of a chain of renames",
                [launch, _renamed(_OBPI, _RENAMED_OBPI), _renamed(_RENAMED_OBPI, later)],
                later,
            ),
            (
                "the middle of a chain of renames",
                [launch, _renamed(_OBPI, _RENAMED_OBPI), _renamed(_RENAMED_OBPI, later)],
                _RENAMED_OBPI,
            ),
            (
                "a rename recorded before the launch",
                [_renamed(_OBPI, _RENAMED_OBPI), launch],
                _OBPI,
            ),
        )
        for name, rows, given in cases:
            with self.subTest(given=name):
                self.assertEqual(in_flight_launch_id(rows, given), _OBPI)
                self.assertEqual(runs_in_flight(rows), [_OBPI], "the run keeps its launch id")

    @covers("REQ-0.35.0-15-02")
    def test_a_rename_that_moves_the_semver_keeps_the_short_form_the_tasks_carry(self) -> None:
        """A TASK id holds the short form of the launch id, whatever the OBPI is called now."""
        rows = [_launched("full", _LAUNCHED_AT), _renamed(_OBPI, _MOVED_OBPI)]
        spellings = {
            "the short form of the launch id": _SHORT_OBPI,
            "the short form of the new id": "OBPI-0.98.0-07",
            "the new id": _MOVED_OBPI,
            "the old id": _OBPI,
        }
        for name, given in spellings.items():
            with self.subTest(given=name):
                self.assertEqual(in_flight_launch_id(rows, given), _OBPI)

    @covers("REQ-0.35.0-15-02")
    def test_a_receipt_or_a_retirement_under_the_new_id_ends_the_run(self) -> None:
        """The row that ends a run carries the id the OBPI has when it is written."""
        launch = _launched("full", _LAUNCHED_AT)
        rename = _renamed(_OBPI, _RENAMED_OBPI)
        endings = {
            "completion receipt": _receipted(_CROSSED_LATER_AT, obpi_id=_RENAMED_OBPI),
            **{
                how: _retired(how, _CROSSED_LATER_AT, obpi_id=_RENAMED_OBPI) for how in _RETIREMENTS
            },
        }
        for how, ending in endings.items():
            rows = [launch, rename, ending]
            for given in (_OBPI, _RENAMED_OBPI, _SHORT_OBPI):
                with self.subTest(ended_by=how, given=given):
                    self.assertIsNone(in_flight_launch_id(rows, given))
            with self.subTest(ended_by=how):
                self.assertEqual(runs_in_flight(rows), [])

    @covers("REQ-0.35.0-15-02")
    def test_a_relaunch_under_the_new_id_is_the_one_run_in_flight(self) -> None:
        """A later launch under either id starts a new run in place of the old one."""
        rows = [
            _launched("full", _LAUNCHED_AT),
            _renamed(_OBPI, _RENAMED_OBPI),
            _launched("verify", _CROSSED_LATER_AT, obpi_id=_RENAMED_OBPI),
        ]
        for given in (_OBPI, _RENAMED_OBPI, _SHORT_OBPI):
            with self.subTest(given=given):
                self.assertEqual(in_flight_launch_id(rows, given), _RENAMED_OBPI)
        self.assertEqual(runs_in_flight(rows), [_RENAMED_OBPI])

    @covers("REQ-0.35.0-15-02")
    def test_two_runs_one_id_names_after_a_rename_record_nothing_and_warn(self) -> None:
        """A rename that brings a second run under one short form makes that form name two."""
        rows = [
            _launched("full", _LAUNCHED_AT),
            _launched("full", _CROSSED_AT, obpi_id=_OTHER_OBPI),
            _renamed(_OTHER_OBPI, _SIBLING_OBPI, _CROSSED_LATER_AT),
        ]
        self.assertIsNone(in_flight_launch_id(rows, _SHORT_OBPI))
        self.assertEqual(in_flight_launch_id(rows, _OBPI), _OBPI)
        self.assertEqual(in_flight_launch_id(rows, _SIBLING_OBPI), _OTHER_OBPI)
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            for row in rows:
                ledger.append(row)
            with self.assertLogs(level="WARNING") as logged:
                reached = record_position(
                    ledger, Path(tmp) / "plans", _SHORT_OBPI, RunCrossing(boundary="precomplete")
                )
            self.assertIsNone(reached)
            self.assertIn("names 2 runs in flight", "\n".join(logged.output))
            self.assertEqual(
                [row for row in ledger.read_all() if row.event == "pipeline_stage_transition"], []
            )

    def test_a_rename_of_another_obpi_changes_nothing_for_this_run(self) -> None:
        """Controls: these read the same before and after the recorder followed renames."""
        launch = _launched("full", _LAUNCHED_AT)
        elsewhere = _renamed(_OTHER_OBPI, "OBPI-0.99.0-02-another-name")
        cycle = [_renamed(_OBPI, _RENAMED_OBPI), _renamed(_RENAMED_OBPI, _OBPI)]
        cases: tuple[tuple[str, list[LedgerEvent], str, str | None], ...] = (
            ("the launch id", [launch, elsewhere], _OBPI, _OBPI),
            ("the short form", [launch, elsewhere], _SHORT_OBPI, _OBPI),
            ("the other OBPI's new id", [launch, elsewhere], "OBPI-0.99.0-02-another-name", None),
            ("a rename and no launch", [_renamed(_OBPI, _RENAMED_OBPI)], _RENAMED_OBPI, None),
            ("a cycle of renames is not followed for ever", [launch, *cycle], _OBPI, _OBPI),
        )
        for name, rows, given, expected in cases:
            with self.subTest(case=name):
                self.assertEqual(in_flight_launch_id(rows, given), expected)

    @covers("REQ-0.35.0-15-02")
    def test_a_run_launched_under_an_intermediate_name_and_renamed_back_is_named_by_every_spelling(
        self,
    ) -> None:
        """An id's current name is the ledger's fold of its renames, round trips included.

        Review findings
        fin-fc5A-REQ02-a-rename-back-to-an-earlier-id-leaves-the-resolvers-id-naming-no-run
        and
        fin-fc5A-REQ02-a-rename-reverted-after-the-launch-leaves-the-run-named-by-no-id-the-resolver-returns
        (operator ruling 2026-10-12, Open Design Question 22). The OBPI is
        renamed, launched under the name it then has, and renamed back while
        the run is in flight. The resolver gives every spelling the id the
        OBPI has now, the earlier one, and that id must name the run, as the
        launch row's own id and each short form do. The record is still filed
        under the launch row's id.
        """
        there_and_back: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
            "the slug changes": ((_RENAMED_OBPI,), (_OBPI, _RENAMED_OBPI, _SHORT_OBPI)),
            "the semver and the item change": (
                (_MOVED_OBPI,),
                (_OBPI, _MOVED_OBPI, _SHORT_OBPI, "OBPI-0.98.0-07"),
            ),
            "back through a third id": (
                (_RENAMED_OBPI, _MOVED_OBPI),
                (_OBPI, _RENAMED_OBPI, _MOVED_OBPI, _SHORT_OBPI),
            ),
        }
        for name, (through, spellings) in there_and_back.items():
            between = through[0]
            rows = [
                _renamed(_OBPI, between, _LAUNCHED_AT),
                _launched("full", _CROSSED_AT, obpi_id=between),
                *(
                    _renamed(old_id, new_id, _CROSSED_LATER_AT)
                    for old_id, new_id in zip(through, (*through[1:], _OBPI), strict=True)
                ),
            ]
            for given in spellings:
                with self.subTest(renamed=name, given=given):
                    self.assertEqual(in_flight_launch_id(rows, given), between)
            with self.subTest(renamed=name):
                self.assertEqual(runs_in_flight(rows), [between], "the run keeps its launch id")

    @covers("REQ-0.35.0-15-02")
    def test_a_run_renamed_back_ends_under_either_of_its_ids(self) -> None:
        """A receipt or a retirement under either id ends a run whose rename was reversed."""
        rows = [
            _renamed(_OBPI, _RENAMED_OBPI, _LAUNCHED_AT),
            _launched("full", _CROSSED_AT, obpi_id=_RENAMED_OBPI),
            _renamed(_RENAMED_OBPI, _OBPI, _CROSSED_LATER_AT),
        ]
        for ended_under in (_OBPI, _RENAMED_OBPI):
            endings = {
                "completion receipt": _receipted(_CROSSED_LATER_AT, obpi_id=ended_under),
                **{
                    how: _retired(how, _CROSSED_LATER_AT, obpi_id=ended_under)
                    for how in _RETIREMENTS
                },
            }
            for how, ending in endings.items():
                with self.subTest(ended_by=how, ended_under=ended_under):
                    self.assertEqual(runs_in_flight([*rows, ending]), [])
                    for given in (_OBPI, _RENAMED_OBPI, _SHORT_OBPI):
                        self.assertIsNone(in_flight_launch_id([*rows, ending], given))

    @covers("REQ-0.35.0-15-02")
    def test_a_rename_round_trip_of_another_obpi_changes_nothing_for_this_run(self) -> None:
        """Another OBPI that is renamed and renamed back is where it was, and so is this run.

        The other OBPI passes through an id that shares this run's short
        form and returns to its own. It then has its first name again, so the
        short form names this run alone and the boundary is recorded on it.
        """
        rows = [
            _launched("full", _LAUNCHED_AT),
            _launched("full", _CROSSED_AT, obpi_id=_OTHER_OBPI),
            _renamed(_OTHER_OBPI, _SIBLING_OBPI, _CROSSED_AT),
            _renamed(_SIBLING_OBPI, _OTHER_OBPI, _CROSSED_LATER_AT),
        ]
        named = {
            _OBPI: _OBPI,
            _SHORT_OBPI: _OBPI,
            _OTHER_OBPI: _OTHER_OBPI,
            "OBPI-0.99.0-02": _OTHER_OBPI,
            _SIBLING_OBPI: _OTHER_OBPI,
        }
        for given, launch_id in named.items():
            with self.subTest(given=given):
                self.assertEqual(in_flight_launch_id(rows, given), launch_id)
        self.assertEqual(runs_in_flight(rows), [_OTHER_OBPI, _OBPI], "the latest launched first")
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            for row in rows:
                ledger.append(row)
            plans = Path(tmp) / "plans"
            plans.mkdir()

            record_position(ledger, plans, _SHORT_OBPI, RunCrossing(boundary="precomplete"))

            recorded = [
                row for row in ledger.read_all() if row.event == "pipeline_stage_transition"
            ]
            self.assertEqual([row.id for row in recorded], [_OBPI])
            self.assertEqual(recorded[0].extra["position_label"], "precomplete")


class TestAnIdNamesTheRunInFlightOrNone(unittest.TestCase):
    """The matching rule every producer's record passes through, read on its own."""

    @covers("REQ-0.35.0-15-02")
    def test_a_run_ends_when_its_obpi_is_parked_or_withdrawn(self) -> None:
        """Retirement ends a run as a receipt does (Open Design Questions 12 and 16).

        Parked, withdrawn or superseded: every way ``_RETIREMENTS`` names.

        The run that ends is the retired id's own, and a later launch of that
        id starts a new one. A sibling's launch that its retirement followed
        is then no candidate for the short form: beside a live run it is no
        ambiguity, and alone it is no run.
        """
        launch = _launched("full", _LAUNCHED_AT)
        sibling = _launched("full", _LAUNCHED_AT, obpi_id=_SIBLING_OBPI)
        relaunch = _launched("verify", _CROSSED_LATER_AT)
        for how in _RETIREMENTS:
            retired = _retired(how, _CROSSED_AT)
            sibling_retired = _retired(how, _CROSSED_AT, obpi_id=_SIBLING_OBPI)
            cases: tuple[tuple[str, list[LedgerEvent], str, str | None], ...] = (
                ("the launch id", [launch, retired], _OBPI, None),
                ("the short form", [launch, retired], _SHORT_OBPI, None),
                ("the short form, launched again", [launch, retired, relaunch], _SHORT_OBPI, _OBPI),
                (
                    "the short form beside a retired sibling",
                    [sibling, launch, sibling_retired],
                    _SHORT_OBPI,
                    _OBPI,
                ),
                (
                    "the live run's own id beside a retired sibling",
                    [sibling, launch, sibling_retired],
                    _OBPI,
                    _OBPI,
                ),
                (
                    "the retired sibling's own id",
                    [sibling, launch, sibling_retired],
                    _SIBLING_OBPI,
                    None,
                ),
                (
                    "the short form, only a retired sibling launched",
                    [sibling, sibling_retired],
                    _SHORT_OBPI,
                    None,
                ),
            )
            for name, rows, given, expected in cases:
                with self.subTest(retired=how, case=name):
                    self.assertEqual(in_flight_launch_id(rows, given), expected)

    @covers("REQ-0.35.0-15-02")
    def test_only_a_completion_receipt_ends_a_run(self) -> None:
        """The completion receipt ends the run; any other receipt ends nothing.

        Open Design Question 8 rules that the COMPLETION receipt ends a run.
        The receipt event also carries a ``validated`` receipt, and a row that
        names no kind at all is no completion either: nothing is defaulted.
        """
        launch = _launched("full", _LAUNCHED_AT)
        validated = _receipted(_CROSSED_AT, receipt_event="validated")
        completed = _receipted(_CROSSED_LATER_AT)
        unnamed = completed.model_copy(
            update={"extra": {k: v for k, v in completed.extra.items() if k != "receipt_event"}}
        )
        cases: tuple[tuple[str, list[LedgerEvent], str, str | None], ...] = (
            ("validated, by the launch id", [launch, validated], _OBPI, _OBPI),
            ("validated, by the short form", [launch, validated], _SHORT_OBPI, _OBPI),
            ("a receipt naming no kind", [launch, unnamed], _OBPI, _OBPI),
            ("completed", [launch, completed], _OBPI, None),
            ("validated, then completed", [launch, validated, completed], _SHORT_OBPI, None),
            ("completed, then validated", [launch, completed, validated], _OBPI, None),
        )

        for name, rows, given, expected in cases:
            with self.subTest(case=name):
                self.assertEqual(in_flight_launch_id(rows, given), expected)

    @covers("REQ-0.35.0-15-02")
    def test_an_adr_audit_ceremony_is_no_pipeline_run(self) -> None:
        """``gz adr audit-begin`` writes ``pipeline_launched`` too, and launches no run.

        Its row carries the ADR's id and the entry ``audit``. A run is what
        ``gz obpi pipeline`` launches: the full launch or a ``--from`` entry.
        A launch row with no entry is the full launch, as the replay reads it.
        """
        audit = pipeline_launched_event(
            obpi_id=_ADR,
            parent_adr=_ADR,
            lane="audit",
            nonce=_NONCE,
            marker_path=f".gzkit/audits/{_ADR}.json",
            entry="audit",
        )
        launch = _launched("full", _LAUNCHED_AT)
        no_entry = launch.model_copy(
            update={"extra": {k: v for k, v in launch.extra.items() if k != "entry"}}
        )

        self.assertIsNone(in_flight_launch_id([audit], _ADR))
        self.assertEqual(in_flight_launch_id([audit, launch], _OBPI), _OBPI)
        self.assertEqual(in_flight_launch_id([no_entry], _OBPI), _OBPI)
        for entry in ("full", "verify", "ceremony", "sync"):
            with self.subTest(entry=entry):
                self.assertEqual(
                    in_flight_launch_id([_launched(entry, _LAUNCHED_AT)], _OBPI), _OBPI
                )

    @covers("REQ-0.35.0-15-02")
    def test_the_short_form_is_the_whole_of_the_item_number(self) -> None:
        """The short form ends where the item number does, whatever its width.

        It is the launch id up to the ``-`` that follows the item, or the whole
        id when nothing follows. Item 10 and item 100 in flight together are
        two runs with two short forms, never one ambiguity.
        """
        ten, hundred, seven = (
            "OBPI-0.99.0-10-tenth-item",
            "OBPI-0.99.0-100-hundredth-item",
            "OBPI-0.99.0-7-seventh-item",
        )
        launches = {
            launch_id: _launched("full", _LAUNCHED_AT, obpi_id=launch_id)
            for launch_id in (ten, hundred, seven, "OBPI-0.99.0-100")
        }
        cases: tuple[tuple[str, list[str], str, str | None], ...] = (
            ("item 100 by its short form", [hundred], "OBPI-0.99.0-100", hundred),
            ("item 100 by item 10's short form", [hundred], "OBPI-0.99.0-10", None),
            ("item 100 by item 1's short form", [hundred], "OBPI-0.99.0-1", None),
            ("item 100 by item 1000's short form", [hundred], "OBPI-0.99.0-1000", None),
            ("item 100 with no slug by item 10's", ["OBPI-0.99.0-100"], "OBPI-0.99.0-10", None),
            ("item 10 by its short form", [ten], "OBPI-0.99.0-10", ten),
            ("item 10 by item 100's short form", [ten], "OBPI-0.99.0-100", None),
            ("item 10 beside item 100", [ten, hundred], "OBPI-0.99.0-10", ten),
            ("item 100 beside item 10", [ten, hundred], "OBPI-0.99.0-100", hundred),
            ("a one-digit item by its short form", [seven], "OBPI-0.99.0-7", seven),
            ("a one-digit item by a longer item's", [seven], "OBPI-0.99.0-70", None),
        )

        for name, in_flight, given, expected in cases:
            with self.subTest(case=name):
                rows = [launches[launch_id] for launch_id in in_flight]

                self.assertEqual(in_flight_launch_id(rows, given), expected)

    @covers("REQ-0.35.0-15-02")
    def test_the_run_is_the_launch_in_flight_by_its_id_or_by_its_short_form(self) -> None:
        """The id given, then the short form; one run or none, never a guess.

        A run is in flight from its latest launch until a receipt for that id,
        the ending these cases use; a retirement ends it too, in the test
        above. The id a launch carries always names it. The short form names it when
        no other run in flight shares that form, and names nothing when one
        does. A launch whose own id is the short form is an exact match, so a
        slugged sibling does not make it ambiguous.
        """
        launch = _launched("full", _LAUNCHED_AT)
        sibling = _launched("full", _CROSSED_AT, obpi_id=_SIBLING_OBPI)
        short_launch = _launched("full", _CROSSED_AT, obpi_id=_SHORT_OBPI)
        relaunch = _launched("verify", _CROSSED_LATER_AT)
        ended = _receipted(_CROSSED_AT)
        sibling_ended = _receipted(_CROSSED_LATER_AT, obpi_id=_SIBLING_OBPI)
        cases: tuple[tuple[str, list[LedgerEvent], str, str | None], ...] = (
            ("the launch id", [launch], _OBPI, _OBPI),
            ("its short form", [launch], _SHORT_OBPI, _OBPI),
            ("never launched", [], _SHORT_OBPI, None),
            ("another OBPI's id", [launch], _OTHER_OBPI, None),
            ("another item's short form", [launch], "OBPI-0.99.0-02", None),
            ("a prefix shorter than the short form", [launch], "OBPI-0.99.0-0", None),
            ("a prefix longer than the short form", [launch], f"{_SHORT_OBPI}-run", None),
            ("the launch id, its run ended", [launch, ended], _OBPI, None),
            ("the short form, its run ended", [launch, ended], _SHORT_OBPI, None),
            ("the short form, relaunched", [launch, ended, relaunch], _SHORT_OBPI, _OBPI),
            ("the short form of two runs in flight", [launch, sibling], _SHORT_OBPI, None),
            ("one of two runs by its own id", [launch, sibling], _SIBLING_OBPI, _SIBLING_OBPI),
            (
                "the short form, the sibling's run ended",
                [launch, sibling, sibling_ended],
                _SHORT_OBPI,
                _OBPI,
            ),
            (
                "a launch carrying the short form itself",
                [launch, short_launch],
                _SHORT_OBPI,
                _SHORT_OBPI,
            ),
        )

        for name, rows, given, expected in cases:
            with self.subTest(case=name):
                self.assertEqual(in_flight_launch_id(rows, given), expected)


class TestNeitherAReadNorARebuildMovesUpdatedAt(_RecordingFixture):
    """Requirement 6: ``updated_at`` moves only when the run crosses a boundary."""

    @covers("REQ-0.35.0-15-05")
    def test_reading_a_position_moves_no_marker_and_appends_nothing(self) -> None:
        """Every reader of the run's position leaves both files byte for byte."""
        self._launch_on_ledger()
        self._record("verification")
        (crossing,) = self._crossings()
        held = self._markers()
        rows_held = self.ledger.path.read_bytes()
        rows = list(Ledger(self.ledger.path).read_all())
        now = datetime.fromisoformat(crossing.ts) + timedelta(hours=1)
        readers: dict[str, Callable[[], object]] = {
            "the ledger replay": lambda: replay_pipeline_position(rows, _OBPI),
            "the run in flight": lambda: in_flight_launch_id(rows, _SHORT_OBPI),
            "the runs in flight": lambda: runs_in_flight(rows),
            "the marker loader": lambda: load_obpi_pipeline_marker(self.plans, _OBPI),
            "the dispatch cache": lambda: load_dispatch_state(self.plans, _OBPI),
            "the fence": lambda: marker_stage(self.per_obpi),
            "the resume command": lambda: pipeline_resume_command(_read(self.per_obpi)),
            "stale detection": lambda: find_stale_pipeline_markers(self.plans),
            "a rebuild with the marker on disk": lambda: rebuild_marker(
                rows, self.plans, _OBPI, now=now
            ),
        }

        for name, read in readers.items():
            with self.subTest(reader=name):
                read()

                self.assertEqual(self._markers(), held)
                self.assertEqual(_read(self.per_obpi)["updated_at"], crossing.ts)
                self.assertEqual(self.ledger.path.read_bytes(), rows_held)

    @covers("REQ-0.35.0-15-05")
    def test_a_rebuild_restores_the_time_of_the_last_crossing_whenever_it_runs(self) -> None:
        """The time rebuilt is the crossing's, never the clock's, up to the stale bound.

        Past the bound the marker would be stale on arrival, so none is
        built: a rebuild cannot make an abandoned run look live. The bound is
        the one stale detection uses, older than ``STALE_MARKER_HOURS``.
        """
        rows = [
            _launched("full", _LAUNCHED_AT),
            _crossed("verify", "phase", "verification", _CROSSED_AT),
        ]
        crossed = datetime.fromisoformat(_CROSSED_AT)
        bound = timedelta(hours=STALE_MARKER_HOURS)
        live = {
            "a minute after the crossing": timedelta(minutes=1),
            "a minute inside the bound": bound - timedelta(minutes=1),
            "at the bound": bound,
        }
        for name, after in live.items():
            with self.subTest(rebuilt=name):
                rebuild = rebuild_marker(rows, self.plans, _OBPI, now=crossed + after)

                assert rebuild is not None and rebuild.payload is not None
                self.assertEqual(rebuild.payload["updated_at"], _CROSSED_AT)
                self.assertEqual(rebuild.payload["started_at"], _LAUNCHED_AT)
                self.assertIsNone(rebuild.declined)
        abandoned = {
            "a minute past the bound": bound + timedelta(minutes=1),
            "a month after the crossing": timedelta(days=30),
        }
        for name, after in abandoned.items():
            with self.subTest(rebuilt=name):
                rebuild = rebuild_marker(rows, self.plans, _OBPI, now=crossed + after)

                assert rebuild is not None
                self.assertIsNone(rebuild.payload)
                self.assertIn(_CROSSED_AT, rebuild.declined or "")
        self.assertEqual(list(self.plans.iterdir()), [])

    @covers("REQ-0.35.0-15-05")
    def test_a_launch_never_crossed_is_stale_by_the_time_of_its_launch(self) -> None:
        rows = [_launched("verify", _LAUNCHED_AT)]
        launched = datetime.fromisoformat(_LAUNCHED_AT)
        bound = timedelta(hours=STALE_MARKER_HOURS)

        inside = rebuild_marker(rows, self.plans, _OBPI, now=launched + bound)
        past = rebuild_marker(rows, self.plans, _OBPI, now=launched + bound + timedelta(minutes=1))

        assert inside is not None and inside.payload is not None and past is not None
        self.assertEqual(inside.payload["updated_at"], _LAUNCHED_AT)
        self.assertNotIn("position", inside.payload)
        self.assertIsNone(past.payload)


def _hours_ago(hours: float) -> str:
    moment = datetime.now(UTC) - timedelta(hours=hours)
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


class TestStaleMarkerHandlingIsUnchanged(unittest.TestCase):
    """Requirement 6 of OBPI-0.35.0-15: recording a position changes no stale rule.

    Each marker here is one the run-position work could have disturbed: it
    carries a recorded position, or it is one of the shapes the loader reads
    as unreadable. Stale detection, ``--clear-stale``, the launcher's orphan
    purge and the concurrency block treat each as they did before.

    These tests are bound here and not in ``tests/test_pipeline_runtime.py``,
    where the plan placed them: brief reconciliation reads the imports of every
    module that binds a REQ as that brief's reach, and that module reaches
    ``adr_eval`` and ``pipeline_dispatch``, which this OBPI does not touch.
    """

    _OBPI = "OBPI-0.99.0-01-run-position-demo"
    _OTHER = "OBPI-0.99.0-02-another-run"
    _ADR = "ADR-0.99.0-run-position-demo"

    #: Marker contents no loader reads: the unreadable marker the suite always
    #: had, and the two shapes the loader reads as unreadable since Task 1.
    _UNREADABLE: tuple[tuple[str, bytes], ...] = (
        ("text that is not JSON", b"CORRUPT"),
        ("JSON that is not an object", b'["OBPI-0.99.0-01-run-position-demo"]'),
        ("bytes that are not UTF-8", b"\xff\xfe\x00{}"),
    )

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.plans = Path(tmp.name)
        self.per_obpi, self.legacy = pipeline_marker_paths(self.plans, self._OBPI)

    def _advanced(self, obpi_id: str, updated_at: str | None) -> dict[str, Any]:
        """Return a marker advanced to ``verify`` with a position, last updated then."""
        payload = pipeline_marker_payload(obpi_id, self._ADR, "heavy", None, "pass")
        payload["current_stage"] = "verify"
        payload["position"] = {
            "kind": "phase",
            "label": "verification",
            "boundary": "gz obpi pipeline",
        }
        if updated_at is None:
            del payload["updated_at"]
        else:
            payload["updated_at"] = updated_at
        return payload

    def _write(self, content: bytes | dict[str, Any]) -> None:
        """Write the same content to the per-OBPI and the legacy marker file."""
        raw = content if isinstance(content, bytes) else json.dumps(content).encode("utf-8")
        for marker_path in (self.per_obpi, self.legacy):
            marker_path.write_bytes(raw)

    def _stale_shapes(self) -> list[tuple[str, bytes | dict[str, Any], dict[str, Any], str]]:
        """Return each stale shape: its content, the payload reported, the id cleared."""
        old = self._advanced(self._OBPI, _hours_ago(STALE_MARKER_HOURS + 1))
        timeless = self._advanced(self._OBPI, None)
        unreadable_time = self._advanced(self._OBPI, "yesterday")
        shapes: list[tuple[str, bytes | dict[str, Any], dict[str, Any], str]] = [
            ("older than the stale bound", old, old, self._OBPI),
            ("no updated_at", timeless, timeless, self._OBPI),
            ("an updated_at that is no time", unreadable_time, unreadable_time, self._OBPI),
        ]
        shapes.extend((name, raw, {}, "unknown") for name, raw in self._UNREADABLE)
        return shapes

    @covers("REQ-0.35.0-15-05")
    def test_stale_detection_flags_each_stale_shape_and_no_live_marker(self) -> None:
        for name, content, reported, _cleared_as in self._stale_shapes():
            with self.subTest(marker=name):
                self._write(content)

                stale = find_stale_pipeline_markers(self.plans)

                self.assertEqual(stale, [(self.per_obpi, reported), (self.legacy, reported)])
        with self.subTest(marker="advanced within the stale bound"):
            self._write(self._advanced(self._OBPI, _hours_ago(STALE_MARKER_HOURS - 1)))

            self.assertEqual(find_stale_pipeline_markers(self.plans), [])

    @covers("REQ-0.35.0-15-05")
    def test_clear_stale_removes_each_stale_shape_and_keeps_a_live_marker(self) -> None:
        for name, content, _reported, cleared_as in self._stale_shapes():
            with self.subTest(marker=name):
                self._write(content)

                removed = clear_stale_pipeline_markers(self.plans)

                self.assertEqual(removed, [(self.per_obpi, cleared_as), (self.legacy, cleared_as)])
                self.assertFalse(self.per_obpi.exists() or self.legacy.exists())
        with self.subTest(marker="advanced within the stale bound"):
            live = self._advanced(self._OBPI, _hours_ago(1))
            self._write(live)

            self.assertEqual(clear_stale_pipeline_markers(self.plans), [])
            self.assertEqual(json.loads(self.per_obpi.read_text(encoding="utf-8")), live)
            self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())

    @covers("REQ-0.35.0-15-05")
    def test_the_orphan_purge_removes_only_a_marker_whose_obpi_is_attested_completed(
        self,
    ) -> None:
        """An advanced marker is purged or kept on its OBPI's ledger state alone.

        Its stage, its position and its age decide nothing. A marker the
        loader cannot read names no OBPI and is left for stale detection.
        """

        def _graph(completion: str) -> dict[str, dict[str, Any]]:
            return {
                self._OBPI: {"type": "obpi", "parent": self._ADR, "obpi_completion": completion}
            }

        attested = _graph("attested_completed")
        for age in (1, STALE_MARKER_HOURS + 1):
            with self.subTest(obpi="attested_completed", hours_old=age):
                self._write(self._advanced(self._OBPI, _hours_ago(age)))

                purged = purge_orphaned_active_markers(self.plans, attested)

                self.assertEqual(
                    purged,
                    [
                        (self.per_obpi, self._OBPI, self._ADR),
                        (self.legacy, self._OBPI, self._ADR),
                    ],
                )
                self.assertFalse(self.per_obpi.exists() or self.legacy.exists())
            with self.subTest(obpi="pending", hours_old=age):
                self._write(self._advanced(self._OBPI, _hours_ago(age)))
                held = self.per_obpi.read_bytes()

                self.assertEqual(purge_orphaned_active_markers(self.plans, _graph("pending")), [])
                self.assertEqual(
                    (self.per_obpi.read_bytes(), self.legacy.read_bytes()), (held, held)
                )
        for name, raw in self._UNREADABLE:
            with self.subTest(marker=name):
                self._write(raw)

                self.assertEqual(purge_orphaned_active_markers(self.plans, attested), [])
                self.assertEqual((self.per_obpi.read_bytes(), self.legacy.read_bytes()), (raw, raw))

    @covers("REQ-0.35.0-15-05")
    def test_the_concurrency_block_is_unchanged_by_a_recorded_position(self) -> None:
        """Another OBPI's marker blocks a launch, in either file; a run's own never does."""
        for age in (1, STALE_MARKER_HOURS + 1):
            with self.subTest(hours_old=age):
                self._write(self._advanced(self._OBPI, _hours_ago(age)))

                blocked = pipeline_concurrency_blockers(self.plans, self._OTHER)

                self.assertEqual(len(blocked), 2)
                for blocker in blocked:
                    self.assertIn(self._OBPI, blocker)
                self.assertEqual(pipeline_concurrency_blockers(self.plans, self._OBPI), [])
        for name, raw in self._UNREADABLE:
            with self.subTest(marker=name):
                self._write(raw)

                self.assertEqual(pipeline_concurrency_blockers(self.plans, self._OTHER), [])


_ORIENTATION_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "session_orientation.py"


def _load_orientation_module() -> Any:
    """Load ``scripts/session_orientation.py``, which lives outside the package.

    The way ``tests/scripts/test_session_orientation.py`` loads it. The tests
    bound to REQ-0.35.0-15-06 sit in this module and not that one because a
    bound test module's reach is read as the brief's, and that module's other
    tests reach modules the brief does not allow.
    """
    spec = importlib.util.spec_from_file_location("session_orientation", _ORIENTATION_SCRIPT)
    assert spec is not None and spec.loader is not None, f"cannot load {_ORIENTATION_SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_orientation"] = module
    spec.loader.exec_module(module)
    return module


class TestPipelineSectionShowsWhereARunIs(unittest.TestCase):
    """Requirement 10 of OBPI-0.35.0-15: the stage reached and the position inside it.

    GHI #1172: a marker named the stage the launch command named for the whole
    run, so a new process read ``implement`` for a run already in its ceremony.
    Each case here launches a run and crosses boundaries through the recorder,
    as the run's own commands do, and then reads the orientation. What is
    expected comes from Requirement 2: the stage a work-starting boundary
    enters, the kind of position that stage holds (the Stage 2 task, the
    Stage 3 phase, the Stage 4 round, the Stage 5 step) and the label the
    boundary gives it.
    """

    OBPI = "OBPI-0.3.0-01-example"
    ADR = "ADR-0.3.0-example"
    TASK = "TASK-0.3.0-01-01-01"

    #: (``--from`` value, boundaries crossed, launch stage, stage reached,
    #: kind, label). ``None`` is the full launch.
    ADVANCED: tuple[tuple[str | None, tuple[tuple[str, str | None], ...], str, str, str, str], ...]
    ADVANCED = (
        (None, (("verification", None),), "implement", "verify", "phase", "verification"),
        (
            None,
            (("verification", None), ("verification-passed", None), ("present-evidence", None)),
            "implement",
            "ceremony",
            "round",
            "present-evidence",
        ),
        (None, (("ceremony", None), ("complete", None)), "implement", "sync", "step", "complete"),
        ("verify", (("task-start", TASK),), "verify", "implement", "task", TASK),
    )

    def setUp(self) -> None:
        self.mod = _load_orientation_module()
        self.now = datetime(2026, 10, 12, 12, 0, 0, tzinfo=UTC)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.plans = self.root / ".claude" / "plans"
        (self.root / ".gzkit").mkdir()
        self.ledger = Ledger(self.root / ".gzkit" / "ledger.jsonl")

    def _launch(self, start_from: str | None) -> dict:
        """Write both markers and append the launch, as the pipeline launcher does."""
        payload = pipeline_marker_payload(self.OBPI, self.ADR, "heavy", start_from, "pass")
        per_obpi, _legacy = write_pipeline_markers(self.plans, payload)
        self.ledger.append(
            pipeline_launched_event(
                obpi_id=self.OBPI,
                parent_adr=self.ADR,
                lane="heavy",
                nonce=str(payload["nonce"]),
                marker_path=per_obpi.relative_to(self.root).as_posix(),
                entry=str(payload["entry"]),
            )
        )
        return payload

    def _advance(self, start_from: str | None, crossings: tuple) -> None:
        launched = self._launch(start_from)
        self.assertNotIn("position", launched)
        for boundary, task in crossings:
            crossing = RunCrossing(boundary=boundary, task=task)
            self.assertIsNotNone(record_position(self.ledger, self.plans, self.OBPI, crossing))

    def _start_over(self) -> None:
        self.ledger.path.write_text("", encoding="utf-8")
        for left in self.plans.glob(".pipeline-active*.json"):
            left.unlink()

    @covers("REQ-0.35.0-15-06")
    def test_an_advanced_run_reports_the_stage_reached_and_its_position(self) -> None:
        for start_from, crossings, launch_stage, stage, kind, label in self.ADVANCED:
            with self.subTest(reached=stage):
                self._start_over()
                self._advance(start_from, crossings)

                (run,) = self.mod.collect_adr_pipeline(self.root)

                self.assertEqual(run["obpi_id"], self.OBPI)
                self.assertEqual(run["stage"], stage)
                self.assertNotEqual(run["stage"], launch_stage)
                self.assertIsNotNone(run["position"])
                self.assertEqual((run["position"]["kind"], run["position"]["label"]), (kind, label))

    @covers("REQ-0.35.0-15-06")
    def test_a_position_the_marker_does_not_hold_whole_is_reported_as_none(self) -> None:
        """A marker is a cache anyone can write: a part of a position is no position.

        The run and its stage are still reported, so a marker edited by hand
        degrades to what the orientation said before positions existed.
        """
        not_a_position = {
            "a string": "phase verification",
            "a list": ["phase", "verification"],
            "a kind with no label": {"kind": "phase", "boundary": "gz obpi pipeline"},
            "a label with no kind": {"label": "verification", "boundary": "gz obpi pipeline"},
            "an empty label": {"kind": "phase", "label": " ", "boundary": "gz obpi pipeline"},
            "a kind that is no text": {"kind": 3, "label": "verification"},
        }
        for name, held in not_a_position.items():
            with self.subTest(position=name):
                self._start_over()
                self._advance(None, (("verification", None),))
                for marker_path in self.plans.glob(".pipeline-active*.json"):
                    marker = json.loads(marker_path.read_text(encoding="utf-8"))
                    marker["position"] = held
                    marker_path.write_text(json.dumps(marker), encoding="utf-8")

                (run,) = self.mod.collect_adr_pipeline(self.root)

                self.assertEqual((run["obpi_id"], run["stage"]), (self.OBPI, "verify"))
                self.assertIsNone(run["position"])

    def _run_lines(self) -> tuple[str, list[str]]:
        """Return the rendered line that names the run, and the lines under it."""
        runs = self.mod.collect_adr_pipeline(self.root)
        rendered = self.mod.render({"adr_pipeline": runs}, self.now)
        section = rendered.split("## Active ADR pipeline state", 1)[1].split("\n## ", 1)[0]
        lines = section.splitlines()
        (named,) = [index for index, line in enumerate(lines) if line.startswith(f"- {self.OBPI}")]
        under = []
        for line in lines[named + 1 :]:
            if not line.startswith("  "):
                break
            under.append(line)
        return lines[named], under

    @covers("REQ-0.35.0-15-06")
    def test_the_section_shows_the_stage_reached_and_its_position(self) -> None:
        """The launch stage never stands in for the stage reached or the position."""
        # output-contract: the orientation section is what a new process reads.
        for start_from, crossings, launch_stage, stage, kind, label in self.ADVANCED:
            with self.subTest(reached=stage):
                self._start_over()
                self._advance(start_from, crossings)

                headline, under = self._run_lines()

                self.assertIn(stage, headline)
                self.assertNotIn(launch_stage, headline)
                positioned = [line for line in under if kind in line and label in line]
                self.assertEqual(len(positioned), 1, under)
                self.assertNotIn(launch_stage, positioned[0])

    @covers("REQ-0.35.0-15-06")
    def test_a_launch_with_nothing_after_it_shows_its_stage_and_claims_no_position(self) -> None:
        """No boundary crossed is no position: the section invents none (Requirement 4)."""
        # output-contract: the orientation section is what a new process reads.
        self._advance(None, (("verification", None),))
        _headline, positioned = self._run_lines()
        position_lines = [line for line in positioned if "phase" in line]
        self.assertEqual(len(position_lines), 1, positioned)
        said = position_lines[0].split("phase", 1)[0]
        for start_from, launch_stage in ((None, "implement"), ("ceremony", "ceremony")):
            with self.subTest(entry=start_from or "full"):
                self._start_over()
                self._launch(start_from)

                (run,) = self.mod.collect_adr_pipeline(self.root)
                headline, under = self._run_lines()

                self.assertEqual(run["stage"], launch_stage)
                self.assertIsNone(run["position"])
                self.assertIn(launch_stage, headline)
                self.assertEqual([line for line in under if line.startswith(said)], [])


class TestAMarkerRecordsAWholePositionOrNone(unittest.TestCase):
    """Requirement 10 of OBPI-0.35.0-15: what counts as a position on a marker.

    The session orientation shows the position inside the stage for every run
    in flight, and it reads that position from a marker, a cache any process
    can write. One function decides what the marker records: a kind and a
    label in text, with the boundary that marked them. Anything short of that
    is no position, and the orientation then shows the stage alone. Nothing
    is refused on what a marker says (Requirement 12): a marker with no whole
    position is read, not rejected.
    """

    _WHOLE = {"kind": "phase", "label": "verification", "boundary": "gz obpi pipeline"}

    @covers("REQ-0.35.0-15-06")
    def test_a_kind_and_a_label_in_text_are_a_position_and_nothing_less_is(self) -> None:
        whole = dict(self._WHOLE)
        no_boundary = {"kind": "phase", "label": "verification", "boundary": ""}
        cases: tuple[tuple[str, dict[str, Any], dict[str, str] | None], ...] = (
            ("a whole position", {"position": dict(whole)}, whole),
            (
                "text with space around it",
                {"position": {"kind": " phase ", "label": " verification\n", "boundary": " x "}},
                {"kind": "phase", "label": "verification", "boundary": "x"},
            ),
            ("no position key", {"current_stage": "verify"}, None),
            ("a position that is null", {"position": None}, None),
            ("a position that is text", {"position": "phase verification"}, None),
            ("a position that is a list", {"position": ["phase", "verification"]}, None),
            ("no kind", {"position": {"label": "verification", "boundary": "b"}}, None),
            ("a blank kind", {"position": {**whole, "kind": "  "}}, None),
            ("a kind that is no text", {"position": {**whole, "kind": 3}}, None),
            ("no label", {"position": {"kind": "phase", "boundary": "b"}}, None),
            ("a blank label", {"position": {**whole, "label": ""}}, None),
            ("a label that is no text", {"position": {**whole, "label": ["verification"]}}, None),
            (
                "no boundary",
                {"position": {"kind": "phase", "label": "verification"}},
                no_boundary,
            ),
            ("a boundary that is no text", {"position": {**whole, "boundary": 7}}, no_boundary),
        )
        for name, marker, expected in cases:
            with self.subTest(marker_holds=name):
                self.assertEqual(marker_position(marker), expected)


if __name__ == "__main__":
    unittest.main()
