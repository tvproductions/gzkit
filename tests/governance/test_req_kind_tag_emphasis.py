"""Every reader of the ADR-0.0.59 kind-tag syntax tolerates emphasis (GHI #809).

Three modules parse `REQ-X.Y.Z-NN-MM [KIND]:` out of an OBPI brief's
`## Acceptance Criteria`, and they disagreed about markdown emphasis:

  - ``gzkit.triangle`` tolerated it around both the REQ id and the kind tag,
    fixed under GHI #700 with the reason stated in its own comment — "ADR-0.0.59
    mandates the tag, not its typographic weight".
  - ``gzkit.commands.validate_req_kind`` tolerated it around the REQ id only.
  - ``gzkit.governance.req_coverage`` tolerated it in neither position.

The GHI #700 fix landed in one reader; its two siblings never received it.

**The dangerous branch is the quiet one.** In
``_validate_req_kind_discipline_for_brief``, a brief whose tags all fail to match
takes the ``if not tagged: return []`` path — the all-untagged legacy
grandfather — so an emphasised brief does not fail, it *passes without being
checked*. Under-enforcement that presents as a clean run is exactly the
false-green shape `.gzkit/rules/tests.md` § Verification exit-code integrity
exists to refuse elsewhere.

This module pins the rule at the level of the class rather than the instance: a
fourth reader of the same syntax that does not tolerate emphasis turns one of
these assertions red, instead of silently under-counting a REQ set.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.validate_req_kind import _REQ_KIND_TAG_RE
from gzkit.governance.req_coverage import parse_brief_req_kinds
from gzkit.governance.trust_audits.briefs import _REQ_KIND_TAG as _BRIEFS_KIND_TAG_RE
from gzkit.governance.trust_audits.closeout_proof import _KIND_TAG_RE as _CLOSEOUT_KIND_TAG_RE
from gzkit.triangle import extract_reqs_from_brief

# Emphasis on the kind tag, which ADR-0.0.59 does not constrain. The REQ ids are
# deliberately un-emphasised so a failure isolates the kind-tag axis: emphasis
# around the id was already tolerated by two of the three readers.
EMPHASISED_BRIEF = """## Acceptance Criteria

- [ ] REQ-0.34.0-04-01 **[BEHAVIOR]**: `gz adr demote` moves an unstarted foundation to pool.
- [ ] REQ-0.34.0-04-02 **[SUPPORT]**: each grandfathered foundation receives one manifest entry.
- [x] REQ-0.34.0-04-03 **[STRUCTURAL-FENCE]**: the taxonomy gate is wired into `gz check`.
"""

EXPECTED_KINDS = {
    "REQ-0.34.0-04-01": "BEHAVIOR",
    "REQ-0.34.0-04-02": "SUPPORT",
    "REQ-0.34.0-04-03": "STRUCTURAL-FENCE",
}


class TestKindTagEmphasisAcrossReaders(unittest.TestCase):
    """All three readers must agree that an emphasised tag is still a tag."""

    def test_triangle_reader_tolerates_emphasis(self) -> None:
        """Control: the reader fixed under GHI #700 already passes."""
        reqs = extract_reqs_from_brief(EMPHASISED_BRIEF, "OBPI-0.34.0-04")
        self.assertEqual([str(r.id) for r in reqs], sorted(EXPECTED_KINDS))

    def test_discipline_validator_reads_emphasised_tags_as_tagged(self) -> None:
        """An emphasised brief must not fall through the all-untagged grandfather."""
        found = {
            req_id: kind.upper() for req_id, kind in _REQ_KIND_TAG_RE.findall(EMPHASISED_BRIEF)
        }
        self.assertEqual(
            found,
            EXPECTED_KINDS,
            "emphasised kind tags read as untagged; the brief then takes the "
            "`if not tagged: return []` grandfather path and passes unchecked "
            "(GHI #809)",
        )

    def test_coverage_reader_reads_emphasised_tags_as_tagged(self) -> None:
        """The covers-channel reader must resolve the same kinds from the same text."""
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "OBPI-0.34.0-04-demote.md"
            brief.write_text(EMPHASISED_BRIEF, encoding="utf-8")
            self.assertEqual(parse_brief_req_kinds(brief), EXPECTED_KINDS)

    def test_trust_audit_readers_tolerate_emphasis(self) -> None:
        """The two remaining readers are immune by construction — pin that.

        ``trust_audits/briefs`` and ``trust_audits/closeout_proof`` match the
        bracketed tag ALONE, unanchored and with no trailing ``:``, so emphasis
        outside the brackets never mattered to them. Neither needed the GHI #809
        fix. They are pinned here anyway because their immunity is incidental
        rather than intended: tightening either one for precision — adding the
        trailing colon that ``req_coverage`` carries, say — would reintroduce the
        defect in a reader nobody was watching. Enumerating the family without
        binding its immune members leaves exactly the gap that let the sibling
        readers of GHI #700 go unfixed for as long as they did.
        """
        line = "- [ ] REQ-0.34.0-04-01 **[BEHAVIOR]**: does the thing.\n"
        for name, pattern in (
            ("trust_audits.briefs", _BRIEFS_KIND_TAG_RE),
            ("trust_audits.closeout_proof", _CLOSEOUT_KIND_TAG_RE),
        ):
            with self.subTest(reader=name):
                self.assertIsNotNone(pattern.search(line))

    def test_plain_tags_still_read(self) -> None:
        """The tolerance is additive — unemphasised tags keep working."""
        plain = EMPHASISED_BRIEF.replace("**[", "[").replace("]**", "]")
        found = {req_id: kind.upper() for req_id, kind in _REQ_KIND_TAG_RE.findall(plain)}
        self.assertEqual(found, EXPECTED_KINDS)
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "OBPI-0.34.0-04-demote.md"
            brief.write_text(plain, encoding="utf-8")
            self.assertEqual(parse_brief_req_kinds(brief), EXPECTED_KINDS)
