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

from gzkit.commands.common import ObpiAmbiguityError, _prefix_match_obpi, resolve_obpi
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


class TestPhantomCandidateDisambiguation(unittest.TestCase):
    """GHI #666: an append-only ledger keeps ``obpi_created`` events for OBPIs
    whose parent ADR was later demoted to pool or renamed. The freed semver slot
    is reused, so a short-form id acquires two expansion candidates — one real,
    one phantom. Prefix expansion then bails, the caller's bare ``except``
    swallows the error, and the raw short id is written into the plan-audit
    receipt, dead-blocking every ``src/`` write at the pipeline gate.

    A phantom has no brief on disk. Disk presence is therefore the disambiguator.
    """

    def test_phantom_candidate_dropped_when_no_brief_on_disk(self) -> None:
        real = "OBPI-0.33.0-01-airlock-data-model-and-events"
        phantom = "OBPI-0.33.0-01-refs-index"
        graph = {real: {"type": "obpi"}, phantom: {"type": "obpi"}}

        with tempfile.TemporaryDirectory() as tmp:
            docs_root = Path(tmp) / "docs"
            brief_dir = docs_root / "design" / "adr" / "pre-release"
            brief_dir.mkdir(parents=True)
            (brief_dir / f"{real}.md").write_text("# brief\n", encoding="utf-8")
            # The phantom deliberately has NO brief on disk.

            result = _prefix_match_obpi(graph, "OBPI-0.33.0-01", docs_root=docs_root)

        self.assertEqual(result, real)

    def test_genuine_ambiguity_survives_disk_check(self) -> None:
        """Two REAL briefs remain ambiguous — disk presence must not fabricate a winner."""
        alpha = "OBPI-0.1.0-01-alpha"
        beta = "OBPI-0.1.0-01-beta"
        graph = {alpha: {"type": "obpi"}, beta: {"type": "obpi"}}

        with tempfile.TemporaryDirectory() as tmp:
            docs_root = Path(tmp) / "docs"
            docs_root.mkdir(parents=True)
            (docs_root / f"{alpha}.md").write_text("# a\n", encoding="utf-8")
            (docs_root / f"{beta}.md").write_text("# b\n", encoding="utf-8")

            result = _prefix_match_obpi(graph, "OBPI-0.1.0-01", docs_root=docs_root)

        self.assertIsNone(result)

    def test_no_brief_on_disk_for_any_candidate_stays_ambiguous(self) -> None:
        """Filtering must never drop every candidate and invent a match."""
        graph = {
            "OBPI-0.1.0-01-alpha": {"type": "obpi"},
            "OBPI-0.1.0-01-beta": {"type": "obpi"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            docs_root = Path(tmp) / "docs"
            docs_root.mkdir(parents=True)
            result = _prefix_match_obpi(graph, "OBPI-0.1.0-01", docs_root=docs_root)
        self.assertIsNone(result)


class TestResolveObpiAmbiguityIsLoud(unittest.TestCase):
    """GHI #666: genuine ambiguity must raise a diagnostic naming the candidates,
    never be reported as the generic 'OBPI not found'. A caller that swallows the
    error and returns the short id turns a resolvable ambiguity into a silent
    wrong answer three layers away (.claude/rules/guardrail-feedback-prose.md).
    """

    def test_ambiguous_short_form_raises_naming_candidates(self) -> None:
        alpha = "OBPI-0.1.0-01-alpha"
        beta = "OBPI-0.1.0-01-beta"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir(parents=True)
            (docs / f"{alpha}.md").write_text("# a\n", encoding="utf-8")
            (docs / f"{beta}.md").write_text("# b\n", encoding="utf-8")

            ledger = unittest.mock.MagicMock()
            ledger.canonicalize_id.side_effect = lambda x: x
            ledger.get_artifact_graph.return_value = {
                alpha: {"type": "obpi"},
                beta: {"type": "obpi"},
            }
            config = unittest.mock.MagicMock(spec=GzkitConfig)
            config.paths = unittest.mock.MagicMock()
            config.paths.design_root = "design"

            with (
                patch("gzkit.commands.common.scan_existing_artifacts", return_value={"obpis": []}),
                self.assertRaises(ObpiAmbiguityError) as ctx,
            ):
                resolve_obpi(root, config, ledger, "OBPI-0.1.0-01")

        message = str(ctx.exception)
        self.assertIn("OBPI-0.1.0-01", message)
        self.assertIn(alpha, message)
        self.assertIn(beta, message)

    def test_phantom_sibling_resolves_instead_of_raising(self) -> None:
        """The real-world GHI #666 shape: one real brief, one phantom ledger id."""
        real = "OBPI-0.33.0-01-airlock-data-model-and-events"
        phantom = "OBPI-0.33.0-01-refs-index"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir(parents=True)
            brief = docs / f"{real}.md"
            brief.write_text(f"---\nid: {real}\n---\n", encoding="utf-8")

            ledger = unittest.mock.MagicMock()
            ledger.canonicalize_id.side_effect = lambda x: x
            ledger.get_artifact_graph.return_value = {
                real: {"type": "obpi"},
                phantom: {"type": "obpi"},
            }
            config = unittest.mock.MagicMock(spec=GzkitConfig)
            config.paths = unittest.mock.MagicMock()
            config.paths.design_root = "design"

            with (
                patch(
                    "gzkit.commands.common.scan_existing_artifacts",
                    return_value={"obpis": [brief]},
                ),
                patch(
                    "gzkit.commands.common.parse_artifact_metadata",
                    return_value={"id": real},
                ),
            ):
                resolved_id, _ = resolve_obpi(root, config, ledger, "OBPI-0.33.0-01")

        self.assertEqual(resolved_id, real)


if __name__ == "__main__":
    unittest.main()
