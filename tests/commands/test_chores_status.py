"""`gz chores status` — the chore staleness indicator (GHI #936).

Before this verb, a chore's staleness was observable only by running the chore,
so nothing outside a run ever reported that a chore was overdue. The verb reads
every registered chore's band without running any of them, and it ANNOUNCES:
operator ruling 2026-09-12, *"indicators, chores shouldn't have a bunch of gates
like the adr/obpi system"*, carried into step 2 of
``docs/governance/chore-class-system.md`` § Implementation order as
"Announces; never gates" — so an overdue chore still exits 0.
"""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.cli import main
from gzkit.commands import chores, chores_exec
from gzkit.commands.chores_staleness import (
    git_artifact_changed,
    git_first_commit_after,
    git_newest_commit,
)
from tests.commands.common import CliRunner, _isolated_git_env, _quick_init
from tests.commands.test_chores import _project_chores_root, _write_acceptance, _write_v2_registry

_BASE = {
    "rung": "observe",
    "idempotent": True,
    "remediation": {"category": "no_fix_planned", "details": "A fixture repairs nothing."},
    "nonAuthority": "Never edits anything.",
    "governingRule": "none",
}


def _pointer(slug: str, chore_class: str, staleness: dict[str, object]) -> dict[str, object]:
    return {
        "slug": slug,
        "title": slug,
        "version": "1.0.0",
        "path": str(_project_chores_root() / slug),
        "lane": "lite",
        "timeoutSeconds": 60,
        "class": chore_class,
        "staleness": staleness,
        **_BASE,
    }


def _write_run(slug: str, days_ago: int) -> None:
    when = datetime.now(UTC) - timedelta(days=days_ago)
    log = _project_chores_root() / slug / "proofs" / "CHORE-LOG.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(f"## {when.isoformat()}\n- Status: PASS\n", encoding="utf-8")


def _fixture_estate() -> None:
    """One chore per band the verb must tell apart."""
    elapsed = {"signal": "elapsed-time", "periodDays": 30, "graceDays": 7}
    chores = [
        _pointer("fresh-mining", "mining", elapsed),
        _pointer("late-mining", "mining", elapsed),
        _pointer("never-mining", "mining", elapsed),
        _pointer("dormant-mining", "mining", {**elapsed, "paused": True}),
        _pointer("pile-curation", "curation", {"signal": "accumulated-work", "graceDays": 7}),
    ]
    _write_v2_registry(chores)
    for chore in chores:
        criterion = {"type": "exitCodeEquals", "command": "git --version", "expected": 0}
        _write_acceptance(str(chore["path"]), [criterion])
    _write_run("fresh-mining", 2)
    _write_run("late-mining", 60)


