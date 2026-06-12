"""Unit tests for the stop-turn-feedback hook (OBPI-0.0.70-01).

The hook is the turn-end deterministic sensor (ADR-0.0.70): it runs ruff
over git-dirty Python files when an agent turn ends and blocks the stop
with agent-actionable prose so the agent self-corrects before declaring
done. Tests pin the REQ semantics — block shape, single-block-per-turn,
off-switch, fail-open, telemetry bounding, settings wiring, and demo mode
— so a future edit cannot silently regress the fail-open contract
(Boundary Invariant 1: a turn can always end).
"""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.traceability import covers

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HOOK_PATH = _REPO_ROOT / ".claude" / "hooks" / "stop-turn-feedback.py"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("stop_turn_feedback_hook", _HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_HOOK = _load_hook_module()

_RUFF_FINDINGS = "x.py:1:1: F401 [*] `os` imported but unused\nFound 1 error.\n"


def _payload(stop_hook_active: bool = False, cwd: str | None = None) -> str:
    data: dict[str, object] = {"stop_hook_active": stop_hook_active}
    if cwd is not None:
        data["cwd"] = cwd
    return json.dumps(data)


class TestBlockOnFindings(unittest.TestCase):
    """REQ-0.0.70-01-01 and the three-part prose bar."""

    @covers("REQ-0.0.70-01-01")
    @covers("REQ-0.0.70-03-02")
    def test_dirty_files_with_findings_block_with_three_part_prose(self):
        stderr = io.StringIO()
        with (
            patch.object(_HOOK, "collect_dirty_python_files", return_value=["src/x.py"]),
            patch.object(_HOOK, "run_ruff", return_value=(1, _RUFF_FINDINGS)),
            patch.object(_HOOK, "append_telemetry"),
            patch.object(sys, "stdin", io.StringIO(_payload(stop_hook_active=False))),
            patch.object(sys, "stderr", stderr),
            patch.dict(_HOOK.os.environ, {}, clear=False),
        ):
            _HOOK.os.environ.pop(_HOOK.OFF_SWITCH_ENV, None)
            exit_code = _HOOK.main([])
        self.assertEqual(exit_code, 2)
        prose = stderr.getvalue()
        # Three-part guardrail-feedback-prose bar: what failed, why it is
        # forbidden (citing the binding rule), the governed next step.
        self.assertIn("F401", prose)
        self.assertIn("Why this is forbidden", prose)
        self.assertIn("Never #5", prose)
        self.assertIn("Governed next step", prose)
        self.assertIn("uv run ruff check", prose)


class TestSingleBlockPerTurn(unittest.TestCase):
    """REQ-0.0.70-01-02: stop_hook_active true never blocks."""

    @covers("REQ-0.0.70-01-02")
    def test_stop_hook_active_true_exits_zero_even_with_findings(self):
        stderr = io.StringIO()
        with (
            patch.object(_HOOK, "collect_dirty_python_files", return_value=["src/x.py"]),
            patch.object(_HOOK, "run_ruff", return_value=(1, _RUFF_FINDINGS)),
            patch.object(sys, "stdin", io.StringIO(_payload(stop_hook_active=True))),
            patch.object(sys, "stderr", stderr),
        ):
            exit_code = _HOOK.main([])
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")


class TestOffSwitch(unittest.TestCase):
    """REQ-0.0.70-01-03: GZ_STOP_FEEDBACK=off disables without settings edits."""

    @covers("REQ-0.0.70-01-03")
    def test_off_switch_exits_zero_without_invoking_ruff(self):
        with (
            patch.object(_HOOK, "run_ruff") as ruff,
            patch.object(sys, "stdin", io.StringIO(_payload())),
            patch.dict(_HOOK.os.environ, {_HOOK.OFF_SWITCH_ENV: "off"}),
        ):
            exit_code = _HOOK.main([])
        self.assertEqual(exit_code, 0)
        ruff.assert_not_called()


class TestFailOpen(unittest.TestCase):
    """REQ-0.0.70-01-04: every internal failure allows the turn to end."""

    @covers("REQ-0.0.70-01-04")
    def test_malformed_stdin_fails_open(self):
        with patch.object(sys, "stdin", io.StringIO("this is not json")):
            self.assertEqual(_HOOK.main([]), 0)

    @covers("REQ-0.0.70-01-04")
    def test_ruff_unavailable_fails_open(self):
        with (
            patch.object(_HOOK, "collect_dirty_python_files", return_value=["src/x.py"]),
            patch.object(_HOOK.subprocess, "run", side_effect=FileNotFoundError),
            patch.object(sys, "stdin", io.StringIO(_payload())),
        ):
            self.assertEqual(_HOOK.main([]), 0)

    @covers("REQ-0.0.70-01-04")
    def test_ruff_timeout_fails_open(self):
        with (
            patch.object(_HOOK, "collect_dirty_python_files", return_value=["src/x.py"]),
            patch.object(
                _HOOK.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(cmd="ruff", timeout=2),
            ),
            patch.object(sys, "stdin", io.StringIO(_payload())),
        ):
            self.assertEqual(_HOOK.main([]), 0)

    @covers("REQ-0.0.70-01-04")
    def test_non_git_directory_fails_open(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(sys, "stdin", io.StringIO(_payload(cwd=tmp))),
        ):
            self.assertEqual(_HOOK.main([]), 0)


class TestTelemetry(unittest.TestCase):
    """REQ-0.0.70-01-05: one bounded JSON line per block."""

    @covers("REQ-0.0.70-01-05")
    def test_block_appends_exactly_one_json_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            with (
                patch.object(_HOOK, "collect_dirty_python_files", return_value=["src/x.py"]),
                patch.object(_HOOK, "run_ruff", return_value=(1, _RUFF_FINDINGS)),
                patch.object(sys, "stdin", io.StringIO(_payload(cwd=tmp))),
                patch.object(sys, "stderr", io.StringIO()),
            ):
                exit_code = _HOOK.main([])
            self.assertEqual(exit_code, 2)
            log = Path(tmp) / _HOOK.TELEMETRY_PATH
            lines = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertTrue(record["blocked"])
            self.assertEqual(record["files"], 1)

    @covers("REQ-0.0.70-01-05")
    def test_over_cap_log_is_rewritten_keeping_newest_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / _HOOK.TELEMETRY_PATH
            log.parent.mkdir(parents=True)
            old_lines = [json.dumps({"blocked": True, "seq": i}) for i in range(10)]
            log.write_text("\n".join(old_lines) + "\n", encoding="utf-8")
            with (
                patch.object(_HOOK, "TELEMETRY_MAX_BYTES", 10),
                patch.object(_HOOK, "TELEMETRY_KEEP_LINES", 3),
            ):
                _HOOK.append_telemetry(Path(tmp), files=2, findings_lines=4)
            lines = log.read_text(encoding="utf-8").splitlines()
            # newest 3 retained after rewrite, plus the new record
            self.assertEqual(len(lines), 4)
            self.assertEqual(json.loads(lines[0])["seq"], 7)
            self.assertEqual(json.loads(lines[-1])["files"], 2)


class TestSettingsWiring(unittest.TestCase):
    """REQ-0.0.70-01-06: the Stop matcher invokes an existing script."""

    @covers("REQ-0.0.70-01-06")
    def test_settings_json_wires_stop_hook_to_existing_script(self):
        settings = json.loads(
            (_REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
        )
        stop_entries = settings["hooks"]["Stop"]
        commands = [
            hook["command"]
            for entry in stop_entries
            for hook in entry["hooks"]
            if hook.get("type") == "command"
        ]
        self.assertTrue(any("stop-turn-feedback.py" in cmd for cmd in commands))
        self.assertTrue(_HOOK_PATH.is_file())


class TestDemoMode(unittest.TestCase):
    """REQ-0.0.70-01-08: --demo prints the block prose without side effects."""

    @covers("REQ-0.0.70-01-08")
    def test_demo_prints_prose_without_stdin_or_telemetry(self):
        stdout = io.StringIO()
        with (
            patch.object(_HOOK, "append_telemetry") as telemetry,
            patch.object(sys, "stdin", None),  # any stdin read would raise
            patch.object(sys, "stdout", stdout),
        ):
            exit_code = _HOOK.main(["--demo"])
        self.assertEqual(exit_code, 0)
        telemetry.assert_not_called()
        prose = stdout.getvalue()
        self.assertIn("Why this is forbidden", prose)
        self.assertIn("Governed next step", prose)


if __name__ == "__main__":
    unittest.main()
