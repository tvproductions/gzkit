"""Sync parity ignores Python runtime cache files."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.validate_pkg.sync_parity import _collect_files


class TestSyncParityRuntimeCache(unittest.TestCase):
    """Generated surface snapshots must exclude ignored bytecode caches."""

    def test_collect_files_skips_python_runtime_caches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / ".agents" / "skills" / "demo-skill"
            skill.mkdir(parents=True)
            skill_file = skill / "SKILL.md"
            skill_file.write_text("# Skill\n", encoding="utf-8")
            pycache = skill / "scripts" / "__pycache__"
            pycache.mkdir(parents=True)
            cache_file = pycache / "helper.cpython-314.pyc"
            cache_file.write_bytes(b"\x00\x00\x00")

            files = _collect_files(root)

            self.assertIn(skill_file, files)
            self.assertNotIn(cache_file, files)
