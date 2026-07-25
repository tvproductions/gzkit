"""ghi-triage blocker-freshness contract.

`ghi-close/SKILL.md` § Phase 1 step 1a binds every agent to re-derive a GHI's
recorded preconditions before honoring them -- *"A blocker you did not re-check
is hearsay, not a gate."* The obligation shipped with no instrument: `fetch()`
never requested comments, so the automated triage path could not read the text
that decays. Three stale blockers (#614, #580, #696) were found by hand in one
2026-07-24 session, which is the failure rate the obligation alone produces.

This pins the instrument. The semantics under test come from the rule, not from
a run of the code:

* a blocker citing a settled reference is surfaced, because a precondition that
  has already closed cannot still gate;
* an *unresolvable* reference is never surfaced as settled, because missing
  evidence is not evidence of a closed precondition (the distinction `#696`
  established on the handoff surface and paid for on its first real run);
* a non-blocker comment carries no preconditions and must not be mined for
  them, or every issue discussion becomes a false gate.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / ".gzkit"
    / "skills"
    / "ghi-triage"
    / "scripts"
    / "triage.py"
)


def _load_triage_module():
    spec = importlib.util.spec_from_file_location("ghi_triage_blocker_script", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_TRIAGE = _load_triage_module()


def _issue(number: int = 1, *, comments: list | None = None):
    return _TRIAGE.Issue(
        number=number,
        title="t",
        labels=["defect"],
        body="b",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-02T00:00:00Z",
        comments=comments or [],
    )


def _comment(body: str, created_at: str = "2026-06-03T06:10:43Z"):
    return _TRIAGE.Comment(body=body, created_at=created_at)


class TestBlockerDetection(unittest.TestCase):
    """Which comments carry preconditions at all."""

    def test_blocker_marker_is_recognized(self) -> None:
        self.assertTrue(_TRIAGE.is_blocker_comment("**Blocker (open-with-blocker).** No route."))

    def test_sequence_after_is_a_precondition(self) -> None:
        # `ghi-close` names this shape explicitly alongside blocker comments:
        # "a 'sequence this after #M' note ... is a claim about the tree".
        self.assertTrue(_TRIAGE.is_blocker_comment("sequence after #664 settles req_count"))

    def test_blocked_on_is_a_precondition(self) -> None:
        self.assertTrue(_TRIAGE.is_blocker_comment("blocked on the in-flight OBPI-0.1.0-01"))

    def test_ordinary_discussion_is_not_a_blocker(self) -> None:
        # Mining every comment would turn each cross-link into a false gate.
        self.assertFalse(_TRIAGE.is_blocker_comment("Cross-link from #712, filed today."))


class TestReferenceExtraction(unittest.TestCase):
    """What a precondition cites."""

    def test_bare_hash_form_counts(self) -> None:
        refs = _TRIAGE.extract_references("sequence after #664")
        self.assertEqual([("GHI", "664")], [(r.kind, r.identifier) for r in refs])

    def test_obpi_does_not_yield_a_phantom_adr(self) -> None:
        # An OBPI id embeds its parent's semver. Matching ADR first would strand
        # the suffix and invent a second, bogus reference to adjudicate.
        refs = _TRIAGE.extract_references("blocked on OBPI-0.0.37-12")
        self.assertEqual([("OBPI", "OBPI-0.0.37-12")], [(r.kind, r.identifier) for r in refs])

    def test_repeated_citation_yields_one_reference(self) -> None:
        refs = _TRIAGE.extract_references("blocked on #580; see #580 again")
        self.assertEqual(1, len(refs))

    def test_unresolved_reference_defaults_to_unknown(self) -> None:
        # Never LIVE by default: an unchecked reference has not been verified.
        refs = _TRIAGE.extract_references("blocked on #999")
        self.assertEqual("unknown", refs[0].state)

    def test_ordinal_into_another_document_is_not_a_citation(self) -> None:
        # Observed on the first live run: GHI #691's blocker cites
        # "`skill-surface-sync.md` #6" -- a RULE number. It resolved to GHI #6,
        # which is genuinely closed, and produced a confident false gate on an
        # issue whose precondition had not moved at all. A freshness signal that
        # cries wolf is worse than none, because it gets ignored wholesale.
        self.assertEqual([], _TRIAGE.extract_references("blocked on `some-rule.md` #6"))
        self.assertEqual([], _TRIAGE.extract_references("blocked on rule #6"))
        self.assertEqual([], _TRIAGE.extract_references("see § Behavior Rules item #13"))

    def test_genuine_citation_survives_the_ordinal_guard(self) -> None:
        # The guard must not swallow the shape it exists to protect.
        self.assertEqual(
            [("GHI", "696")],
            [(r.kind, r.identifier) for r in _TRIAGE.extract_references("blocked on #696")],
        )
        self.assertEqual(
            [("GHI", "696")],
            [(r.kind, r.identifier) for r in _TRIAGE.extract_references("blocked on GHI #696")],
        )


class TestBlockerFreshness(unittest.TestCase):
    """Whether a recorded precondition still holds."""

    def test_settled_citation_is_surfaced(self) -> None:
        issue = _issue(comments=[_comment("**Blocker.** sequence after #664")])
        found = _TRIAGE.blockers(issue, lambda n: "settled" if n == 664 else "live")
        self.assertEqual(1, len(found))
        self.assertTrue(found[0].cites_settled)

    def test_live_citation_is_not_surfaced(self) -> None:
        issue = _issue(comments=[_comment("**Blocker.** sequence after #664")])
        found = _TRIAGE.blockers(issue, lambda n: "live")
        self.assertFalse(found[0].cites_settled)

    def test_unknown_is_not_settled(self) -> None:
        # The load-bearing negative. An ADR reference has no resolver, so it
        # stays UNKNOWN -- and UNKNOWN must not be reported as a closed
        # precondition, or the flag manufactures evidence it does not have.
        issue = _issue(comments=[_comment("**Blocker.** blocked on ADR-0.0.37")])
        found = _TRIAGE.blockers(issue, lambda n: "settled")
        self.assertEqual(["unknown"], [r.state for r in found[0].references])
        self.assertFalse(found[0].cites_settled)

    def test_non_blocker_comments_are_not_mined(self) -> None:
        issue = _issue(comments=[_comment("Cross-link from #712.")])
        self.assertEqual([], _TRIAGE.blockers(issue, lambda n: "settled"))

    def test_issue_without_comments_has_no_blockers(self) -> None:
        self.assertEqual([], _TRIAGE.blockers(_issue(), lambda n: "settled"))


class TestFreshnessReachesTheOperator(unittest.TestCase):
    """A signal computed and never rendered is the same as no signal."""

    def test_rationale_names_the_settled_citation(self) -> None:
        issue = _issue(comments=[_comment("**Blocker.** sequence after #664")])
        text = _TRIAGE.rationale(issue, "direct-fix", {}, blocker_resolver=lambda n: "settled")
        self.assertIn("stale blocker", text.lower())
        self.assertIn("664", text)

    def test_rationale_is_silent_when_preconditions_hold(self) -> None:
        issue = _issue(comments=[_comment("**Blocker.** sequence after #664")])
        text = _TRIAGE.rationale(issue, "direct-fix", {}, blocker_resolver=lambda n: "live")
        self.assertNotIn("stale blocker", text.lower())

    def test_json_carries_blocker_records(self) -> None:
        import json

        issue = _issue(comments=[_comment("**Blocker.** sequence after #664")])
        payload = json.loads(
            _TRIAGE.render_json([issue], 5, {}, blocker_resolver=lambda n: "settled")
        )
        record = payload["issues"][0]
        self.assertTrue(record["blockers"][0]["cites_settled"])

    def test_fetch_requests_comments(self) -> None:
        # The structural fence. Everything above is unreachable in production if
        # the gh query never asks for comments -- which is exactly how the
        # obligation shipped uninstrumented.
        self.assertIn("comments", _TRIAGE.ISSUE_JSON_FIELDS)


if __name__ == "__main__":
    unittest.main()
