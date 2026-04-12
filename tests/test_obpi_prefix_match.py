"""Tests for OBPI short-form prefix matching in resolve_obpi.

Short-form IDs like ``OBPI-0.0.12-02`` should resolve to full slugs like
``OBPI-0.0.12-02-implementer-agent-persona`` when a unique prefix match
exists in the ledger graph.
"""

import tempfile
import unittest
import unittest.mock
from pathlib import Path
from unittest.mock import patch

from gzkit.commands.common import _prefix_match_obpi, resolve_obpi
from gzkit.config import GzkitConfig


class TestPrefixMatchObpi(unittest.TestCase):
    """_prefix_match_obpi resolves short-form OBPI IDs."""

    def test_unique_prefix_resolves(self) -> None:
        graph = {
            "OBPI-0.0.12-01-main-session-persona": {"type": "obpi"},
            "OBPI-0.0.12-02-implementer-agent-persona": {"type": "obpi"},
        }
        result = _prefix_match_obpi(graph, "OBPI-0.0.12-02")
        self.assertEqual(result, "OBPI-0.0.12-02-implementer-agent-persona")

    def test_exact_match_not_returned_as_prefix(self) -> None:
        """Exact ID in graph should not match (caller already tried exact)."""
        graph = {
            "OBPI-0.0.12-02": {"type": "obpi"},
        }
        result = _prefix_match_obpi(graph, "OBPI-0.0.12-02")
        self.assertIsNone(result)

    def test_ambiguous_prefix_returns_none(self) -> None:
        graph = {
            "OBPI-0.1.0-01-alpha": {"type": "obpi"},
            "OBPI-0.1.0-01-alpha-extended": {"type": "obpi"},
        }
        result = _prefix_match_obpi(graph, "OBPI-0.1.0-01")
        self.assertIsNone(result)

    def test_no_match_returns_none(self) -> None:
        graph = {
            "OBPI-0.0.12-01-main-session-persona": {"type": "obpi"},
        }
        result = _prefix_match_obpi(graph, "OBPI-0.0.12-99")
        self.assertIsNone(result)

    def test_non_obpi_type_ignored(self) -> None:
        graph = {
            "OBPI-0.0.12-02-implementer-agent-persona": {"type": "adr"},
        }
        result = _prefix_match_obpi(graph, "OBPI-0.0.12-02")
        self.assertIsNone(result)


class TestResolveObpiSymmetricExpansion(unittest.TestCase):
    """GHI-114: resolve_obpi must apply prefix expansion to file IDs too.

    A brief frontmatter ``id: OBPI-0.0.15-03`` (short form) must still match
    the ledger graph entry ``OBPI-0.0.15-03-version-sync-integration`` (full
    slug). Before the fix, only the input was expanded, not the file ID,
    so the file lookup returned ``None``.
    """

    def test_short_form_brief_id_matches_full_slug_graph(self) -> None:
        full_slug = "OBPI-0.0.15-03-version-sync-integration"
        short_form = "OBPI-0.0.15-03"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief_path = root / f"{short_form}.md"
            brief_path.write_text(
                f"---\nid: {short_form}\n---\n# OBPI-0.0.15-03\n",
                encoding="utf-8",
            )

            ledger = unittest.mock.MagicMock()
            ledger.canonicalize_id.side_effect = lambda x: x  # identity
            ledger.get_artifact_graph.return_value = {
                full_slug: {"type": "obpi"},
            }

            config = unittest.mock.MagicMock(spec=GzkitConfig)
            config.paths = unittest.mock.MagicMock()
            config.paths.design_root = "design"

            with (
                patch(
                    "gzkit.commands.common.scan_existing_artifacts",
                    return_value={"obpis": [brief_path]},
                ),
                patch(
                    "gzkit.commands.common.parse_artifact_metadata",
                    return_value={"id": short_form},
                ),
            ):
                resolved_id, resolved_path = resolve_obpi(root, config, ledger, short_form)

            self.assertEqual(resolved_id, full_slug)
            self.assertEqual(resolved_path, brief_path)


if __name__ == "__main__":
    unittest.main()
