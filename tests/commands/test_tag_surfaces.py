"""The surface registry `gz wp tag issue` resolves a tag's surface through: RP-12 O3 task 2.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: a tag's surface is
`<kind>:<name>`, resolved against the registry that holds that kind today (ruling
112): `gz validate`'s scopes in their flag's spelling, `gz check`'s steps in lower
case with spaces hyphenated, the hook scripts `.claude/settings.json` registers and
the hook ids `.pre-commit-config.yaml` declares, and the tree (ruling 123). The
command reads them and passes the writer the registry's own name (ruling 119), so
this adapter lives in the commands layer and imports no `gzkit.cli` (ruling 125).
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import override

from gzkit.commands.tag_surfaces import ProjectSurfaces
from gzkit.core.exceptions import ValidationError

_SETTINGS = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": 'uv run python "$CLAUDE_PROJECT_DIR/.claude/hooks/'
                        'dispatch-stamp.py"',
                    }
                ],
            }
        ]
    }
}
_PRE_COMMIT = """\
repos:
  - repo: local
    hooks:
      - id: forbid-pytest
        name: forbid pytest
        entry: uv run python scripts/forbid.py
        language: system
"""


class _ProjectCase(unittest.TestCase):
    @override
    def setUp(self) -> None:
        outer = Path(self.enterContext(TemporaryDirectory()))
        self.root = outer / "project"
        (self.root / ".claude" / "hooks").mkdir(parents=True)
        (self.root / "src").mkdir()
        (self.root / "src" / "stamp.py").write_text("", encoding="utf-8")
        (self.root / ".claude" / "hooks" / "unregistered.py").write_text("", encoding="utf-8")
        (outer / "outside.py").write_text("", encoding="utf-8")
        settings = json.dumps(_SETTINGS)
        (self.root / ".claude" / "settings.json").write_text(settings, encoding="utf-8")
        (self.root / ".pre-commit-config.yaml").write_text(_PRE_COMMIT, encoding="utf-8")
        self.surfaces = ProjectSurfaces(self.root)


class ValidatorSurfaceTests(_ProjectCase):
    def test_a_scope_in_its_flags_spelling_resolves_to_its_stem(self) -> None:
        # given the `gz validate --hexagon-tests` scope, whose stem is hexagon_tests
        # when
        resolved = self.surfaces.resolve("validator", "hexagon-tests")
        # then
        self.assertEqual(resolved, "hexagon_tests")

    def test_a_scope_in_its_stems_spelling_resolves_to_nothing(self) -> None:
        # given ruling 123: a validator is written as its flag is spelt
        # when
        resolved = self.surfaces.resolve("validator", "hexagon_tests")
        # then
        self.assertIsNone(resolved)

    def test_an_unknown_scope_resolves_to_nothing(self) -> None:
        # given no scope by this name
        # when
        resolved = self.surfaces.resolve("validator", "no-such-scope")
        # then
        self.assertIsNone(resolved)


class CheckSurfaceTests(_ProjectCase):
    def test_a_step_lower_cased_and_hyphenated_resolves_to_its_display_name(self) -> None:
        # given the `gz check` step named "Module size"
        # when
        resolved = self.surfaces.resolve("check", "module-size")
        # then
        self.assertEqual(resolved, "Module size")

    def test_a_step_by_its_display_name_resolves_to_nothing(self) -> None:
        # given ruling 123: a step is written lower case with its spaces hyphenated
        # when
        resolved = self.surfaces.resolve("check", "Module size")
        # then
        self.assertIsNone(resolved)

    def test_an_unknown_step_resolves_to_nothing(self) -> None:
        # given no step by this name
        # when
        resolved = self.surfaces.resolve("check", "no-such-step")
        # then
        self.assertIsNone(resolved)


class HookSurfaceTests(_ProjectCase):
    def test_a_registered_script_resolves_with_or_without_its_suffix(self) -> None:
        # given .claude/settings.json registers .claude/hooks/dispatch-stamp.py
        # when
        resolved = {
            name: self.surfaces.resolve("hook", name)
            for name in ("dispatch-stamp", "dispatch-stamp.py")
        }
        # then both spellings name the one script, recorded with its registry (ruling 127)
        self.assertEqual(
            resolved,
            {
                "dispatch-stamp": "settings:dispatch-stamp.py",
                "dispatch-stamp.py": "settings:dispatch-stamp.py",
            },
        )

    def test_a_declared_pre_commit_id_resolves_to_itself(self) -> None:
        # given .pre-commit-config.yaml declares the hook id forbid-pytest
        # when
        resolved = self.surfaces.resolve("hook", "forbid-pytest")
        # then it is named with its registry (ruling 127)
        self.assertEqual(resolved, "pre-commit:forbid-pytest")

    def test_a_hook_written_with_its_registry_resolves_in_that_registry_alone(self) -> None:
        # given dispatch-stamp.py registered in settings and forbid-pytest declared in pre-commit
        # when
        resolved = [
            self.surfaces.resolve("hook", written)
            for written in (
                "settings:dispatch-stamp",
                "pre-commit:forbid-pytest",
                "pre-commit:dispatch-stamp",
                "settings:forbid-pytest",
            )
        ]
        # then each resolves only in the registry it names (ruling 127)
        self.assertEqual(
            resolved, ["settings:dispatch-stamp.py", "pre-commit:forbid-pytest", None, None]
        )

    def test_a_bare_name_both_registries_hold_is_refused_as_ambiguous(self) -> None:
        # given a pre-commit id trailing-space beside a settings script trailing-space.sh
        config = (self.root / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        config += "      - id: trailing-space\n        name: trim\n        entry: x\n"
        config += "        language: system\n"
        (self.root / ".pre-commit-config.yaml").write_text(config, encoding="utf-8")
        settings = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        settings["hooks"]["PreToolUse"][0]["hooks"].append(
            {"type": "command", "command": "bash .claude/hooks/trailing-space.sh"}
        )
        (self.root / ".claude" / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        surfaces = ProjectSurfaces(self.root)
        # when
        with self.assertRaises(ValidationError) as raised:
            surfaces.resolve("hook", "trailing-space")
        qualified = surfaces.resolve("hook", "settings:trailing-space")
        # then the bare name is refused, naming both forms, and a qualified one resolves,
        # a non-Python script counting as a script (ruling 127)
        self.assertIn("hook:pre-commit:trailing-space", str(raised.exception))
        self.assertIn("hook:settings:trailing-space.sh", str(raised.exception))
        self.assertEqual(qualified, "settings:trailing-space.sh")

    def test_a_script_no_settings_register_resolves_to_nothing(self) -> None:
        # given a hook script on disk that .claude/settings.json does not register
        # when
        resolved = self.surfaces.resolve("hook", "unregistered")
        # then
        self.assertIsNone(resolved)

    def test_a_project_without_hook_registries_holds_no_hook(self) -> None:
        # given a project with neither registry file
        (self.root / ".claude" / "settings.json").unlink()
        (self.root / ".pre-commit-config.yaml").unlink()
        # when
        resolved = ProjectSurfaces(self.root).resolve("hook", "forbid-pytest")
        # then
        self.assertIsNone(resolved)

    def test_an_unparseable_registry_is_refused_not_read_as_empty(self) -> None:
        # given a .claude/settings.json that is not JSON
        (self.root / ".claude" / "settings.json").write_text("{", encoding="utf-8")
        # when
        with self.assertRaises(ValidationError) as raised:
            ProjectSurfaces(self.root).resolve("hook", "dispatch-stamp")
        # then the refusal names the file at fault
        self.assertIn(".claude/settings.json", str(raised.exception))

    def test_an_unparseable_pre_commit_config_is_refused_not_read_as_empty(self) -> None:
        # given a .pre-commit-config.yaml that is not YAML
        (self.root / ".pre-commit-config.yaml").write_text("repos: [", encoding="utf-8")
        # when
        with self.assertRaises(ValidationError) as raised:
            ProjectSurfaces(self.root).resolve("hook", "forbid-pytest")
        # then the refusal names the file at fault
        self.assertIn(".pre-commit-config.yaml", str(raised.exception))


class PathSurfaceTests(_ProjectCase):
    def test_a_file_in_the_tree_resolves_to_its_normalized_repo_path(self) -> None:
        # given src/stamp.py in the tree
        # when
        resolved = {
            name: self.surfaces.resolve("path", name)
            for name in ("src/stamp.py", "src/./x/../stamp.py")
        }
        # then
        self.assertEqual(
            resolved, {"src/stamp.py": "src/stamp.py", "src/./x/../stamp.py": "src/stamp.py"}
        )

    def test_a_path_escaping_the_root_resolves_to_nothing(self) -> None:
        # given a file beside the project, outside its tree
        # when
        resolved = [
            self.surfaces.resolve("path", name)
            for name in ("../outside.py", (self.root.parent / "outside.py").as_posix())
        ]
        # then
        self.assertEqual(resolved, [None, None])

    def test_a_backslashed_or_missing_path_resolves_to_nothing(self) -> None:
        # given a path not written with forward slashes, a path not in the tree, the root
        # when
        resolved = [
            self.surfaces.resolve("path", name) for name in ("src\\stamp.py", "src/gone.py", ".")
        ]
        # then
        self.assertEqual(resolved, [None, None, None])

    def test_a_path_written_in_another_case_never_names_a_second_surface(self) -> None:
        # given src/stamp.py in the tree, written as SRC/Stamp.py
        # when
        resolved = self.surfaces.resolve("path", "SRC/Stamp.py")
        # then a case-insensitive volume names the file as the tree spells it, and a
        # case-sensitive one names nothing, so one tag-out per surface holds (ruling 122)
        self.assertIn(resolved, {"src/stamp.py", None})

    def test_an_absolute_path_inside_the_tree_resolves_to_nothing(self) -> None:
        # given src/stamp.py written as an absolute path, not repo-relative (ruling 123)
        written = (self.root / "src" / "stamp.py").as_posix()
        # when
        resolved = self.surfaces.resolve("path", written)
        # then
        self.assertIsNone(resolved)


class UnknownKindTests(_ProjectCase):
    def test_a_kind_no_registry_holds_resolves_to_nothing(self) -> None:
        # given a kind beyond ruling 112's four
        # when
        resolved = self.surfaces.resolve("guard", "forbid-pytest")
        # then
        self.assertIsNone(resolved)


if __name__ == "__main__":
    unittest.main()
