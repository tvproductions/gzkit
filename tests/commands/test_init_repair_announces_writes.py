"""``gz init`` repair announces every write it makes, and a dry run makes none (GHI #1098).

``--help`` promises that re-running init "repairs missing artifacts" and that
``--dry-run`` shows "planned actions without executing". On the gzkit repo the
dry run printed "no files written" while it rewrote three canonical skills and
added a chore file, and the real run then mirrored those rewrites into nine
vendor copies without a line of output. Two writers caused it: the skill and
chore scaffolders ran during the dry run with ``skip_existing=False``, and the
control-surface sync ran unreported on every real repair.

Each test compares the bytes of the whole tree before and after, so a writer
this file does not name still fails here.
"""

import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import (
    CliRunner,
    start_init_subprocess_patches,
    stop_init_subprocess_patches,
)

_ROUTER = Path(".gzkit/skills/gz-context/SKILL.md")
_LOCAL_ROW = "| local scan | `local-scan` |\n"


def setUpModule() -> None:
    """Stub the init subprocess boundaries (uv sync + ruff format)."""
    start_init_subprocess_patches()


def tearDownModule() -> None:
    stop_init_subprocess_patches()


def _snapshot() -> dict[str, bytes]:
    """Map every file under the working directory to its bytes."""
    return {
        path.as_posix(): path.read_bytes() for path in sorted(Path().rglob("*")) if path.is_file()
    }


def _changed(before: dict[str, bytes], after: dict[str, bytes]) -> set[str]:
    """Paths created, modified or removed between two snapshots."""
    return {path for path in before.keys() | after.keys() if before.get(path) != after.get(path)}


def _route_to_a_local_skill() -> None:
    """Give a canonical router a row to a skill the wheel does not deliver.

    gzkit's own ``gz-context`` routes ``parity`` to ``airlineops-parity-scan``,
    which lives only in this repository. Delivery-scoping drops such rows from
    the wheel copy, so any scaffold over the canonical file deletes the route.
    """
    local = Path(".gzkit/skills/local-scan/SKILL.md")
    local.parent.mkdir(parents=True)
    # Valid canon, so the sync preflight passes and only the router row is at issue.
    local.write_text(
        "---\nname: local-scan\ndescription: Repo-local scan.\nlifecycle_state: active\n"
        "owner: gzkit-governance\nlast_reviewed: 2026-01-01\n"
        'metadata:\n  skill-version: "0.1.0"\n---\n\n# local-scan\n',
        encoding="utf-8",
    )
    body = _ROUTER.read_text(encoding="utf-8")
    anchor = "| orientation | `gz-skill-router` |\n"
    if anchor not in body:
        raise AssertionError(f"precondition: {_ROUTER} intent table lacks {anchor!r}")
    _ROUTER.write_text(body.replace(anchor, _LOCAL_ROW + anchor), encoding="utf-8")


def _drop_a_chore_file() -> Path:
    """Remove one file from an existing chore package that the wheel carries."""
    chores = sorted(Path(".gzkit/chores").glob("*/CHORE.md"))
    if not chores:
        raise AssertionError("precondition: init scaffolded no chores")
    victim = chores[0]
    victim.unlink()
    return victim


class DryRunWritesNothing(unittest.TestCase):
    """A dry run leaves every byte of the tree as it found it."""

    def test_dry_run_leaves_canonical_skills_and_chores_untouched(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            _route_to_a_local_skill()
            _drop_a_chore_file()
            before = _snapshot()

            result = runner.invoke(main, ["init", "--no-skeleton", "--dry-run"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(_changed(before, _snapshot()), set(), result.output)


class RepairPreservesCanon(unittest.TestCase):
    """Repair restores what is missing; it never rewrites canonical skills."""

    def test_real_repair_keeps_a_route_to_a_local_skill(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            _route_to_a_local_skill()
            canonical = _ROUTER.read_bytes()

            runner.invoke(main, ["init", "--no-skeleton", "--dry-run"])
            result = runner.invoke(main, ["init", "--no-skeleton"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(_ROUTER.read_bytes(), canonical, result.output)


class RepairAnnouncesEveryWrite(unittest.TestCase):
    """The dry run names each path the real run writes, and the summary counts them."""

    def _assert_plan_matches_writes(self, runner: CliRunner, expected: set[str]) -> None:
        planned = runner.invoke(main, ["init", "--no-skeleton", "--dry-run"])
        self.assertEqual(planned.exit_code, 0, planned.output)
        before = _snapshot()

        result = runner.invoke(main, ["init", "--no-skeleton"])

        self.assertEqual(result.exit_code, 0, result.output)
        written = _changed(before, _snapshot()) - {".gzkit/ledger.jsonl"}
        self.assertEqual(written, expected, result.output)
        for path in written:
            self.assertIn(path, planned.output, f"dry run did not announce {path}")
            self.assertIn(path, result.output, f"real run did not report {path}")
        self.assertIn(f"Repaired {len(written)} artifact(s)", result.output)

    def test_drifted_vendor_mirror_is_announced_then_written(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            mirror = Path(".claude/skills/gz-context/SKILL.md")
            mirror.write_text("drifted\n", encoding="utf-8")

            self._assert_plan_matches_writes(runner, {mirror.as_posix()})

    def test_missing_chores_surface_file_is_announced_then_written(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            readme = Path(".gzkit/chores/README.md")
            if not readme.is_file():
                raise AssertionError("precondition: init delivered no chores README.md")
            readme.unlink()

            self._assert_plan_matches_writes(runner, {readme.as_posix()})

    def test_repaired_tree_reports_and_writes_nothing(self) -> None:
        """Control: with nothing to repair, repair writes nothing — the ledger included."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            before = _snapshot()

            result = runner.invoke(main, ["init", "--no-skeleton"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Nothing to repair", result.output)
            self.assertEqual(_changed(before, _snapshot()), set(), result.output)


if __name__ == "__main__":
    unittest.main()
