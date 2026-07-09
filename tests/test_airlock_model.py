"""Tests for the airlock pure data layer (OBPI-0.33.0-01).

Assertions derive from the brief's Acceptance Criteria (REQ-0.33.0-01-01
through REQ-0.33.0-01-05), NOT from a run of the implementation.
"""

from __future__ import annotations

import unittest

import pydantic

from gzkit.airlock.model import (
    Authority,
    Decision,
    DriftDiff,
    Preflight,
    Provenance,
    SeamEdge,
    SeamKind,
    SeamMap,
    Verdict,
    seam_map_json_schema,
)
from gzkit.schemas import load_schema
from gzkit.traceability import covers


def _edge(kind: SeamKind = SeamKind.PUSH) -> SeamEdge:
    return SeamEdge(
        kind=kind,
        provenance=Provenance.LAW,
        source="a",
        target="b",
        accounted=True,
    )


class TestAirlockModel(unittest.TestCase):
    @covers("REQ-0.33.0-01-01")
    def test_models_frozen_and_extra_forbid(self) -> None:
        edge = _edge()
        seam_map = SeamMap(
            bodies=("region",),
            push_edges=(edge,),
            pull_edges=(),
            unaccounted=(),
        )
        preflight = Preflight(
            seam_map=seam_map,
            blast_radius=1,
            authority=Authority.CAPTAIN,
            decision=Decision.PROCEED,
        )
        drift = DriftDiff(drift=(edge,), verdict=Verdict.CLEAN, resolutions=())

        # Unknown kwarg is rejected (extra="forbid").
        with self.assertRaises(pydantic.ValidationError):
            SeamEdge(
                kind=SeamKind.PUSH,
                provenance=Provenance.LAW,
                source="a",
                target="b",
                accounted=True,
                bogus=1,
            )
        with self.assertRaises(pydantic.ValidationError):
            SeamMap(bodies=(), push_edges=(), pull_edges=(), unaccounted=(), bogus=1)
        with self.assertRaises(pydantic.ValidationError):
            Preflight(
                seam_map=seam_map,
                blast_radius=1,
                authority=Authority.CAPTAIN,
                decision=None,
                bogus=1,
            )
        with self.assertRaises(pydantic.ValidationError):
            DriftDiff(drift=(), verdict=Verdict.CLEAN, resolutions=(), bogus=1)

        # Mutation post-construction is rejected (frozen=True).
        with self.assertRaises(pydantic.ValidationError):
            edge.source = "z"
        with self.assertRaises(pydantic.ValidationError):
            seam_map.bodies = ()
        with self.assertRaises(pydantic.ValidationError):
            preflight.blast_radius = 2
        with self.assertRaises(pydantic.ValidationError):
            drift.verdict = Verdict.BLOCK

    @covers("REQ-0.33.0-01-02")
    def test_seam_map_two_layer(self) -> None:
        # The four fields exist as separate members.
        self.assertEqual(
            set(SeamMap.model_fields),
            {"bodies", "push_edges", "pull_edges", "unaccounted"},
        )

        push = _edge(SeamKind.PUSH)
        pull = _edge(SeamKind.PULL)
        stray = SeamEdge(
            kind=SeamKind.PUSH,
            provenance=Provenance.OBSERVED,
            source="x",
            target="y",
            accounted=False,
        )
        seam_map = SeamMap(
            bodies=("region-a", "region-b"),
            push_edges=(push,),
            pull_edges=(pull,),
            unaccounted=(stray,),
        )

        # bodies holds region strings; edge fields hold SeamEdge instances.
        for body in seam_map.bodies:
            self.assertIsInstance(body, str)
        for edge in (*seam_map.push_edges, *seam_map.pull_edges):
            self.assertIsInstance(edge, SeamEdge)

        # An unaccounted edge is preserved there and does not leak into the joins.
        self.assertIn(stray, seam_map.unaccounted)
        self.assertNotIn(stray, seam_map.push_edges)
        self.assertNotIn(stray, seam_map.pull_edges)

    @covers("REQ-0.33.0-01-03")
    def test_provenance_non_erasable(self) -> None:
        # The vocabulary is CLOSED to exactly LAW / OBSERVED — no third vein. Rejecting
        # one out-of-enum value proves the set lacks THAT value, never that it lacks
        # every other; without this, adding Provenance.FABRICATED passes every assertion
        # below. A smuggled third vein in a non-erasable L2 field is what the
        # state-doctrine section-2 guard exists to prevent.
        self.assertEqual([p.value for p in Provenance], ["LAW", "OBSERVED"])

        # (a) An out-of-enum provenance value is rejected at construction.
        with self.assertRaises(pydantic.ValidationError):
            SeamEdge(
                kind=SeamKind.PUSH,
                provenance="observed",  # lowercase is not a member value
                source="a",
                target="b",
                accounted=True,
            )
        # (b) Reassigning provenance on a constructed edge is rejected (frozen).
        edge = _edge()
        with self.assertRaises(pydantic.ValidationError):
            edge.provenance = Provenance.OBSERVED

    @covers("REQ-0.33.0-01-04")
    def test_preflight_and_driftdiff_shape(self) -> None:
        # Each vocabulary is CLOSED to exactly its declared members — the "closed
        # StrEnum" half of the REQ, which out-of-enum rejection alone cannot prove.
        self.assertEqual([k.value for k in SeamKind], ["push", "pull"])
        self.assertEqual([a.value for a in Authority], ["captain", "delegated"])
        self.assertEqual([d.value for d in Decision], ["proceed", "pause", "hold", "revert"])
        self.assertEqual([v.value for v in Verdict], ["clean", "block", "surface", "resolve"])

        seam_map = SeamMap(bodies=(), push_edges=(), pull_edges=(), unaccounted=())
        # Valid instances construct.
        Preflight(
            seam_map=seam_map,
            blast_radius=0,
            authority=Authority.DELEGATED,
            decision=Decision.HOLD,
        )
        DriftDiff(drift=(), verdict=Verdict.SURFACE, resolutions=("noted",))

        # decision accepts None.
        pf = Preflight(
            seam_map=seam_map,
            blast_radius=0,
            authority=Authority.CAPTAIN,
            decision=None,
        )
        self.assertIsNone(pf.decision)

        # Out-of-enum values are rejected on kind / authority / decision / verdict.
        with self.assertRaises(pydantic.ValidationError):
            SeamEdge(
                kind="sideways",
                provenance=Provenance.LAW,
                source="a",
                target="b",
                accounted=True,
            )
        with self.assertRaises(pydantic.ValidationError):
            Preflight(
                seam_map=seam_map,
                blast_radius=0,
                authority="admiral",
                decision=None,
            )
        with self.assertRaises(pydantic.ValidationError):
            Preflight(
                seam_map=seam_map,
                blast_radius=0,
                authority=Authority.CAPTAIN,
                decision="maybe",
            )
        with self.assertRaises(pydantic.ValidationError):
            DriftDiff(drift=(), verdict="fuzzy", resolutions=())

    def test_load_schema_matches_projection(self) -> None:
        # Drift guard, not a REQ proof: REQ-0.33.0-01-05 is [SUPPORT], whose channel
        # is a ledger event + `gz validate --documents` — never `@covers`
        # (.claude/rules/tests.md § REQ Scope Discipline). The committed projection
        # must not drift from the model; docstrings render as schema descriptions.
        self.assertEqual(load_schema("seam_map"), seam_map_json_schema())


if __name__ == "__main__":
    unittest.main()
