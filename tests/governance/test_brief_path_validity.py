"""Brief allowed-path validity primitives (GHI #419).

Tests cover the shared-module shape: drift detection, vendor-mirror
detection, glob-root resolution, brief-level Creates-marker exemption, and
the convenience wrapper that combines extract + check.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.brief_path_validity import (
    allowed_path_resolves,
    check_brief_path_validity,
    check_brief_path_validity_for_brief,
    extract_allowed_paths,
    extract_brief_creates_paths,
    extract_plan_creates_paths,
    glob_root,
    has_glob_chars,
    vendor_mirror_canonical,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestHasGlobChars(unittest.TestCase):
    def test_literal_path_has_no_globs(self) -> None:
        self.assertFalse(has_glob_chars("src/gzkit/foo.py"))

    def test_star_is_glob(self) -> None:
        self.assertTrue(has_glob_chars("src/gzkit/**"))

    def test_question_mark_is_glob(self) -> None:
        self.assertTrue(has_glob_chars("src/gzkit/foo?.py"))


class TestGlobRoot(unittest.TestCase):
    def test_double_star(self) -> None:
        self.assertEqual(glob_root("src/gzkit/**/*.py"), "src/gzkit")

    def test_placeholder_is_glob(self) -> None:
        self.assertEqual(glob_root(".gzkit/skills/<slug>/SKILL.md"), ".gzkit/skills")

    def test_pure_glob_returns_empty(self) -> None:
        self.assertEqual(glob_root("*.md"), "")

    def test_literal_path_returned_whole(self) -> None:
        self.assertEqual(glob_root("src/gzkit/foo.py"), "src/gzkit/foo.py")


class TestVendorMirrorCanonical(unittest.TestCase):
    def test_claude_rules_mirror(self) -> None:
        self.assertEqual(
            vendor_mirror_canonical(".claude/rules/tests.md"),
            ".gzkit/rules/tests.md",
        )

    def test_claude_skills_mirror(self) -> None:
        self.assertEqual(
            vendor_mirror_canonical(".claude/skills/ghi-close/SKILL.md"),
            ".gzkit/skills/ghi-close/SKILL.md",
        )

    def test_github_skills_mirror(self) -> None:
        self.assertEqual(
            vendor_mirror_canonical(".github/skills/foo/SKILL.md"),
            ".gzkit/skills/foo/SKILL.md",
        )

    def test_canonical_path_returns_none(self) -> None:
        self.assertIsNone(vendor_mirror_canonical(".gzkit/rules/tests.md"))

    def test_unrelated_path_returns_none(self) -> None:
        self.assertIsNone(vendor_mirror_canonical("src/gzkit/foo.py"))


class TestAllowedPathResolves(unittest.TestCase):
    def test_existing_file_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "src" / "foo.py", "x = 1\n")
            self.assertTrue(allowed_path_resolves(root, "src/foo.py"))

    def test_missing_file_does_not_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertFalse(allowed_path_resolves(root, "src/missing.py"))

    def test_glob_root_existence_drives_decision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "src" / "gzkit" / "foo.py", "x = 1\n")
            self.assertTrue(allowed_path_resolves(root, "src/gzkit/**/*.py"))
            self.assertFalse(allowed_path_resolves(root, "src/missing/**/*.py"))

    def test_pure_glob_resolves_to_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertTrue(allowed_path_resolves(root, "*.md"))

    def test_flag_token_treated_as_resolvable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertTrue(allowed_path_resolves(root, "--skill"))


class TestExtractAllowedPaths(unittest.TestCase):
    def test_extracts_backtick_tokens_from_bullets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            brief = Path(td) / "OBPI-test.md"
            brief.write_text(
                "## Allowed Paths\n\n"
                "- `src/foo.py` -- target module\n"
                "- `tests/test_foo.py` -- coverage\n\n"
                "## Other Section\n",
                encoding="utf-8",
            )
            paths = extract_allowed_paths(brief)
            self.assertEqual(paths, ["src/foo.py", "tests/test_foo.py"])

    def test_uppercase_heading_with_lane_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            brief = Path(td) / "OBPI-test.md"
            brief.write_text(
                "## ALLOWED PATHS (Foundational)\n\n- `src/foo.py`\n",
                encoding="utf-8",
            )
            self.assertEqual(extract_allowed_paths(brief), ["src/foo.py"])

    def test_no_section_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            brief = Path(td) / "OBPI-test.md"
            brief.write_text("# Title\n\nNo allowed paths.\n", encoding="utf-8")
            self.assertIsNone(extract_allowed_paths(brief))


class TestExtractBriefCreatesPaths(unittest.TestCase):
    """Brief-level Creates-marker extractor (GHI #419 brief analogue of GHI #403)."""

    def test_creates_these_files_heading_section(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            brief = Path(td) / "OBPI-test.md"
            brief.write_text(
                "## Allowed Paths\n\n"
                "- `src/gzkit/governance/brief_path_validity.py`\n\n"
                "## Creates these files\n\n"
                "- `src/gzkit/governance/brief_path_validity.py`\n"
                "- `tests/governance/test_brief_path_validity.py`\n",
                encoding="utf-8",
            )
            creates = extract_brief_creates_paths(brief)
            self.assertIn("src/gzkit/governance/brief_path_validity.py", creates)
            self.assertIn("tests/governance/test_brief_path_validity.py", creates)

    def test_create_marker_inline(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            brief = Path(td) / "OBPI-test.md"
            brief.write_text(
                "Some prose **CREATE** `src/gzkit/new_module.py` more prose\n",
                encoding="utf-8",
            )
            creates = extract_brief_creates_paths(brief)
            self.assertIn("src/gzkit/new_module.py", creates)

    def test_no_creates_section_returns_empty_set(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            brief = Path(td) / "OBPI-test.md"
            brief.write_text("## Allowed Paths\n\n- `src/foo.py`\n", encoding="utf-8")
            self.assertEqual(extract_brief_creates_paths(brief), set())


class TestExtractPlanCreatesPaths(unittest.TestCase):
    """Plan-level extractor parity (GHI #403 carryover)."""

    def test_plan_creates_section_extracted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan = Path(td) / "plan.md"
            plan.write_text(
                "## Creates these files\n\n- `src/foo.py`\n",
                encoding="utf-8",
            )
            self.assertIn("src/foo.py", extract_plan_creates_paths(plan))


class TestCheckBriefPathValidity(unittest.TestCase):
    def test_existing_paths_produce_no_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "src" / "foo.py", "x = 1\n")
            gaps = check_brief_path_validity(root, ["src/foo.py"])
            self.assertEqual(gaps, [])

    def test_missing_path_produces_existence_gap(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gaps = check_brief_path_validity(root, ["src/drifted.py"])
            self.assertEqual(len(gaps), 1)
            self.assertIn("does not exist", gaps[0])
            self.assertIn("src/drifted.py", gaps[0])

    def test_vendor_mirror_path_produces_mirror_gap_even_if_exists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / ".claude" / "rules" / "tests.md", "doc\n")
            _write(root / ".gzkit" / "rules" / "tests.md", "doc\n")
            gaps = check_brief_path_validity(root, [".claude/rules/tests.md"])
            self.assertEqual(len(gaps), 1)
            self.assertIn("vendor mirror", gaps[0])
            self.assertIn(".gzkit/rules/tests.md", gaps[0])

    def test_creates_paths_exempt_missing_path_from_gap(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gaps = check_brief_path_validity(
                root,
                ["src/net_new.py"],
                creates_paths={"src/net_new.py"},
            )
            self.assertEqual(gaps, [])

    def test_vendor_mirror_not_exempt_via_creates_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gaps = check_brief_path_validity(
                root,
                [".claude/rules/tests.md"],
                creates_paths={".claude/rules/tests.md"},
            )
            self.assertEqual(len(gaps), 1)
            self.assertIn("vendor mirror", gaps[0])


class TestCheckBriefPathValidityForBrief(unittest.TestCase):
    """End-to-end: extract allowed + creates from brief and run validity."""

    def test_brief_with_drifted_path_surfaces_gap(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = root / "obpis" / "OBPI-test.md"
            _write(
                brief,
                "## Allowed Paths\n\n- `src/drifted.py`\n",
            )
            gaps = check_brief_path_validity_for_brief(root, brief)
            self.assertEqual(len(gaps), 1)
            self.assertIn("src/drifted.py", gaps[0])

    def test_brief_with_creates_marker_exempts_net_new(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = root / "obpis" / "OBPI-test.md"
            _write(
                brief,
                "## Allowed Paths\n\n"
                "- `src/net_new.py`\n\n"
                "## Creates these files\n\n"
                "- `src/net_new.py`\n",
            )
            gaps = check_brief_path_validity_for_brief(root, brief)
            self.assertEqual(gaps, [])

    def test_brief_without_allowed_section_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = root / "obpis" / "OBPI-test.md"
            _write(brief, "# Title\n\nFresh scaffold, no paths yet.\n")
            self.assertEqual(check_brief_path_validity_for_brief(root, brief), [])

    def test_existing_paths_with_no_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "src" / "foo.py", "x = 1\n")
            brief = root / "obpis" / "OBPI-test.md"
            _write(brief, "## Allowed Paths\n\n- `src/foo.py`\n")
            self.assertEqual(check_brief_path_validity_for_brief(root, brief), [])


if __name__ == "__main__":
    unittest.main()
