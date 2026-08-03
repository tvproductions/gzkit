"""Ingress matrix for the shared tri-state frontmatter reader (GHI #736).

Five rounds of adversarial validation against OBPI-0.34.0-05 found a new bypass
in this family each round. The matrix below is the standing fence: BOM
positions, Unicode line separators, BOM-less UTF-16/32, CRLF, and the HR-first
pool document that a naive normalization turned INTO frontmatter.

The discriminating assertion throughout is `state`, never truthiness. A test
that only asks "did I get fields back" collapses `absent` and `malformed` into
the single permissive answer this module exists to split apart.
"""

import unittest

from gzkit.frontmatter import (
    SPLIT_DIVERGENT_SEPARATORS,
    read_frontmatter,
    read_frontmatter_bytes,
)

_CANONICAL = "---\nid: ADR-0.0.99-probe\nkind: foundation\nstatus: Draft\n---\n\n# body\n"


class ValidBlocks(unittest.TestCase):
    """Shapes that are genuinely readable must stay readable."""

    def test_canonical_block_parses(self) -> None:
        read = read_frontmatter(_CANONICAL)
        self.assertEqual(read.state, "valid")
        self.assertEqual(read.fields["kind"], "foundation")
        self.assertEqual(read.fields["id"], "ADR-0.0.99-probe")
        self.assertTrue(read.is_readable)

    def test_leading_bom_is_normalized_not_refused(self) -> None:
        """GHI #735's case: a BOM is noise to strip, not damage to refuse."""
        read = read_frontmatter("﻿" + _CANONICAL)
        self.assertEqual(read.state, "valid")
        self.assertEqual(read.fields["kind"], "foundation")

    def test_bom_appended_to_opening_marker_is_normalized(self) -> None:
        """`utf-8-sig` strips only a LEADING BOM; one on the marker hides the block."""
        read = read_frontmatter("---﻿\nkind: foundation\n---\n")
        self.assertEqual(read.state, "valid")
        self.assertEqual(read.fields["kind"], "foundation")

    def test_crlf_line_endings_parse(self) -> None:
        read = read_frontmatter("---\r\nkind: feature\r\nstatus: Draft\r\n---\r\n\r\n# body\r\n")
        self.assertEqual(read.state, "valid")
        self.assertEqual(read.fields["kind"], "feature")

    def test_quoted_values_are_unwrapped(self) -> None:
        read = read_frontmatter('---\nid: "ADR-0.0.99-probe"\n---\n')
        self.assertEqual(read.fields["id"], "ADR-0.0.99-probe")

    def test_body_content_after_the_closing_marker_is_not_parsed_as_fields(self) -> None:
        """Only the block is the block; `key: value` prose below it is body."""
        read = read_frontmatter("---\nkind: feature\n---\n\nnot_a_field: leaked\n")
        self.assertEqual(read.state, "valid")
        self.assertNotIn("not_a_field", read.fields)


class AbsentIsDistinctFromMalformed(unittest.TestCase):
    """`absent` means "this artifact has nothing to say", and must stay narrow."""

    def test_plain_markdown_is_absent(self) -> None:
        read = read_frontmatter("# ADR-0.1.0: an ADR that predates the frontmatter mandate\n")
        self.assertEqual(read.state, "absent")
        self.assertEqual(read.fields, {})
        self.assertFalse(read.is_readable)

    def test_horizontal_rule_after_blank_lines_is_absent_not_frontmatter(self) -> None:
        """The reverted round-5 regression, now a permanent fence.

        `lstrip()`-ing before marker detection made this parse as a block.
        Normalization that CREATES frontmatter is worse than the gap it closes.
        """
        read = read_frontmatter("\n\n---\n\nSome prose after a thematic break.\n")
        self.assertEqual(read.state, "absent")

    def test_marker_not_alone_on_its_line_is_absent(self) -> None:
        read = read_frontmatter("---not-a-marker\nkind: foundation\n")
        self.assertEqual(read.state, "absent")

    def test_empty_content_is_absent(self) -> None:
        self.assertEqual(read_frontmatter("").state, "absent")


