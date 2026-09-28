"""Quality-gate commands are bounded and kill their whole process tree (GHI #1143).

``run_command`` used to call ``subprocess.run`` with no timeout, so a deadlocked
``unittest-parallel`` worker held ``gz check`` and the pre-push hook open for
24+ minutes with no output. These tests pin the repaired contract: the bound
comes from ``quality_command_timeout.json`` shipped in the gzkit package
(pointed at a temp declaration here), an
explicit ``timeout_seconds`` overrides it, a timeout kills the grandchildren
too, and a missing or malformed declaration fails closed instead of running
unbounded.
"""

import importlib.resources
import json
import os
import shlex
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit import quality
from gzkit.quality import run_command

_CONFIG_REL = Path("data") / "quality_command_timeout.json"

# The sleeping child outlives any sane test bound so a missing timeout is visible
# as elapsed time, yet exits on its own so a RED run leaks nothing for long.
_SLEEP_SECONDS = 25
_ELAPSED_BOUND = 20.0


def _write_config(root: Path, payload: object) -> None:
    path = root / _CONFIG_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    text = payload if isinstance(payload, str) else json.dumps(payload)
    path.write_text(text, encoding="utf-8")


def _sleep_argv(seconds: int = _SLEEP_SECONDS) -> list[str]:
    return [sys.executable, "-c", f"import time; time.sleep({seconds})"]


class TestQualityCommandTimeout(unittest.TestCase):
    """The hang bound, its tree kill, and its JSON authority."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        # Point the declaration lookup at this test's root, never the real repo.
        locator = patch.object(
            quality,
            "_quality_command_timeout_file",
            return_value=(self.root / _CONFIG_REL).resolve(),
        )
        locator.start()
        self.addCleanup(locator.stop)

    def tearDown(self) -> None:
        # The grandchild may still hold its heartbeat file open for a moment on
        # Windows; retry cleanup rather than fail the test on a sharing violation.
        for _ in range(20):
            try:
                self._tmp.cleanup()
                return
            except OSError:
                time.sleep(0.25)

    def test_timeout_default_read_from_json_fails_closed_with_124(self) -> None:
        _write_config(self.root, {"_doc": "test", "default_seconds": 2})
        argv = _sleep_argv()

        start = time.monotonic()
        result = run_command(argv, cwd=self.root)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, _ELAPSED_BOUND, "the JSON default did not bound the command")
        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 124)
        self.assertIn(shlex.join(argv), result.stderr)
        self.assertIn("2", result.stderr)
        self.assertIn("process tree", result.stderr)
        self.assertIn("GHI #1143", result.stderr)
        self.assertIn(quality.QUALITY_COMMAND_TIMEOUT_FILE, result.stderr)

    def test_explicit_timeout_seconds_overrides_json_default(self) -> None:
        _write_config(self.root, {"_doc": "test", "default_seconds": 900})
        argv = _sleep_argv()

        start = time.monotonic()
        result = run_command(argv, cwd=self.root, timeout_seconds=2)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, _ELAPSED_BOUND)
        self.assertEqual(result.returncode, 124)
        self.assertIn("exceeded 2", result.stderr)

    def test_timeout_kills_grandchild_not_just_child(self) -> None:
        _write_config(self.root, {"_doc": "test", "default_seconds": 2})
        heartbeat = self.root / "heartbeat.txt"
        grandchild = self.root / "grandchild.py"
        grandchild.write_text(
            textwrap.dedent(
                f"""
                import time
                deadline = time.monotonic() + 40
                with open({str(heartbeat)!r}, "a", encoding="utf-8") as fh:
                    while time.monotonic() < deadline:
                        fh.write("x")
                        fh.flush()
                        time.sleep(0.1)
                """
            ),
            encoding="utf-8",
        )
        child = self.root / "child.py"
        child.write_text(
            textwrap.dedent(
                f"""
                import subprocess, sys, time
                subprocess.Popen(
                    [sys.executable, {str(grandchild)!r}],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep({_SLEEP_SECONDS})
                """
            ),
            encoding="utf-8",
        )

        result = run_command([sys.executable, str(child)], cwd=self.root)

        self.assertTrue(heartbeat.exists(), "grandchild never started")
        time.sleep(0.5)
        size_after_return = heartbeat.stat().st_size
        time.sleep(2.0)
        self.assertEqual(
            heartbeat.stat().st_size,
            size_after_return,
            "grandchild still writing after run_command returned: tree was not killed",
        )
        self.assertEqual(result.returncode, 124)

    def test_fast_command_output_unchanged(self) -> None:
        _write_config(self.root, {"_doc": "test", "default_seconds": 30})
        result = run_command(
            [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
            cwd=self.root,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "out")
        self.assertEqual(result.stderr.strip(), "err")

    def test_malformed_config_fails_closed_without_running(self) -> None:
        marker = self.root / "ran.txt"
        argv = [sys.executable, "-c", f"open({str(marker)!r}, 'w').close()"]
        for payload in ("{not json", {"default_seconds": "900"}, {"default_seconds": 0}, {}):
            with self.subTest(payload=payload):
                _write_config(self.root, payload)
                result = run_command(argv, cwd=self.root)
                self.assertFalse(result.success)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(marker.exists(), "command ran under an invalid bound")
                self.assertIn(quality.QUALITY_COMMAND_TIMEOUT_FILE, result.stderr)
                self.assertIn("GHI #1143", result.stderr)

    def test_missing_config_fails_closed_without_running(self) -> None:
        marker = self.root / "ran.txt"
        argv = [sys.executable, "-c", f"open({str(marker)!r}, 'w').close()"]
        result = run_command(argv, cwd=self.root)
        self.assertFalse(result.success)
        self.assertFalse(marker.exists(), "command ran unbounded")
        self.assertIn(quality.QUALITY_COMMAND_TIMEOUT_FILE, result.stderr)

    def test_packaged_declaration_is_a_positive_hang_bound(self) -> None:
        resource = importlib.resources.files("gzkit").joinpath(quality.QUALITY_COMMAND_TIMEOUT_FILE)
        data = json.loads(resource.read_text(encoding="utf-8"))
        self.assertIn("GHI #1143", data["_doc"])
        self.assertIsInstance(data["default_seconds"], int)
        self.assertGreater(data["default_seconds"], 0)


class TestBoundTravelsWithThePackage(unittest.TestCase):
    """An adopter project has no gzkit `data/`; the bound must still apply there."""

    def test_command_runs_from_a_project_without_gzkit_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = Path.cwd()
            os.chdir(tmp)
            try:
                result = run_command([sys.executable, "-c", "print('bounded')"], cwd=Path(tmp))
            finally:
                os.chdir(previous)
        self.assertTrue(result.success, result.stderr)
        self.assertEqual(result.stdout.strip(), "bounded")


if __name__ == "__main__":
    unittest.main()
