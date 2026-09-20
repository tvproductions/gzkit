"""ghi-triage v4 deliverable contract — GHI #324.

Pins the rank-deliverable rendering and rank-input validation against the
v4 contract. The deliverable equation is:

    deliverable == script(static_args, agent_cognition_input)

with no `agent_render(...)` term in the equation. Byte-stable rendering
across runs (given a frozen issue set + frozen agent input) is the regression
gate that catches inline-Python heredoc rendering, prose drift, and any
future "let's add one nice touch" inline addition that v3 collapsed onto
the agent.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
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
    spec = importlib.util.spec_from_file_location("ghi_triage_script", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_TRIAGE = _load_triage_module()


def _issue(number: int, title: str, body: str = "", labels: tuple[str, ...] = ()) -> object:
    return _TRIAGE.Issue(
        number=number,
        title=title,
        labels=list(labels),
        body=body,
        created_at="2026-04-25T00:00:00Z",
        updated_at="2026-04-25T00:00:00Z",
    )


class TestRankDeliverableIsByteStable(unittest.TestCase):
    """deliverable == script(static_args, agent_cognition_input)."""

    def setUp(self) -> None:
        self.issues = [
            _issue(324, "ghi-triage skill: vibed deliverable contract", labels=("defect",)),
            _issue(323, "behave-req-tags fires on Draft briefs", labels=("defect",)),
            _issue(316, "ghi-author: cross-repo defect filing", labels=("enhancement",)),
        ]
        self.issue_index = {i.number: i for i in self.issues}
        self.routes = {324: "direct-fix", 323: "direct-fix", 316: "OBPI"}
        self.precedent = 110
        self.agent_input = {
            "rankings": [
                {"number": 324, "severity": "blocking"},
                {"number": 323, "severity": "degrading"},
            ]
        }

    def test_render_rank_is_deterministic_across_invocations(self) -> None:
        items = _TRIAGE.parse_rank_input(self.agent_input, set(self.issue_index))
        outputs = {
            _TRIAGE.render_rank(
                items,
                self.issue_index,
                self.routes,
                self.precedent,
                len(self.issues),
            )
            for _ in range(20)
        }
        self.assertEqual(len(outputs), 1, "render_rank produced non-byte-stable output")

    def test_render_rank_preserves_caller_supplied_order(self) -> None:
        items = _TRIAGE.parse_rank_input(self.agent_input, set(self.issue_index))
        rendered = _TRIAGE.render_rank(
            items, self.issue_index, self.routes, self.precedent, len(self.issues)
        )
        idx_324 = rendered.find("#324")
        idx_323 = rendered.find("#323")
        self.assertGreater(idx_324, -1)
        self.assertGreater(idx_323, -1)
        self.assertLess(idx_324, idx_323, "agent-supplied order must be preserved verbatim")

    def test_render_rank_includes_severity_route_and_title(self) -> None:
        items = _TRIAGE.parse_rank_input(self.agent_input, set(self.issue_index))
        rendered = _TRIAGE.render_rank(
            items, self.issue_index, self.routes, self.precedent, len(self.issues)
        )
        self.assertIn("[blocking]", rendered)
        self.assertIn("direct-fix", rendered)
        self.assertIn("vibed deliverable contract", rendered)

    def test_render_rank_omits_agent_prose_fields(self) -> None:
        """GHI #424 round 3: rank-input schema carries no prose; render mirrors that."""
        items = _TRIAGE.parse_rank_input(self.agent_input, set(self.issue_index))
        rendered = _TRIAGE.render_rank(
            items, self.issue_index, self.routes, self.precedent, len(self.issues)
        )
        # Renderer never emits the legacy `action`/`why` tokens because the
        # schema no longer accepts them. This guards against a regression that
        # would re-introduce prose duplication between input and output.
        for legacy_phrase in (
            "fix triage skill rendering",
            "operator-facing surface degrades chat output every invocation",
            "scope behave-req-tags to post-impl briefs",
        ):
            self.assertNotIn(legacy_phrase, rendered)


