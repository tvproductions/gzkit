"""Tests for the airlock-IN primitive (OBPI-0.33.0-02).

Assertions derive from the brief's Acceptance Criteria
(REQ-0.33.0-02-01 through REQ-0.33.0-02-05), NOT from a run of the
implementation. The primitive is exercised with an injected fake ``reach_fn``
so the core runs with NO ontology projection built (hexagonal rule 6).
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from gzkit.airlock.enter import CaptainOverride, airlock_enter, build_refusal
from gzkit.airlock.model import Authority, Decision
from gzkit.ledger import Ledger
from gzkit.traceability import covers

_BRIEF_ACCOUNTED = """# Brief

## Allowed Paths

- `src/gzkit/airlock/enter.py`
- `tests/test_airlock_enter.py`

The entry accounts for DEP-ACCOUNTED and INV-ACCOUNTED as declared seams.
"""

_BRIEF_UNACCOUNTED = """# Brief

## Allowed Paths

- `src/gzkit/airlock/enter.py`
- `tests/test_airlock_enter.py`

Only DEP-ACCOUNTED is named as a declared seam; the second reach dependent
is deliberately never named, so it stays un-accounted.
"""


class _AirlockEnterCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self._brief_seq = 0

    def _brief(self, text: str) -> Path:
        self._brief_seq += 1
        path = self.tmp / f"brief-{self._brief_seq}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def _ledger(self) -> Ledger:
        return Ledger(self.tmp / "ledger.jsonl")


class TestThreeBeat(_AirlockEnterCase):
    @covers("REQ-0.33.0-02-01")
    def test_three_beat_pings_books_l2_and_never_attests(self) -> None:
        brief = self._brief(_BRIEF_ACCOUNTED)
        pinged: list[str] = []

        def fake_reach(node_id: str) -> list[str]:
            pinged.append(node_id)
            return ["DEP-ACCOUNTED"]

        ledger = self._ledger()
        preflight = airlock_enter("OBPI-X", brief, reach_fn=fake_reach, ledger=ledger)

        self.assertEqual(pinged, ["OBPI-X"], "PING beat must call reach_fn(target)")
        # PING is ADVISORY, not the verdict: reach returned DEP-ACCOUNTED, which is
        # named in the brief, so the gate reconciles it as accounted and reaches
        # PROCEED from the accounting — not from the raw reach reading. Paired with
        # TestUnaccountedSeamBlocksGo (same non-empty reach, unaccounted -> HOLD),
        # this proves reach INFORMS but never DECIDES (REQ-01; state-doctrine Rule 5).
        self.assertIs(
            preflight.decision,
            Decision.PROCEED,
            "a fully-accounted entry proceeds; the decision derives from accounting, "
            "not from the raw PING reading",
        )
        booked = {e.event for e in ledger.read_all()}
        self.assertIn("airlock_in", booked, "the transit books an airlock_in event")
        self.assertNotIn(
            "attested",
            booked,
            "acknowledge-and-decide is NOT a Gate-5 completion attestation (BI #3)",
        )


class TestSeamMap(_AirlockEnterCase):
    @covers("REQ-0.33.0-02-02")
    def test_two_layer_seam_map_bodies_declared_push_from_reach(self) -> None:
        brief = self._brief(_BRIEF_ACCOUNTED)

        preflight = airlock_enter(
            "OBPI-X",
            brief,
            parent_invariants=("INV-ACCOUNTED",),
            reach_fn=lambda _node: ["DEP-ACCOUNTED"],
        )
        seam_map = preflight.seam_map

        self.assertEqual(
            seam_map.bodies,
            ("src/gzkit/airlock/enter.py", "tests/test_airlock_enter.py"),
            "bodies must equal the DECLARED Allowed Paths, read from L1 (never inferred)",
        )
        push_targets = {edge.target for edge in seam_map.push_edges}
        self.assertIn(
            "DEP-ACCOUNTED",
            push_targets,
            "a known reach dependent must surface as a push edge",
        )
        pull_targets = {edge.target for edge in seam_map.pull_edges}
        self.assertIn(
            "INV-ACCOUNTED",
            pull_targets,
            "a declared parent-ADR invariant must surface as a pull edge",
        )
        # No statistical body inference: every body is a declared path, never a
        # reach-derived artifact id or an invariant (parent ADR § Negative #2).
        self.assertNotIn("DEP-ACCOUNTED", seam_map.bodies)
        self.assertNotIn("INV-ACCOUNTED", seam_map.bodies)


class TestUnaccountedSeamBlocksGo(_AirlockEnterCase):
    @covers("REQ-0.33.0-02-03")
    def test_unaccounted_reach_edge_makes_go_unreachable(self) -> None:
        brief = self._brief(_BRIEF_UNACCOUNTED)

        # DEP-HIDDEN is a real reach push edge omitted from the declared seam-set.
        preflight = airlock_enter(
            "OBPI-X",
            brief,
            reach_fn=lambda _node: ["DEP-ACCOUNTED", "DEP-HIDDEN"],
        )

        self.assertIsNot(
            preflight.decision,
            Decision.PROCEED,
            "an un-accounted seam makes GO structurally unreachable (BI #4)",
        )
        self.assertIs(
            preflight.decision,
            Decision.HOLD,
            "fail-closed: absence of accounting is a NO-GO, never a default-proceed",
        )
        hidden = {edge.target for edge in preflight.seam_map.unaccounted}
        self.assertEqual(hidden, {"DEP-HIDDEN"}, "the omitted edge is the un-accounted seam")


class TestDiagnosticRefusal(_AirlockEnterCase):
    @covers("REQ-0.33.0-02-04")
    def test_refusal_names_seam_provenance_and_resense(self) -> None:
        brief = self._brief(_BRIEF_UNACCOUNTED)

        preflight = airlock_enter(
            "OBPI-X",
            brief,
            parent_invariants=("INV-HIDDEN",),
            reach_fn=lambda _node: ["DEP-ACCOUNTED", "DEP-HIDDEN"],
        )
        message = build_refusal(preflight.seam_map, "OBPI-X")

        # (a) the exact un-accounted seam ids
        self.assertIn("DEP-HIDDEN", message, "refusal must name the un-accounted push seam")
        self.assertIn("INV-HIDDEN", message, "refusal must name the un-accounted pull seam")
        # (b) provenance: direction AND vein
        self.assertIn("push-from-reach", message, "push seam names its direction")
        self.assertIn("pull-from-invariant", message, "pull seam names its direction")
        self.assertIn("OBSERVED", message, "push-from-reach carries the OBSERVED vein")
        self.assertIn("LAW", message, "pull-from-invariant carries the LAW vein")
        # (c) one-command re-sense with the real target interpolated
        self.assertIn(
            "gz ontology resense OBPI-X",
            message,
            "refusal must offer the one-command re-sense (never a bare NO-GO)",
        )


class TestCaptainOverrideAndDelegationDial(_AirlockEnterCase):
    @covers("REQ-0.33.0-02-05")
    def test_override_logged_and_revocable(self) -> None:
        brief = self._brief(_BRIEF_UNACCOUNTED)
        ledger = self._ledger()
        override = CaptainOverride(attestor="g0", seam="DEP-HIDDEN")

        preflight = airlock_enter(
            "OBPI-X",
            brief,
            reach_fn=lambda _node: ["DEP-ACCOUNTED", "DEP-HIDDEN"],
            override=override,
            ledger=ledger,
        )

        self.assertIs(
            preflight.decision,
            Decision.PROCEED,
            "a captain override of a NO-GO permits the transit",
        )
        events = ledger.read_all()
        self.assertTrue(events, "the override transit is booked to L2")
        payload = events[-1].extra
        self.assertEqual(payload.get("override_seam"), "DEP-HIDDEN")
        self.assertEqual(payload.get("override_attestor"), "g0")

        revoked = airlock_enter(
            "OBPI-X",
            brief,
            reach_fn=lambda _node: ["DEP-ACCOUNTED", "DEP-HIDDEN"],
            override=CaptainOverride(attestor="g0", seam="DEP-HIDDEN", revoked=True),
        )
        self.assertIsNot(
            revoked.decision,
            Decision.PROCEED,
            "a revoked override restores the NO-GO",
        )

    @covers("REQ-0.33.0-02-05")
    def test_blast_radius_is_delegation_dial_only(self) -> None:
        accounted = self._brief(_BRIEF_ACCOUNTED)

        delegated = airlock_enter(
            "OBPI-X",
            accounted,
            reach_fn=lambda _node: ["DEP-ACCOUNTED"],
            blast_radius=1,
        )
        self.assertIs(delegated.decision, Decision.PROCEED)
        self.assertIs(
            delegated.authority,
            Authority.DELEGATED,
            "a small, fully-accounted entry may auto-proceed under delegation",
        )

        unaccounted = self._brief(_BRIEF_UNACCOUNTED)
        blocked = airlock_enter(
            "OBPI-X",
            unaccounted,
            reach_fn=lambda _node: ["DEP-ACCOUNTED", "DEP-HIDDEN"],
            blast_radius=1000,
        )
        self.assertIsNot(
            blocked.decision,
            Decision.PROCEED,
            "blast_radius is never a responsibility dial: an un-accounted seam is "
            "never auto-proceeded by blast_radius alone",
        )


class TestStage1AirlockGate(_AirlockEnterCase):
    """REQ-0.33.0-02-06: airlock_enter is reached at the pipeline Stage-1 seam."""

    def _project(self) -> Path:
        (self.tmp / ".gzkit").mkdir(exist_ok=True)
        return self.tmp

    @covers("REQ-0.33.0-02-06")
    def test_stage1_gate_reaches_primitive_and_books_l2(self) -> None:
        from gzkit.pipeline_runtime import check_airlock_in_gate

        brief = self._brief(_BRIEF_ACCOUNTED)
        root = self._project()

        blockers = check_airlock_in_gate(
            "OBPI-X", brief, root, reach_fn=lambda _node: ["DEP-ACCOUNTED"]
        )

        self.assertEqual(
            blockers,
            [],
            "a fully-accounted entry crosses the Stage-1 airlock gate (no blockers)",
        )
        booked = {e.event for e in Ledger(root / ".gzkit" / "ledger.jsonl").read_all()}
        self.assertIn(
            "airlock_in",
            booked,
            "the Stage-1 pre-flight seam reaches airlock_enter and books airlock_in to L2",
        )

    @covers("REQ-0.33.0-02-06")
    def test_stage1_gate_blocks_on_unaccounted_seam(self) -> None:
        from gzkit.pipeline_runtime import check_airlock_in_gate

        brief = self._brief(_BRIEF_UNACCOUNTED)
        root = self._project()

        blockers = check_airlock_in_gate(
            "OBPI-X", brief, root, reach_fn=lambda _node: ["DEP-ACCOUNTED", "DEP-HIDDEN"]
        )

        self.assertTrue(
            blockers,
            "an un-accounted seam yields a Stage-1 blocker (surfaced as a diagnostic "
            "warning at the call site until real-entry calibration lands)",
        )
        self.assertIn(
            "DEP-HIDDEN",
            blockers[0],
            "the blocker is the diagnostic refusal naming the un-accounted seam "
            "(never a bare NO-GO)",
        )

    @covers("REQ-0.33.0-02-06")
    def test_gate_is_wired_into_stage1_call_site_not_orphan(self) -> None:
        import inspect

        from gzkit.commands import obpi_cmd

        self.assertTrue(
            hasattr(obpi_cmd, "check_airlock_in_gate"),
            "the airlock gate is imported into obpi_cmd (wired, not an orphan)",
        )
        # Wiring chain: obpi_pipeline_cmd -> _run_airlock_in_diagnostic -> check_airlock_in_gate.
        # The diagnostic is extracted into its own helper to keep obpi_pipeline_cmd under the
        # xenon C ceiling; the test follows the chain rather than pinning the call to one frame.
        pipeline_source = inspect.getsource(obpi_cmd.obpi_pipeline_cmd)
        self.assertIn(
            "_run_airlock_in_diagnostic",
            pipeline_source,
            "obpi_pipeline_cmd reaches the airlock at the Stage-1 pre-flight seam",
        )
        diagnostic_source = inspect.getsource(obpi_cmd._run_airlock_in_diagnostic)
        self.assertIn(
            "check_airlock_in_gate",
            diagnostic_source,
            "the Stage-1 diagnostic invokes the airlock gate (the wiring is real, not an orphan)",
        )


class TestAirlockEnforcementClaimRegistration(unittest.TestCase):
    """REQ-0.33.0-02-07 (SUPPORT): the §5 enforcement claim is registered and un-orphaned.

    SUPPORT-kind proof channel is the ledger event + structural validator, NOT a
    ``@covers`` behavior test (ADR-0.0.59). These plain unit tests assert the
    registration function is reachable from the single production-discovery seam
    and that the un-forced negative control genuinely bites.
    """

    def setUp(self) -> None:
        from gzkit.enforcement import reset_enforcement_registry

        reset_enforcement_registry()
        self.addCleanup(reset_enforcement_registry)

    def test_ensure_airlock_claims_registers_the_claim(self) -> None:
        from gzkit.airlock.enter import _ensure_airlock_claims_registered
        from gzkit.enforcement import get_enforcement_registry

        _ensure_airlock_claims_registered()

        claims = {r.claim_id for r in get_enforcement_registry()}
        self.assertIn("airlock-in-unaccounted-seam", claims)

    def test_claim_reachable_from_production_registration_seam(self) -> None:
        from gzkit.enforcement import (
            _ensure_production_claims_registered,
            get_enforcement_registry,
        )

        _ensure_production_claims_registered()

        claims = {r.claim_id for r in get_enforcement_registry()}
        self.assertIn(
            "airlock-in-unaccounted-seam",
            claims,
            "the airlock claim must be reachable from the single production-discovery "
            "seam (a registration authored but un-wired is an ORPHAN — the §5 failure class)",
        )

    def test_airlock_nc_genuinely_bites_un_forced(self) -> None:
        from gzkit.enforcement import (
            _ensure_production_claims_registered,
            get_enforcement_registry,
            run_meta_validator,
        )

        _ensure_production_claims_registered()
        records = [
            r for r in get_enforcement_registry() if r.claim_id == "airlock-in-unaccounted-seam"
        ]
        self.assertEqual(len(records), 1, "exactly one airlock claim registered")

        result = run_meta_validator(registry=records, root=None)

        self.assertEqual(result.facade_count, 0, "the airlock NC is not a facade")
        self.assertEqual(result.test_bug_count, 0, "the airlock NC fixture/entrypoint do not raise")
        self.assertEqual(
            result.verified_count,
            1,
            "the un-forced airlock NC PASSES: production _decide computes HOLD on an "
            "un-accounted seam — no forcing kwarg pre-binds the verdict",
        )

    def test_nc_catches_the_sentinel_special_case_mutation(self) -> None:
        """The §5 NC must be un-gameable, not merely green (Step-4b hardening, 2026-07-11).

        A Step-4b adversary refuted the prior NC: it used a FIXED sentinel dependent
        and only asserted "not PROCEED", so a broken ``_decide`` that HELD only for
        that one guessable string passed the control while failing to block every
        other un-accounted seam. This test pins the fix: the NC's own entrypoint must
        return falsy (FACADE) under three distinct broken gates — a sentinel-special-
        case, an always-PROCEED, and an always-HOLD. If any mutation slips through,
        the NC has decayed back into theatre.
        """
        import gzkit.airlock.enter as airlock_mod

        original = airlock_mod._decide
        root = airlock_mod._build_unaccounted_seam_violation()
        try:

            def sentinel_special_case(unaccounted, override):  # type: ignore[no-untyped-def]
                # Recognizes the OLD fixed sentinel; blind to the runtime-unique id.
                fixed = any(edge.target == "DEP-UNACCOUNTED-NC" for edge in unaccounted)
                if fixed and (override is None or override.revoked):
                    return Decision.HOLD
                return Decision.PROCEED

            mutations = {
                "sentinel-special-case": sentinel_special_case,
                "always-proceed": lambda _u, _o: Decision.PROCEED,
                "always-hold": lambda _u, _o: Decision.HOLD,
            }
            for name, mutation in mutations.items():
                airlock_mod._decide = mutation
                bit = airlock_mod._ep_airlock_unaccounted_seam(root)
                self.assertEqual(
                    bit,
                    0,
                    f"the {name} mutation must be caught (NC returns falsy) — a gate that "
                    "does not track accountedness for an arbitrary seam is a facade",
                )

            airlock_mod._decide = original
            self.assertEqual(
                airlock_mod._ep_airlock_unaccounted_seam(root),
                1,
                "the genuine gate still bites (control for the mutation assertions above)",
            )
        finally:
            airlock_mod._decide = original
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
