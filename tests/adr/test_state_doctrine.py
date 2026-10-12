"""Tests for gz state --repair (OBPI-0.0.9-03: State Repair Command).

Validates that state_repair force-reconciles frontmatter status from
ledger-derived state, reports changes, and is idempotent; and that it rebuilds
a deleted pipeline marker from the ledger alone (OBPI-0.35.0-15).
"""

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit import obpi_dispatch_channel as chan
from gzkit.commands.state import (
    _derive_expected_status,
    _scan_obpi_briefs,
    state,
    state_repair,
)
from gzkit.ledger import (
    Ledger,
    LedgerEvent,
    obpi_receipt_emitted_event,
    pipeline_launched_event,
    pipeline_stage_transition_event,
)
from gzkit.ledger_events import obpi_parked_event, obpi_unparked_event, obpi_withdrawn_event
from gzkit.pipeline_runtime import (
    STALE_MARKER_HOURS,
    RunCrossing,
    find_stale_pipeline_markers,
    pipeline_marker_paths,
    pipeline_marker_payload,
    pipeline_receipt_path,
    record_position,
    write_pipeline_markers,
)
from gzkit.traceability import covers

_quiet_console = Console(file=StringIO())


class TestDeriveExpectedStatus(unittest.TestCase):
    """Unit tests for mapping ledger graph info to expected frontmatter status."""

    def test_completed_obpi(self) -> None:
        info = {"type": "obpi", "ledger_completed": True, "withdrawn": False}
        self.assertEqual(_derive_expected_status(info), "Completed")

    def test_withdrawn_obpi(self) -> None:
        info = {"type": "obpi", "ledger_completed": False, "withdrawn": True}
        self.assertEqual(_derive_expected_status(info), "Abandoned")

    def test_withdrawn_takes_precedence_over_completed(self) -> None:
        info = {"type": "obpi", "ledger_completed": True, "withdrawn": True}
        self.assertEqual(_derive_expected_status(info), "Abandoned")

    def test_pending_obpi_returns_none(self) -> None:
        info = {"type": "obpi", "ledger_completed": False, "withdrawn": False}
        self.assertIsNone(_derive_expected_status(info))

    def test_non_obpi_returns_none(self) -> None:
        info = {"type": "adr", "attested": False}
        self.assertIsNone(_derive_expected_status(info))


class TestScanObpiBriefs(unittest.TestCase):
    """Unit tests for OBPI brief file scanning."""

    def test_scan_finds_obpi_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp) / "docs" / "design" / "adr" / "ADR-0.1.0" / "obpis"
            adr_dir.mkdir(parents=True)
            brief = adr_dir / "OBPI-0.1.0-01-test.md"
            brief.write_text(
                "---\nid: OBPI-0.1.0-01-test\nparent: ADR-0.1.0\n"
                "item: 1\nlane: lite\nstatus: Draft\n---\n# Test\n",
                encoding="utf-8",
            )
            result = _scan_obpi_briefs(Path(tmp), "docs/design")
            self.assertEqual(len(result), 1)
            self.assertIn("OBPI-0.1.0-01", result)
            self.assertEqual(result["OBPI-0.1.0-01"]["frontmatter_status"], "Draft")

    def test_scan_empty_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _scan_obpi_briefs(Path(tmp), "docs/design")
            self.assertEqual(result, {})


