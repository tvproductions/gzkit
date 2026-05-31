"""Tests for gz validate --task-envelope-coherence (OBPI-0.0.64-04).

REQ-derived assertions for:
  REQ-0.0.64-04-01: signature (a) — worklog event under active TASK with no task_id
  REQ-0.0.64-04-02: signature (b) — OBPI all-seq=01 without req_atomic suppression
  REQ-0.0.64-04-03: signature (c) — layer-drift across frontmatter tasks: and ledger task_id
  REQ-0.0.64-04-05: gz task envelope diagnose renders per-channel declarations
  REQ-0.0.64-04-06: validator is registered in the gz check pipeline
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from gzkit.commands import validate_cmd
from gzkit.commands.validate_cmd import _validate_task_envelope_coherence
from gzkit.traceability import covers


def _write_ledger(root: Path, lines: list[str]) -> None:
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)
    (gzkit_dir / "ledger.jsonl").write_text("\n".join(lines), encoding="utf-8")


def _write_brief(root: Path, frontmatter: dict) -> Path:
    brief_dir = (
        root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.64-test-fixture" / "obpis"
    )
    brief_dir.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.dump(frontmatter, default_flow_style=False)
    body = "\n# Test Brief\n\n## Acceptance Criteria\n\n- [ ] REQ-0.0.64-04-01\n"
    brief_path = brief_dir / "OBPI-0.0.64-04-fixture.md"
    brief_path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")
    return brief_path


_BASE_FM = {
    "id": "OBPI-0.0.64-04",
    "parent": "ADR-0.0.64-task-envelope-and-planning-decomposition",
    "lane": "Heavy",
    "status": "Draft",
    "allowlist": ["src/gzkit/commands/validate_cmd.py"],
    "reqs": ["REQ-0.0.64-04-01"],
    "verification": ["uv run gz lint"],
}


def _write_brief_with_id(root: Path, obpi_id: str) -> Path:
    """Write a minimal OBPI brief whose frontmatter ``id`` is ``obpi_id``.

    Used to populate the drift loop with several distinct OBPIs so a per-OBPI
    subprocess regression is observable as a call count > 1.
    """
    safe = obpi_id.replace(".", "_")
    brief_dir = root / "docs" / "design" / "adr" / "foundation" / f"ADR-fixture-{safe}" / "obpis"
    brief_dir.mkdir(parents=True, exist_ok=True)
    fm = {**_BASE_FM, "id": obpi_id}
    fm_text = yaml.dump(fm, default_flow_style=False)
    body = "\n# Test Brief\n\n## Acceptance Criteria\n\n- [ ] REQ-0.0.64-04-01\n"
    brief_path = brief_dir / f"{obpi_id}.md"
    brief_path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")
    return brief_path


class TestSignatureA(unittest.TestCase):
    """Signature (a): worklog event under active TASK with no task_id."""

    @covers("REQ-0.0.64-04-01")
    def test_worklog_without_task_id_under_active_task_fails(self) -> None:
        """Worklog event with no task_id while a TASK is active → violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "session": "s1",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-3",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:02:00Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertGreater(len(errors), 0, "Expected signature (a) violation")

    @covers("REQ-0.0.64-04-01")
    def test_worklog_with_task_id_under_active_task_passes(self) -> None:
        """Worklog event WITH task_id under active TASK → no signature (a) violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "session": "s1",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-3",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:02:00Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_worklog_without_active_task_is_clean(self) -> None:
        """Worklog event with no task_id and no active TASK → no violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "session": "s1",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-01")
    def test_historical_worklog_before_enforcement_epoch_is_clean(self) -> None:
        """Pre-recovery TASK rows are bounded historical drift, not current failure."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T14:43:59Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "session": "s1",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T14:43:59Z",
                        }
                    ),
                ],
            )
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (a)" in e.message
            ]
            self.assertEqual(len(errors), 0)


class TestSignatureB(unittest.TestCase):
    """Signature (b): OBPI with all-seq=01 TASKs and no req_atomic exemption."""

    @covers("REQ-0.0.64-04-02")
    @covers("REQ-0.0.64-04-07")
    def test_obpi_all_seq01_no_req_atomic_fails(self) -> None:
        """All-seq=01 TASKs no req_atomic → signature (b); no other bypass exists."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:10:00Z",
                        }
                    ),
                ],
            )
            _write_brief(root, _BASE_FM)
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]
            self.assertGreater(len(errors), 0, "Expected signature (b) violation")

    @covers("REQ-0.0.64-04-02")
    def test_obpi_all_seq01_req_atomic_covers_all_reqs_passes(self) -> None:
        """req_atomic covering all REQs → signature (b) suppressed entirely."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:10:00Z",
                        }
                    ),
                ],
            )
            fm = {**_BASE_FM, "req_atomic": ["REQ-0.0.64-04-01"]}
            _write_brief(root, fm)
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-02")
    def test_obpi_seq02_exists_no_violation(self) -> None:
        """When seq=02 exists for a REQ on a completed OBPI, no signature (b) violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-02",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:01:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:10:00Z",
                        }
                    ),
                ],
            )
            _write_brief(root, _BASE_FM)
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-02")
    def test_historical_completed_obpi_before_enforcement_epoch_is_clean(self) -> None:
        """Closed pre-recovery default-bucket OBPIs do not block the prospective gate."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T14:43:59Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T14:43:59Z",
                        }
                    ),
                ],
            )
            _write_brief(root, _BASE_FM)
            errors = [
                e for e in _validate_task_envelope_coherence(root) if "Signature (b)" in e.message
            ]
            self.assertEqual(len(errors), 0)


class TestSignatureC(unittest.TestCase):
    """Signature (c): layer-drift across frontmatter tasks: and ledger task_id."""

    @covers("REQ-0.0.64-04-03")
    def test_layer_drift_frontmatter_vs_ledger_fails(self) -> None:
        """Different TASK IDs in frontmatter tasks: vs ledger task_started → drift violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # Ledger channel (ch4) is built from task_started events with obpi_id
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-02",  # ch4 says TASK-02
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                ],
            )
            # ch2 (frontmatter) says TASK-01, ch4 (ledger) says TASK-02 → drift
            fm = {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-01"]}
            _write_brief(root, fm)
            errors = [
                e
                for e in _validate_task_envelope_coherence(root)
                if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
            ]
            self.assertGreater(len(errors), 0, "Expected layer-drift violation")

    @covers("REQ-0.0.64-04-03")
    def test_same_task_id_all_channels_passes(self) -> None:
        """Same TASK ID in frontmatter tasks: and ledger task_started → no drift."""
        task_id = "TASK-0.0.64-04-01-01"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": task_id,
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                ],
            )
            fm = {**_BASE_FM, "tasks": [task_id]}
            _write_brief(root, fm)
            errors = [
                e
                for e in _validate_task_envelope_coherence(root)
                if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
            ]
            self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.64-04-03")
    def test_only_one_channel_populated_no_drift(self) -> None:
        """Drift requires two channels; one populated → no violation."""
        task_id = "TASK-0.0.64-04-01-01"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_ledger(
                root,
                [
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "id": "evt-1",
                            "schema_": "1.0",
                            "timestamp": "2026-05-30T15:00:00Z",
                        }
                    ),
                ],
            )
            # ch2 has tasks, ch4 has nothing → no drift (one channel only)
            fm = {**_BASE_FM, "tasks": [task_id]}
            _write_brief(root, fm)
            errors = [
                e
                for e in _validate_task_envelope_coherence(root)
                if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
            ]
            self.assertEqual(len(errors), 0)


