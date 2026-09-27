"""Pending bare-to-slug renames block the gate instead of waiting for a manual run (GHI #1118).

``gz migrate-semver`` detects ledger events under a bare ``ADR-X.Y.Z`` /
``OBPI-X.Y.Z-NN`` whose artifact's on-disk id is its slug, and appends the
rename. Nothing ran the detector, so 87 rows under 21 bare ids accumulated
between manual runs: reconciliation as a maintenance chore (AGENTS.md
§ Architectural Boundaries 4). ``gz validate --pending-renames`` runs the same
detector in the default tier and fails while any rename is pending.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger
from gzkit.ledger_events import adr_eval_completed_event
from tests.commands.common import CliRunner, _quick_init

_SLUG = "ADR-0.1.0-thing"
_ADR = """\
---
id: ADR-0.1.0-thing
status: Proposed
semver: 0.1.0
lane: lite
kind: feature
---

# ADR-0.1.0-thing: Thing
"""


class PendingRenamesTests(unittest.TestCase):
    def _seed(self, event_id: str) -> None:
        _quick_init()
        adrs = Path(GzkitConfig.load(Path(".gzkit.json")).paths.adrs)
        package = adrs / "pre-release" / _SLUG
        package.mkdir(parents=True, exist_ok=True)
        (package / f"{_SLUG}.md").write_text(_ADR, encoding="utf-8")
        Ledger(Path(".gzkit/ledger.jsonl")).append(
            adr_eval_completed_event(event_id, "GO", 4.0, 0, 0)
        )

    def test_a_pending_rename_fails_and_names_the_repair(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed("ADR-0.1.0")
            result = runner.invoke(main, ["validate", "--pending-renames"])
            self.assertEqual(result.exit_code, 3, result.output)
            flat = " ".join(result.output.split())
            # Three-part recovery prose (.gzkit/rules/guardrail-feedback-prose.md):
            self.assertIn(f"ADR-0.1.0 -> {_SLUG}", flat)  # what failed
            self.assertIn("Architectural Boundaries 4", flat)  # why it is forbidden
            self.assertIn("gz migrate-semver", flat)  # the governed next step

    def test_migrate_semver_clears_it(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed("ADR-0.1.0")
            migrate = runner.invoke(main, ["migrate-semver"])
            self.assertEqual(migrate.exit_code, 0, migrate.output)
            result = runner.invoke(main, ["validate", "--pending-renames"])
            self.assertEqual(result.exit_code, 0, result.output)

    def test_events_under_the_slug_leave_nothing_pending(self) -> None:
        """Control: an artifact recorded by its slug needs no rename."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed(_SLUG)
            result = runner.invoke(main, ["validate", "--pending-renames"])
            self.assertEqual(result.exit_code, 0, result.output)


if __name__ == "__main__":
    unittest.main()
