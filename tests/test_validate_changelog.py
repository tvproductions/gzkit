"""Tests for the hermetic changelog structural validator (GHI #685).

The validator asserts CHANGELOG.md conforms to
``.gzkit/templates/changelog.md``: SemVer/ISO version headers, the closed
category set, and a ``GHI #N`` citation on every entry (Release highlights
exempt). It is offline/deterministic — the closed-GHI *coverage* half lives in
``gz-patch-release``, not here (hermeticity split, ``.gzkit/rules/changelog-release-notes.md``).
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.validate_pkg.changelog import validate_changelog

_CONFORMING = """# Changelog

Intro prose that is ignored before the first version block.

## [Unreleased]

### Added

- A new capability (GHI #685)

## v0.33.0 (2026-07-12)

### Fixed

- Something that used to break (GHI #684)
"""


def _root(content: str) -> Path:
    d = Path(tempfile.mkdtemp())
    (d / "CHANGELOG.md").write_text(content, encoding="utf-8")
    return d


class TestValidateChangelog(unittest.TestCase):
    def test_conforming_changelog_has_no_errors(self) -> None:
        self.assertEqual(validate_changelog(_root(_CONFORMING)), [])

    def test_missing_file_is_single_error(self) -> None:
        errors = validate_changelog(Path(tempfile.mkdtemp()))
        self.assertEqual(len(errors), 1)
        self.assertIn("CHANGELOG.md", errors[0].artifact)

    def test_non_semver_or_non_iso_version_header_is_error(self) -> None:
        bad = "# Changelog\n\n## version 1 (July)\n\n### Added\n\n- x (GHI #1)\n"
        errors = validate_changelog(_root(bad))
        self.assertTrue(any(e.field == "version" for e in errors))

    def test_entry_missing_ghi_citation_is_error(self) -> None:
        bad = "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- no citation here\n"
        errors = validate_changelog(_root(bad))
        self.assertTrue(any(e.field == "ghi-citation" for e in errors))

    def test_disallowed_category_is_error(self) -> None:
        bad = "# Changelog\n\n## [Unreleased]\n\n### Frobnicated\n\n- x (GHI #1)\n"
        errors = validate_changelog(_root(bad))
        self.assertTrue(any(e.field == "category" for e in errors))

    def test_release_highlights_bullets_exempt_from_citation(self) -> None:
        ok = (
            "# Changelog\n\n## v1.2.3 (2026-01-01)\n\n### Release highlights\n\n"
            "- a plain summary sentence\n\n### Added\n\n- thing (GHI #1)\n"
        )
        self.assertEqual(validate_changelog(_root(ok)), [])


if __name__ == "__main__":
    unittest.main()
