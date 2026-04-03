"""Tests for OBPI short-form prefix matching in resolve_obpi.

Short-form IDs like ``OBPI-0.0.12-02`` should resolve to full slugs like
``OBPI-0.0.12-02-implementer-agent-persona`` when a unique prefix match
exists in the ledger graph.
"""

import unittest

from gzkit.commands.common import _prefix_match_obpi


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


if __name__ == "__main__":
    unittest.main()