class TestCheckPipelineIntegration(unittest.TestCase):
    """REQ-0.0.64-04-06: validator is registered in the gz check pipeline."""

    @covers("REQ-0.0.64-04-06")
    def test_task_envelope_coherence_in_gz_check_steps(self) -> None:
        """gz check pipeline includes 'Task envelope coherence' step."""
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn("Task envelope coherence", step_names)


class TestDiagnoseCmd(unittest.TestCase):
    """REQ-0.0.64-04-05: gz task envelope diagnose is callable."""

    @covers("REQ-0.0.64-04-05")
    def test_diagnose_cmd_is_callable(self) -> None:
        """task_envelope_diagnose_cmd is importable and callable."""
        from gzkit.commands.task import task_envelope_diagnose_cmd

        self.assertTrue(callable(task_envelope_diagnose_cmd))


class TestSignatureCCommitTrailerChannel(unittest.TestCase):
    """Signature (c): the commit-trailer channel participates in drift detection.

    The temp-dir fixtures elsewhere are not git repos, so the commit-trailer
    channel is never exercised there. These mock the single ``git log`` walk to
    pin that commit-trailer declarations still feed drift detection across the
    hoisted (once-per-audit) code path.
    """

    @covers("REQ-0.0.64-04-03")
    def test_layer_drift_commit_trailer_vs_frontmatter_fails(self) -> None:
        """A commit-trailer TASK id disagreeing with frontmatter → drift violation."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fm = {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-01"]}
            _write_brief(root, fm)
            # Commit trailer declares a DIFFERENT TASK for the same OBPI.
            git_log = "fix(x): change\n\nTask: TASK-0.0.64-04-01-02\n--EOC--\n"
            fake = mock.Mock(returncode=0, stdout=git_log)
            with mock.patch.object(validate_cmd.subprocess, "run", return_value=fake):
                errors = [
                    e
                    for e in _validate_task_envelope_coherence(root)
                    if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
                ]
            self.assertGreater(len(errors), 0, "Expected commit-trailer vs frontmatter drift")

    @covers("REQ-0.0.64-04-03")
    def test_commit_trailer_agreeing_with_frontmatter_passes(self) -> None:
        """Same TASK id in commit trailer and frontmatter → no drift."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fm = {**_BASE_FM, "tasks": ["TASK-0.0.64-04-01-01"]}
            _write_brief(root, fm)
            git_log = "fix(x): change\n\nTask: TASK-0.0.64-04-01-01\n--EOC--\n"
            fake = mock.Mock(returncode=0, stdout=git_log)
            with mock.patch.object(validate_cmd.subprocess, "run", return_value=fake):
                errors = [
                    e
                    for e in _validate_task_envelope_coherence(root)
                    if "Signature (c)" in e.message or "layer-drift" in e.message.lower()
                ]
            self.assertEqual(len(errors), 0)


