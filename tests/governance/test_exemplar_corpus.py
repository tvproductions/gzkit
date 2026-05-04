"""Governance tests for `data/exemplar_corpus.json` (ADR-0.0.27, OBPI-0.0.27-02).

These tests assert REQ-derived semantics on the canonical on-disk corpus, not
fixture data. The corpus is doctrine; these tests are the structural defense
against silent drift away from the seven selection criteria and the corpus
anti-patterns canonized in `.gzkit/rules/complexity-doctrine.md`.

Coverage map:
- REQ-0.0.27-02-01 — corpus size in 12-15 band; archetypal-cell coverage
- REQ-0.0.27-02-02 — every commit_sha is 40-char lowercase hex
- REQ-0.0.27-02-03 — every entry has path filters and rationale
- REQ-0.0.27-02-04 — archetypal-cell coverage >= 8 of 10
- REQ-0.0.27-02-05 — pytest absent; Pydantic absent
- REQ-0.0.27-02-06 — six pool stubs exist with canonical shape and cite OBPI-02
- REQ-0.0.27-02-09 — path filters explicit at module-subset level (no whole-project globs)
- REQ-0.0.27-02-11 — operator personal email never appears in corpus content
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.models.exemplar import ExemplarCorpus, load_corpus
from gzkit.traceability import covers  # noqa: F401

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CORPUS_PATH = _REPO_ROOT / "data" / "exemplar_corpus.json"
_POOL_DIR = _REPO_ROOT / "docs" / "design" / "adr" / "pool"

_REQUIRED_POOL_STUB_SLUGS = (
    "attestation-quality-measurement",
    "doctrine-amendment-protocol",
    "complexity-doctrine-validate-suite",
    "canon-pillar-codification",
    "complexity-doctrine-meets-chore-system",
    "complexity-guide-obpi-authoring-integration",
)

_DOCTRINE_VIOLATING_PROJECTS = frozenset({"pytest", "pydantic"})

_SHA40 = re.compile(r"^[0-9a-f]{40}$")

# Email patterns the operator-PII rule forbids inside repo-bound artifacts.
# `ahuimanu@gmail.com` is the operator's personal address; the structural
# guard also rejects any `@gmail.com` plain-text appearance in the corpus
# content (corpus authoring should never reach into operator identity space).
_FORBIDDEN_EMAIL_FRAGMENTS = ("ahuimanu@gmail.com", "@gmail.com")


def _load() -> ExemplarCorpus:
    return load_corpus(_CORPUS_PATH)


class TestCorpusSizeAndCellCoverage(unittest.TestCase):
    """Corpus is 12-15 projects covering >= 8 of 10 archetypal cells."""

    @covers("REQ-0.0.27-02-01")
    def test_corpus_size_in_target_band(self) -> None:
        corpus = _load()
        size = len(corpus.projects)
        self.assertGreaterEqual(size, 12, f"corpus has {size} projects, below 12 minimum")
        self.assertLessEqual(size, 15, f"corpus has {size} projects, above 15 maximum")

    @covers("REQ-0.0.27-02-04")
    def test_archetypal_cell_coverage_meets_floor(self) -> None:
        corpus = _load()
        cells_with_projects = {p.archetypal_cell for p in corpus.projects}
        self.assertGreaterEqual(
            len(cells_with_projects),
            8,
            f"only {len(cells_with_projects)} of 10 cells populated; doctrine floor is 8",
        )

    @covers("REQ-0.0.27-02-04")
    def test_archetypal_cell_range_is_one_through_ten(self) -> None:
        corpus = _load()
        cells = {p.archetypal_cell for p in corpus.projects}
        cells |= {v.archetypal_cell for v in corpus.vacant_cells}
        for cell in cells:
            self.assertGreaterEqual(cell, 1)
            self.assertLessEqual(cell, 10)


class TestCorpusShaPinning(unittest.TestCase):
    """Every commit_sha is a 40-char lowercase hex SHA (no branch names, no tags)."""

    @covers("REQ-0.0.27-02-02")
    def test_every_commit_sha_is_pinned_40_char_hex(self) -> None:
        corpus = _load()
        for project in corpus.projects:
            with self.subTest(project=project.name):
                self.assertRegex(
                    project.commit_sha,
                    _SHA40,
                    f"{project.name}: commit_sha {project.commit_sha!r} not 40-char lowercase hex",
                )


class TestCorpusPathFilterDiscipline(unittest.TestCase):
    """Every entry has explicit module-subset path filters with rationale."""

    @covers("REQ-0.0.27-02-03")
    def test_every_project_has_included_paths(self) -> None:
        corpus = _load()
        for project in corpus.projects:
            with self.subTest(project=project.name):
                self.assertGreaterEqual(
                    len(project.included_paths),
                    1,
                    f"{project.name}: empty included_paths violates REQ-03",
                )

    @covers("REQ-0.0.27-02-03")
    def test_every_project_has_path_filter_rationale(self) -> None:
        corpus = _load()
        for project in corpus.projects:
            with self.subTest(project=project.name):
                self.assertGreater(
                    len(project.path_filter_rationale.strip()),
                    0,
                    f"{project.name}: empty path_filter_rationale",
                )

    @covers("REQ-0.0.27-02-03")
    def test_no_whole_project_inclusion_globs(self) -> None:
        """Whole-project wildcards (`*`, `**`) are rejected — module-subset discipline."""
        corpus = _load()
        for project in corpus.projects:
            for glob in project.included_paths:
                with self.subTest(project=project.name, glob=glob):
                    self.assertNotEqual(
                        glob.strip(),
                        "*",
                        f"{project.name}: bare '*' glob violates module-subset discipline",
                    )
                    self.assertNotEqual(
                        glob.strip(),
                        "**",
                        f"{project.name}: bare '**' glob violates module-subset discipline",
                    )
                    self.assertNotEqual(
                        glob.strip(),
                        "**/*",
                        f"{project.name}: bare '**/*' glob violates module-subset discipline",
                    )


class TestCorpusDoctrineFitness(unittest.TestCase):
    """Doctrinally-incompatible projects are absent (REQ-05)."""

    @covers("REQ-0.0.27-02-05")
    def test_pytest_absent_from_corpus(self) -> None:
        corpus = _load()
        names = {p.name.lower() for p in corpus.projects}
        self.assertNotIn(
            "pytest",
            names,
            "pytest violates Stdlib-First doctrine (forbid-pytest hook); corpus inclusion blocked",
        )

    @covers("REQ-0.0.27-02-05")
    def test_pydantic_absent_from_corpus(self) -> None:
        corpus = _load()
        names = {p.name.lower() for p in corpus.projects}
        self.assertNotIn(
            "pydantic",
            names,
            "Pydantic v2 has Rust core; pure-Python criterion fails; corpus blocked",
        )

    @covers("REQ-0.0.27-02-05")
    def test_no_doctrine_violating_project_names(self) -> None:
        """Defense-in-depth: explicit reject list."""
        corpus = _load()
        names = {p.name.lower() for p in corpus.projects}
        for forbidden in _DOCTRINE_VIOLATING_PROJECTS:
            with self.subTest(project=forbidden):
                self.assertNotIn(forbidden, names)


class TestPoolStubExistence(unittest.TestCase):
    """Six cluster pool-stub files exist under docs/design/adr/pool/ (REQ-06)."""

    @covers("REQ-0.0.27-02-06")
    def test_all_six_cluster_pool_stubs_exist(self) -> None:
        for slug in _REQUIRED_POOL_STUB_SLUGS:
            path = _POOL_DIR / f"ADR-pool.{slug}.md"
            with self.subTest(stub=slug):
                self.assertTrue(
                    path.is_file(),
                    f"missing pool stub: {path.relative_to(_REPO_ROOT).as_posix()}",
                )

    @covers("REQ-0.0.27-02-06")
    def test_each_pool_stub_carries_canonical_id_frontmatter(self) -> None:
        for slug in _REQUIRED_POOL_STUB_SLUGS:
            path = _POOL_DIR / f"ADR-pool.{slug}.md"
            with self.subTest(stub=slug):
                content = path.read_text(encoding="utf-8")
                self.assertIn(
                    f"id: ADR-pool.{slug}",
                    content,
                    f"pool stub {slug} missing canonical id frontmatter",
                )
                self.assertIn(
                    "status: Pool",
                    content,
                    f"pool stub {slug} missing 'status: Pool' frontmatter",
                )

    @covers("REQ-0.0.27-02-06")
    def test_each_pool_stub_cites_obpi_02_as_booking_event(self) -> None:
        """Forward-reference contract: each stub names OBPI-0.0.27-02 as booking event."""
        for slug in _REQUIRED_POOL_STUB_SLUGS:
            path = _POOL_DIR / f"ADR-pool.{slug}.md"
            with self.subTest(stub=slug):
                content = path.read_text(encoding="utf-8")
                self.assertIn(
                    "OBPI-0.0.27-02",
                    content,
                    f"pool stub {slug} does not cite OBPI-0.0.27-02 as booking event",
                )


class TestCorpusOperatorPiiHardening(unittest.TestCase):
    """No operator personal email anywhere in the corpus content.

    Defense-in-depth check for the brief's REQ-11 ("NEVER include the operator's
    personal email"). Not a brief-acceptance-criteria REQ, so no @covers decoration —
    this is a structural guard, not a coverage claim.
    """

    def test_corpus_text_contains_no_personal_email(self) -> None:
        text = _CORPUS_PATH.read_text(encoding="utf-8")
        for fragment in _FORBIDDEN_EMAIL_FRAGMENTS:
            with self.subTest(fragment=fragment):
                self.assertNotIn(
                    fragment.lower(),
                    text.lower(),
                    f"operator-PII fragment {fragment!r} appears in corpus content",
                )


if __name__ == "__main__":
    unittest.main()
