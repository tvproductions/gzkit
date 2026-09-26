"""Review age is judged by ``gz skill audit`` alone; sync never refuses on it (GHI #1099).

A stale ``last_reviewed`` is a maintenance signal on canon, not corruption. The
sync preflight used to judge it too, against the machine clock. So the day any
shipped skill's review crossed 90 days, every ``gz agent sync`` refused, as did
every test that synced wheel skills and every adopter tree carrying delivered
content. Operator ruling on GHI #1099: "Audit only, sync stops (Recommended)".
"""

import re
import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import (
    CliRunner,
    start_init_subprocess_patches,
    stop_init_subprocess_patches,
)

_LAST_REVIEWED = re.compile(r"^last_reviewed:.*$", re.MULTILINE)


def setUpModule() -> None:
    """Stub the init subprocess boundaries (uv sync + ruff format)."""
    start_init_subprocess_patches()


def tearDownModule() -> None:
    stop_init_subprocess_patches()


def _age_every_canonical_review() -> int:
    """Set every canonical skill's review to a date stale on any clock."""
    aged = 0
    for skill in sorted(Path(".gzkit/skills").glob("*/SKILL.md")):
        body = skill.read_text(encoding="utf-8")
        new_body, count = _LAST_REVIEWED.subn("last_reviewed: 2000-01-01", body, count=1)
        if count:
            skill.write_text(new_body, encoding="utf-8")
            aged += 1
    return aged


class ReviewAgeScope(unittest.TestCase):
    """Sync propagates aged canon; the audit still reports it."""

    def test_sync_proceeds_when_every_review_has_aged(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            self.assertGreater(_age_every_canonical_review(), 0, "precondition: no skill aged")

            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertEqual(result.exit_code, 0, result.output)
            mirror = Path(".claude/skills/gz-status/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("last_reviewed: 2000-01-01", mirror, "sync must propagate aged canon")

    def test_skill_audit_still_blocks_aged_reviews(self) -> None:
        """Control: the audit keeps the live-tree signal the preflight gave up."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            _age_every_canonical_review()

            result = runner.invoke(main, ["skill", "audit"])

            self.assertNotEqual(result.exit_code, 0, result.output)
            self.assertIn("SKA-LAST-REVIEWED-STALE", result.output)


if __name__ == "__main__":
    unittest.main()
