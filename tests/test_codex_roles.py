"""Native role delivery must carry canonical governance instructions."""

import hashlib
import json
import tempfile
import tomllib
import unittest
from pathlib import Path

from gzkit.codex_roles import MARKER, render_codex_role, sync_codex_roles
from gzkit.config import GzkitConfig
from gzkit.surface_write import capture_surface_writes
from gzkit.sync_surfaces import sync_all

ROOT = Path(__file__).resolve().parents[1]


class TestShippedRoleRendering(unittest.TestCase):
    def test_native_instructions_deliver_canonical_body(self):
        registry = json.loads((ROOT / ".gzkit/agents/roles.json").read_text(encoding="utf-8"))
        for name in registry["roles"]:
            with self.subTest(role=name):
                body = (ROOT / f".gzkit/agents/{name}.md").read_text(encoding="utf-8").strip()
                native = tomllib.loads(
                    (ROOT / f".codex/agents/{name}.toml").read_text(encoding="utf-8")
                )
                self.assertEqual(native["developer_instructions"].strip(), body)

    def test_canonical_capture_preserves_claude_body(self):
        registry = json.loads((ROOT / ".gzkit/agents/roles.json").read_text(encoding="utf-8"))
        for name in registry["roles"]:
            with self.subTest(role=name):
                canonical = (ROOT / f".gzkit/agents/{name}.md").read_text(encoding="utf-8")
                claude = (ROOT / f".claude/agents/{name}.md").read_text(encoding="utf-8")
                self.assertEqual(canonical.strip(), claude.split("---", 2)[2].strip())


class TestCodexRoleRendering(unittest.TestCase):
    def test_preserves_native_metadata_and_escapes_body(self):
        source = '''name = "custom"
description = "Keep this description"
sandbox_mode = "read-only"
developer_instructions = """
Old instructions.
"""
[extra]
date = 2026-09-12
flags = [true, false]
'''
        body = 'Use C:\\work and """quoted""" text.\nUnicode: Δ\tend.'
        rendered = render_codex_role(source, body)
        expected = {**tomllib.loads(source), "developer_instructions": body}
        self.assertEqual(tomllib.loads(rendered), expected)
        self.assertIn("[extra]\ndate = 2026-09-12\nflags = [true, false]", rendered)
        self.assertEqual(render_codex_role(rendered, body), rendered)

    def test_does_not_replace_key_inside_another_string_or_table(self):
        source = '''description = """
developer_instructions = 'inside description'
"""
'developer_instructions' = 'old'
[extra]
developer_instructions = 'nested'
'''
        expected = {**tomllib.loads(source), "developer_instructions": "replacement"}
        self.assertEqual(tomllib.loads(render_codex_role(source, "replacement")), expected)


class TestCodexRoleSync(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.canonical = self.root / ".gzkit/agents"
        self.canonical.mkdir(parents=True)
        self.native = self.root / ".codex/agents"
        self.native.mkdir(parents=True)
        self.roles: dict[str, dict[str, str]] = {}
        self.registry = {"version": 1, "roles": self.roles}

    def register(self, name="reviewer", body="Canonical obligation", legacy="Legacy body"):
        self.roles[name] = {
            "description": "A project role",
            "legacy_codex_body_sha256": hashlib.sha256(legacy.encode()).hexdigest(),
        }
        (self.canonical / f"{name}.md").write_text(body + "\n", encoding="utf-8")
        (self.canonical / "roles.json").write_text(json.dumps(self.registry), encoding="utf-8")

    def test_migrates_legacy_and_updates_managed_body_without_metadata_changes(self):
        self.register()
        path = self.native / "reviewer.toml"
        path.write_text(
            'name = "local-name"\ndeveloper_instructions = "Legacy body"\n', encoding="utf-8"
        )
        self.assertEqual(sync_codex_roles(self.root), [".codex/agents/reviewer.toml"])
        first = path.read_text(encoding="utf-8")
        self.assertTrue(first.startswith(MARKER + "\n"))
        self.register(body="An updated obligation")
        sync_codex_roles(self.root)
        self.assertEqual(
            tomllib.loads(path.read_text(encoding="utf-8")),
            {"name": "local-name", "developer_instructions": "An updated obligation"},
        )
        mtime = path.stat().st_mtime_ns
        self.assertEqual(sync_codex_roles(self.root), [".codex/agents/reviewer.toml"])
        self.assertEqual(path.stat().st_mtime_ns, mtime)

    def test_sync_all_keeps_role_paths_stable_and_captures_source_change(self):
        self.register()
        config = GzkitConfig.model_validate(
            {
                "project_name": "role-fixture",
                "vendors": {"claude": {"enabled": False}, "codex": {"enabled": True}},
            }
        )
        first = sync_all(self.root, config, emit_event=False)
        second = sync_all(self.root, config, emit_event=False)
        role_path = ".codex/agents/reviewer.toml"
        self.assertIn(role_path, first)
        self.assertIn(role_path, second)
        self.assertEqual(first, second)
        self.register(body="New canonical proof obligation")
        before = {
            path: (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*")
            if path.is_file()
        }
        with capture_surface_writes() as sink:
            planned = sync_all(self.root, config, emit_event=False)
        self.assertEqual(planned, second)
        captured = tomllib.loads(sink.written[(self.root / role_path).resolve()].decode())
        self.assertEqual(captured["developer_instructions"], "New canonical proof obligation")
        self.assertEqual(
            {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in before}, before
        )
        self.assertEqual({path for path in self.root.rglob("*") if path.is_file()}, set(before))

    def test_preserves_custom_collision_and_unregistered_role(self):
        self.register()
        for name in ("reviewer", "user-role"):
            (self.native / f"{name}.toml").write_text(
                'developer_instructions = "User instructions"\n', encoding="utf-8"
            )
        before = {p: p.read_bytes() for p in self.native.iterdir()}
        self.assertEqual(sync_codex_roles(self.root), [])
        self.assertEqual({p: p.read_bytes() for p in self.native.iterdir()}, before)

    def test_capture_plans_missing_role_without_creating_it_or_adding_policy(self):
        self.register()
        with capture_surface_writes() as sink:
            self.assertEqual(sync_codex_roles(self.root), [".codex/agents/reviewer.toml"])
        destination = self.native / "reviewer.toml"
        self.assertFalse(destination.exists())
        self.assertEqual(
            tomllib.loads(sink.written[destination.resolve()].decode()),
            {
                "name": "reviewer",
                "description": "A project role",
                "developer_instructions": "Canonical obligation",
            },
        )

    def test_invalid_later_role_cannot_leave_partial_migration(self):
        self.register(name="a-role")
        self.register(name="z-role")
        broken = self.native / "z-role.toml"
        broken.write_text('developer_instructions = "unterminated', encoding="utf-8")
        with self.assertRaises(tomllib.TOMLDecodeError):
            sync_codex_roles(self.root)
        self.assertFalse((self.native / "a-role.toml").exists())
        self.assertEqual(
            broken.read_text(encoding="utf-8"), 'developer_instructions = "unterminated'
        )

    def test_absent_registry_does_not_claim_native_roles(self):
        self.assertEqual(sync_codex_roles(self.root), [])

    def test_rejects_path_traversal_before_reading_or_writing_role(self):
        self.roles["../escape"] = {}
        (self.canonical / "roles.json").write_text(json.dumps(self.registry), encoding="utf-8")
        with self.assertRaises(ValueError):
            sync_codex_roles(self.root)
        self.assertEqual(list(self.native.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
