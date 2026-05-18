"""Drift test asserting zero self-close references in canon and vendor-mirror surfaces.

Asserts the deleted lite-lane self-close path (eliminated by ADR-0.0.36) has
zero remaining references in every surface an agent reads at runtime.

Allow-list: references inside docs/design/adr/foundation/ADR-0.0.36-*/
and docs/design/adr/foundation/ADR-0.0.36-*/obpis/OBPI-0.0.36-05-*
are preserved as historical narrative and are NOT in the scanned dirs
(.gzkit/skills/, .gzkit/rules/, .claude/skills/, etc.), so no in-scan
allow-list is needed.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.traceability import covers

REPO_ROOT = Path(__file__).resolve().parents[2]

# Directories an agent reads at runtime — all must be clean post-sweep.
_SCAN_DIRS = [
    ".gzkit/skills",
    ".gzkit/rules",
    ".claude/skills",
    ".claude/rules",
    ".github/skills",
    ".github/instructions",
    ".agents/skills",
]

# Deleted patterns: specific constructs that are remnants of the deprecated
# lite-lane self-close path eliminated by ADR-0.0.36. Patterns are precise —
# they target the deprecated constructs (attestation_type values, section
# headers, task names, and mode-detection snippets), NOT the compound word
# "self-close" as a bare term that might appear in explanatory context.
_DELETED_PATTERNS: list[str] = [
    "self-close-exception",  # deprecated attestation_type value
    "Self-closeable",  # deprecated matrix cell (capital-S)
    r"Exception Mode.*SELF.CLOSE",  # deprecated skill prose section header
    r"mode=exception",  # deprecated SVFR mode detection assignment
    "Record OBPI Evidence and Self-Close",  # deprecated exception task name
    r"Exception.*SVFR",  # deprecated SVFR mode reference
    r"attestation_type.*self.close",  # deprecated attestation_type with self-close value
]


def _find_offenders(pattern: str) -> list[str]:
    """Return rel-paths of scanned files matching *pattern* (regex, DOTALL)."""
    compiled = re.compile(pattern, re.IGNORECASE | re.DOTALL)
    offenders: list[str] = []
    for dir_rel in _SCAN_DIRS:
        scan_dir = REPO_ROOT / dir_rel
        if not scan_dir.exists():
            continue
        for path in scan_dir.rglob("*.md"):
            if ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if compiled.search(text):
                offenders.append(path.relative_to(REPO_ROOT).as_posix())
    return offenders


class TestSkillSelfCloseDrift(unittest.TestCase):
    """Assert the deleted self-close path has zero references in agent-readable surfaces."""

    @covers("REQ-0.0.36-05-05")
    def test_zero_self_close_references_in_canon_and_mirrors(self) -> None:
        """Every scanned surface must contain zero deleted self-close patterns.

        REQ-05-05 semantic: grep for the deleted patterns across .gzkit/skills/**,
        .gzkit/rules/**, .claude/skills/**, .claude/rules/**, .github/skills/**,
        .github/instructions/**, and .agents/skills/** returns zero matches
        outside an explicit allow-list (which is empty for the scanned dirs --
        ADR-0.0.36 and OBPI-0.0.36-05 narratives live under docs/, not in
        the agent-readable surfaces).
        """
        all_offenders: dict[str, list[str]] = {}
        for pattern in _DELETED_PATTERNS:
            hits = _find_offenders(pattern)
            if hits:
                all_offenders[pattern] = hits

        if all_offenders:
            lines = [
                "Deleted self-close patterns found in agent-readable surfaces:",
                "(These are remnants of the deprecated lite-lane self-close path "
                "eliminated by ADR-0.0.36 OBPI-05 sweep.)",
            ]
            for pattern, paths in all_offenders.items():
                lines.append(f"\n  Pattern: {pattern!r}")
                for p in paths:
                    lines.append(f"    {p}")
            self.fail("\n".join(lines))

    @covers("REQ-0.0.36-05-01")
    def test_canon_skill_files_have_no_self_close(self) -> None:
        """Canonical .gzkit/skills/** must be clean.

        REQ-05-01 semantic: every skill file under .gzkit/skills/**/SKILL.md
        containing a reference to 'self-clos', 'Self-closeable', 'self-close',
        'feature.*lite.*self' MUST have been edited to remove the reference.
        """
        patterns = [
            "self-close-exception",
            "Self-closeable",
            r"Exception Mode.*SELF.CLOSE",
            r"mode=exception",
            r"Exception.*SVFR",
        ]
        offenders: list[str] = []
        canon_skills = REPO_ROOT / ".gzkit" / "skills"
        if not canon_skills.exists():
            self.skipTest(".gzkit/skills not found")
        for path in canon_skills.rglob("SKILL.md"):
            if ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for pat in patterns:
                if re.search(pat, text, re.IGNORECASE | re.DOTALL):
                    rel = path.relative_to(REPO_ROOT).as_posix()
                    if rel not in offenders:
                        offenders.append(rel)
                    break

        self.assertFalse(
            offenders,
            "Canon skill files still contain deleted self-close references:\n"
            + "\n".join(f"  - {o}" for o in offenders),
        )

    @covers("REQ-0.0.36-05-02")
    def test_canon_rule_files_have_no_self_close(self) -> None:
        """Canonical .gzkit/rules/** must be clean.

        REQ-05-02 semantic: every rule file under .gzkit/rules/**/*.md
        containing the same self-close references MUST be edited identically.
        """
        patterns = ["self-close-exception", "Self-closeable", "self-closeable"]
        offenders: list[str] = []
        canon_rules = REPO_ROOT / ".gzkit" / "rules"
        if not canon_rules.exists():
            self.skipTest(".gzkit/rules not found")
        for path in canon_rules.rglob("*.md"):
            if ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for pat in patterns:
                if re.search(pat, text, re.IGNORECASE):
                    rel = path.relative_to(REPO_ROOT).as_posix()
                    if rel not in offenders:
                        offenders.append(rel)
                    break

        self.assertFalse(
            offenders,
            "Canon rule files still contain deleted self-close references:\n"
            + "\n".join(f"  - {o}" for o in offenders),
        )

    @covers("REQ-0.0.36-05-03")
    def test_edited_skills_have_bumped_version(self) -> None:
        """Every edited skill MUST have a bumped skill-version.

        REQ-05-03 semantic: every edited skill's frontmatter skill-version has
        been incremented per the version-discipline table in skill-surface-sync.md
        (governance rule/procedure change warrants a minor bump).
        """
        import re as _re

        # Skills known to have been edited in this sweep
        edited_skills = {
            ".gzkit/skills/gz-obpi-pipeline/SKILL.md": "6.17.0",
            ".gzkit/skills/gz-adr-closeout-ceremony/SKILL.md": "7.11.0",
            ".gzkit/skills/gz-obpi-lock/SKILL.md": "6.1.0",
        }
        for rel_path, expected_version in edited_skills.items():
            path = REPO_ROOT / rel_path
            if not path.exists():
                self.fail(f"Expected edited skill not found: {rel_path}")
            text = path.read_text(encoding="utf-8")
            # Extract YAML frontmatter (between first two ---)
            fm_match = _re.match(r"^---\n(.*?)\n---", text, _re.DOTALL)
            self.assertIsNotNone(fm_match, f"No frontmatter found in {rel_path}")
            fm_text = fm_match.group(1)  # type: ignore[union-attr]
            # skill-version may be at top-level or nested under metadata:
            sv_match = _re.search(r'skill-version[:\s]+"?([^"\n]+)"?', fm_text)
            self.assertIsNotNone(
                sv_match,
                f"skill-version not found in {rel_path}",
            )
            actual = sv_match.group(1).strip().strip('"')  # type: ignore[union-attr]
            self.assertEqual(
                actual,
                expected_version,
                f"Expected skill-version {expected_version!r} in {rel_path}, got {actual!r}",
            )

    @covers("REQ-0.0.36-05-04")
    def test_vendor_mirrors_match_canonical_post_sync(self) -> None:
        """Canonical and vendor mirror content must be consistent post-sync.

        REQ-05-04 semantic: after gz agent sync control-surfaces, each
        canon-mirror pair is consistent; zero divergent mirrors for the edited
        surfaces. The test checks that the skill-version in each vendor mirror
        matches its canonical value (byte-parity is governed by sync; the
        version marker is the human-verifiable signal).
        """
        import re as _re

        # Map canonical skill path → list of vendor mirror paths
        mirror_map = {
            ".gzkit/skills/gz-obpi-pipeline/SKILL.md": [
                ".claude/skills/gz-obpi-pipeline/SKILL.md",
                ".github/skills/gz-obpi-pipeline/SKILL.md",
                ".agents/skills/gz-obpi-pipeline/SKILL.md",
            ],
            ".gzkit/skills/gz-adr-closeout-ceremony/SKILL.md": [
                ".claude/skills/gz-adr-closeout-ceremony/SKILL.md",
                ".github/skills/gz-adr-closeout-ceremony/SKILL.md",
                ".agents/skills/gz-adr-closeout-ceremony/SKILL.md",
            ],
            ".gzkit/skills/gz-obpi-lock/SKILL.md": [
                ".claude/skills/gz-obpi-lock/SKILL.md",
                ".github/skills/gz-obpi-lock/SKILL.md",
                ".agents/skills/gz-obpi-lock/SKILL.md",
            ],
        }

        def _extract_skill_version(text: str) -> str | None:
            m = _re.search(r'skill-version[:\s]+"?([^"\n]+)"?', text)
            return m.group(1).strip().strip('"') if m else None

        for canon_rel, mirror_rels in mirror_map.items():
            canon_path = REPO_ROOT / canon_rel
            canon_version = _extract_skill_version(canon_path.read_text(encoding="utf-8"))
            for mirror_rel in mirror_rels:
                mirror_path = REPO_ROOT / mirror_rel
                with self.subTest(mirror=mirror_rel):
                    if not mirror_path.exists():
                        self.fail(f"Vendor mirror missing after sync: {mirror_rel}")
                    mirror_version = _extract_skill_version(mirror_path.read_text(encoding="utf-8"))
                    self.assertEqual(
                        canon_version,
                        mirror_version,
                        f"Vendor mirror {mirror_rel} skill-version {mirror_version!r} "
                        f"diverges from canonical {canon_version!r}",
                    )

    @covers("REQ-0.0.36-05-06")
    def test_pipeline_and_closeout_skills_cross_reference_dead_letter(self) -> None:
        """gz-obpi-pipeline and gz-adr-closeout-ceremony must cross-reference dead-letter.

        REQ-05-06 semantic: gz-obpi-pipeline/SKILL.md and gz-adr-closeout-ceremony/SKILL.md
        each cross-reference ghi-close's NEVER, EVER, EVER dead-letter doctrine where
        closure-flow prose discusses GHI lifecycle.
        """
        skills_requiring_crossref = [
            ".gzkit/skills/gz-obpi-pipeline/SKILL.md",
            ".gzkit/skills/gz-adr-closeout-ceremony/SKILL.md",
        ]
        # The cross-reference must cite the dead-letter doctrine from ghi-close.
        # Check for "dead-letter" language near GHI context in these skills.
        dead_letter_patterns = ["dead-letter", "dead_letter", "NEVER.*EVER.*dead"]
        for rel_path in skills_requiring_crossref:
            path = REPO_ROOT / rel_path
            if not path.exists():
                self.fail(f"Skill not found: {rel_path}")
            text = path.read_text(encoding="utf-8")
            found = any(re.search(p, text, re.IGNORECASE | re.DOTALL) for p in dead_letter_patterns)
            self.assertTrue(
                found,
                f"{rel_path} must cross-reference ghi-close dead-letter doctrine "
                f"(patterns: {dead_letter_patterns}) — REQ-0.0.36-05-06 not satisfied.",
            )
