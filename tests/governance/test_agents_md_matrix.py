"""Tests for AGENTS.md matrix collapse (ADR-0.0.36, OBPI-0.0.36-01).

Assertions derive from OBPI brief REQ-0.0.36-01-01..03, not from observed
post-collapse string shape.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.traceability import covers

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAgentsMdMatrixCollapse(unittest.TestCase):
    """Assert the AGENTS.md attestation matrix was collapsed to universal attestation."""

    @covers("REQ-0.0.36-01-01")
    def test_self_closeable_phrase_is_absent(self) -> None:
        """'Self-closeable after evidence' MUST NOT appear in AGENTS.md or any mirror.

        REQ-01 semantic: the deprecated matrix attestation phrase is structurally
        absent from the canon and all its mirrors. The check is case-sensitive on
        the capital-S form ("Self-closeable after evidence", "Self-closeable") as
        specified in the Acceptance Criteria — the lowercase "self-closeable" that
        appears in the security-sensitivity doctrine ("is never self-closeable") is
        a distinct, semantically-correct usage that is NOT the deprecated matrix path.
        """
        agents_md_paths = list(REPO_ROOT.rglob("AGENTS.md"))
        self.assertTrue(agents_md_paths, "No AGENTS.md files found under REPO_ROOT")

        # Deprecated phrases from the old matrix (capital-S, as in the matrix column)
        deprecated_phrases = ("Self-closeable after evidence", "Self-closeable after")

        offenders: list[str] = []
        for path in agents_md_paths:
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel.startswith(".git/"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if any(phrase in text for phrase in deprecated_phrases):
                offenders.append(rel)

        self.assertFalse(
            offenders,
            "AGENTS.md files still contain the deprecated matrix phrase "
            "'Self-closeable after evidence' (the old matrix attestation path):\n"
            + "\n".join(f"  - {o}" for o in offenders),
        )

    @covers("REQ-0.0.36-01-02")
    def test_universal_attestation_binding_rule_present(self) -> None:
        """AGENTS.md OBPI Acceptance Protocol must contain a universal-attestation binding rule.

        REQ-02 semantic: a rule asserting that brief-level human attestation is
        required for every OBPI completion, regardless of parent kind or lane,
        must be present and use MUST/ALWAYS/NEVER language. The assertion checks
        for the concept — not an exact string — so future rephrasing that
        preserves the binding semantics does not break this test.
        """
        agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        # Locate the OBPI Acceptance Protocol section
        self.assertIn(
            "OBPI Acceptance Protocol",
            agents_text,
            "AGENTS.md must contain an 'OBPI Acceptance Protocol' section",
        )

        # The universal binding must use strong MUST/ALWAYS/NEVER language
        # paired with "every OBPI" or "regardless of" to signal universality.
        universal_markers = [
            # Possible phrasings that satisfy REQ-02's semantic contract
            ("ALWAYS required", "every OBPI"),
            ("MUST NOT mark", "regardless"),
            ("universal", "ALWAYS"),
            ("universal", "every OBPI"),
            ("ALWAYS required", "regardless"),
        ]

        found = any(
            all(marker in agents_text for marker in combo) for combo in universal_markers
        )

        self.assertTrue(
            found,
            "AGENTS.md OBPI Acceptance Protocol lacks a universal-attestation binding rule "
            "with MUST/ALWAYS/NEVER language paired with 'every OBPI' or 'regardless of'. "
            "REQ-0.0.36-01-02 requires this rule to be explicit and unconditional.",
        )

    @covers("REQ-0.0.36-01-03")
    def test_lane_kind_axes_retained_for_gate_firing_scope(self) -> None:
        """AGENTS.md must retain lane/kind axes explicitly for gate-firing scope.

        REQ-03 semantic: the collapse narrows ONLY Gate 5 attestation. The
        lane and kind taxonomy must remain present and explicitly tied to
        gate-firing scope (Gate 3 docs, Gate 4 BDD) so a reader cannot
        mistake the matrix collapse for removal of the lane/kind taxonomy.
        """
        agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        # The lane/kind taxonomy must still be present
        taxonomy_markers = ("foundation", "feature", "lite", "heavy")
        for marker in taxonomy_markers:
            self.assertIn(
                marker,
                agents_text,
                f"AGENTS.md must retain lane/kind taxonomy term '{marker}' for gate-firing scope",
            )

        # Gate 3 or Gate 4 must be explicitly mentioned in relation to lane/kind
        gate_scope_present = "Gate 3" in agents_text or "Gate 4" in agents_text
        self.assertTrue(
            gate_scope_present,
            "AGENTS.md must explicitly mention Gate 3 and/or Gate 4 in relation to lane/kind "
            "axes to clarify that the collapse affects only Gate 5 attestation. "
            "REQ-0.0.36-01-03 requires the gate-firing scope to be retained.",
        )

        # The gate-firing scope must be tied to the axes
        # Look for language connecting gate scope to lane or kind
        gate_axis_markers = [
            ("gate-firing scope", "lane"),
            ("gate-firing scope", "kind"),
            ("Gate 3", "lane"),
            ("Gate 3", "foundation"),
            ("Gate 4", "lane"),
            ("Gate 4", "foundation"),
            ("Gate 3", "heavy"),
            ("Gate 4", "heavy"),
        ]
        gate_axis_found = any(
            all(marker in agents_text for marker in combo) for combo in gate_axis_markers
        )
        self.assertTrue(
            gate_axis_found,
            "AGENTS.md must connect Gate 3/Gate 4 scope explicitly to lane/kind axes. "
            "The collapse must not remove or obscure this connection.",
        )


    @covers("REQ-0.0.36-01-04")
    def test_amendment_cites_ghi_and_adr_inline(self) -> None:
        """AGENTS.md must cite GHI #342 and ADR-0.0.36 inline.

        REQ-04 semantic: future agents tracing the doctrine backward via grep
        must reach the source ADR and GHI directly from the AGENTS.md text —
        narrative-recall is the failure mode this requirement closes.
        """
        agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn(
            "GHI #342",
            agents_text,
            "AGENTS.md must cite GHI #342 inline in the universal attestation section",
        )
        self.assertIn(
            "ADR-0.0.36",
            agents_text,
            "AGENTS.md must cite ADR-0.0.36 inline so grep traces reach the source ADR",
        )

    @covers("REQ-0.0.36-01-05")
    def test_mirrors_reflect_amended_canon(self) -> None:
        """All **/AGENTS.md mirrors must reflect the universal attestation rule.

        REQ-05 semantic: after `gz agent sync control-surfaces`, every directory-level
        mirror carries the new universal-attestation section. A mirror still containing
        the old matrix heading would prove sync failed to propagate the change.
        """
        agents_md_paths = [
            p
            for p in REPO_ROOT.rglob("AGENTS.md")
            if not p.relative_to(REPO_ROOT).as_posix().startswith(".git/")
        ]
        self.assertTrue(agents_md_paths, "No AGENTS.md files found under REPO_ROOT")

        stale_mirrors: list[str] = []
        for path in agents_md_paths:
            rel = path.relative_to(REPO_ROOT).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            # Skip files that are not mirrors of the main AGENTS.md
            # (e.g. template with placeholders that hasn't had sync-time substitution)
            if "{project_name}" in text:
                continue
            # Stale mirror: still has the old matrix heading
            if "Lane & Kind & Sensitivity Attestation Matrix" in text:
                stale_mirrors.append(rel)

        self.assertFalse(
            stale_mirrors,
            "AGENTS.md mirrors still carry the old matrix heading "
            "(sync did not propagate the universal attestation rule):\n"
            + "\n".join(f"  - {m}" for m in stale_mirrors),
        )


if __name__ == "__main__":
    unittest.main()