class TestSignatureCPerformance(unittest.TestCase):
    """Signature (c) scans git history once per audit, not once per OBPI."""

    @covers("REQ-0.0.64-04-03")
    def test_commit_history_scanned_once_regardless_of_obpi_count(self) -> None:
        """The git-log commit-trailer scan runs once per audit, not once per brief.

        Regression guard for the O(N) subprocess pattern: a fresh ``git log``
        per OBPI (562 briefs on this repo) made this audit the single largest
        time sink in ``gz check``. The semantic guarantee is that the number of
        git invocations is independent of the brief count.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for obpi_id in ("OBPI-0.0.64-91", "OBPI-0.0.64-92", "OBPI-0.0.64-93"):
                _write_brief_with_id(root, obpi_id)
            fake = mock.Mock(returncode=0, stdout="")
            with mock.patch.object(validate_cmd.subprocess, "run", return_value=fake) as run_mock:
                validate_cmd._sig_c_layer_drift(root)
            self.assertEqual(
                run_mock.call_count,
                1,
                "git history must be scanned once per audit, not once per OBPI "
                f"(saw {run_mock.call_count} subprocess calls for 3 briefs)",
            )


class TestObpiIdForTask(unittest.TestCase):
    """The TASK→OBPI grouping key mirrors ``_task_matches_obpi`` exactly."""

    @covers("REQ-0.0.64-04-03")
    def test_grouping_key_agrees_with_task_matches_obpi(self) -> None:
        """``_obpi_id_for_task`` returns the one OBPI a TASK matches (or None)."""
        from gzkit.commands.validate_cmd import _obpi_id_for_task, _task_matches_obpi

        cases = [
            "TASK-0.0.64-04-01-01",
            "TASK-1.2.3-07-02-05",
            "TASK-task-spine-restoration-#552",  # slug-form: no OBPI parent
            "not-a-task",
        ]
        for tid in cases:
            obpi = _obpi_id_for_task(tid)
            if obpi is None:
                self.assertFalse(
                    _task_matches_obpi(tid, "OBPI-0.0.64-04"),
                    f"{tid!r} mapped to no OBPI but matched one",
                )
            else:
                self.assertTrue(
                    _task_matches_obpi(tid, obpi),
                    f"{tid!r} mapped to {obpi!r} but did not match it",
                )
        self.assertEqual(_obpi_id_for_task("TASK-0.0.64-04-01-01"), "OBPI-0.0.64-04")
        self.assertIsNone(_obpi_id_for_task("TASK-task-spine-restoration-#552"))


if __name__ == "__main__":
    unittest.main()