class TestStatusReportsEveryBandWithoutGating(unittest.TestCase):
    """The verb reads each chore's band and exits 0 whatever it finds."""

    def test_json_carries_each_chore_band(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _fixture_estate()

            result = runner.invoke(main, ["chores", "status", "--json"])

            self.assertEqual(result.exit_code, 0, result.output)
            payload = json.loads(result.output[result.output.index("{") :])
            bands = {row["slug"]: row["band"] for row in payload["chores"]}
            self.assertEqual(
                bands,
                {
                    "fresh-mining": "current",
                    "late-mining": "overdue",
                    "never-mining": "overdue",
                    "dormant-mining": "paused",
                    "pile-curation": "unmeasured",
                },
            )
            self.assertEqual(
                payload["counts"],
                {"overdue": 2, "due": 0, "unmeasured": 1, "paused": 1, "current": 1},
            )

    def test_overdue_chores_never_change_the_exit_status(self) -> None:
        """Indicator, not gate: the human view announces overdue chores and exits 0."""
        # output-contract: the human table must name each overdue chore in full.
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _fixture_estate()

            result = runner.invoke(main, ["chores", "status"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("late-mining", result.output)
            self.assertIn("overdue", result.output)

    def test_running_no_chore_to_read_the_status(self) -> None:
        """Reading staleness must not execute the criteria of the chores it reads."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _fixture_estate()

            with (
                patch.object(chores_exec, "_evaluate_criterion") as evaluate_exec,
                patch.object(chores, "_evaluate_criterion") as evaluate,
            ):
                result = runner.invoke(main, ["chores", "status", "--json"])

            self.assertEqual(result.exit_code, 0, result.output)
            evaluate.assert_not_called()
            evaluate_exec.assert_not_called()
            proofs = _project_chores_root() / "never-mining" / "proofs"
            self.assertFalse(proofs.exists(), "a status read must not write a run log")


class TestGitSurfaceHistory(unittest.TestCase):
    """The git readers answer by committer date for the declared surfaces only."""

    def _commit(self, root: Path, rel: str, when: datetime) -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(when.isoformat(), encoding="utf-8")
        env = _isolated_git_env(
            {
                **os.environ,
                "GIT_AUTHOR_DATE": when.isoformat(),
                "GIT_COMMITTER_DATE": when.isoformat(),
            }
        )
        for args in (["add", rel], ["commit", "-q", "-m", rel]):
            subprocess.run(["git", *args], cwd=root, env=env, check=True)

    def test_oldest_commit_after_a_moment_on_the_declared_surface(self) -> None:
        base = datetime(2026, 8, 1, tzinfo=UTC)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = _isolated_git_env()
            subprocess.run(["git", "init", "-q"], cwd=root, env=env, check=True)
            for key, value in (("user.name", "fixture"), ("user.email", "fixture@example.invalid")):
                subprocess.run(["git", "config", key, value], cwd=root, env=env, check=True)
            self._commit(root, "watched/a.txt", base)
            self._commit(root, "other/b.txt", base + timedelta(days=2))
            self._commit(root, "watched/c.txt", base + timedelta(days=5))
            self._commit(root, "watched/d.txt", base + timedelta(days=9))

            newest = git_newest_commit(root)
            first_after = git_first_commit_after(root)

            self.assertEqual(newest(("watched",)), base + timedelta(days=9))
            self.assertIsNone(newest(("absent",)))
            self.assertEqual(first_after(("watched",), base), base + timedelta(days=5))
            self.assertIsNone(first_after(("watched",), base + timedelta(days=9)))
            self.assertEqual(first_after(("other",), base), base + timedelta(days=2))

    def test_scan_record_change_reads_its_commit_or_its_uncommitted_edit(self) -> None:
        """A record being written reads as now; a removed one never does (GHI #935).

        The gate's recovery is: write the scan record, then run. Requiring a commit
        in between would make that a two-step dance, so an uncommitted edit counts.
        Deleting the record must not, or removing it would pass for writing it.
        """
        base = datetime(2026, 8, 1, tzinfo=UTC)
        now = datetime(2026, 9, 14, tzinfo=UTC)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = _isolated_git_env()
            subprocess.run(["git", "init", "-q"], cwd=root, env=env, check=True)
            for key, value in (("user.name", "fixture"), ("user.email", "fixture@example.invalid")):
                subprocess.run(["git", "config", key, value], cwd=root, env=env, check=True)
            self._commit(root, "proofs/scan-record.md", base)
            self._commit(root, "proofs/removed.md", base + timedelta(days=3))
            changed = git_artifact_changed(root, now)

            self.assertEqual(changed(("proofs/scan-record.md",)), base)
            self.assertIsNone(changed(("proofs/never-written.md",)))

            (root / "proofs" / "removed.md").unlink()
            self.assertEqual(changed(("proofs/removed.md",)), base + timedelta(days=3))

            (root / "proofs" / "scan-record.md").write_text("rescanned\n", encoding="utf-8")
            self.assertEqual(changed(("proofs/scan-record.md",)), now)

            (root / "proofs" / "fresh.md").write_text("first scan\n", encoding="utf-8")
            self.assertEqual(changed(("proofs/fresh.md",)), now)

    def test_a_directory_or_pattern_never_dates_a_scan(self) -> None:
        """Only the named file is the record; its neighbours include the run log.

        A directory or glob would be dated by whatever else lives beside the record,
        so a committed FAIL block in CHORE-LOG.md would move the clock (GHI #935).
        """
        base = datetime(2026, 8, 1, tzinfo=UTC)
        now = datetime(2026, 9, 14, tzinfo=UTC)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = _isolated_git_env()
            subprocess.run(["git", "init", "-q"], cwd=root, env=env, check=True)
            for key, value in (("user.name", "fixture"), ("user.email", "fixture@example.invalid")):
                subprocess.run(["git", "config", key, value], cwd=root, env=env, check=True)
            self._commit(root, "proofs/CHORE-LOG.md", base)
            (root / "proofs" / "CHORE-LOG.md").write_text("FAIL run\n", encoding="utf-8")
            changed = git_artifact_changed(root, now)

            self.assertIsNone(changed(("proofs",)))
            self.assertIsNone(changed(("proofs/*.md",)))


if __name__ == "__main__":
    unittest.main()