@patch("gzkit.commands.state.console", _quiet_console)
class TestStateRepairIdempotency(unittest.TestCase):
    """Verify repair is idempotent: second run produces no changes."""

    def _setup_brief(self, tmp: str, status: str = "Draft") -> Path:
        adr_dir = Path(tmp) / "docs" / "design" / "adr" / "ADR-0.1.0" / "obpis"
        adr_dir.mkdir(parents=True)
        brief = adr_dir / "OBPI-0.1.0-01-test.md"
        brief.write_text(
            f"---\nid: OBPI-0.1.0-01-test\nparent: ADR-0.1.0\n"
            f"item: 1\nlane: lite\nstatus: {status}\n---\n# Test\n",
            encoding="utf-8",
        )
        return brief

    def _make_graph(self, completed: bool = True) -> dict:
        return {
            "OBPI-0.1.0-01": {
                "type": "obpi",
                "ledger_completed": completed,
                "withdrawn": False,
                "parent": "ADR-0.1.0",
            },
        }

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_repair_updates_frontmatter(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._setup_brief(tmp, status="Draft")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = self._make_graph(completed=True)
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            state_repair(as_json=False)

            updated = brief.read_text(encoding="utf-8")
            self.assertIn("status: Completed", updated)

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_repair_is_idempotent(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._setup_brief(tmp, status="Completed")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = self._make_graph(completed=True)
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            # Should produce no changes
            state_repair(as_json=False)

            updated = brief.read_text(encoding="utf-8")
            self.assertIn("status: Completed", updated)

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_repair_json_output(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._setup_brief(tmp, status="Draft")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = self._make_graph(completed=True)
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            with patch("builtins.print") as mock_print:
                state_repair(as_json=True)
                output = mock_print.call_args[0][0]
                data = json.loads(output)
                self.assertIsInstance(data, dict)
                self.assertIn("changes", data)
                self.assertEqual(len(data["changes"]), 1)
                self.assertEqual(data["changes"][0]["old_status"], "Draft")
                self.assertEqual(data["changes"][0]["new_status"], "Completed")

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_repair_withdrawn_obpi(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._setup_brief(tmp, status="Draft")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            graph = {
                "OBPI-0.1.0-01": {
                    "type": "obpi",
                    "ledger_completed": False,
                    "withdrawn": True,
                    "parent": "ADR-0.1.0",
                },
            }
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = graph
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            state_repair(as_json=False)

            updated = brief.read_text(encoding="utf-8")
            self.assertIn("status: Abandoned", updated)

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_no_changes_when_already_aligned(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        """No changes reported when frontmatter already matches ledger."""
        with tempfile.TemporaryDirectory() as tmp:
            self._setup_brief(tmp, status="Completed")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = self._make_graph(completed=True)
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            with patch("builtins.print") as mock_print:
                state_repair(as_json=True)
                output = mock_print.call_args[0][0]
                data = json.loads(output)
                self.assertEqual(len(data["changes"]), 0)


@patch("gzkit.commands.state.console", _quiet_console)
class TestStateWithdrawnFilter(unittest.TestCase):
    """GHI #221: withdrawn OBPIs are hidden from gz state --json by default."""

    def _graph_with_withdrawn(self) -> dict:
        return {
            "ADR-0.0.16": {
                "type": "adr",
                "attested": True,
                "children": [
                    "OBPI-0.0.16-01",
                    "OBPI-0.0.16-06",
                ],
            },
            "OBPI-0.0.16-01": {
                "type": "obpi",
                "parent": "ADR-0.0.16",
                "ledger_completed": True,
                "withdrawn": False,
                "children": [],
            },
            "OBPI-0.0.16-06": {
                "type": "obpi",
                "parent": "ADR-0.0.16",
                "ledger_completed": False,
                "withdrawn": True,
                "children": [],
            },
        }

    def _invoke(self, include_withdrawn: bool) -> dict:
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch("gzkit.commands.state.ensure_initialized") as mock_init,
            patch("gzkit.commands.state.get_project_root") as mock_root,
            patch("gzkit.commands.state.Ledger") as mock_ledger_cls,
        ):
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            config.mode = "lite"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = self._graph_with_withdrawn()
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            with patch("builtins.print") as mock_print:
                state(
                    as_json=True,
                    blocked=False,
                    ready=False,
                    include_withdrawn=include_withdrawn,
                )
                return json.loads(mock_print.call_args[0][0])

    def test_withdrawn_obpi_hidden_by_default(self) -> None:
        data = self._invoke(include_withdrawn=False)
        self.assertNotIn("OBPI-0.0.16-06", data)
        self.assertIn("OBPI-0.0.16-01", data)

    def test_withdrawn_id_scrubbed_from_parent_children(self) -> None:
        data = self._invoke(include_withdrawn=False)
        self.assertEqual(data["ADR-0.0.16"]["children"], ["OBPI-0.0.16-01"])

    def test_include_withdrawn_restores_entry_and_child_ref(self) -> None:
        data = self._invoke(include_withdrawn=True)
        self.assertIn("OBPI-0.0.16-06", data)
        self.assertIn("OBPI-0.0.16-06", data["ADR-0.0.16"]["children"])


_RUN = "OBPI-0.99.0-01-run-position-demo"
_OTHER_RUN = "OBPI-0.99.0-02-another-run"
_RUN_ADR = "ADR-0.99.0-run-position-demo"
_TASK = "TASK-0.99.0-01-01-01"
_FAILURE = "uv run gz test: exit 1"

#: How a run launched in full reaches each stage, as (boundary, task, blockers)
#: crossings, and the position Requirement 2 says its last crossing names: the
#: kind is the kind of the stage reached, the label the task or the boundary.
_REACHED: dict[str, tuple[tuple[tuple[str, str | None, list[str]], ...], tuple[str, str]]] = {
    "implement": ((("task-start", _TASK, []),), ("task", _TASK)),
    "verify": (
        (("verification", None, []), ("verification-failed", None, [_FAILURE])),
        ("phase", "verification-failed"),
    ),
    "ceremony": (
        (
            ("verification", None, []),
            ("verification-passed", None, []),
            ("ceremony", None, []),
            ("present-evidence", None, []),
        ),
        ("round", "present-evidence"),
    ),
    "sync": (
        (("ceremony", None, []), ("complete", None, []), ("precomplete", None, [])),
        ("step", "precomplete"),
    ),
}

#: What a launch with nothing after it reads (Requirement 5), by ``--from``
#: value: ``entry``, ``current_stage``, ``resume_point`` and whether the launch
#: asks a human action. ``None`` is the full launch.
_LAUNCHED_AS: dict[str | None, tuple[str, str, str | None, bool]] = {
    None: ("full", "implement", "verify", False),
    "verify": ("verify", "verify", "ceremony", False),
    "ceremony": ("ceremony", "ceremony", "sync", True),
    "sync": ("sync", "sync", None, False),
}


def _ago(hours: float) -> str:
    """Return the ledger timestamp of a moment ``hours`` before now."""
    return (datetime.now(UTC) - timedelta(hours=hours)).isoformat()


def _read_marker(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _but(marker: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {key: value for key, value in marker.items() if key not in keys}


class _RepairableRun(unittest.TestCase):
    """A project whose ledger holds pipeline runs, repaired through ``state_repair``."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.plans = self.root / ".claude" / "plans"
        self.plans.mkdir(parents=True)
        (self.root / ".gzkit").mkdir()
        (self.root / ".gzkit" / "ledger.jsonl").touch()
        self.ledger = Ledger(self.root / ".gzkit" / "ledger.jsonl")
        self.per_obpi, self.legacy = pipeline_marker_paths(self.plans, _RUN)

    def _start_over(self) -> None:
        """Empty the ledger and the plans directory, for the next case of a table."""
        self.ledger.path.write_text("", encoding="utf-8")
        self.ledger = Ledger(self.ledger.path)
        for left in self.plans.iterdir():
            left.unlink()

    def _repair(self, *, as_json: bool = True) -> dict[str, Any]:
        """Run ``gz state --repair --json`` on the project and return its report."""
        config = MagicMock()
        config.paths.ledger = ".gzkit/ledger.jsonl"
        config.paths.design_root = "docs/design"
        with (
            patch("gzkit.commands.state.ensure_initialized", return_value=config),
            patch("gzkit.commands.state.get_project_root", return_value=self.root),
            patch("builtins.print") as printed,
        ):
            state_repair(as_json=as_json)
        return json.loads(printed.call_args[0][0]) if as_json else {}

    def _launch(
        self, start_from: str | None = None, *, obpi_id: str = _RUN, ts: str | None = None
    ) -> dict[str, Any]:
        """Write both markers and append the launch, as ``gz obpi pipeline`` does."""
        payload = pipeline_marker_payload(
            obpi_id, _RUN_ADR, "heavy", start_from, "pass", requires_human_attestation=True
        )
        per_obpi, _legacy = write_pipeline_markers(self.plans, payload)
        launch = pipeline_launched_event(
            obpi_id=obpi_id,
            parent_adr=_RUN_ADR,
            lane="heavy",
            nonce=str(payload["nonce"]),
            marker_path=per_obpi.relative_to(self.root).as_posix(),
            entry=str(payload["entry"]),
        )
        self.ledger.append(launch if ts is None else launch.model_copy(update={"ts": ts}))
        return payload

    def _cross(
        self, boundary: str, task: str | None = None, blockers: list[str] | None = None
    ) -> None:
        """Cross one ruled boundary through the recorder, as its command does."""
        crossing = RunCrossing(boundary=boundary, task=task, blockers=blockers or [])
        self.assertIsNotNone(record_position(self.ledger, self.plans, _RUN, crossing))

    def _crossed_at(self, ts: str, *, obpi_id: str = _RUN) -> None:
        """Append a verification crossing at a time of the test's choosing."""
        crossed = pipeline_stage_transition_event(
            obpi_id=obpi_id,
            parent_adr=_RUN_ADR,
            stage="verify",
            position_kind="phase",
            position_label="verification",
            boundary="gz obpi pipeline",
        )
        self.ledger.append(crossed.model_copy(update={"ts": ts}))

    def _rows(self, event: str, *, obpi_id: str = _RUN) -> list[LedgerEvent]:
        return [
            row
            for row in Ledger(self.ledger.path).read_all()
            if row.event == event and row.id == obpi_id
        ]

    def _receipt_on_disk(self, verdict: str = "PASS") -> None:
        pipeline_receipt_path(self.plans, _RUN).write_text(
            json.dumps({"obpi_id": _RUN, "verdict": verdict}) + "\n", encoding="utf-8"
        )

    def _delete_markers(self, *, obpi_id: str = _RUN) -> None:
        for marker_path in pipeline_marker_paths(self.plans, obpi_id):
            marker_path.unlink(missing_ok=True)

    def _markers_on_disk(self) -> list[str]:
        return sorted(path.name for path in self.plans.glob(".pipeline-active*.json"))

    def _rebuilt(self) -> dict[str, Any]:
        """Return the rebuilt marker, read from both files, which must agree."""
        for marker_path in (self.per_obpi, self.legacy):
            self.assertTrue(marker_path.is_file(), f"{marker_path.name} was not rebuilt")
        self.assertEqual(self.per_obpi.read_bytes(), self.legacy.read_bytes())
        return _read_marker(self.per_obpi)


class TestRepairRebuildsADeletedMarker(_RepairableRun):
    """Requirement 4: a deleted marker is rebuilt from Layer 1 and Layer 2 alone."""

    @covers("REQ-0.35.0-15-03")
    def test_a_deleted_marker_is_rebuilt_to_the_stage_and_position_it_held(self) -> None:
        """Same stage, same position, a launch's nonce, the last crossing's time.

        Everything else the marker held comes back too, because every key has
        a ledger source or is read back from the receipt file. ``started_at``
        is the one exception: the launch event's own time replaces the
        launcher's clock reading.
        """
        for stage, (crossings, (kind, label)) in _REACHED.items():
            with self.subTest(stage=stage):
                self._start_over()
                self._receipt_on_disk()
                launched = self._launch()
                for boundary, task, blockers in crossings:
                    self._cross(boundary, task, blockers)
                held = _read_marker(self.per_obpi)
                (launch,) = self._rows("pipeline_launched")
                last = self._rows("pipeline_stage_transition")[-1]
                self._delete_markers()

                report = self._repair()

                rebuilt = self._rebuilt()
                self.assertEqual(rebuilt["current_stage"], stage)
                self.assertEqual(rebuilt["current_stage"], held["current_stage"])
                self.assertEqual(rebuilt["position"], held["position"])
                self.assertEqual(
                    (rebuilt["position"]["kind"], rebuilt["position"]["label"]), (kind, label)
                )
                self.assertEqual(rebuilt["updated_at"], last.ts)
                self.assertEqual(rebuilt["nonce"], launch.extra["nonce"])
                self.assertEqual(rebuilt["nonce"], launched["nonce"])
                self.assertEqual(rebuilt["started_at"], launch.ts)
                self.assertEqual(_but(rebuilt, "started_at"), _but(held, "started_at"))
                self.assertEqual(
                    report["markers"],
                    {
                        "rebuilt": [
                            {
                                "obpi_id": _RUN,
                                "current_stage": stage,
                                "position": held["position"],
                                "updated_at": last.ts,
                            }
                        ],
                        "declined": [],
                    },
                )
                self.assertEqual((report["changes"], report["total"]), ([], 0))

    @covers("REQ-0.35.0-15-03")
    def test_the_rebuilt_time_is_the_last_crossing_and_not_the_rebuild(self) -> None:
        launched_at, crossed_at = _ago(3), _ago(2)
        self._launch(ts=launched_at)
        self._crossed_at(_ago(2.5))
        self._crossed_at(crossed_at)
        self._delete_markers()
        repair_began = datetime.now(UTC)

        self._repair()

        rebuilt = self._rebuilt()
        self.assertEqual(rebuilt["updated_at"], crossed_at)
        self.assertEqual(rebuilt["started_at"], launched_at)
        self.assertLess(datetime.fromisoformat(rebuilt["updated_at"]), repair_began)

    @covers("REQ-0.35.0-15-03")
    def test_a_launch_with_nothing_after_it_rebuilds_to_its_launch_values(self) -> None:
        for start_from, (entry, stage, resume_point, asks_a_human) in _LAUNCHED_AS.items():
            with self.subTest(entry=entry):
                self._start_over()
                self._receipt_on_disk()
                launched_at = _ago(1)
                launched = self._launch(start_from, ts=launched_at)
                held = _read_marker(self.per_obpi)
                self._delete_markers()

                self._repair()

                rebuilt = self._rebuilt()
                self.assertEqual(rebuilt["entry"], entry)
                self.assertEqual(rebuilt["current_stage"], stage)
                self.assertEqual(rebuilt["resume_point"], resume_point)
                self.assertEqual(rebuilt["blockers"], [])
                self.assertEqual(rebuilt["required_human_action"] is not None, asks_a_human)
                self.assertNotIn("position", rebuilt)
                self.assertEqual(rebuilt["nonce"], launched["nonce"])
                self.assertEqual(rebuilt["updated_at"], launched_at)
                self.assertEqual(rebuilt["started_at"], launched_at)
                clocks = ("started_at", "updated_at")
                self.assertEqual(_but(rebuilt, *clocks), _but(held, *clocks))

    @covers("REQ-0.35.0-15-03")
    def test_a_relaunched_run_is_rebuilt_from_its_latest_launch(self) -> None:
        """The run is the latest launch: its nonce, its entry, the crossings after it."""
        self._launch()
        self._cross("verification")
        relaunched = self._launch("ceremony")
        self._delete_markers()

        self._repair()

        rebuilt = self._rebuilt()
        self.assertEqual(rebuilt["nonce"], relaunched["nonce"])
        self.assertEqual((rebuilt["entry"], rebuilt["current_stage"]), ("ceremony", "ceremony"))
        self.assertNotIn("position", rebuilt)

    def test_the_receipt_state_is_read_back_from_the_receipt_file(self) -> None:
        for on_disk, expected in ((None, "missing"), ("PASS", "pass"), ("FAIL", "fail")):
            with self.subTest(receipt=on_disk):
                self._start_over()
                if on_disk is not None:
                    self._receipt_on_disk(on_disk)
                self._launch()
                self._delete_markers()

                self._repair()

                self.assertEqual(self._rebuilt()["receipt_state"], expected)

    def test_the_dispatch_caches_are_not_rebuilt_and_credit_still_reads_the_ledger(self) -> None:
        """``dispatch_state`` and the single-driver declaration are caches (GHI #886)."""
        self._launch()
        chan.record_dispatch(self.root, _RUN, role="Implementer", model="sonnet", task_id=1)
        chan.declare_single_driver(self.root, _RUN, reason="cron run, no Agent tool")
        held = _read_marker(self.per_obpi)
        self.assertIn("dispatch_state", held)
        self.assertIn("single_driver_declaration", held)
        self._delete_markers()

        self._repair()

        rebuilt = self._rebuilt()
        self.assertNotIn("dispatch_state", rebuilt)
        self.assertNotIn("single_driver_declaration", rebuilt)
        self.assertEqual(rebuilt["position"], held["position"])
        by_role = {entry.role: entry for entry in chan.dispatch_channel(self.root, _RUN)}
        self.assertEqual(by_role["Implementer"].disposition, chan.DispatchDisposition.DISPATCHED)
        self.assertTrue(chan.single_driver_declaration(self.root, _RUN))


class TestRepairRebuildsOnlyARunInFlightWhoseMarkerIsGone(_RepairableRun):
    """A rebuild moves no marker on disk and writes nothing the ledger does not hold."""

    def test_a_marker_on_disk_is_never_moved(self) -> None:
        """Even behind the ledger, and even when only the legacy file is gone."""
        self._launch()
        self._cross("verification")
        self._crossed_at(_ago(-0.01))
        for gone in ((), (self.legacy,)):
            with self.subTest(gone=[path.name for path in gone]):
                for marker_path in gone:
                    marker_path.unlink()
                held = self.per_obpi.read_bytes()
                on_disk = self._markers_on_disk()

                report = self._repair()

                self.assertEqual(self.per_obpi.read_bytes(), held)
                self.assertEqual(self._markers_on_disk(), on_disk)
                self.assertEqual(report["markers"], {"rebuilt": [], "declined": []})

    def test_a_run_that_is_not_in_flight_is_not_rebuilt(self) -> None:
        """The recorder's own rule: ended by its completion, parked, withdrawn, unparked."""
        completed = obpi_receipt_emitted_event(
            _RUN,
            receipt_event="completed",
            attestor="test",
            obpi_completion="attested_completed",
            parent_adr=_RUN_ADR,
        )
        parked = obpi_parked_event(_RUN, _RUN_ADR, "ADR-pool.interrogate")
        ended: dict[str, list[LedgerEvent]] = {
            "completed": [completed],
            "parked": [parked],
            "withdrawn": [obpi_withdrawn_event(_RUN, _RUN_ADR, "superseded", "g0")],
            "parked, then unparked and not launched again": [
                parked,
                obpi_unparked_event(_RUN, _RUN_ADR, "ADR-pool.interrogate"),
            ],
        }
        for name, rows in ended.items():
            with self.subTest(ended=name):
                self._start_over()
                self._launch()
                self._cross("verification")
                for row in rows:
                    self.ledger.append(row)
                self._delete_markers()

                report = self._repair()

                self.assertEqual(self._markers_on_disk(), [])
                self.assertEqual(report["markers"], {"rebuilt": [], "declined": []})

    def test_a_receipt_that_is_not_a_completion_leaves_the_run_to_be_rebuilt(self) -> None:
        self._launch()
        self._cross("verification")
        self.ledger.append(
            obpi_receipt_emitted_event(
                _RUN, receipt_event="validated", attestor="test", parent_adr=_RUN_ADR
            )
        )
        self._delete_markers()

        self._repair()

        self.assertEqual(self._rebuilt()["current_stage"], "verify")

    def test_an_adr_audit_ceremony_is_not_rebuilt_as_a_run(self) -> None:
        """``gz adr audit`` writes ``pipeline_launched`` under the ADR's id; it is no run."""
        self.ledger.append(
            pipeline_launched_event(
                obpi_id=_RUN_ADR,
                parent_adr=_RUN_ADR,
                lane="audit",
                nonce="0123456789abcdef0123456789abcdef",
                marker_path=f".gzkit/audits/{_RUN_ADR}.json",
                entry="audit",
            )
        )

        report = self._repair()

        self.assertEqual(self._markers_on_disk(), [])
        self.assertEqual(report["markers"], {"rebuilt": [], "declined": []})

    def test_another_runs_marker_file_is_never_overwritten(self) -> None:
        """A rebuild writes both files, so it stands down when either is not its own."""
        other = pipeline_marker_payload(
            _OTHER_RUN, _RUN_ADR, "heavy", None, "pass", requires_human_attestation=True
        )
        in_the_way: dict[str, Any] = {
            "the legacy marker names another OBPI": lambda: write_pipeline_markers(
                self.plans, other
            ),
            "the legacy marker is unreadable": lambda: self.legacy.write_text(
                "CORRUPT", encoding="utf-8"
            ),
            "its own marker file is unreadable": lambda: self.per_obpi.write_text(
                "CORRUPT", encoding="utf-8"
            ),
        }
        for name, arrange in in_the_way.items():
            with self.subTest(case=name):
                self._start_over()
                self._launch()
                self._delete_markers()
                arrange()
                held = {path.name: path.read_bytes() for path in self.plans.iterdir()}

                report = self._repair()

                after = {path.name: path.read_bytes() for path in self.plans.iterdir()}
                self.assertEqual(after, held)
                self.assertEqual(report["markers"]["rebuilt"], [])
                (declined,) = report["markers"]["declined"]
                self.assertEqual(declined["obpi_id"], _RUN)
                self.assertTrue(declined["reason"])

    def test_of_two_runs_in_flight_the_one_launched_last_is_rebuilt(self) -> None:
        """The legacy marker is one file: it names the latest launch, as a launch leaves it."""
        self._launch(ts=_ago(3))
        self._launch(obpi_id=_OTHER_RUN, ts=_ago(2))
        self._delete_markers()
        self._delete_markers(obpi_id=_OTHER_RUN)

        report = self._repair()

        self.assertEqual([each["obpi_id"] for each in report["markers"]["rebuilt"]], [_OTHER_RUN])
        self.assertEqual([each["obpi_id"] for each in report["markers"]["declined"]], [_RUN])
        self.assertEqual(_read_marker(self.legacy)["obpi_id"], _OTHER_RUN)
        self.assertFalse(self.per_obpi.exists())


class TestRepairDeclinesARunStaleOnArrival(_RepairableRun):
    """Requirement 6: a rebuild never makes an abandoned run look live."""

    @covers("REQ-0.35.0-15-05")
    def test_a_run_whose_last_crossing_is_past_the_stale_bound_is_declined(self) -> None:
        """Its marker would be stale on arrival, so none is written and the run is named."""
        last_crossing = _ago(STALE_MARKER_HOURS + 1)
        self._launch(ts=_ago(STALE_MARKER_HOURS + 2))
        self._crossed_at(last_crossing)
        held = _read_marker(self.per_obpi)
        self._delete_markers()

        report = self._repair()

        self.assertEqual(self._markers_on_disk(), [])
        self.assertEqual(report["markers"]["rebuilt"], [])
        (declined,) = report["markers"]["declined"]
        self.assertEqual(declined["obpi_id"], _RUN)
        self.assertIn(last_crossing, declined["reason"])
        # The marker it declined to write is one stale detection would flag at once.
        write_pipeline_markers(self.plans, {**held, "updated_at": last_crossing})
        self.assertEqual(len(find_stale_pipeline_markers(self.plans)), 2)

    @covers("REQ-0.35.0-15-05")
    def test_a_run_inside_the_stale_bound_is_rebuilt_and_is_not_stale(self) -> None:
        last_crossing = _ago(STALE_MARKER_HOURS - 1)
        self._launch(ts=_ago(STALE_MARKER_HOURS + 2))
        self._crossed_at(last_crossing)
        self._delete_markers()

        self._repair()

        self.assertEqual(self._rebuilt()["updated_at"], last_crossing)
        self.assertEqual(find_stale_pipeline_markers(self.plans), [])


@patch("gzkit.commands.state.console", _quiet_console)
class TestRepairReportRendering(_RepairableRun):
    """The human report names each marker rebuilt and each run declined, with its reason."""

    def _render(self) -> str:
        shown = StringIO()
        with patch("gzkit.commands.state.console", Console(file=shown, width=400)):
            self._repair(as_json=False)
        return shown.getvalue()

    def test_a_rebuilt_marker_is_named_with_its_stage(self) -> None:
        # output-contract: `gz state --repair` reports what it rebuilt.
        self._launch()
        self._cross("verification")
        self._delete_markers()

        shown = self._render()

        self.assertIn(f"Rebuilt pipeline marker: {_RUN} at stage verify", shown)

    def test_a_declined_run_is_named_with_its_reason(self) -> None:
        # output-contract: `gz state --repair` reports each run it declines, and why.
        last_crossing = _ago(STALE_MARKER_HOURS + 1)
        self._launch(ts=last_crossing)
        self._delete_markers()

        shown = self._render()

        self.assertIn(f"Pipeline marker not rebuilt: {_RUN}", shown)
        self.assertIn(last_crossing, shown)


if __name__ == "__main__":
    unittest.main()
