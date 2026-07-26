"""Tests for the `gz validate --brief-structure` scope (GHI #615 cut 3).

`BriefStructure` shipped with ADR-0.0.37-04 but nothing ever enforced it:
`parse_brief` defaults to `strict=False`, so a brief without structured
frontmatter silently falls back to `LegacyBriefShape` and is "validated" by
regex-scraping its markdown body. A schema built and never enforced, with a
regex fallback scraping prose, is the vibing surface AGENTS.md § MAKE LLM
STOCHASTIC VIBES INERT exists to close.

The scope is deliberately scoped to the NON-TERMINAL corpus. A terminal brief
is a sealed historical record; demanding it migrate would either rewrite an
attested artifact or hold the gate red over a tree nobody may repair.
"""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits.brief_structure import validate_brief_structure
from gzkit.traceability import covers

_LEGACY = textwrap.dedent(
    """\
    ---
    id: OBPI-0.1.0-01-legacy
    parent: ADR-0.1.0-f
    lane: Lite
    status: {status}
    ---

    # OBPI-0.1.0-01-legacy: Legacy

    ## Allowed Paths

    - `src/gzkit/alpha.py`
    """
)

_STRUCTURED = textwrap.dedent(
    """\
    ---
    id: OBPI-0.1.0-02-structured
    parent: ADR-0.1.0-f
    lane: Lite
    status: Draft
    allowlist:
    - src/gzkit/alpha.py
    reqs:
    - REQ-0.1.0-02-01
    verification:
    - uv run gz validate
    ---

    # OBPI-0.1.0-02-structured: Structured
    """
)


class TestBriefStructureScope(unittest.TestCase):
    def _root(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "docs" / "design" / "adr" / "pkg" / "obpis").mkdir(parents=True)
        return root

    def _write(self, root: Path, name: str, text: str) -> None:
        (root / "docs" / "design" / "adr" / "pkg" / "obpis" / name).write_text(
            text, encoding="utf-8"
        )

    @covers("REQ-0.0.37-04-04")
    def test_live_legacy_brief_fails_closed(self):
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._write(root, "OBPI-0.1.0-01-legacy.md", _LEGACY.format(status="Draft"))
            errors = validate_brief_structure(root)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "brief_structure")
        self.assertIn("OBPI-0.1.0-01-legacy.md", errors[0].artifact)

    @covers("REQ-0.0.37-04-04")
    def test_terminal_legacy_brief_is_not_gated(self):
        # A sealed record must not be dragged into the live schema: the only
        # available "repair" would rewrite an attested governance artifact.
        for status in ("Completed", "attested_completed", "Withdrawn", "archived"):
            with self.subTest(status=status), TemporaryDirectory() as tmp:
                root = self._root(tmp)
                self._write(root, "OBPI-0.1.0-01-legacy.md", _LEGACY.format(status=status))
                self.assertEqual(validate_brief_structure(root), [])

    @covers("REQ-0.0.37-04-04")
    def test_structured_live_brief_passes(self):
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._write(root, "OBPI-0.1.0-02-structured.md", _STRUCTURED)
            self.assertEqual(validate_brief_structure(root), [])

    @covers("REQ-0.0.37-04-04")
    def test_malformed_structured_brief_fails_closed(self):
        # Carrying the three keys is not enough — the values must satisfy the
        # model. Otherwise the gate would accept `reqs: [nonsense]` and the
        # schema would be enforced in name only, which is the defect #615 names.
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            self._write(
                root,
                "OBPI-0.1.0-02-structured.md",
                _STRUCTURED.replace("- REQ-0.1.0-02-01", "- NOT-A-REQ-ID"),
            )
            errors = validate_brief_structure(root)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "brief_structure")

    @covers("REQ-0.0.37-04-04")
    def test_real_corpus_is_clean(self):
        # The corpus migrated under GHI #615 cut 2; this is the standing guard
        # that a newly authored live brief cannot land unstructured.
        self.assertEqual(validate_brief_structure(Path(__file__).parent.parent.parent), [])


if __name__ == "__main__":
    unittest.main()
