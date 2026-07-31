"""Tests for audit_persona_witness validator scope (GHI #741).

AGENTS.md § Persona declares "Every agent frame MUST include a Persona", but
no validator ever witnessed that MUST for ADRs. Five ADRs shipped carrying the
literal scaffold token ``{persona}``; four of them reached Validated/Completed,
i.e. they passed Gate 5 with an unfilled section.

The sibling section ``## Why foundation tier?`` has been mechanically enforced
since OBPI-0.0.35-04. This scope is its counterpart for ``## Persona``, with
two differences the tests below pin:

    * enumeration spans foundation AND pre-release ADRs (persona is universal;
      foundation-tier justification is not)
    * the placeholder detector recognises brace-token residue and
      comment-only bodies, neither of which the original detector caught

Tests assert semantics, not strings (Invariant 6f).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_persona_witness

_SUBSTANTIVE_PERSONA = (
    "## Persona\n\n"
    "**Active persona:** `main-session` — craftsperson, governance-aware. "
    "Treats an unwitnessed MUST as an absent MUST, and refuses to read a "
    "rendered scaffold token as authored content.\n\n"
    "## Intent\n\nSomething.\n"
)


def _write_adr(root: Path, adr_id: str, *, tier: str, body: str) -> Path:
    """Write a canonical ADR fixture under docs/design/adr/<tier>/<adr_id>/."""
    adr_dir = root / "docs" / "design" / "adr" / tier / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file = adr_dir / f"{adr_id}.md"
    adr_file.write_text(
        f"---\nid: {adr_id}\nstatus: Draft\nlane: lite\n---\n\n# {adr_id}: Test ADR\n\n{body}",
        encoding="utf-8",
    )
    return adr_file


def _write_grandfather(root: Path, ids: list[str]) -> None:
    """Write the persona grandfather manifest with *ids* exempted."""
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "persona_grandfather.json").write_text(
        json.dumps(
            {
                "_doc": "test fixture",
                "cutover": "2026-07-31T00:00:00+00:00",
                "added_under": "GHI-741",
                "grandfathered_adrs": ids,
            }
        ),
        encoding="utf-8",
    )


class TestPersonaWitnessAudit(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    # -------------------------------------------------------------------
    # The defect that motivated the scope: unsubstituted template residue
    # -------------------------------------------------------------------

    def test_brace_token_residue_fails(self) -> None:
        """An ADR whose Persona body is the unsubstituted `{persona}` token fails.

        Semantic: this is the exact shape five ADRs shipped with. `SafeDict.
        __missing__` renders an omitted template variable as its own literal
        token, so scaffold residue reads as prose to every string-based check.
        A body that is only a template token carries no authored content and
        must be a policy breach.
        """
        _write_adr(
            self.root,
            "ADR-0.1.0-brace-residue",
            tier="pre-release",
            body="## Persona\n\n{persona}\n\n## Intent\n\nSomething.\n",
        )

        errors = audit_persona_witness(self.root)

        self.assertGreater(len(errors), 0, "Unsubstituted {persona} token must be a breach")
        self.assertTrue(
            all(e.type == "persona_witness" for e in errors),
            "Error type must be persona_witness",
        )

    def test_comment_plus_brace_token_fails(self) -> None:
        """The full scaffold shape — HTML author-prompt comment plus token — fails.

        Semantic: this is the byte-exact body `gz plan create` emits today. The
        original `_is_placeholder_body` passed it because the body is non-empty,
        is not a STRICT_PLACEHOLDERS token, contains neither "paste" nor
        "one-sentence", and survives the `_[...]_` bracket strip. Stripping HTML
        comments before the substance test is what closes it.
        """
        scaffold = (
            "## Persona\n\n"
            "<!-- Describe the behavioral identity for agents working on this ADR.\n"
            "     Frame as values and craftsmanship standards, not expertise claims.\n"
            "     See .gzkit/personas/ for reusable persona definitions. -->\n\n"
            "{persona}\n\n"
            "## Intent\n\nSomething.\n"
        )
        _write_adr(self.root, "ADR-0.1.0-scaffold", tier="pre-release", body=scaffold)

        errors = audit_persona_witness(self.root)

        self.assertGreater(len(errors), 0, "Rendered scaffold body must be a breach")

    def test_comment_only_body_fails(self) -> None:
        """A Persona body consisting solely of an HTML author-prompt fails.

        Semantic: an author-prompt is an instruction to write content, never the
        content. Whether the token beside it rendered or not is irrelevant.
        """
        _write_adr(
            self.root,
            "ADR-0.1.0-comment-only",
            tier="pre-release",
            body="## Persona\n\n<!-- Describe the behavioral identity. -->\n\n## Intent\n\nX.\n",
        )

        errors = audit_persona_witness(self.root)

        self.assertGreater(len(errors), 0, "Comment-only body must be a breach")

    # -------------------------------------------------------------------
    # Section presence and substance
    # -------------------------------------------------------------------

    def test_substantive_persona_passes(self) -> None:
        """An ADR with an authored Persona section produces no errors."""
        _write_adr(
            self.root,
            "ADR-0.1.0-authored",
            tier="pre-release",
            body=_SUBSTANTIVE_PERSONA,
        )

        errors = audit_persona_witness(self.root)

        self.assertEqual(errors, [], "Authored persona must pass")

    def test_missing_section_fails(self) -> None:
        """An ADR with no ## Persona heading at all fails.

        Semantic: AGENTS.md § Persona makes the section mandatory. Absence is
        the same breach as an unfilled body — the MUST is unwitnessed either way.
        """
        _write_adr(
            self.root,
            "ADR-0.1.0-no-section",
            tier="pre-release",
            body="## Intent\n\nNo persona section here.\n",
        )

        errors = audit_persona_witness(self.root)

        self.assertGreater(len(errors), 0, "Missing Persona section must be a breach")

    # -------------------------------------------------------------------
    # Enumeration — persona is universal, unlike foundation-tier justification
    # -------------------------------------------------------------------

    def test_foundation_adrs_are_enumerated(self) -> None:
        """Foundation-tier ADRs are checked too, not only pre-release ones.

        Semantic: the Persona MUST is kind-independent. `kind_invariance` scopes
        itself to foundation/ by directory predicate because foundation-tier
        justification only applies there; persona applies to every ADR, so
        scoping this audit the same way would exempt half the corpus.
        """
        _write_adr(
            self.root,
            "ADR-0.0.99-foundation-no-persona",
            tier="foundation",
            body="## Intent\n\nNo persona.\n",
        )

        errors = audit_persona_witness(self.root)

        self.assertGreater(len(errors), 0, "Foundation ADR must be enumerated")

    def test_sidecar_is_not_enumerated(self) -> None:
        """A closeout-form sidecar beside the canonical ADR is not an ADR.

        Semantic: the canonical ADR file of a package is the one whose stem
        matches its parent directory name. Sidecars match the ADR-*.md glob but
        carry no persona obligation.
        """
        adr_id = "ADR-0.1.0-with-sidecar"
        _write_adr(self.root, adr_id, tier="pre-release", body=_SUBSTANTIVE_PERSONA)
        sidecar = self.root / "docs" / "design" / "adr" / "pre-release" / adr_id
        (sidecar / "ADR-CLOSEOUT-FORM.md").write_text(
            "# ADR Closeout Form\n\n## Attestation\n\nNo persona here.\n",
            encoding="utf-8",
        )

        errors = audit_persona_witness(self.root)

        self.assertEqual(errors, [], "Sidecar must not be enumerated")

    # -------------------------------------------------------------------
    # Grandfather roster (operator ruling 2026-07-31)
    # -------------------------------------------------------------------

    def test_grandfathered_adr_is_exempt(self) -> None:
        """An ADR listed in the grandfather manifest does not produce an error.

        Semantic: four ADRs passed Gate 5 carrying the token. Backfilling prose
        into attested Layer-1 canon would be retroactive authorship, so the
        operator ruled the existing population is booked in a committed,
        diff-visible roster instead — the same mechanism ADR-0.34.0 used to
        close the foundation kind over its existing population.
        """
        adr_id = "ADR-0.1.0-legacy"
        _write_adr(
            self.root,
            adr_id,
            tier="pre-release",
            body="## Persona\n\n{persona}\n\n## Intent\n\nX.\n",
        )
        _write_grandfather(self.root, [adr_id])

        errors = audit_persona_witness(self.root)

        self.assertEqual(errors, [], "Grandfathered ADR must be exempt")

    def test_grandfather_does_not_exempt_unlisted_adrs(self) -> None:
        """The roster exempts only its listed members.

        Semantic: this is what makes the exemption finite rather than a silent
        skip. A manifest that suppressed the whole scope would reproduce the
        hole it was authored to close.
        """
        _write_adr(
            self.root,
            "ADR-0.1.0-listed",
            tier="pre-release",
            body="## Persona\n\n{persona}\n\n## Intent\n\nX.\n",
        )
        unlisted = "ADR-0.1.1-unlisted"
        _write_adr(
            self.root,
            unlisted,
            tier="pre-release",
            body="## Persona\n\n{persona}\n\n## Intent\n\nX.\n",
        )
        _write_grandfather(self.root, ["ADR-0.1.0-listed"])

        errors = audit_persona_witness(self.root)

        self.assertEqual(len(errors), 1, "Only the unlisted ADR must fail")
        self.assertIn(unlisted, errors[0].artifact or "")

    def test_absent_manifest_exempts_nothing(self) -> None:
        """With no manifest on disk, every ADR is held to the gate.

        Semantic: fail-closed. `grandfathered_foundation_ids` returning an empty
        frozenset when its manifest is absent is precisely the behaviour GHI
        #740 flagged as an adopter footgun on the *refusal* side; on the
        *exemption* side the same default is correct — a missing roster must
        widen the gate's reach, never narrow it.
        """
        _write_adr(
            self.root,
            "ADR-0.1.0-no-manifest",
            tier="pre-release",
            body="## Persona\n\n{persona}\n\n## Intent\n\nX.\n",
        )

        errors = audit_persona_witness(self.root)

        self.assertGreater(len(errors), 0, "Absent manifest must exempt nothing")

    def test_no_adrs_returns_no_errors(self) -> None:
        """An empty ADR tree produces no errors."""
        self.assertEqual(audit_persona_witness(self.root), [])


if __name__ == "__main__":
    unittest.main()
