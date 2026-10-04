"""A control named in `.gzkit.json` `disabled` loses its automatic standing and nothing else.

Operator ruling 2026-10-04 (verbatim: "no, i want to be able to enable. maybe we turn off
then see the effects of turning things back on?"): hooks and skills are switched off one
name at a time, survive every `gz agent sync control-surfaces`, and come back by deleting
the name. These tests pin that contract on the generator, the catalog and the skill list.
Record: docs/governance/control-switchboard-2026-10-04.md.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.commands.quality import _scope_skips
from gzkit.config import DisabledControlsConfig, GzkitConfig
from gzkit.hooks.claude import generate_claude_settings, merge_settings
from gzkit.skills import list_skills
from gzkit.sync_skills import collect_skills_catalog


def _commands(settings: dict) -> list[str]:
    return [
        hook["command"]
        for groups in settings["hooks"].values()
        for group in groups
        for hook in group["hooks"]
    ]


class DisabledHooksLeaveTheGeneratedSettings(unittest.TestCase):
    def test_an_empty_list_changes_nothing(self) -> None:
        self.assertEqual(
            generate_claude_settings(GzkitConfig()),
            generate_claude_settings(GzkitConfig(disabled=DisabledControlsConfig())),
        )

    def test_a_named_hook_is_absent_and_its_neighbours_remain(self) -> None:
        config = GzkitConfig(disabled=DisabledControlsConfig(hooks=["verifier-pipe-gate.py"]))
        commands = _commands(generate_claude_settings(config))
        self.assertFalse(any("verifier-pipe-gate.py" in c for c in commands))
        self.assertTrue(any("pipeline-completion-reminder.py" in c for c in commands))

    def test_a_group_and_a_phase_left_empty_disappear(self) -> None:
        config = GzkitConfig(
            disabled=DisabledControlsConfig(hooks=["mx-awareness.py", "plan-audit-gate.py"])
        )
        settings = generate_claude_settings(config)
        self.assertNotIn("UserPromptSubmit", settings["hooks"])
        matchers = [g["matcher"] for g in settings["hooks"]["PreToolUse"]]
        self.assertNotIn("ExitPlanMode", matchers)
        self.assertIn("Bash", matchers)

    def test_the_merge_drops_the_stale_copy_and_keeps_user_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(
                '{"hooks": {"UserPromptSubmit": [{"matcher": "*", "hooks": [{"type": "command", '
                '"command": "uv run python '
                '\\"$CLAUDE_PROJECT_DIR/.claude/hooks/mx-awareness.py\\""}]}],'
                ' "PreCompact": [{"matcher": "*", "hooks": [{"type": "command", '
                '"command": "uv run python scripts/session_orientation.py"}]}]}}',
                encoding="utf-8",
            )
            config = GzkitConfig(disabled=DisabledControlsConfig(hooks=["mx-awareness.py"]))
            merged = merge_settings(path, generate_claude_settings(config), ".claude/hooks")
        self.assertNotIn("UserPromptSubmit", merged["hooks"])
        self.assertIn("PreCompact", merged["hooks"])


def _skill(root: Path, name: str) -> None:
    skill_dir = root / ".gzkit" / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {name} does a thing.\n"
        f"lifecycle_state: active\n---\n\n# {name}\n",
        encoding="utf-8",
    )


class DisabledSkillsLeaveTheCatalogAndTheList(unittest.TestCase):
    def test_the_list_hides_a_switched_off_skill_unless_asked_for_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _skill(root, "kept-skill")
            _skill(root, "off-skill")
            config = GzkitConfig(disabled=DisabledControlsConfig(skills=["off-skill"]))
            names = {s.name for s in list_skills(root, config)}
            all_names = {s.name for s in list_skills(root, config, include_retired=True)}
        self.assertEqual(names, {"kept-skill"})
        self.assertEqual(all_names, {"kept-skill", "off-skill"})

    def test_the_catalog_excludes_what_the_project_switched_off(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _skill(root, "kept-skill")
            _skill(root, "off-skill")
            catalog = collect_skills_catalog(
                root, ".gzkit/skills", exclude=frozenset({"off-skill"})
            )
        self.assertEqual([s["name"] for s in catalog], ["kept-skill"])


class DisabledCheckStepsLeaveEveryScopeButFull(unittest.TestCase):
    def test_a_named_step_is_dropped_from_change_and_fast_but_not_full(self) -> None:
        config = GzkitConfig(disabled=DisabledControlsConfig(check_steps=["Module size"]))
        self.assertIn("Module size", _scope_skips("change", config))
        self.assertIn("Module size", _scope_skips("fast", config))
        self.assertNotIn("Module size", _scope_skips("full", config))

    def test_an_empty_list_leaves_only_the_declared_skips(self) -> None:
        self.assertEqual(_scope_skips("change", GzkitConfig()), frozenset({"Behave", "Preflight"}))


def _orientation_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "session_orientation.py"
    spec = importlib.util.spec_from_file_location("session_orientation_under_test", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DisabledOrientationSectionsAreNotCollected(unittest.TestCase):
    def test_a_listed_heading_is_switched_off_and_an_unlisted_one_is_not(self) -> None:
        mod = _orientation_module()
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / ".gzkit.json"
            cfg.write_text(
                json.dumps({"disabled": {"orientation_sections": ["Chores due or overdue"]}}),
                encoding="utf-8",
            )
            self.assertTrue(mod._section_switched_off("Chores due or overdue", cfg))
            self.assertFalse(mod._section_switched_off("Open blockers", cfg))
            self.assertFalse(
                mod._section_switched_off("Chores due or overdue", Path(tmp) / "no.json")
            )


if __name__ == "__main__":
    unittest.main()
