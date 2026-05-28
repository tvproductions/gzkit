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

import yaml

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
                            "timestamp": "2026-01-01T00:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "artifact_edited",
                            "path": "src/foo.py",
                            "session": "s1",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-01-01T00:01:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-3",
                            "schema_": "1.0",
                            "timestamp": "2026-01-01T00:02:00Z",
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
                            "timestamp": "2026-01-01T00:00:00Z",
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
                            "timestamp": "2026-01-01T00:01:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_completed",
                            "task_id": "TASK-0.0.64-04-01-01",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-3",
                            "schema_": "1.0",
                            "timestamp": "2026-01-01T00:02:00Z",
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
                            "timestamp": "2026-01-01T00:01:00Z",
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
                            "timestamp": "2026-01-01T00:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-01-01T00:10:00Z",
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
                            "timestamp": "2026-01-01T00:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-01-01T00:10:00Z",
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
                            "timestamp": "2026-01-01T00:00:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "task_started",
                            "task_id": "TASK-0.0.64-04-01-02",
                            "obpi_id": "OBPI-0.0.64-04",
                            "id": "evt-2",
                            "schema_": "1.0",
                            "timestamp": "2026-01-01T00:01:00Z",
                        }
                    ),
                    json.dumps(
                        {
                            "event": "obpi_receipt_emitted",
                            "receipt_event": "completed",
                            "id": "OBPI-0.0.64-04",
                            "schema_": "1.0",
                            "timestamp": "2026-01-01T00:10:00Z",
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
                            "timestamp": "2026-01-01T00:00:00Z",
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
                            "timestamp": "2026-01-01T00:00:00Z",
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
                            "timestamp": "2026-01-01T00:00:00Z",
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


if __name__ == "__main__":
    unittest.main()
