"""Skill preview must record copy intent without mutating mirrors."""

import tempfile
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.surface_write import capture_surface_writes
from gzkit.sync_skills import bootstrap_canonical_skills, sync_skill_mirrors


class TestSkillMirrorCapture(unittest.TestCase):
    def test_bootstrap_preview_does_not_create_missing_canonical_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / ".agents/skills/demo/SKILL.md"
            legacy.parent.mkdir(parents=True)
            legacy.write_bytes(b"Legacy skill\n")
            config = GzkitConfig()
            with capture_surface_writes() as sink:
                planned = bootstrap_canonical_skills(root, config)
            self.assertFalse((root / ".gzkit").exists())
            self.assertEqual(planned, [".gzkit/skills/demo/SKILL.md"])
            self.assertEqual(
                sink.written[(root / ".gzkit/skills/demo/SKILL.md").resolve()],
                b"Legacy skill\n",
            )

    def test_drifted_and_missing_skills_preview_without_writes_then_apply_repairs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".gzkit/skills"
            target = root / ".agents/skills"
            for name in ("drifted", "missing", "unchanged"):
                skill = source / name / "SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_bytes(f"Canonical {name}\n".encode())
            for name, body in (("drifted", b"Old body\n"), ("unchanged", b"Canonical unchanged\n")):
                skill = target / name / "SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_bytes(body)
            config = GzkitConfig.model_validate(
                {"vendors": {"claude": {"enabled": False}, "codex": {"enabled": True}}}
            )
            before = {path: path.stat().st_mtime_ns for path in root.rglob("*")}
            contents = {path: path.read_bytes() for path in before if path.is_file()}
            with capture_surface_writes() as sink:
                planned = sync_skill_mirrors(root, config, vendor_aware=True)
            self.assertEqual({path: path.read_bytes() for path in contents}, contents)
            self.assertEqual({path: path.stat().st_mtime_ns for path in root.rglob("*")}, before)
            for name in ("drifted", "missing", "unchanged"):
                self.assertEqual(
                    sink.written[(target / name / "SKILL.md").resolve()],
                    (source / name / "SKILL.md").read_bytes(),
                )
            self.assertFalse((target / "missing").exists())
            self.assertIn((target / "missing").resolve(), sink.created_dirs)
            expected = [".agents/skills/drifted/SKILL.md", ".agents/skills/missing/SKILL.md"]
            self.assertEqual(planned, expected)
            self.assertEqual(sync_skill_mirrors(root, config, vendor_aware=True), expected)
            for name in ("drifted", "missing", "unchanged"):
                self.assertEqual(
                    (target / name / "SKILL.md").read_bytes(),
                    (source / name / "SKILL.md").read_bytes(),
                )
            applied_mtimes = {path: path.stat().st_mtime_ns for path in target.rglob("*")}
            self.assertEqual(sync_skill_mirrors(root, config, vendor_aware=True), [])
            self.assertEqual(
                {path: path.stat().st_mtime_ns for path in target.rglob("*")}, applied_mtimes
            )
