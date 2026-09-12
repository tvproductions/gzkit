"""Interim Codex delivery: native registration, recovery, and shared decisions."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.config import GzkitConfig, VendorConfig, VendorsConfig
from gzkit.hooks.codex import hook_output, sync_codex_hooks
from gzkit.session_start import Advisement
from gzkit.surface_write import capture_surface_writes
from gzkit.sync_surfaces import sync_all
from gzkit.validate_pkg.sync_parity import check_sync_parity


class TestCodexHookRecovery(unittest.TestCase):
    def test_surface_validator_detects_native_hook_and_role_drift_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "session_orientation.py").write_text("", encoding="utf-8")
            agents = root / ".gzkit" / "agents"
            agents.mkdir(parents=True)
            (agents / "reviewer.md").write_text("Canonical obligation", encoding="utf-8")
            (agents / "roles.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "roles": {
                            "reviewer": {
                                "description": "Review",
                                "legacy_codex_body_sha256": "unused",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            config = GzkitConfig(
                project_name="fixture",
                vendors=VendorsConfig(
                    codex=VendorConfig(enabled=True), claude=VendorConfig(enabled=False)
                ),
            )
            sync_all(root, config, emit_event=False)
            hooks = root / ".codex" / "hooks.json"
            role = root / ".codex" / "agents" / "reviewer.toml"
            hooks.write_text(
                hooks.read_text(encoding="utf-8").replace(
                    "scripts/session_orientation.py", "scripts/broken.py"
                ),
                encoding="utf-8",
            )
            role.write_text(
                role.read_text(encoding="utf-8").replace(
                    "Canonical obligation", "Tampered obligation"
                ),
                encoding="utf-8",
            )
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in (hooks, role)}
            errors = check_sync_parity(root, config)
            artifacts = {e.artifact for e in errors}
            self.assertIn(".codex/hooks.json", artifacts)
            self.assertIn(".codex/agents/reviewer.toml", artifacts)
            self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})

    def test_sync_repairs_managed_handler_without_losing_its_operator_neighbor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "session_orientation.py").write_text("", encoding="utf-8")
            sync_codex_hooks(root)
            path = root / ".codex" / "hooks.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            group = payload["hooks"]["SessionStart"][0]
            group["hooks"][0]["command"] = "echo stale generated hook"
            operator = {"type": "command", "command": "echo custom sibling"}
            group["hooks"].append(operator)
            path.write_text(json.dumps(payload), encoding="utf-8")
            sync_codex_hooks(root)
            result = json.loads(path.read_text(encoding="utf-8"))
            handlers = [h for g in result["hooks"]["SessionStart"] for h in g["hooks"]]
            self.assertIn(operator, handlers)
            self.assertFalse(any(h["command"] == "echo stale generated hook" for h in handlers))
            self.assertEqual(len(handlers), 3)

    def test_sync_delivers_handoff_advisement_and_shared_shell_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "session_orientation.py").write_text("", encoding="utf-8")
            sync_codex_hooks(root)
            hooks = json.loads((root / ".codex" / "hooks.json").read_text(encoding="utf-8"))[
                "hooks"
            ]
            self.assertIn("PreToolUse", hooks)
            self.assertEqual(hooks["PreToolUse"][0]["matcher"], "Bash")
            start_commands = [h["command"] for g in hooks["SessionStart"] for h in g["hooks"]]
            self.assertTrue(any("-m gzkit.hooks.codex" in command for command in start_commands))

    def test_sync_recreates_native_start_and_compaction_orientation(self):
        """The recovery prescribed by orientation-freshness must actually work."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "session_orientation.py").write_text("", encoding="utf-8")
            with capture_surface_writes() as sink:
                sync_all(root, GzkitConfig(project_name="fixture"), emit_event=False)
            target = (root / ".codex" / "hooks.json").resolve()
            self.assertIn(target, list(sink.written))
            self.assertFalse(target.exists(), "a preview must not create the surface")
            config = json.loads(sink.written[target])
            groups = config["hooks"]["SessionStart"]
            orientation = [
                (group, hook)
                for group in groups
                for hook in group["hooks"]
                if "scripts/session_orientation.py" in hook["command"]
            ]
            self.assertEqual(len(orientation), 1)
            group, hook = orientation[0]
            self.assertEqual(
                set(group["matcher"].split("|")), {"startup", "resume", "clear", "compact"}
            )
            self.assertEqual(hook["type"], "command")
            self.assertIsInstance(hook["command"], str)
            self.assertNotIn("UserPromptSubmit", config["hooks"])

    def test_migration_preserves_operator_hooks_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "session_orientation.py").write_text("", encoding="utf-8")
            path = root / ".codex" / "hooks.json"
            path.parent.mkdir()
            legacy = {
                "command": [
                    "sh",
                    "-c",
                    'uv run --cache-dir "$(git rev-parse --show-toplevel)/.gzkit/cache/uv" '
                    'python "$(git rev-parse --show-toplevel)/scripts/session_orientation.py"',
                ],
                "inject": "additionalContext",
            }
            operator = {"hooks": [{"type": "command", "command": "echo operator"}]}
            path.write_text(
                json.dumps(
                    {
                        "description": "operator settings",
                        "hooks": {
                            "SessionStart": [legacy, operator],
                            "UserPromptSubmit": [dict(legacy, guard="post_compaction"), operator],
                            "Stop": [operator],
                        },
                    }
                ),
                encoding="utf-8",
            )
            sync_codex_hooks(root)
            after = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(after["description"], "operator settings")
            self.assertEqual(after["hooks"]["UserPromptSubmit"], [operator])
            self.assertEqual(after["hooks"]["Stop"], [operator])
            self.assertEqual(after["hooks"]["SessionStart"][0], operator)
            self.assertEqual(len(after["hooks"]["SessionStart"]), 3)
            before = path.stat().st_mtime_ns
            sync_codex_hooks(root)
            self.assertEqual(path.stat().st_mtime_ns, before)

    def test_no_dangling_orientation_for_adopters_without_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(sync_codex_hooks(root), [])
            self.assertFalse((root / ".codex").exists())

    def test_malformed_operator_json_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "session_orientation.py").write_text("", encoding="utf-8")
            path = root / ".codex" / "hooks.json"
            path.parent.mkdir()
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(ValueError):
                sync_codex_hooks(root)
            self.assertEqual(path.read_text(encoding="utf-8"), "{broken")


