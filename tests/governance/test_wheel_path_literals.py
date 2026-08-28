"""Regression fence for machine-local path literals in wheel-shipped instructions (GHI #900).

``pip install py-gzkit`` hands an adopter the ``.md`` trees named in
``[tool.hatch.build.targets.wheel] include``.  ``gz validate --distribution``
proves those bytes *arrive*; nothing proved the instruction they carry can
**resolve** for the party it was delivered to.  Four wheel-shipped files
instructed a reader to open a path that existed on one laptop, and the
delivery gate read green the whole time because the bytes were intact.

The class is *environment-rooted literal in delivered instruction text*, not
the one string a home-directory grep happens to catch — the issue's own first
count missed a fourth file for exactly that reason.  So the teeth tests drive
four different roots (macOS home, Linux home, Windows drive, machine
provisioning), and the false-positive tests pin the shapes that are the
**remedy** rather than the defect: ``~/`` and ``$HOME/`` expand per-reader by
construction, and ``/tmp`` resolves on every POSIX machine (23 legitimate uses
measured in wheel ``.md`` at authoring).

``ScopeFollowsWheelTests`` is the load-bearing one.  A transcribed glob list
would cover the trees that existed the day it was written and silently miss
the next tree added to the wheel; the audit reads the same ``include`` block
the delivery gate reads, so scope and delivery cannot drift apart.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands import validate_cmd
from gzkit.governance.trust_audits.wheel_path_literals import (
    audit_wheel_path_literals,
    wheel_instruction_files,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

_PYPROJECT = """\
[tool.hatch.build.targets.wheel]
packages = ["src/gzkit"]
include = [
    "src/gzkit/skills/**/*.md",
]
"""


def _fake_project(tmp: str, body: str, *, pyproject: str = _PYPROJECT) -> Path:
    """Write a minimal wheel-shipping project whose one skill doc holds ``body``."""
    root = Path(tmp)
    (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    doc = root / "src" / "gzkit" / "skills" / "demo" / "SKILL.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(body, encoding="utf-8")
    return root


class LiveTreeTests(unittest.TestCase):
    """The shipped surface must stay resolvable, not merely have been repaired once."""

    def test_wheel_shipped_instructions_carry_no_environment_rooted_literal(self) -> None:
        errors = audit_wheel_path_literals(REPO_ROOT)
        self.assertEqual(
            [],
            errors,
            "wheel-shipped instruction text names a path that cannot resolve for an "
            f"adopter: {[e.message for e in errors]}",
        )


class TeethTests(unittest.TestCase):
    """Each root in the family must fail closed — the class, not the one literal."""

    def _flags(self, body: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            return [e.message for e in audit_wheel_path_literals(_fake_project(tmp, body))]

    def test_macos_home_rooted_literal_is_flagged(self) -> None:
        self.assertTrue(self._flags("Open `/Users/someone/Code/corpus.zip` first.\n"))

    def test_linux_home_rooted_literal_is_flagged(self) -> None:
        self.assertTrue(self._flags("Open `/home/someone/Code/corpus.zip` first.\n"))

    def test_windows_drive_rooted_literal_is_flagged(self) -> None:
        self.assertTrue(self._flags(r"Open `C:\Users\someone\corpus.zip` first." + "\n"))

    def test_machine_provisioning_root_is_flagged(self) -> None:
        self.assertTrue(self._flags("The binary lives at `/opt/corpus/bin/run`.\n"))

    def test_finding_names_the_file_and_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fake_project(tmp, "intro\n\nOpen `/Users/someone/x.zip`.\n")
            errors = audit_wheel_path_literals(root)
        self.assertEqual(1, len(errors))
        self.assertEqual("src/gzkit/skills/demo/SKILL.md", errors[0].artifact)
        self.assertIn("SKILL.md:3", errors[0].message)


class RemedyShapesAreNotDefectsTests(unittest.TestCase):
    """The portable forms an author is steered toward must never fail closed.

    Flagging these would push authors back to the literal they just left, so
    each one is a correctness requirement of the fence, not a convenience.
    """

    def _clean(self, body: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            errors = audit_wheel_path_literals(_fake_project(tmp, body))
        self.assertEqual([], errors, [e.message for e in errors])

    def test_tilde_rooted_path_expands_per_reader(self) -> None:
        self._clean("Session logs live under `~/.claude/projects/`.\n")

    def test_home_variable_expands_per_reader(self) -> None:
        self._clean('Run `node "$HOME/.claude/plugins/cache/x.mjs"`.\n')
        self._clean('Run `node "${HOME}/.claude/plugins/cache/x.mjs"`.\n')

    def test_posix_scratch_and_system_roots_resolve_everywhere(self) -> None:
        self._clean("Write it to `/tmp/candidate.md`, then read it back.\n")
        self._clean("#!/usr/bin/env python3\n")

    def test_url_path_segment_is_not_a_filesystem_literal(self) -> None:
        self._clean("See <https://example.invalid/Users/someone/guide> for context.\n")

    def test_placeholder_form_lets_doctrine_name_the_shape(self) -> None:
        """The rule that forbids this class is itself wheel-shipped."""
        self._clean("Never ship a literal rooted at `/Users/<name>/` — pass an override.\n")


class ScopeFollowsWheelTests(unittest.TestCase):
    """Scope is derived from the wheel's own include block, never transcribed."""

    def test_markdown_outside_the_include_block_is_not_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _fake_project(tmp, "clean\n")
            stray = root / "docs" / "notes.md"
            stray.parent.mkdir(parents=True, exist_ok=True)
            stray.write_text("Open `/Users/someone/x.zip`.\n", encoding="utf-8")
            self.assertEqual([], audit_wheel_path_literals(root))

    def test_a_tree_added_to_the_include_block_becomes_covered(self) -> None:
        widened = _PYPROJECT.replace(
            '    "src/gzkit/skills/**/*.md",\n',
            '    "src/gzkit/skills/**/*.md",\n    "src/gzkit/newtree/**/*.md",\n',
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = _fake_project(tmp, "clean\n", pyproject=widened)
            fresh = root / "src" / "gzkit" / "newtree" / "GUIDE.md"
            fresh.parent.mkdir(parents=True, exist_ok=True)
            fresh.write_text("Open `/Users/someone/x.zip`.\n", encoding="utf-8")
            self.assertEqual(1, len(audit_wheel_path_literals(root)))

    def test_shipped_python_is_out_of_scope(self) -> None:
        """Executable modules are code, not instruction text a reader resolves.

        ``hooks/scripts/validation.py`` names ``C:/Users/RUNNER~1/...`` in a
        docstring describing the Windows 8.3 short-name bug it defends against
        — an illustration, not a step. Scoping to instruction text excludes it
        on principle instead of by waiver.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = _fake_project(tmp, "clean\n")
            mod = root / "src" / "gzkit" / "hooks" / "scripts" / "validation.py"
            mod.parent.mkdir(parents=True, exist_ok=True)
            mod.write_text('"""On Windows, C:/Users/RUNNER~1/... differs."""\n', encoding="utf-8")
            self.assertEqual([], audit_wheel_path_literals(root))
            self.assertNotIn(mod, wheel_instruction_files(root))


class NoWheelProjectTests(unittest.TestCase):
    """A default-tier scope runs where no wheel is declared at all."""

    def test_project_without_pyproject_yields_no_findings(self) -> None:
        """No build config means no delivered instruction text, not a crash.

        ``--distribution`` is explicit-tier and exits 2 on a missing
        pyproject.toml, which is right for an audit an operator aimed. This
        audit runs in the default ``gz check`` scope, which the QC negative
        controls exercise against synthetic roots that ship no wheel.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "x.md").write_text("Open `/Users/someone/x`.\n", encoding="utf-8")
            self.assertEqual([], audit_wheel_path_literals(root))

    def test_unparseable_pyproject_stays_fatal(self) -> None:
        """Absence is a clean result; corruption is breakage and must not pass silently."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("this is [not toml\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                audit_wheel_path_literals(root)


class DispatchTests(unittest.TestCase):
    """A fence only reachable behind a remembered flag is an inert fence."""

    def test_scope_runs_in_the_default_gz_check_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertIn("wheel_path_literals", entries)
        self.assertEqual("default", entries["wheel_path_literals"].tier)


if __name__ == "__main__":
    unittest.main()
