"""GHI #1155 — the SUPPORT-REQ proof declaration (GHI #888) carries load-bearing claims.

The parser once inferred a REQ's proof channel from any event name in its prose. These tests
weaken it the way that defect did, and the ways its repair could regress, and require the
matching control to fail.
"""

from __future__ import annotations

import re
import unittest
from unittest import mock

from gzkit import req_kind_support as support
from gzkit.enforcement import production_enforcement_registry, run_meta_validator
from gzkit.req_kind_support_claims import (
    ADMIT_CLAIM_ID,
    REFUSE_CLAIM_ID,
    declared_req,
    undeclared_shape_population,
    undeclared_shapes,
)

_GATE = "gzkit.req_kind_support:parse_support_citation"


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


def _infers_from_the_whole_body(req_text):
    """The pre-#888 parser: any known event name anywhere in the prose is the proof."""
    found = [et for et in sorted(support._KNOWN_LEDGER_EVENT_TYPES) if et in req_text]
    scopes = {s.replace("-", "_") for s in support._GZ_VALIDATE_SCOPE_RE.findall(req_text)}
    if not found or len(scopes) != 1:
        return None
    return support.SupportCitation(event_types=found, scope=next(iter(scopes)))


def _first_marker_wins(req_text):
    """A clause reader that stops refusing a doubled declaration."""
    marker = support._WITNESS_MARKER_RE.search(req_text)
    return req_text[marker.end() :] if marker else None


def _substring_event(clause):
    """An event reader that matches inside a longer token."""
    found = sorted(et for et in support._KNOWN_LEDGER_EVENT_TYPES if et in clause)
    return found[0] if found else None


class TestSupportCitationClaims(unittest.TestCase):
    def test_both_claims_name_the_parser_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertIn(_GATE, records[claim_id].gate_targets)
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})

    def test_every_planted_shape_mentions_a_recognized_event(self):
        # The present-but-false property: each text names an event the old parser accepted.
        for shape, text in undeclared_shapes().items():
            with self.subTest(shape):
                self.assertTrue(
                    any(et in text for et in support._KNOWN_LEDGER_EVENT_TYPES), msg=text
                )

    def test_the_old_parser_accepted_the_denial_the_alternative_and_the_doubled_clause(self):
        # Proves the shapes are the old defect's input, not strings the new parser merely dislikes.
        accepted = {
            shape
            for shape, text in undeclared_shapes().items()
            if _infers_from_the_whole_body(text) is not None
        }
        self.assertTrue({"denial", "rejected-alternative", "doubled-clause"} <= accepted)

    def test_the_declared_req_names_a_second_event_outside_its_clause(self):
        text, event = declared_req()
        named = {et for et in support._KNOWN_LEDGER_EVENT_TYPES if re.search(rf"\b{et}\b", text)}
        self.assertGreater(len(named), 1)
        self.assertIn(event, named)

    def test_the_population_names_every_shape(self):
        self.assertEqual(undeclared_shape_population(), list(undeclared_shapes()))


class TestControlsFailWhenTheParserIsWeakened(unittest.TestCase):
    def test_inferring_from_the_whole_body_fails_the_refuse_control(self):
        with mock.patch.object(support, "parse_support_citation", _infers_from_the_whole_body):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_tolerating_a_doubled_clause_fails_the_refuse_control(self):
        with mock.patch.object(support, "_witness_clause", _first_marker_wins):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_matching_an_event_inside_a_longer_token_fails_the_refuse_control(self):
        with mock.patch.object(support, "_sole_event_type", _substring_event):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_an_always_refuse_parser_fails_the_admit_control(self):
        with mock.patch.object(support, "parse_support_citation", lambda text: None):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")

    def test_a_parser_that_reads_the_body_event_fails_the_admit_control(self):
        # The declared REQ names a second event in its body; reading it is the #888 hole.
        with mock.patch.object(support, "parse_support_citation", _infers_from_the_whole_body):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
