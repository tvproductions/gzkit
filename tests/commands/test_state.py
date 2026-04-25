"""Tests for the gz state command surface (GHI #319)."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event
from tests.commands.common import CliRunner, _quick_init

_LONG_ADR_SLUG = "ADR-0.99.0-extremely-long-slug-to-force-truncation-without-full-flag"


def _seed_long_id_adr() -> None:
    config = GzkitConfig.load(Path(".gzkit.json"))
    adr_path = Path(config.paths.adrs) / f"{_LONG_ADR_SLUG}.md"
    adr_path.parent.mkdir(parents=True, exist_ok=True)
    adr_path.write_text(
        f"---\nid: {_LONG_ADR_SLUG}\nlane: lite\nkind: feature\n---\n\n# Long-slug ADR\n",
        encoding="utf-8",
    )
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(adr_created_event(_LONG_ADR_SLUG, "", "lite"))


class TestStateFullFlag(unittest.TestCase):
    """gz state --full preserves identity-bearing fields per GHI #319."""

    def test_state_full_renders_complete_artifact_id(self) -> None:
        """Every character of a long artifact ID must survive --full rendering.

        At a wide enough terminal the column fits the full ID on one line;
        the GHI's operator-facing semantic is "no truncation," verified
        here at 240 columns where wrapping does not interfere.
        """
        runner = CliRunner()
        with (
            patch.dict(os.environ, {"COLUMNS": "240"}, clear=False),
            runner.isolated_filesystem(),
        ):
            _quick_init()
            _seed_long_id_adr()

            result = runner.invoke(main, ["state", "--full"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(_LONG_ADR_SLUG, result.output)

    def test_state_full_does_not_ellipsize_long_ids(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_long_id_adr()

            result = runner.invoke(main, ["state", "--full"])
            self.assertEqual(result.exit_code, 0)
            # The Rich ellipsis character is U+2026 (`…`); a --full table must
            # never collapse identity-bearing IDs to it.
            self.assertNotIn("…", result.output)


class TestStateFullOutputForm(unittest.TestCase):
    """Output-form fixture for gz state --full per Invariant 3.

    Asserts the rendering contract (Rich table markers + folded ID column)
    that the GHI #319 close requires. Lives in a separate class from
    TestStateFullFlag so semantic and string-shape assertions never collide
    (.gzkit/rules/tests.md § Output-form fixture carve-out).
    """

    def test_state_full_renders_rich_table_with_artifact_state_title(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_long_id_adr()

            result = runner.invoke(main, ["state", "--full"])
            self.assertEqual(result.exit_code, 0)
            # Rich box-drawing markers (heavy box used by default Rich Table).
            self.assertIn("┃", result.output)
            self.assertIn("Artifact State", result.output)


if __name__ == "__main__":
    unittest.main()
