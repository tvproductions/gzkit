"""REQ-derived tests for the OKF bundle generator (OBPI-0.30.0-02).

Assertions are derived from the brief's Requirements (FAIL-CLOSED), NOT from a
run of the implementation (`.gzkit/rules/tests.md` § "Tests assert semantics,
not strings").

The two load-bearing correctness properties under test:
  - Source docs are byte-unchanged after generation (read-only).
  - Generation is idempotent: re-running over unchanged sources yields a
    byte-identical bundle.

Tests are hermetic: the tracer slice under test is a FIXTURE built in a
``tempfile.TemporaryDirectory`` (small fake source ``.md`` files), never the
live ``docs/governance/`` paths. The real ``TRACER_SLICE`` constant is
exercised only by the module ``__main__`` block, not by these unit tests.
"""

import re
import tempfile
import unittest
from pathlib import Path

import yaml

from gzkit.knowledge import ConceptFrontmatter, generate_bundle
from gzkit.traceability import covers


def _build_fixture_slice(root: Path) -> list[tuple[str, Path]]:
    """Write small fake source .md files and return the (slug, path) slice."""
    src_dir = root / "sources"
    src_dir.mkdir(parents=True, exist_ok=True)
    entries = [
        ("state-doctrine", "State doctrine body.\n"),
        ("trust-doctrine", "Trust doctrine body.\n"),
        ("agent-contract-rationale", "Agent contract rationale body.\n"),
        ("active-campaign", "Active campaign body.\n"),
    ]
    slice_: list[tuple[str, Path]] = []
    for slug, body in entries:
        path = src_dir / f"{slug}.md"
        path.write_text(f"# {slug}\n\n{body}", encoding="utf-8")
        slice_.append((slug, path))
    return slice_


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Parse a ``---``-delimited YAML frontmatter block + body from md text."""
    assert text.startswith("---\n"), "concept doc must open with a YAML frontmatter fence"
    _, fm_text, body = text.split("---\n", 2)
    return yaml.safe_load(fm_text), body


class TestBundleGenerator(unittest.TestCase):
    """OKF bundle generator — REQ-derived behavior."""

    @covers("REQ-0.30.0-02-01")
    def test_generator_emits_root_index_and_concept_docs(self) -> None:
        """REQ-01: root index.md + one OKF concept doc per source, each with
        frontmatter the ConceptFrontmatter model validates (non-empty type)."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sources = _build_fixture_slice(tmp_path)
            out = tmp_path / "bundle"

            generate_bundle(sources, out)

            self.assertTrue((out / "index.md").is_file(), "root index.md must exist")
            for slug, _source in sources:
                concept = out / f"{slug}.md"
                self.assertTrue(concept.is_file(), f"concept doc for {slug} must exist")
                fm, _body = _split_frontmatter(concept.read_text(encoding="utf-8"))
                # Validates via the OBPI-01 model: non-empty `type` required.
                model = ConceptFrontmatter(**fm)
                self.assertTrue(model.type, "concept frontmatter `type` must be non-empty")

    @covers("REQ-0.30.0-02-02")
    def test_concept_docs_link_to_source_and_have_progressive_disclosure(self) -> None:
        """REQ-02: directory index.md progressive disclosure exists; each concept
        doc links to its canonical source (markdown-link / resource edge)."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sources = _build_fixture_slice(tmp_path)
            out = tmp_path / "bundle"

            generate_bundle(sources, out)

            index_text = (out / "index.md").read_text(encoding="utf-8")
            index_fm, index_body = _split_frontmatter(index_text)
            # The index is itself an OKF node (progressive-disclosure entry).
            self.assertTrue(index_fm.get("type"), "index.md must carry an OKF `type`")

            for slug, source in sources:
                # Progressive disclosure: root index links to each concept doc.
                self.assertIn(f"{slug}.md", index_body, f"index must link to {slug}.md")

                concept_text = (out / f"{slug}.md").read_text(encoding="utf-8")
                fm, body = _split_frontmatter(concept_text)
                # Graph edge: `resource` frontmatter points at the source doc.
                self.assertEqual(
                    fm.get("resource"),
                    source.as_posix(),
                    f"concept {slug} resource edge must point at its source",
                )
                # Body carries a markdown link whose target is a PORTABLE
                # relative path that RESOLVES from the concept doc's own
                # location to the canonical source — semantics, not mere string
                # containment. A repo-root-relative (or absolute) link string is
                # present in the body but does NOT resolve from a file three
                # levels deep in the bundle; the link must be navigable.
                link_targets = re.findall(r"\]\(([^)]+)\)", body)
                self.assertTrue(link_targets, f"{slug} body must contain a markdown link")
                link = link_targets[0]
                self.assertFalse(
                    Path(link).is_absolute(),
                    f"{slug} body link must be a portable relative path, not root-anchored",
                )
                # Concept doc lives at out/<slug>.md, so resolve link against `out`.
                resolved = (out / link).resolve()
                self.assertEqual(
                    resolved,
                    source.resolve(),
                    f"{slug} body link must resolve to its canonical source, not a dead path",
                )

    @covers("REQ-0.30.0-02-02")
    def test_index_links_preserved_authored_node(self) -> None:
        """REQ-02 (progressive disclosure, no orphans): an authored OKF node
        preserved in the bundle (e.g. OBPI-06's content-boundary doctrine) is
        reachable from the root index, never left an orphan typed node."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sources = _build_fixture_slice(tmp_path)
            out = tmp_path / "bundle"
            out.mkdir(parents=True, exist_ok=True)
            # An authored, OKF-conformant node placed in the bundle BEFORE generation.
            (out / "content-boundary.md").write_text(
                "---\ntype: doctrine\ntitle: Content Boundary\n---\n\n# Content Boundary\n",
                encoding="utf-8",
            )

            generate_bundle(sources, out)

            _index_fm, index_body = _split_frontmatter(
                (out / "index.md").read_text(encoding="utf-8")
            )
            self.assertIn(
                "content-boundary.md",
                index_body,
                "root index must link the preserved authored node (no orphan typed nodes)",
            )

    @covers("REQ-0.30.0-02-03")
    def test_generator_does_not_modify_source_docs(self) -> None:
        """REQ-03: no source document is modified (byte-unchanged after run)."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sources = _build_fixture_slice(tmp_path)
            out = tmp_path / "bundle"

            before = {slug: source.read_bytes() for slug, source in sources}
            generate_bundle(sources, out)
            after = {slug: source.read_bytes() for slug, source in sources}

            self.assertEqual(before, after, "source docs must be byte-unchanged")

    @covers("REQ-0.30.0-02-04")
    def test_generation_is_idempotent(self) -> None:
        """REQ-04: re-running over unchanged sources yields a byte-identical bundle."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sources = _build_fixture_slice(tmp_path)
            out = tmp_path / "bundle"

            generate_bundle(sources, out)
            first = {p.name: p.read_bytes() for p in sorted(out.iterdir()) if p.is_file()}
            generate_bundle(sources, out)
            second = {p.name: p.read_bytes() for p in sorted(out.iterdir()) if p.is_file()}

            self.assertEqual(first, second, "re-generation must be byte-identical")


if __name__ == "__main__":
    unittest.main()
