"""Doctrine retirement and coupled-surface closure (ADR-0.34.0 / OBPI-03).

Sealing the foundation kind mechanically is only half the movement. If the
authoring surfaces keep teaching ``foundation`` as a live choice, the taxonomy
tells an operator one thing and the gate tells them another — the parent ADR
names this as its first Negative consequence.

Two facts are asserted here:

* ADR-0.0.18 (which taught foundation-authoring) is FROZEN-HISTORIC — its
  guidance carries a superseded marker while the record itself stays on disk.
  Void as instruction, preserved as history.
* The coupled authoring surfaces no longer present ``foundation`` as a
  selectable kind for a new gzkit ADR.

These read repository canon rather than a temp fixture: the artifacts under
assertion ARE the deliverable, so a fixture copy would prove nothing.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.traceability import covers

_REPO_ROOT = Path(__file__).resolve().parents[1]

_ADR_0018 = (
    _REPO_ROOT
    / "docs"
    / "design"
    / "adr"
    / "foundation"
    / "ADR-0.0.18-adr-taxonomy-doctrine"
    / "ADR-0.0.18-adr-taxonomy-doctrine.md"
)
_GZ_DESIGN_SKILL = _REPO_ROOT / ".gzkit" / "skills" / "gz-design" / "SKILL.md"
_INVARIANCE_DOC = (
    _REPO_ROOT / "docs" / "user" / "concepts" / "foundation-feature-invariance-test.md"
)
_TAXONOMY_DOC = _REPO_ROOT / "docs" / "user" / "concepts" / "adr-taxonomy.md"

_SUNSET_ADR = "ADR-0.34.0"

# Phrases that assert the OPPOSITE of closure for gzkit. Token-presence checks
# cannot tell "foundation is closed for gzkit" from the same words arranged to
# mean the reverse, so closure polarity is guarded explicitly. This is a
# denylist and therefore not exhaustive by construction — see the REQ-kind
# caveat in the brief's Evidence: the durable proof channel for a doc-content
# claim is SUPPORT (structural validator), not a `@covers` grep.
_CONTRADICTION_PHRASES: tuple[str, ...] = (
    "foundation is an available kind",
    "choose foundation",
    "foundation remains available",
    "no longer operative",
    "foundation is still available",
    "remains an available kind",
)


def _assert_no_closure_contradiction(case: unittest.TestCase, text: str, where: str) -> None:
    """Fail if ``text`` affirmatively offers `foundation` for new gzkit ADRs."""
    lowered = text.lower()
    for phrase in _CONTRADICTION_PHRASES:
        case.assertNotIn(
            phrase,
            lowered,
            f"{where} contains {phrase!r}, which contradicts the closure it claims to declare",
        )


def _admonition_block(doc: Path, needle: str) -> str:
    """Return the mkdocs admonition block containing ``needle``, or ``""``.

    A block is the ``!!! <type>`` line plus its indented continuation, per the
    mkdocs admonition contract. Scoping assertions to the block — rather than
    to a single line or the whole page — is what keeps a closure-note check
    falsifiable: both pages discuss adopters elsewhere, so a page-wide
    substring would pass no matter what the note said.
    """
    lines = doc.read_text(encoding="utf-8").splitlines()
    for start, line in enumerate(lines):
        if not line.startswith("!!! "):
            continue
        end = start + 1
        while end < len(lines) and (not lines[end].strip() or lines[end].startswith("    ")):
            end += 1
        block = "\n".join(lines[start:end])
        if needle in block:
            return block
    return ""


_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _visible_lines(text: str) -> list[str]:
    """Return source lines with code fences and HTML comments neutralised.

    Both hide content from a reader while leaving it greppable. A heading or
    marker inside a fence renders as sample text, and one inside an HTML
    comment renders as nothing at all — an adversarial pass smuggled a decoy
    heading through a fence and a marker through a comment. Blanking them
    keeps line indices stable while removing what the reader never sees.
    """
    lines = _HTML_COMMENT_RE.sub("", text).splitlines()
    out: list[str] = []
    fenced = False
    for line in lines:
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return out


def _heading_annotation(lines: list[str], at: int) -> str:
    """Return the blockquote annotation contiguous with ``lines[at]``.

    Walks outward while lines are blockquote (``>``), tolerating at most ONE
    blank line on each side. A distance window is deliberately NOT used: on a
    short file any window degenerates to the whole document, so a marker
    dropped anywhere satisfies it (observed live — a disconnected marker slipped
    past a +/-16-line window). Unbounded blank runs fail the same way, which is
    why the gap is capped at one: a marker forty blank lines from its heading is
    not attached to it by any reader's measure.
    """

    def _walk(index: int, step: int) -> int:
        blanks = 0
        cursor = index
        while 0 <= cursor + step < len(lines):
            line = lines[cursor + step]
            if not line.strip():
                blanks += 1
                if blanks > 1:
                    break
            elif line.lstrip().startswith(">"):
                blanks = 0
            else:
                break
            cursor += step
        return cursor

    return "\n".join(lines[_walk(at, -1) : _walk(at, 1) + 1])


class TestAdr0018FrozenHistoric(unittest.TestCase):
    """ADR-0.0.18's choose-foundation guidance is retired, its record preserved."""

    @covers("REQ-0.34.0-03-03")
    def test_record_remains_on_disk(self) -> None:
        """The ADR-0.0.18 package is NOT deleted.

        Half of "frozen-historic" is the freezing; this is the other half.
        Retirement of doctrine must never destroy the record of why the
        doctrine existed — the parent ADR calls ADR-0.0.18 a museum piece,
        and a museum piece that has been thrown away is just a gap.
        """
        self.assertTrue(_ADR_0018.is_file(), f"{_ADR_0018} must remain on disk")

    @covers("REQ-0.34.0-03-03")
    def test_superseded_marker_is_seated_at_the_guidance(self) -> None:
        """The marker sits AT the guidance sections, not merely somewhere in the file.

        Seating is the whole requirement. A marker anywhere in a 170-line ADR
        satisfies a page-wide substring check while a reader who lands on
        `## Why foundation tier?` or `## Decision` — the two sections that
        actually teach foundation-authoring — sees live-looking instructions
        and follows them into a rejected `gz plan create`. Asserting adjacency
        is what makes this test fail for a mis-seated marker.
        """
        lines = _visible_lines(_ADR_0018.read_text(encoding="utf-8"))

        for heading in ("## Why foundation tier?", "## Decision"):
            occurrences = [i for i, line in enumerate(lines) if line.strip() == heading]
            self.assertTrue(occurrences, f"{heading} must still be present")

            # EVERY occurrence must be marked, not just the first. Checking
            # only `lines.index(...)` lets a marked decoy shadow a real,
            # unmarked section further down the file.
            for at in occurrences:
                with self.subTest(section=heading, line=at + 1):
                    annotation = _heading_annotation(lines, at)

                    self.assertIn(
                        "Superseded",
                        annotation,
                        f"a superseded marker must be seated at {heading} as a "
                        "blockquote annotation contiguous with the heading",
                    )
                    self.assertIn(
                        _SUNSET_ADR,
                        annotation,
                        f"the marker at {heading} must name the superseding ADR",
                    )

    @covers("REQ-0.34.0-03-03")
    def test_decision_text_is_preserved_not_redacted(self) -> None:
        """Retirement annotates; it never rewrites the historical Decision.

        The negative control on the marker: a "retirement" that deleted the
        doctrine body would satisfy a naive marker check while destroying the
        history the frozen-historic ruling exists to keep.
        """
        text = _ADR_0018.read_text(encoding="utf-8")

        self.assertIn("## Decision", text)
        self.assertIn("Land operator doctrine as a concept page", text)