class MalformedIsRefusedNotReadAsAbsent(unittest.TestCase):
    """The core of GHI #736: unreadable input must never answer "nothing here"."""

    def test_every_split_divergent_separator_is_refused(self) -> None:
        """Table-driven over the full set, so a new member cannot ship untested."""
        for sep in SPLIT_DIVERGENT_SEPARATORS:
            with self.subTest(codepoint=f"U+{ord(sep):04X}"):
                read = read_frontmatter(sep + _CANONICAL)
                self.assertEqual(
                    read.state,
                    "malformed",
                    msg=(
                        f"U+{ord(sep):04X} before a canonical block must be "
                        "refused, not read as absent"
                    ),
                )
                self.assertIsNotNone(read.reason)
                self.assertIn(f"U+{ord(sep):04X}", read.reason or "")

    def test_bomless_utf16_and_utf32_are_refused(self) -> None:
        """These decode as UTF-8 *successfully*, so "did the decoder raise?" returns False."""
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            with self.subTest(encoding=encoding):
                decoded = _CANONICAL.encode(encoding).decode("utf-8")
                read = read_frontmatter(decoded)
                self.assertEqual(read.state, "malformed", msg=f"{encoding} must be refused")
                self.assertIn("NUL", read.reason or "")

    def test_unclosed_block_is_refused_not_read_as_empty(self) -> None:
        read = read_frontmatter("---\nkind: foundation\n\n# body with no closing marker\n")
        self.assertEqual(read.state, "malformed")
        self.assertIn("closing", read.reason or "")

    def test_malformed_carries_actionable_reason_prose(self) -> None:
        """`.claude/rules/guardrail-feedback-prose.md` — a refusal names what and why."""
        read = read_frontmatter("\x0b" + _CANONICAL)
        self.assertEqual(read.state, "malformed")
        self.assertTrue((read.reason or "").strip(), msg="a malformed verdict owes a reason")

    def test_malformed_never_leaks_fields(self) -> None:
        """A refused read must not hand back a partially-parsed mapping."""
        read = read_frontmatter("\x85" + _CANONICAL)
        self.assertEqual(read.fields, {})


class ByteLevelReads(unittest.TestCase):
    """A decode failure is a `malformed` verdict, never an `absent` one."""

    def test_utf8_bytes_parse(self) -> None:
        read = read_frontmatter_bytes(_CANONICAL.encode("utf-8"))
        self.assertEqual(read.state, "valid")

    def test_utf8_bom_bytes_parse(self) -> None:
        read = read_frontmatter_bytes(_CANONICAL.encode("utf-8-sig"))
        self.assertEqual(read.state, "valid")
        self.assertEqual(read.fields["kind"], "foundation")

    def test_undecodable_bytes_are_malformed(self) -> None:
        read = read_frontmatter_bytes(b"\xff\xfe\x00\x00bogus")
        self.assertEqual(read.state, "malformed")

    def test_bom_bearing_utf16_bytes_are_malformed(self) -> None:
        read = read_frontmatter_bytes(_CANONICAL.encode("utf-16"))
        self.assertEqual(read.state, "malformed")


class SeparatorSetIsDefinedByPredicate(unittest.TestCase):
    """The set is *derived*, not enumerated by taste.

    Membership is "characters `splitlines()` treats as a line boundary but
    `split('\\n')` does not" — that is precisely where two decoders must
    disagree. This test asserts the predicate rather than the literal tuple, so
    the definition survives someone editing the tuple.
    """

    def test_every_member_actually_splits_divergently(self) -> None:
        for sep in SPLIT_DIVERGENT_SEPARATORS:
            with self.subTest(codepoint=f"U+{ord(sep):04X}"):
                probe = f"a{sep}b"
                self.assertEqual(len(probe.splitlines()), 2, msg="must split under splitlines()")
                self.assertEqual(len(probe.split("\n")), 1, msg="must NOT split under split('\\n')")

    def test_newline_is_not_a_member(self) -> None:
        """`\\n` splits under both strategies, so it cannot cause divergence."""
        self.assertNotIn("\n", SPLIT_DIVERGENT_SEPARATORS)


