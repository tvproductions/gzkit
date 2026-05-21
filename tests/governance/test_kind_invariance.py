"""Tests for audit_kind_invariance validator scope (OBPI-0.0.35-04).

Covers:
    REQ-0.0.35-04-02 — Foundation ADR with substantive section passes
    REQ-0.0.35-04-03 — Foundation ADR missing section fails
    REQ-0.0.35-04-04 — Foundation ADR with placeholder-only body fails
    REQ-0.0.35-04-05 — Feature ADR is not enumerated

All tests use ``tempfile.TemporaryDirectory`` for sandbox isolation; never
write to the live repo root.
Tests assert semantics, not strings (Invariant 6f).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_kind_invariance
from gzkit.traceability import covers


def _write_foundation_adr(root: Path, adr_id: str, *, body: str) -> Path:
    """Write a foundation-kind ADR fixture under docs/design/adr/foundation/."""
    adr_dir = root / "docs" / "design" / "adr" / "foundation" / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file = adr_dir / f"{adr_id}.md"
    adr_file.write_text(
        f"---\nid: {adr_id}\nstatus: Draft\nkind: foundation\nlane: lite\nsemver: 0.0.99\n---\n\n"
        f"# {adr_id}: Test ADR\n\n{body}",
        encoding="utf-8",
    )
    return adr_file


def _write_feature_adr(root: Path, adr_id: str, *, body: str) -> Path:
    """Write a feature-kind ADR fixture under docs/design/adr/pre-release/."""
    adr_dir = root / "docs" / "design" / "adr" / "pre-release" / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file = adr_dir / f"{adr_id}.md"
    adr_file.write_text(
        f"---\nid: {adr_id}\nstatus: Draft\nkind: feature\nlane: lite\nsemver: 0.1.0\n---\n\n"
        f"# {adr_id}: Test Feature ADR\n\n{body}",
        encoding="utf-8",
    )
    return adr_file


_SUBSTANTIVE_BODY = (
    "## Why foundation tier?\n\n"
    "Without this ADR, the project would not be the project because "
    "it defines the port that every governance surface reads against — "
    "removing it collapses kind classification to per-author vibe.\n\n"
    "## Other Section\n\nFoo.\n"
)


class TestKindInvarianceAudit(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    # -------------------------------------------------------------------
    # Cycle 1 — Enumeration: only foundation ADRs under foundation/ dir
    # -------------------------------------------------------------------

    @covers("REQ-0.0.35-04-05")
    def test_selects_only_foundation_adrs(self) -> None:
        """Feature ADR without the section does not produce errors.

        Semantic: the validator enumerates only canonical ADR files under
        docs/design/adr/foundation/. A feature ADR in pre-release/ with no
        section must not appear in the error list.
        """
        # Foundation ADR passes (has the section)
        _write_foundation_adr(self.root, "ADR-0.0.99-test", body=_SUBSTANTIVE_BODY)
        # Feature ADR without the section — must NOT be enumerated
        _write_feature_adr(
            self.root,
            "ADR-0.1.0-test-feature",
            body="## Intent\n\nSome intent.\n",
        )

        errors = audit_kind_invariance(self.root)

        feature_errors = [e for e in errors if "ADR-0.1.0-test-feature" in (e.artifact or "")]
        self.assertEqual(
            feature_errors,
            [],
            "Feature ADR must not be enumerated by kind-invariance validator",
        )

    @covers("REQ-0.0.35-04-03")
    def test_no_frontmatter_foundation_adr_is_enumerated(self) -> None:
        """Foundation-dir ADR with no frontmatter block is still checked (GHI #483).

        Semantic: directory placement is the foundation predicate. An ADR that
        predates the mechanical kind: frontmatter mandate (ADR-0.0.17) carries
        no frontmatter at all; the prior frontmatter-keyed filter silently
        exempted it from the ## Why foundation tier? section requirement. It
        must now be enumerated and flagged like any other foundation ADR.
        """
        adr_id = "ADR-0.0.97-legacy-no-frontmatter"
        adr_dir = self.root / "docs" / "design" / "adr" / "foundation" / adr_id
        adr_dir.mkdir(parents=True, exist_ok=True)
        adr_file = adr_dir / f"{adr_id}.md"
        adr_file.write_text(
            f"# {adr_id}: Legacy ADR\n\n## Intent\n\nNo frontmatter, no section.\n",
            encoding="utf-8",
        )

        errors = audit_kind_invariance(self.root)

        legacy_errors = [e for e in errors if adr_id in (e.artifact or "")]
        self.assertGreater(
            len(legacy_errors),
            0,
            "No-frontmatter foundation-dir ADR must be enumerated and flagged",
        )
        self.assertTrue(
            all(e.type == "kind_invariance" for e in legacy_errors),
            "Error type must be kind_invariance",
        )

    @covers("REQ-0.0.35-04-05")
    def test_closeout_form_sidecar_not_enumerated(self) -> None:
        """ADR-CLOSEOUT-FORM.md sidecar is not the canonical ADR file (GHI #483).

        Semantic: the canonical ADR file of a package is the one whose stem
        matches its parent directory name. Sidecar files (closeout forms,
        audit forms) living beside it in the same directory are not foundation
        ADRs and must not be enumerated even though they match the ADR-*.md
        glob and lack the section.
        """
        adr_id = "ADR-0.0.96-with-sidecar"
        adr_dir = self.root / "docs" / "design" / "adr" / "foundation" / adr_id
        adr_dir.mkdir(parents=True, exist_ok=True)
        (adr_dir / f"{adr_id}.md").write_text(
            f"---\nid: {adr_id}\nstatus: Draft\nkind: foundation\nlane: lite\nsemver: 0.0.96\n"
            f"---\n\n# {adr_id}: Test ADR\n\n{_SUBSTANTIVE_BODY}",
            encoding="utf-8",
        )
        (adr_dir / "ADR-CLOSEOUT-FORM.md").write_text(
            "# ADR Closeout Form\n\n## Attestation\n\nNo section here.\n",
            encoding="utf-8",
        )

        errors = audit_kind_invariance(self.root)

        sidecar_errors = [e for e in errors if "ADR-CLOSEOUT-FORM" in (e.artifact or "")]
        self.assertEqual(
            sidecar_errors,
            [],
            "Closeout-form sidecar must not be enumerated as a foundation ADR",
        )

    # -------------------------------------------------------------------
    # Cycle 2 — Section-presence check
    # -------------------------------------------------------------------

    @covers("REQ-0.0.35-04-03")
    def test_foundation_adr_missing_section_fails(self) -> None:
        """Foundation ADR without ## Why foundation tier? section produces a validation error.

        Semantic: the presence of a non-empty, non-placeholder section is
        mandatory for every kind: foundation ADR. Its absence is a policy breach.
        """
        _write_foundation_adr(
            self.root,
            "ADR-0.0.99-no-section",
            body="## Intent\n\nNo Why-foundation-tier section here.\n",
        )

        errors = audit_kind_invariance(self.root)

        self.assertGreater(len(errors), 0, "Missing section must produce at least one error")
        self.assertTrue(
            any(e.type == "kind_invariance" for e in errors),
            "Error type must be kind_invariance",
        )

    @covers("REQ-0.0.35-04-02")
    def test_foundation_adr_with_substantive_section_passes(self) -> None:
        """Foundation ADR with a substantive ## Why foundation tier? section produces no errors.

        Semantic: a non-empty, non-placeholder section body satisfies the check.
        """
        _write_foundation_adr(
            self.root,
            "ADR-0.0.99-with-section",
            body=_SUBSTANTIVE_BODY,
        )

        errors = audit_kind_invariance(self.root)

        self.assertEqual(
            errors,
            [],
            "Foundation ADR with substantive section must pass with no errors",
        )

    # -------------------------------------------------------------------
    # Cycle 3 — Substantive content check (placeholder detection)
    # -------------------------------------------------------------------

    @covers("REQ-0.0.35-04-04")
    def test_placeholder_body_fails(self) -> None:
        """Foundation ADR with section heading but placeholder-only body fails.

        Semantic: STRICT_PLACEHOLDERS tokens in the body are not substantive.
        The validator must detect them and report a policy breach.
        """
        _write_foundation_adr(
            self.root,
            "ADR-0.0.99-placeholder",
            body="## Why foundation tier?\n\nTBD\n\n## Other\n\nFoo.\n",
        )

        errors = audit_kind_invariance(self.root)

        self.assertGreater(
            len(errors),
            0,
            "Placeholder-only section body must produce at least one error",
        )
        self.assertTrue(
            any(e.type == "kind_invariance" for e in errors),
            "Error type must be kind_invariance for placeholder body",
        )

    @covers("REQ-0.0.35-04-04")
    def test_author_prompt_body_fails(self) -> None:
        """Foundation ADR with OBPI-03 template author-prompts unfilled fails.

        Semantic: _[Author: ...]_ style bracketed prompts are not substantive.
        An unfilled author-prompt with no real answer must fail the check.
        """
        prompt_body = (
            "## Why foundation tier?\n\n"
            "_[Author: Answer the invariance test in one sentence: "
            "without this ADR, the project would not be the project because ...]_\n"
            "_[Port-vs-adapter framing: ...]_\n\n"
            "## Other\n\nFoo.\n"
        )
        _write_foundation_adr(
            self.root,
            "ADR-0.0.99-author-prompt",
            body=prompt_body,
        )

        errors = audit_kind_invariance(self.root)

        self.assertGreater(
            len(errors),
            0,
            "Unfilled author-prompt body must produce at least one error",
        )
        self.assertTrue(
            any(e.type == "kind_invariance" for e in errors),
            "Error type must be kind_invariance for unfilled author-prompt",
        )

    @covers("REQ-0.0.35-04-04")
    def test_empty_section_body_fails(self) -> None:
        """Foundation ADR with section heading followed immediately by next heading fails.

        Semantic: an empty section body (no text between headings) is not substantive.
        """
        _write_foundation_adr(
            self.root,
            "ADR-0.0.99-empty-body",
            body="## Why foundation tier?\n\n## Next Section\n\nSome content.\n",
        )

        errors = audit_kind_invariance(self.root)

        self.assertGreater(
            len(errors),
            0,
            "Empty section body must produce at least one error",
        )

    @covers("REQ-0.0.35-04-02")
    def test_multiple_foundation_adrs_all_pass(self) -> None:
        """Multiple foundation ADRs all with substantive sections produce no errors."""
        _write_foundation_adr(
            self.root,
            "ADR-0.0.91-first",
            body=_SUBSTANTIVE_BODY,
        )
        _write_foundation_adr(
            self.root,
            "ADR-0.0.92-second",
            body=(
                "## Why foundation tier?\n\n"
                "Without this ADR the project's identity collapses — "
                "it defines the port for agent-contract fidelity.\n\n"
            ),
        )

        errors = audit_kind_invariance(self.root)

        self.assertEqual(errors, [], "All foundation ADRs with substantive sections must pass")

    @covers("REQ-0.0.35-04-03")
    def test_mixed_foundation_adrs_partial_fail(self) -> None:
        """When one foundation ADR fails the check, an error is reported for it only.

        Semantic: enumeration is complete — every foundation ADR is checked.
        Passing ADRs do not suppress errors for failing ADRs.
        """
        _write_foundation_adr(
            self.root,
            "ADR-0.0.91-passes",
            body=_SUBSTANTIVE_BODY,
        )
        failing_id = "ADR-0.0.92-fails"
        _write_foundation_adr(
            self.root,
            failing_id,
            body="## Intent\n\nNo section here.\n",
        )

        errors = audit_kind_invariance(self.root)

        failing_errors = [e for e in errors if failing_id in (e.artifact or "")]
        passing_errors = [e for e in errors if "ADR-0.0.91-passes" in (e.artifact or "")]
        self.assertGreater(len(failing_errors), 0, "Failing ADR must produce an error")
        self.assertEqual(passing_errors, [], "Passing ADR must not produce errors")

    @covers("REQ-0.0.35-04-02")
    def test_no_foundation_adrs_returns_no_errors(self) -> None:
        """When the foundation/ directory has no foundation-kind ADRs, result is empty list."""
        errors = audit_kind_invariance(self.root)
        self.assertEqual(errors, [], "Empty foundation dir must produce no errors")


if __name__ == "__main__":
    unittest.main()