class TestCoupledSurfaceClosure(unittest.TestCase):
    """No authoring surface offers `foundation` as a kind for a new ADR."""

    @covers("REQ-0.34.0-03-04")
    def test_gz_design_kind_question_enumerates_feature_and_pool_only(self) -> None:
        """Step 5's kind question offers feature/pool — foundation is not a choice.

        Asserted POSITIVELY, against the question's own enumeration. A bare
        "the old wording is absent" check passes vacuously when the bullet is
        missing, renamed, or replaced by contradictory text — so absence is
        not evidence. The enumeration is the operator-visible contract: it is
        the parenthetical they read before answering.
        """
        lines = _visible_lines(_GZ_DESIGN_SKILL.read_text(encoding="utf-8"))
        starts = [i for i, line in enumerate(lines) if "Confirm: kind" in line]

        self.assertEqual(len(starts), 1, "Step 5 must ask the kind question exactly once")

        # Take the WHOLE bullet, including its indented continuation lines.
        # Reading only the first line lets a contradiction ("...however,
        # choose foundation") sit one line below the enumeration and escape
        # the polarity guard entirely — observed live.
        at = starts[0]
        end = at + 1
        while end < len(lines) and (lines[end].startswith(("  ", "\t")) and lines[end].strip()):
            end += 1
        bullet = "\n".join(lines[at:end])
        first = lines[at]
        enumeration = first[first.index("(") + 1 : first.index(")")]

        self.assertNotIn(
            "foundation",
            enumeration.lower(),
            f"foundation must not be an offered kind; got ({enumeration})",
        )
        for kind in ("feature", "pool"):
            self.assertIn(kind, enumeration.lower(), f"{kind} must remain offered")
        self.assertIn(_SUNSET_ADR, bullet, "the question must cite the closing ADR")
        self.assertIn("CLOSED", bullet, "the question must state the kind is closed")
        _assert_no_closure_contradiction(self, bullet, "the gz-design kind question")

    @covers("REQ-0.34.0-03-04")
    def test_concept_pages_carry_a_scoped_closure_admonition(self) -> None:
        """Both concept pages declare the kind closed for gzkit, in a real note.

        Scoped to the admonition block rather than the page. A page-wide
        substring search for "closed" and the ADR id passes on prose that
        elsewhere still offers `foundation` as an available kind — the exact
        contradiction an adversarial pass demonstrated. Requiring a real
        admonition that names the kind, its closure, and the scope makes the
        assertion fail when the note is absent or gutted.
        """
        for doc in (_INVARIANCE_DOC, _TAXONOMY_DOC):
            with self.subTest(doc=doc.name):
                block = _admonition_block(doc, _SUNSET_ADR).lower()

                self.assertTrue(block, f"{doc.name} carries no {_SUNSET_ADR} admonition")
                self.assertIn("foundation", block, "the note must name the kind it closes")
                self.assertIn("closed", block, "the note must declare the kind closed")
                self.assertIn("gzkit", block, "the note must scope the closure to gzkit")
                _assert_no_closure_contradiction(self, block, f"{doc.name}'s closure note")

    @covers("REQ-0.34.0-03-04")
    def test_closure_notes_preserve_the_adopter_carve_out(self) -> None:
        """The closure is scoped to gzkit; adopters keep the open kind.

        The parent ADR ships the mechanism framework-wide but keeps the
        DECISION project-local — `gz init` scaffolds adopters OPEN. A closure
        note that read as universal would mis-teach every adopter.

        Scoped to the closure note's own admonition block, not the whole page:
        both pages already discuss adopters elsewhere, so a document-wide
        substring check would pass no matter what the note said.
        """
        for doc in (_INVARIANCE_DOC, _TAXONOMY_DOC):
            with self.subTest(doc=doc.name):
                block = _admonition_block(doc, _SUNSET_ADR)

                self.assertTrue(block, f"{doc.name} carries no {_SUNSET_ADR} closure admonition")
                self.assertIn(
                    "adopter",
                    block.lower(),
                    f"{doc.name}'s closure note must scope the closure to gzkit "
                    "and name the adopter carve-out in the note itself",
                )


if __name__ == "__main__":
    unittest.main()