class MembraneRefusesWhatItCannotRead(unittest.TestCase):
    """The ingress matrix run against a real guard, not just the reader.

    A tri-state reader that no guard consults would leave the bypass open. The
    foundation membrane is shaped `if kind != "foundation": allow`, so every
    input that defeats detection is admitted — these are the round-5 cases that
    booked a prohibited package with `REGISTER_EXIT=0`.
    """

    _ADR_ID = "ADR-0.0.99-hand-placed-foundation"
    _BODY = f"---\nid: {_ADR_ID}\nkind: foundation\nstatus: Draft\n---\n\n# probe\n"

    def _probe(self, raw: bytes) -> bool:
        """Return True when the membrane refuses the package."""
        import tempfile  # noqa: PLC0415
        from pathlib import Path  # noqa: PLC0415

        from gzkit.commands.register import is_ungrandfathered_foundation  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            adr_file = Path(tmp) / f"{self._ADR_ID}.md"
            adr_file.write_bytes(raw)
            return is_ungrandfathered_foundation(adr_file, self._ADR_ID, frozenset())

    def test_canonical_foundation_package_is_refused(self) -> None:
        """Baseline: the membrane works on the shape it was built for."""
        self.assertTrue(self._probe(self._BODY.encode("utf-8")))

    def test_grandfathered_package_is_admitted(self) -> None:
        """The guard stays manifest-aware, never a bare `kind` refusal."""
        import tempfile  # noqa: PLC0415
        from pathlib import Path  # noqa: PLC0415

        from gzkit.commands.register import is_ungrandfathered_foundation  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            adr_file = Path(tmp) / f"{self._ADR_ID}.md"
            adr_file.write_text(self._BODY, encoding="utf-8")
            self.assertFalse(
                is_ungrandfathered_foundation(adr_file, self._ADR_ID, frozenset({self._ADR_ID}))
            )

    def test_feature_package_is_admitted(self) -> None:
        """The membrane closes `foundation` only; open kinds must pass."""
        self.assertFalse(self._probe(self._BODY.replace("foundation", "feature").encode("utf-8")))

    def test_unicode_separator_prefixed_foundation_is_refused(self) -> None:
        """Round-5 case: an invisible separator made the package read as kind-less."""
        for sep in SPLIT_DIVERGENT_SEPARATORS:
            with self.subTest(codepoint=f"U+{ord(sep):04X}"):
                self.assertTrue(
                    self._probe((sep + self._BODY).encode("utf-8")),
                    msg=(
                        f"U+{ord(sep):04X} before a foundation package must be refused; "
                        "unreadable must never collapse into 'no kind', which reads as permission"
                    ),
                )

    def test_bomless_utf16_and_utf32_foundation_is_refused(self) -> None:
        """These decode as UTF-8 successfully, so a decoder-raised check returns False."""
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            with self.subTest(encoding=encoding):
                self.assertTrue(
                    self._probe(self._BODY.encode(encoding)),
                    msg=f"BOM-less {encoding} foundation package must be refused",
                )

    def test_bom_prefixed_foundation_is_still_refused(self) -> None:
        """GHI #735's case must not regress when the reader gets stricter."""
        self.assertTrue(self._probe(self._BODY.encode("utf-8-sig")))

    def test_ordinary_non_adr_markdown_is_not_refused(self) -> None:
        """`absent` is not `malformed`: a frontmatter-less doc is not a foundation ADR."""
        self.assertFalse(self._probe(b"# just a document with no frontmatter\n"))


if __name__ == "__main__":
    unittest.main()