class TestRankInputStructuralSchema(unittest.TestCase):
    """Schema is structural-only — number + severity, no prose (GHI #424 round 3)."""

    def setUp(self) -> None:
        self.known = {324, 323}

    def _payload(self, **overrides: object) -> dict:
        entry: dict[str, object] = {"number": 324, "severity": "blocking"}
        entry.update(overrides)
        return {"rankings": [entry]}

    def test_severity_must_be_enum(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(severity="critical"), self.known)

    def test_action_field_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(action="fix it"), self.known)

    def test_why_field_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(why="some reason"), self.known)

    def test_arbitrary_extra_field_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(rationale="anything"), self.known)

    def test_unknown_issue_number_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(number=9999), self.known)

    def test_duplicate_issue_number_rejected(self) -> None:
        payload = {
            "rankings": [
                {"number": 324, "severity": "blocking"},
                {"number": 324, "severity": "latent"},
            ]
        }
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(payload, self.known)

    def test_empty_rankings_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input({"rankings": []}, self.known)

    def test_non_dict_payload_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input([{"number": 324}], self.known)

    def test_well_formed_payload_accepted(self) -> None:
        items = _TRIAGE.parse_rank_input(self._payload(), self.known)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].number, 324)
        self.assertEqual(items[0].severity, "blocking")


