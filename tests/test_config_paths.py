"""Tests for config-paths source path literal scanning.

@covers OBPI-0.0.7-05-lint-rule-and-check-expansion
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.config_paths import (
    _collect_source_path_literal_issues,
    _flatten_manifest_paths,
    _is_path_covered_by_manifest,
)
from gzkit.config import GzkitConfig


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):
        return obj

    return _identity


SAMPLE_MANIFEST = {
    "structure": {
        "source_root": "src",
        "tests_root": "tests",
        "docs_root": "docs",
        "design_root": "docs/design",
    },
    "data": {
        "eval_datasets": "data/eval",
        "schemas": "data/schemas",
    },
    "ops": {
        "chores": "config/chores",
    },
    "artifacts": {
        "adr": {"path": "docs/design/adr"},
    },
    "control_surfaces": {
        "skills": ".gzkit/skills",
    },
}


class TestFlattenManifestPaths(unittest.TestCase):
    """Verify manifest path extraction."""

    def test_extracts_known_paths(self):
        paths = _flatten_manifest_paths(SAMPLE_MANIFEST)
        self.assertIn("data/eval", paths)
        self.assertIn("docs/design", paths)
        self.assertIn("docs/design/adr", paths)
        self.assertIn(".gzkit/skills", paths)

    def test_empty_manifest(self):
        paths = _flatten_manifest_paths({})
        self.assertEqual(paths, set())


class TestIsPathCovered(unittest.TestCase):
    """Verify path coverage matching logic."""

    def test_exact_match(self):
        self.assertTrue(_is_path_covered_by_manifest("data/eval", {"data/eval"}))

    def test_prefix_match(self):
        self.assertTrue(_is_path_covered_by_manifest("data/eval/scores.json", {"data/eval"}))

    def test_parent_match(self):
        self.assertTrue(_is_path_covered_by_manifest("data", {"data/eval"}))

    def test_no_match(self):
        self.assertFalse(_is_path_covered_by_manifest("unknown/dir", {"data/eval"}))

    def test_partial_segment_no_match(self):
        """data/evaluate should NOT match data/eval."""
        self.assertFalse(_is_path_covered_by_manifest("data/evaluate", {"data/eval"}))


class TestSourcePathLiteralScan(unittest.TestCase):
    """Verify source scanning detects unmapped path literals."""

    @covers("REQ-0.0.7-05-04")
    def test_clean_source_no_issues(self):
        """Source with only manifest-mapped paths produces no issues."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "clean.py").write_text(
                'path = "data/eval"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(issues, [])

    @covers("REQ-0.0.7-05-02")
    def test_unmapped_literal_flagged(self):
        """Source with a path literal not in manifest is flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            # Use a directory root not present in SAMPLE_MANIFEST
            (src / "bad.py").write_text(
                'output_dir = "artifacts/unknown/reports"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertTrue(len(issues) > 0)
            self.assertIn("unmapped path literal", issues[0]["issue"])

    @covers("REQ-0.0.7-05-02")
    def test_exempt_literal_not_flagged(self):
        """Path-shaped literals that are not config paths are exempt.

        A forbidden-pattern detector string (``ops/chores/``) and a template
        placeholder example (``config/file.json``) are path-shaped but name no
        real config location; mapping them to the manifest would be wrong, so
        the audit exempts them rather than demanding a mapping.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "detector.py").write_text(
                'FORBIDDEN = "ops/chores/"\nPLACEHOLDER = "config/file.json"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(issues, [])

    def test_url_not_flagged(self):
        """HTTP URLs are not treated as path literals."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "url.py").write_text(
                'endpoint = "https://docs/design/api"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(issues, [])

    def test_missing_src_dir_no_issues(self):
        """If src/gzkit/ doesn't exist, no issues returned."""
        with tempfile.TemporaryDirectory() as tmp:
            issues = _collect_source_path_literal_issues(Path(tmp), SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()


class TestPathConfigDeclaredDefaults(unittest.TestCase):
    """A literal declared as a PathConfig default is governed by config.

    The scanner's question is "is this literal governed by config?", and
    ``GzkitConfig.paths`` is config. Before GHI #938 the scanner consulted the
    manifest alone, so a declared ``PathConfig`` default was reported unmapped
    -- including at the ``config.py`` line that declares it.
    """

    @covers("REQ-0.0.7-05-02")
    def test_declared_default_not_flagged(self):
        """A literal equal to a PathConfig default is not an unmapped literal."""
        config = GzkitConfig()
        # Precondition: the manifest genuinely does not carry this path, so a
        # pass can only come from config coverage, never from manifest overlap.
        self.assertFalse(
            _is_path_covered_by_manifest(
                config.paths.discovery_index, _flatten_manifest_paths(SAMPLE_MANIFEST)
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "declares.py").write_text(
                f'discovery_index: str = "{config.paths.discovery_index}"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, config)
            self.assertEqual(issues, [])

    @covers("REQ-0.0.7-05-02")
    def test_undeclared_sibling_still_flagged(self):
        """Config coverage is exact: a sibling under the same root stays flagged.

        Boundary test. Deriving parent directories from config defaults would
        make ``.github`` itself covered and silently exempt every ``.github/**``
        literal, which is the opposite of what the audit is for.
        """
        config = GzkitConfig()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "sibling.py").write_text(
                'legacy = ".github/skills"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, config)
            self.assertEqual(len(issues), 1)
            self.assertIn(".github/skills", issues[0]["issue"])


class TestModuleDeclaredAuditSubjects(unittest.TestCase):
    """A module may declare which of its path literals are audit SUBJECTS.

    Some path literals are not resource paths at all. A literal naming the
    population a control audits, a vendor-mirror roster iterated to detect a
    retired layout, or a sentinel for a directory that must NOT exist is the
    audit's own subject -- there is no config field it could be sourced from,
    because a config field would describe where that surface lives, which is
    the very thing the check is asserting about (GHI #938).

    The exemption is declared AT THE SITE, in the module that owns the literal,
    rather than in a central roster. A roster drifts from the code it excuses
    and needs an owner; a declaration beside the literal is read by whoever is
    already editing the file. `grep -rn _AUDIT_SUBJECT_LITERALS src/` is the
    complete exemption census, and every entry sits next to its justification.

    These tests pin the SCOPING, which is the whole safety property: a
    declaration credits only the module that makes it. Without that, the
    mechanism degenerates into a global roster with worse ergonomics.
    """

    @covers("REQ-0.0.7-05-02")
    def test_a_module_declared_subject_literal_is_credited(self):
        """A literal the owning module declares as a subject is not flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "control.py").write_text(
                "_AUDIT_SUBJECT_LITERALS = (\n"
                '    ".github/workflows/",  # population this control audits\n'
                ")\n"
                'def audits(p): return p.startswith(".github/workflows/")\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(issues, [])

    @covers("REQ-0.0.7-05-02")
    def test_a_declaration_does_not_reach_another_module(self):
        """Scoping. One module's declaration must not excuse a second module.

        This is the property that separates a site declaration from a central
        roster. If a declaration leaked across modules, any file in the tree
        could silence a literal anywhere else and the census grep would name
        the wrong owner.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "declarer.py").write_text(
                '_AUDIT_SUBJECT_LITERALS = (".github/workflows/",)\n',
                encoding="utf-8",
            )
            (src / "borrower.py").write_text(
                'population = ".github/workflows/"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(len(issues), 1, issues)
            self.assertEqual(issues[0]["path"], "src/gzkit/borrower.py")
            self.assertIn(".github/workflows/", issues[0]["issue"])

    @covers("REQ-0.0.7-05-02")
    def test_an_undeclared_literal_in_a_declaring_module_is_still_flagged(self):
        """Declaring one subject does not blanket-exempt the module."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "partial.py").write_text(
                '_AUDIT_SUBJECT_LITERALS = (".github/workflows/",)\n'
                'resource = ".github/instructions"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(len(issues), 1, issues)
            self.assertIn(".github/instructions", issues[0]["issue"])

    @covers("REQ-0.0.7-05-02")
    def test_a_differently_named_constant_grants_nothing(self):
        """The name is exact, so `grep` is a COMPLETE exemption census.

        If any tuple of path-shaped strings could grant an exemption, the
        census would be unbounded and the audit would be silently weakened by
        ordinary constants that happen to hold paths.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "lookalike.py").write_text(
                '_AUDIT_SUBJECTS = (".github/workflows/",)\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(len(issues), 1, issues)

    @covers("REQ-0.0.7-05-02")
    def test_declaring_a_parent_does_not_exempt_its_children(self):
        """The match is EXACT, never a prefix test.

        This is the blinding failure `_flatten_config_paths` already refuses
        for the same reason: if a declared ".github" were treated as a prefix,
        every ".github/**" literal in the module would go dark and the audit
        would read green over exactly the surface it exists to police. A
        module cannot buy a blanket exemption by declaring a root.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "greedy.py").write_text(
                '_AUDIT_SUBJECT_LITERALS = (".github",)\nresource = ".github/skills"\n',
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(len(issues), 1, issues)
            self.assertIn(".github/skills", issues[0]["issue"])

    @covers("REQ-0.0.7-05-02")
    def test_a_declaration_inside_a_function_grants_nothing(self):
        """Only MODULE-LEVEL declarations count.

        A function-local name is invisible to a reader skimming the module and
        invisible to the census grep's intent, so crediting it would put an
        exemption somewhere nobody looks.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "buried.py").write_text(
                "def f():\n"
                '    _AUDIT_SUBJECT_LITERALS = (".github/workflows/",)\n'
                "    return _AUDIT_SUBJECT_LITERALS\n",
                encoding="utf-8",
            )
            issues = _collect_source_path_literal_issues(root, SAMPLE_MANIFEST, GzkitConfig())
            self.assertEqual(len(issues), 1, issues)

    @covers("REQ-0.0.7-05-02")
    def test_the_real_repository_reports_no_unmapped_literals(self):
        """Acceptance: the proof command is green on this tree.

        `uv run gz check-config-paths` is one of the five proof commands in
        `.claude/rules/governance-core.md`, and it exited 1 for an unknown
        period (GHI #938). A proof command proves nothing while it is red, and
        a standing red teaches readers to discount its exit code. This test is
        what keeps it honest between runs.
        """
        from gzkit.commands.config_paths import load_manifest

        project_root = Path(__file__).resolve().parent.parent
        issues = _collect_source_path_literal_issues(
            project_root, load_manifest(project_root), GzkitConfig()
        )
        self.assertEqual(issues, [], f"unmapped path literals: {issues}")
