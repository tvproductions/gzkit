"""The memory-hygiene witness reports the auto-memory switch beside its drift verdict.

The chore's drift witness can only fire while Claude Code writes memories. With
``autoMemoryEnabled`` false the files on disk are inert, and a "clean" verdict that
hid that would be green by construction (GHI #743's shape). Maintenance visit A,
2026-10-10.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / ".gzkit" / "chores" / "memory-hygiene" / "check_memory_drift.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("_check_memory_drift", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestAutoMemorySetting(unittest.TestCase):
    def setUp(self) -> None:
        self.chore = _load()
        self.home = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def _settings(self, payload: dict[str, object]) -> None:
        target = self.home / ".claude" / "settings.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps(payload), encoding="utf-8")

    def test_disabled_setting_is_read_as_false(self) -> None:
        self._settings({"autoMemoryEnabled": False})
        self.assertIs(self.chore.auto_memory_enabled(self.home), False)

    def test_enabled_setting_is_read_as_true(self) -> None:
        self._settings({"autoMemoryEnabled": True})
        self.assertIs(self.chore.auto_memory_enabled(self.home), True)

    def test_absent_or_non_boolean_setting_is_none(self) -> None:
        self.assertIsNone(self.chore.auto_memory_enabled(self.home))
        self._settings({"autoMemoryEnabled": "yes"})
        self.assertIsNone(self.chore.auto_memory_enabled(self.home))


class TestWitnessReportsTheSwitch(unittest.TestCase):
    def setUp(self) -> None:
        self.chore = _load()
        self.home = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.cwd = Path(self.enterContext(tempfile.TemporaryDirectory()))
        mem_dir = self.chore.memory_dir(self.cwd, self.home)
        mem_dir.mkdir(parents=True)
        (mem_dir / "feedback_old.md").write_text("---\ntype: feedback\n---\n", encoding="utf-8")
        (self.home / ".claude" / "settings.json").write_text(
            json.dumps({"autoMemoryEnabled": False}), encoding="utf-8"
        )
        # A hygiene pass recorded AFTER the memory was written: the surface is clean.
        log = self.cwd / "CHORE-LOG.md"
        log.write_text("## pass\n", encoding="utf-8")
        self.chore.PROOF_LOG = log

    def test_clean_verdict_still_names_the_switch_off(self) -> None:
        out = StringIO()
        with (
            patch.object(Path, "cwd", return_value=self.cwd),
            patch.object(Path, "home", return_value=self.home),
            redirect_stdout(out),
        ):
            code = self.chore.main()
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("auto-memory is OFF", text)
        self.assertIn("none newer than the last hygiene pass", text)


if __name__ == "__main__":
    unittest.main()