class TestCodexHookDecisions(unittest.TestCase):
    def test_raw_exec_arguments_cannot_bypass_the_shared_guard(self):
        result = hook_output(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "exec_command",
                "tool_input": {"cmd": "uv run gz check | tail -5"},
            }
        )
        self.assertEqual(result.get("hookSpecificOutput", {}).get("permissionDecision"), "deny")

    def test_native_shell_aliases_share_masking_refusal_and_preserving_escape(self):
        for tool in ("Bash", "exec_command", "shell", "shell_command"):
            for command, blocked in (
                ("uv run gz check | tail -5", True),
                ("set -o pipefail; uv run gz check | tail -5", False),
                ("uv run gz check", False),
                ("uv run gz check || echo FAILED", True),
                ("git status --short", False),
            ):
                with self.subTest(tool=tool, command=command):
                    result = hook_output(
                        {
                            "hook_event_name": "PreToolUse",
                            "tool_name": tool,
                            "tool_input": {"command": command},
                        }
                    )
                    if blocked:
                        decision = result["hookSpecificOutput"]
                        self.assertEqual(decision["permissionDecision"], "deny")
                        self.assertEqual(decision["hookEventName"], "PreToolUse")
                        reason = decision["permissionDecisionReason"]
                        self.assertIn("WHY:", reason)
                        self.assertIn(".gzkit/rules/tests.md", reason)
                        self.assertIn("NEXT STEP:", reason)
                    else:
                        self.assertEqual(result, {})

    def test_start_uses_shared_advisement_from_repo_root_with_native_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / ".gzkit").mkdir()
            nested = root / "src"
            nested.mkdir()
            advice = Advisement(present=True, text="The handoff advises; it does not authorize.")
            with patch("gzkit.session_start.build_advisement", return_value=advice) as build:
                result = hook_output(
                    {"hook_event_name": "SessionStart", "cwd": str(nested), "source": "compact"}
                )
            self.assertEqual(build.call_args.args, (root,))
            self.assertEqual(
                result,
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": advice.text,
                    }
                },
            )

    def test_unrelated_or_malformed_tool_payloads_do_not_block(self):
        for tool, inputs in (
            ("apply_patch", {"command": "uv run gz check | tail"}),
            ("Bash", "not an object"),
        ):
            self.assertEqual(
                hook_output(
                    {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": inputs}
                ),
                {},
            )
        self.assertEqual(hook_output({"hook_event_name": "Stop"}), {})
