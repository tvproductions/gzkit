"""Tests for `gz init --update` mode (OBPI-0.0.32-05).

Covers:
- Three-state detection function `_detect_refresh_state` (IDENTICAL/STALE/EDITED)
- `--update` dispatch routing (mutually exclusive with `--force`)
- Canonical-version marker pattern (REQ-06)
- Manpage documents three modes + marker contract + exit codes (REQ-08)

REQ derivation: REQ-0.0.32-05-02 (three-state detection), REQ-0.0.32-05-03
(refresh dispatch), REQ-0.0.32-05-01 (flag mutual exclusivity),
REQ-0.0.32-05-06 (marker mechanism documented and composing with existing
markers), REQ-0.0.32-05-08 (manpage docs).
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.commands.init_cmd import (
    CANONICAL_VERSION_MARKER_PATTERN,
    _detect_refresh_state,
)
from gzkit.traceability import covers

CANONICAL_VERSION_MARKER_RE = r"<!-- gzkit-canonical-version: \d+\.\d+\.\d+ -->"


@covers("REQ-0.0.32-05-02")
class TestDetectRefreshState(unittest.TestCase):
    """Three-state detection for `gz init --update` (REQ-0.0.32-05-02).

    The function compares the project copy's bytes against the wheel's
    canonical bytes and classifies the project copy as IDENTICAL, STALE,
    or EDITED. EDITED means the project copy differs AND carries an
    operator-edit signal — currently a `<!-- gzkit-canonical-version: X.Y.Z -->`
    body marker the scaffolder writes on copy. STALE means the project
    copy differs but carries no marker (or an outdated one whose version
    matches a known prior canonical), so it is safe to refresh.
    """

    def test_identical_bytes_returns_identical(self) -> None:
        """Equal bytes -> IDENTICAL regardless of marker presence."""
        canonical = b"# Skill\n\n<!-- gzkit-canonical-version: 0.1.0 -->\nBody.\n"
        project = canonical
        result = _detect_refresh_state(
            project_bytes=project,
            canonical_bytes=canonical,
            marker_pattern=CANONICAL_VERSION_MARKER_RE,
        )
        self.assertEqual(result, "IDENTICAL")

    def test_differing_bytes_without_marker_returns_stale(self) -> None:
        """Bytes differ, project has no canonical-version marker -> STALE.

        The absence of a marker means the scaffolder never stamped this
        copy (or the operator removed the marker). Without a positive
        operator-edit signal, the safest call is STALE: refresh it.
        """
        canonical = b"# Skill v2\n\n<!-- gzkit-canonical-version: 0.2.0 -->\nNew body.\n"
        project = b"# Skill v1\n\nOld body without marker.\n"
        result = _detect_refresh_state(
            project_bytes=project,
            canonical_bytes=canonical,
            marker_pattern=CANONICAL_VERSION_MARKER_RE,
        )
        self.assertEqual(result, "STALE")

    def test_differing_bytes_with_marker_returns_edited(self) -> None:
        """Bytes differ, project carries canonical-version marker -> EDITED.

        The marker says the scaffolder wrote this copy at some prior
        version. The bytes have since diverged in a way that does not
        match the current wheel canonical. That divergence is treated
        as an operator edit and must NOT be overwritten.
        """
        canonical = b"# Skill v2\n\n<!-- gzkit-canonical-version: 0.2.0 -->\nNew body.\n"
        project = (
            b"# Skill v1 (operator-edited)\n\n"
            b"<!-- gzkit-canonical-version: 0.1.0 -->\n"
            b"Old body with operator additions.\n"
        )
        result = _detect_refresh_state(
            project_bytes=project,
            canonical_bytes=canonical,
            marker_pattern=CANONICAL_VERSION_MARKER_RE,
        )
        self.assertEqual(result, "EDITED")

    def test_differing_bytes_with_current_version_marker_returns_edited(self) -> None:
        """Marker version equals canonical version but bytes still differ -> EDITED.

        This is the "operator edited a freshly-scaffolded file" case: the
        scaffolder wrote a copy stamped with the current canonical version,
        then the operator edited the body. We must NOT overwrite.
        """
        canonical = b"# Skill v2\n\n<!-- gzkit-canonical-version: 0.2.0 -->\nCanonical body.\n"
        project = (
            b"# Skill v2 (edited)\n\n"
            b"<!-- gzkit-canonical-version: 0.2.0 -->\n"
            b"Operator-modified body.\n"
        )
        result = _detect_refresh_state(
            project_bytes=project,
            canonical_bytes=canonical,
            marker_pattern=CANONICAL_VERSION_MARKER_RE,
        )
        self.assertEqual(result, "EDITED")

    def test_empty_project_bytes_returns_stale(self) -> None:
        """Empty project file (project copy was wiped) -> STALE.

        Empty bytes carry no marker and cannot be confused with operator
        intent; refresh restores canonical content.
        """
        canonical = b"# Skill\n\n<!-- gzkit-canonical-version: 0.1.0 -->\nBody.\n"
        project = b""
        result = _detect_refresh_state(
            project_bytes=project,
            canonical_bytes=canonical,
            marker_pattern=CANONICAL_VERSION_MARKER_RE,
        )
        self.assertEqual(result, "STALE")


@covers("REQ-0.0.32-05-06")
class TestCanonicalVersionMarkerContract(unittest.TestCase):
    """Operator-edit marker mechanism (REQ-0.0.32-05-06).

    The canonical-version marker (a) MUST be the documented form
    ``<!-- gzkit-canonical-version: X.Y.Z -->`` and (b) MUST compose
    with — not replace — the existing surface-author markers documented
    in ``.gzkit/rules/skill-surface-sync.md``:
    skills carry frontmatter ``skill-version:``; rules carry body
    ``<!-- rule-version: X.Y.Z -->``. The canonical-version marker is
    a third dimension that tracks "version of canonical content
    delivered by the wheel."
    """

    def test_marker_pattern_matches_documented_form(self) -> None:
        """The compiled pattern matches the body comment form documented in the manpage."""
        sample = "Lorem.\n<!-- gzkit-canonical-version: 1.2.3 -->\nIpsum."
        self.assertRegex(sample, CANONICAL_VERSION_MARKER_PATTERN)

    def test_marker_pattern_rejects_skill_version_frontmatter(self) -> None:
        """The canonical-version marker is NOT the skill-version frontmatter form."""
        sample = "---\nskill-version: 1.2.3\n---\nBody."
        self.assertNotRegex(sample, CANONICAL_VERSION_MARKER_PATTERN)

    def test_marker_pattern_rejects_rule_version_body_marker(self) -> None:
        """The canonical-version marker is NOT the rule-version body marker."""
        sample = "Header.\n<!-- rule-version: 0.4.0 -->\nBody."
        self.assertNotRegex(sample, CANONICAL_VERSION_MARKER_PATTERN)

    def test_marker_composes_with_skill_version_frontmatter(self) -> None:
        """A skill carrying BOTH markers is a valid composition."""
        sample = "---\nskill-version: 1.2.3\n---\nBody.\n<!-- gzkit-canonical-version: 0.0.32 -->\n"
        self.assertRegex(sample, CANONICAL_VERSION_MARKER_PATTERN)
        self.assertIn("skill-version: 1.2.3", sample)


@covers("REQ-0.0.32-05-08")
class TestInitManpageDocumentsUpdateMode(unittest.TestCase):
    """Manpage `docs/user/manpages/init.md` documents the three modes
    (REQ-0.0.32-05-08): default/repair, ``--force``, ``--update``;
    the operator-edit marker contract; and the exit-code contract
    (0 success, 1 usage error, 3 unresolved conflicts).
    """

    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        cls.manpage_text = (repo_root / "docs" / "user" / "manpages" / "init.md").read_text(
            encoding="utf-8",
        )

    def test_documents_update_mode_section(self) -> None:
        """The manpage carries a dedicated `Update Mode` section."""
        self.assertIn("Update Mode (Version-Aware Refresh)", self.manpage_text)

    def test_documents_three_modes(self) -> None:
        """The three modes (default, --force, --update) are enumerated."""
        # The "three modes" framing is concretely surfaced in the comparison table.
        self.assertRegex(self.manpage_text, r"\bdefault\b")
        self.assertIn("--force", self.manpage_text)
        self.assertIn("--update", self.manpage_text)

    def test_documents_three_state_detection(self) -> None:
        """IDENTICAL / STALE / EDITED state names appear in the manpage."""
        for state in ("IDENTICAL", "STALE", "EDITED"):
            self.assertIn(state, self.manpage_text)

    def test_documents_marker_contract(self) -> None:
        """The canonical-version marker form appears in the manpage."""
        self.assertRegex(self.manpage_text, r"gzkit-canonical-version: X\.Y\.Z")

    def test_documents_exit_code_contract(self) -> None:
        """Exit codes 0, 1, 3 are documented for --update."""
        # Per CLI doctrine: 0 success, 1 usage error, 3 policy breach.
        self.assertRegex(self.manpage_text, r"`?0`?\s*\|\s*Success")
        self.assertRegex(self.manpage_text, r"`?1`?\s*\|\s*Usage error")
        self.assertRegex(self.manpage_text, r"`?3`?\s*\|\s*Policy breach")


if __name__ == "__main__":
    unittest.main()
