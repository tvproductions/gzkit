"""No command propagates canonical skills to the mirrors past a failing preflight (GHI #1100).

``gz agent sync control-surfaces`` refuses when ``collect_canonical_sync_blockers``
reports corrupted canon. ``gz tidy --fix``, ``gz init`` repair and ``gz init
--force`` reached the same ``sync_all`` through their own call sites and copied
the corruption into every vendor mirror, exiting 0. The manpage clause they
broke: "Before any mirror propagation, sync validates canonical `.gzkit/skills`
integrity."
"""

import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import (
    CliRunner,
    start_init_subprocess_patches,
    stop_init_subprocess_patches,
)

_MIRRORS = (Path(".claude/skills"), Path(".agents/skills"))


def setUpModule() -> None:
    """Stub the init subprocess boundaries (uv sync + ruff format)."""
    start_init_subprocess_patches()


def tearDownModule() -> None:
    stop_init_subprocess_patches()


def _mirror_bytes() -> dict[str, bytes]:
    """Every file under the vendor skill mirrors, by path."""
    return {
        path.as_posix(): path.read_bytes()
        for root in _MIRRORS
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _corrupt_canonical_name(skill: str = "gz-status") -> None:
    """Break a canonical skill's identity: its name no longer matches its directory."""
    path = Path(".gzkit/skills") / skill / "SKILL.md"
    body = path.read_text(encoding="utf-8")
    if f"name: {skill}" not in body:
        raise AssertionError(f"precondition: {path} lacks 'name: {skill}'")
    path.write_text(body.replace(f"name: {skill}", "name: Not_Kebab_Name", 1), encoding="utf-8")


def _add_corrupt_local_skill() -> None:
    """Add a repo-local canonical skill whose name contradicts its directory."""
    path = Path(".gzkit/skills/local-scan/SKILL.md")
    path.parent.mkdir(parents=True)
    path.write_text(
        "---\nname: Not_Kebab_Name\ndescription: Repo-local scan.\nlifecycle_state: active\n"
        "owner: gzkit-governance\nlast_reviewed: 2026-01-01\n"
        'metadata:\n  skill-version: "0.1.0"\n---\n\n# local-scan\n',
        encoding="utf-8",
    )


class CorruptCanonNeverPropagates(unittest.TestCase):
    """Each propagating command refuses, and leaves every mirror byte-identical."""

    def _assert_refused(self, args: list[str], corrupt) -> None:  # noqa: ANN001
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            corrupt()
            before = _mirror_bytes()

            result = runner.invoke(main, args)

            self.assertNotEqual(result.exit_code, 0, result.output)
            self.assertEqual(_mirror_bytes(), before, result.output)
            self.assertIn("Sync preflight failed", result.output)

    def test_tidy_fix_refuses(self) -> None:
        self._assert_refused(["tidy", "--fix"], _corrupt_canonical_name)

    def test_init_repair_refuses(self) -> None:
        self._assert_refused(["init", "--no-skeleton"], _corrupt_canonical_name)

    def test_init_force_refuses_a_corrupt_local_skill(self) -> None:
        """``--force`` re-copies wheel skills but keeps local ones, so it can meet corrupt canon."""
        self._assert_refused(["init", "--no-skeleton", "--force"], _add_corrupt_local_skill)


class CleanCanonStillSyncs(unittest.TestCase):
    """Controls: with canon intact, the same commands still repair a drifted mirror."""

    def _assert_restores_mirror(self, args: list[str]) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            mirror = Path(".claude/skills/gz-status/SKILL.md")
            canonical = mirror.read_bytes()
            mirror.write_text("drifted\n", encoding="utf-8")

            result = runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(mirror.read_bytes(), canonical, result.output)

    def test_tidy_fix_syncs_clean_canon(self) -> None:
        self._assert_restores_mirror(["tidy", "--fix"])

    def test_init_repair_syncs_clean_canon(self) -> None:
        self._assert_restores_mirror(["init", "--no-skeleton"])


if __name__ == "__main__":
    unittest.main()