class TestRankInputCachePathRequirement(unittest.TestCase):
    """GHI #424 round 4: --rank-input must live under .gzkit/cache/triage/.

    Stdin and arbitrary paths are rejected so the inline-pipe shape
    (`echo '<json>' | triage.py --format rank --rank-input -`) is
    structurally impossible. Writing the JSON to a cache file leaves a
    file path on the bash command line; the rank payload itself is
    never echoed into the chat surface.
    """

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self._prev_cwd = Path.cwd()
        os.chdir(self._tmpdir.name)
        self.addCleanup(lambda: os.chdir(self._prev_cwd))
        # Cache dir intentionally NOT pre-created here — the script auto-
        # creates it. Tests that need a file in it create the dir as needed.
        self.cache_dir = Path(self._tmpdir.name) / ".gzkit" / "cache" / "triage"
        self.payload = '{"rankings":[{"number":324,"severity":"blocking"}]}'

    def test_none_path_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError) as ctx:
            _TRIAGE._read_rank_input(None)
        self.assertIn("GHI #424", str(ctx.exception))

    def test_stdin_dash_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError) as ctx:
            _TRIAGE._read_rank_input("-")
        self.assertIn("stdin", str(ctx.exception).lower())
        self.assertIn("GHI #424", str(ctx.exception))

    def test_path_outside_cache_dir_rejected(self) -> None:
        outside = Path(self._tmpdir.name) / "rank.json"
        outside.write_text(self.payload, encoding="utf-8")
        with self.assertRaises(_TRIAGE.RankInputError) as ctx:
            _TRIAGE._read_rank_input(str(outside))
        self.assertIn(".gzkit/cache/triage", str(ctx.exception))

    def test_path_inside_cache_dir_accepted(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        inside = self.cache_dir / "rank.json"
        inside.write_text(self.payload, encoding="utf-8")
        result = _TRIAGE._read_rank_input(str(inside))
        self.assertEqual(result, {"rankings": [{"number": 324, "severity": "blocking"}]})

    def test_empty_cache_file_rejected(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        empty = self.cache_dir / "empty.json"
        empty.write_text("", encoding="utf-8")
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE._read_rank_input(str(empty))

    def test_cache_dir_auto_created_when_missing(self) -> None:
        """Portability: a fresh checkout should not need a manual mkdir."""
        self.assertFalse(self.cache_dir.exists())
        # _ensure_rank_input_cache_dir is the documented portability hook;
        # exercise it directly so the contract is pinned even if the
        # _read_rank_input call sites change.
        resolved = _TRIAGE._ensure_rank_input_cache_dir()
        self.assertTrue(self.cache_dir.exists())
        self.assertEqual(resolved, self.cache_dir.resolve())


class TestStaleAnnotationPass(unittest.TestCase):
    """Row 4: the exact half of the family/staleness pass.

    A transcribed `#N (open)` is decoration over a Layer-2 fact GitHub renders
    live. Reporting its decay is a lookup, so these assert the lookup's
    semantics -- which references it binds to, and that an unresolved state is
    never reported as decayed.
    """

    @staticmethod
    def _resolver(mapping: dict[int, str]):
        return lambda number: mapping.get(number, "unknown")

    def test_reports_annotation_whose_subject_has_closed(self) -> None:
        issue = _issue(1, "t", "blocked by #889 (open) until that lands")
        self.assertEqual(
            _TRIAGE.stale_annotations(issue, self._resolver({889: "settled"})),
            [{"identifier": "#889", "annotated": "open"}],
        )

    def test_live_subject_is_not_decayed(self) -> None:
        issue = _issue(2, "t", "see #929 (open)")
        self.assertEqual(_TRIAGE.stale_annotations(issue, self._resolver({929: "live"})), [])

    def test_unknown_subject_is_not_reported_as_decayed(self) -> None:
        """Missing evidence is not evidence that the subject closed."""
        issue = _issue(3, "t", "see #929 (open)")
        self.assertEqual(_TRIAGE.stale_annotations(issue, self._resolver({})), [])

    def test_annotation_binds_to_the_reference_it_follows(self) -> None:
        """The window trap: a correct `(closed)` list must not lend `(open)`.

        A window-based match reached a 44% false-positive rate on this exact
        shape when the `ghi-cross-reference-staleness` chore first tried it.
        """
        issue = _issue(4, "t", "#929 (open) -- #2, #889 (closed) -- done")
        found = _TRIAGE.stale_annotations(issue, self._resolver({889: "settled", 929: "live"}))
        self.assertEqual(found, [], "annotation read from a neighbouring reference")

    def test_bold_reference_still_binds(self) -> None:
        issue = _issue(5, "t", "**#889** (open)")
        self.assertEqual(
            _TRIAGE.stale_annotations(issue, self._resolver({889: "settled"})),
            [{"identifier": "#889", "annotated": "open"}],
        )

    def test_repeated_subject_reported_once(self) -> None:
        issue = _issue(6, "t", "#889 (open) ... and again #889 (still open)")
        found = _TRIAGE.stale_annotations(issue, self._resolver({889: "settled"}))
        self.assertEqual([entry["identifier"] for entry in found], ["#889"])

    def test_absent_resolver_reports_nothing(self) -> None:
        """Exercisable without `gh`; an unreachable live state never renders as decayed."""
        issue = _issue(7, "t", "#889 (open)")
        self.assertEqual(_TRIAGE.stale_annotations(issue, None), [])


class TestFamilySignalIsCandidateEvidence(unittest.TestCase):
    """Row 4: the inexact half, pinned to the contract it actually meets.

    `family_signal` names candidates for the agent's body read. These tests
    assert that contract rather than a hit rate -- including the blind spot,
    so a later reader cannot mistake an empty list for non-membership.
    """

    def test_names_the_phrases_a_declared_without_mechanism_body_uses(self) -> None:
        issue = _issue(
            1063,
            "registries: 51 validator scopes and 10 event types are never invoked",
            "A registry declares a scope with no caller; nothing enforces it.",
        )
        self.assertEqual(
            _TRIAGE.family_signal(issue),
            ["declares a scope with no", "never invoked", "no caller", "nothing enforces"],
        )

    def test_reads_the_title_as_well_as_the_body(self) -> None:
        """Step 0's skim shows titles only, so a title-only signal must still fire."""
        issue = _issue(8, "commit-trailers: the trailer has no automated witness", "")
        self.assertNotEqual(_TRIAGE.family_signal(issue), [])

    def test_silence_is_not_evidence_of_non_membership(self) -> None:
        """The documented blind spot, held as a test so it cannot be forgotten.

        #1012 ("reserved words and $( ) hide a verifier's head") is a member of
        the family that no surface phrase catches. Root-cause class is not a
        surface-word property -- which is why `ghi-author` Step 0's title skim
        misses the family and why this signal may never be counted.
        """
        issue = _issue(
            1012, "verifier-pipe-gate: reserved words and $( ) hide a verifier's head", ""
        )
        self.assertEqual(_TRIAGE.family_signal(issue), [])

    def test_ordinary_defect_report_produces_no_signal(self) -> None:
        issue = _issue(9, "cli: exits 2 on a valid flag", "Ran the verb, got exit 2, expected 0.")
        self.assertEqual(_TRIAGE.family_signal(issue), [])


class TestRowFourPassStaysOutOfTheRankInput(unittest.TestCase):
    """The pass informs Step 2's read; it must not reopen GHI #424.

    The rank-input schema is structural-only: the agent contributes selection,
    ordering and severity. Adding a family or staleness field there would put
    script-derived prose back on the agent's surface, which is the defect
    GHI #424 closed by removing prose fields from the schema entirely.
    """

    def test_family_signal_rejected_as_agent_input(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(
                {"rankings": [{"number": 1, "severity": "blocking", "family_signal": ["x"]}]},
                {1},
            )

    def test_stale_annotations_rejected_as_agent_input(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(
                {"rankings": [{"number": 1, "severity": "blocking", "stale_annotations": []}]},
                {1},
            )

    def test_render_json_carries_both_fields(self) -> None:
        issue = _issue(1, "surface: nothing enforces the rule", "blocked by #889 (open)")
        payload = json.loads(
            _TRIAGE.render_json(
                [issue], precedent=5, duplicates={}, blocker_resolver=lambda n: "settled"
            )
        )
        record = payload["issues"][0]
        self.assertNotEqual(record["family_signal"], [])
        self.assertEqual(record["stale_annotations"], [{"identifier": "#889", "annotated": "open"}])


if __name__ == "__main__":
    unittest.main()
