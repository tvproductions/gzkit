"""Gate5 floor enrollment-completeness enumeration (GHI #648).

ADR-0.0.74 § Boundary Invariants #9: "Every gate5 floor member's enforcement is
live — enrollment completeness is enumerated. The meta-validator's gate5
claim-source enumerates ``GATE5_INVARIANTS`` membership and requires each member
to carry an ``@enforces`` entry with a passing un-forced NC; a member with no
entry fails the floor (so a future sixth member added without an NC cannot ride
as a facade)."

The floor audit verifies the claims that happen to be *registered*, which is
structurally incapable of noticing an *absence*. These tests pin the dual
check — enumerate membership, demand each member be present — and cover both
absence shapes:

  (a) a floor member with no ``@enforces`` entry declared at all (the future
      sixth member the invariant names);
  (b) a member whose entry exists but whose claim source never reaches
      ``_ensure_production_claims_registered`` (the orphan GHI #648 *was*).
"""

from __future__ import annotations

import unittest
from unittest import mock

from gzkit.enforcement import (
    _ensure_production_claims_registered,
    registered_claims,
    reset_enforcement_registry,
    run_meta_validator,
)
from gzkit.mx import invariants
from gzkit.mx.invariants import GATE5_INVARIANTS, unenrolled_gate5_members


class TestGate5EnrollmentCompleteness(unittest.TestCase):
    """The enumeration itself — membership drives the check, not the registry."""

    def tearDown(self) -> None:
        # The enumeration tests do not mutate the registry, but the meta-validator
        # test below registers production claims; reset so ordering cannot leak.
        reset_enforcement_registry()

    def test_production_floor_is_fully_enrolled(self) -> None:
        """Every current gate5 floor member's enforcement is live.

        This is the standing regression pin: it fails the moment a floor member
        is added to GATE5_INVARIANTS without wiring its claim through to the
        production-discovery seam.
        """
        _ensure_production_claims_registered()
        self.assertEqual(
            [],
            unenrolled_gate5_members(registered_claims()),
            "every GATE5_INVARIANTS member must carry a discovered @enforces entry "
            "(ADR-0.0.74 § Boundary Invariants #9)",
        )

    def test_member_with_no_enforces_entry_is_unenrolled(self) -> None:
        """Absence shape (a): a future sixth member with no entry cannot ride as a facade."""
        every_mapped_claim = list(invariants._GATE5_MEMBER_CLAIMS.values())
        with mock.patch.object(invariants, "GATE5_INVARIANTS", GATE5_INVARIANTS | {"future-guard"}):
            unenrolled = dict(unenrolled_gate5_members(every_mapped_claim))

        self.assertIn(
            "future-guard",
            unenrolled,
            "a floor member with no @enforces entry must fail the floor, not be "
            "silently absent from it",
        )

    def test_declared_but_undiscovered_claim_is_unenrolled(self) -> None:
        """Absence shape (b): the literal GHI #648 orphan — entry authored, never wired.

        Passing an empty registered-claims set models the pre-fix state in which
        the gate5 and grader-gaming sources had @enforces entries that
        ``_ensure_production_claims_registered`` never reached.
        """
        unenrolled = dict(unenrolled_gate5_members([]))

        for member in ("ledger", "gate5-attestation", "grader-gaming"):
            with self.subTest(member=member):
                self.assertIn(
                    member,
                    unenrolled,
                    f"floor member {member!r} whose claim never reaches production "
                    "discovery is an orphan and must fail the floor",
                )

    def test_honest_negative_members_are_exempt(self) -> None:
        """``secrets`` / ``operator-pii`` are named-not-enforced, not unenrolled.

        ADR-0.0.74 § Consequences/Negative #7: no unified gate5 secrets/PII gate
        exists, and binding a narrower proxy to fake coverage is forbidden. The
        enumeration must not pressure a future agent into that forbidden bind.
        """
        unenrolled = dict(unenrolled_gate5_members([]))

        for member in ("secrets", "operator-pii"):
            with self.subTest(member=member):
                self.assertNotIn(
                    member,
                    unenrolled,
                    f"{member!r} is an honest-negative named-not-enforced member; "
                    "the enumeration must exempt it rather than demand a proxy bind",
                )

    def test_meta_validator_fails_closed_on_an_unenrolled_member(self) -> None:
        """The enumeration reaches the floor audit as FACADE, not a silent pass.

        Without this wiring the enumeration would be a library function nothing
        consults — the same facade shape one layer up.
        """
        with mock.patch.object(invariants, "GATE5_INVARIANTS", GATE5_INVARIANTS | {"future-guard"}):
            result = run_meta_validator(root=None)

        facades = [r for r in result.claim_results if r.outcome == "FACADE"]
        self.assertTrue(
            any("future-guard" in r.claim_id for r in facades),
            "an unenrolled floor member must surface as a FACADE claim result so "
            f"run_enforcement_floor_audit fails closed; got outcomes: "
            f"{sorted({r.outcome for r in result.claim_results})}",
        )

    def test_every_mapped_claim_names_a_real_floor_member(self) -> None:
        """The member->claim map cannot drift ahead of the floor it describes."""
        self.assertEqual(
            set(),
            set(invariants._GATE5_MEMBER_CLAIMS) - GATE5_INVARIANTS,
            "_GATE5_MEMBER_CLAIMS maps a name that is not a GATE5_INVARIANTS member",
        )
        self.assertEqual(
            set(),
            set(invariants._GATE5_MEMBER_CLAIMS) & invariants._GATE5_NAMED_NOT_ENFORCED,
            "an honest-negative member must not also carry a bound claim mapping",
        )


if __name__ == "__main__":
    unittest.main()
