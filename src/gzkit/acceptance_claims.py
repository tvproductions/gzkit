"""Enforcement claims for the Step-4b acceptance gate (GHI #1155, gates GHI #959 and #960).

``gz obpi complete`` refuses completion through ``acceptance_store.completion_review``, and
``gz obpi precomplete`` through ``acceptance_blockers``; both reach
``acceptance.assess_readiness``, which decides readiness from the whole review history. GHI
#985 moved the Step-4b refusal there from ``obpi_complete_adversarial``'s verdict gate,
which no production path calls since. The claims first registered for #959 and #960 named
that unwired function, so they witnessed nothing that runs.

#959 and #960 were one defect: a refutation was cleared by something that is not a repair
(a caveat, then a resolution string). In the acceptance model a refutation is a mapped
finding, and only an independent closure that names the repairing proof clears it.

Two claims, on the exemption-half precedent (GHI #797).

* ``adversarial-refutation-loops`` plants, for each finding kind, an adversarial refutation
  followed by the present-but-false clearance: the refuting review still approves the proof,
  and a later adversarial review passes it without closing the finding. Readiness must be
  refused for the open finding.
* ``adversarial-clean-verdict-admitted`` is the admit control: a clean adversarial review,
  and a refutation followed by a verified independent closure, both reach readiness, so an
  always-refuse reducer cannot discharge the first claim alone.
"""

from __future__ import annotations

from typing import Any, get_args

REFUSE_CLAIM_ID = "adversarial-refutation-loops"
ADMIT_CLAIM_ID = "adversarial-clean-verdict-admitted"
ACCEPTANCE_GATE_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

_OPEN = "requires verified closure"
_OBLIGATION = "REQ-0.0.0-00-01"
_DIGEST = "claim-fixture-input"
_FINDING_ID = "claim-finding"


def refutation_population() -> list[str]:
    """Return every kind of finding an adversarial review can map onto an obligation.

    Read from the ``Finding.kind`` vocabulary, never from the reducer under test, so a kind
    added later is planted until the claim is shown to hold for it.
    """
    from gzkit.acceptance import Finding  # noqa: PLC0415

    return list(get_args(Finding.model_fields["kind"].annotation))


def _build_kind(member: str = "counterexample") -> str:
    """Name the finding kind to plant; the runner passes each declared member."""
    return member


def _records(*, repaired: bool = False) -> dict[str, Any]:
    """Return one obligation, its proof and the proof that repairs it."""
    from gzkit.acceptance import Obligation, Proof  # noqa: PLC0415

    def proof(proof_id: str) -> Proof:
        return Proof(
            id=proof_id,
            obligation_id=_OBLIGATION,
            contract_digest="claim-contract",
            input_digest=_DIGEST,
            selectors=("tests.claim_fixture.TestClaim.test_behavior",),
            evidence='{"baseline":"passed"}',
            valid=True,
        )

    obligation = Obligation(
        id=_OBLIGATION,
        kind="BEHAVIOR",
        statement="claim fixture behavior",
        authority="claim-fixture",
        contract_digest="claim-contract",
    )
    proofs = (
        (proof("proof-original"), proof("proof-repair")) if repaired else (proof("proof-original"),)
    )
    return {"obligation": obligation, "proofs": proofs}


def _review(stage: str, review_id: str, proof_ids: tuple[str, ...], **changes: Any) -> Any:
    """Return an independent review of the fixture obligation approving *proof_ids*."""
    from gzkit.acceptance import Review  # noqa: PLC0415

    values: dict[str, Any] = {
        "id": review_id,
        "stage": stage,
        "input_digest": _DIGEST,
        "obligation_ids": (_OBLIGATION,),
        "proof_ids": proof_ids,
        "accepted_proof_ids": proof_ids,
        "receipt_id": f"receipt-{review_id}",
        "reviewer_id": "claim-reviewer",
    }
    values.update(changes)
    return Review.model_validate(values)


def _refutation(kind: str) -> Any:
    """Return an adversarial review that refutes yet still approves the proof."""
    from gzkit.acceptance import Finding  # noqa: PLC0415

    finding = Finding.model_validate(
        {
            "id": _FINDING_ID,
            "obligation_id": _OBLIGATION,
            "kind": kind,
            "description": "claim fixture defect",
        }
    )
    return _review(
        "adversarial", "adv-refutes", ("proof-original",), verdict="refuted", findings=(finding,)
    )


def _assess(gate: Any, records: dict[str, Any], reviews: tuple[Any, ...]) -> Any:
    """Run the real reducer *gate* at Stage 4 over the fixture history."""
    return gate(
        (records["obligation"],),
        records["proofs"],
        reviews,
        input_digest=_DIGEST,
        author_id="claim-implementer",
    )


def _closing_review() -> Any:
    """Return an independent adversarial review that verifies the repair of the finding."""
    from gzkit.acceptance import Closure  # noqa: PLC0415

    closure = Closure(finding_id=_FINDING_ID, obligation_id=_OBLIGATION, proof_id="proof-repair")
    return _review("adversarial", "adv-closes", ("proof-repair",), closures=(closure,))


def _approvals(proof_id: str) -> tuple[Any, ...]:
    return tuple(
        _review(stage, f"{stage}-{proof_id}", (proof_id,)) for stage in ("spec", "quality")
    )


# Each entrypoint imports the reducer itself: the registry derives a claim's `gate_targets`
# from the entrypoint's own imports (GHI #798), so a helper doing the import would leave
# the claim naming no gate at all.


def _ep_refutation_loops(kind: str) -> list[str]:
    """Return a finding naming *kind* when a refutation cleared without closure is refused."""
    from gzkit.acceptance import assess_readiness  # noqa: PLC0415

    records = _records()
    later_pass = _review("adversarial", "adv-passes", ("proof-original",))
    readiness = _assess(
        assess_readiness, records, (*_approvals("proof-original"), _refutation(kind), later_pass)
    )
    open_finding = _FINDING_ID in readiness.open_findings
    refused = not readiness.ready and any(_OPEN in b for b in readiness.blockers)
    return [f"{kind}: {_OPEN}"] if open_finding and refused else []


def _ep_clean_verdict_admitted(kind: str) -> int:
    """Truthy only when a clean round, and a *kind* refutation closed, both reach readiness."""
    from gzkit.acceptance import assess_readiness  # noqa: PLC0415

    clean = _assess(
        assess_readiness,
        _records(),
        (*_approvals("proof-original"), _review("adversarial", "adv-clean", ("proof-original",))),
    )
    repaired = _assess(
        assess_readiness,
        _records(repaired=True),
        (
            _refutation(kind),
            *_approvals("proof-repair"),
            _closing_review(),
        ),
    )
    return 1 if clean.ready and repaired.ready else 0


class _AcceptanceGateMarker:
    """Inert carrier for the acceptance-gate ``@enforces`` registrations."""


def ensure_acceptance_gate_claims_registered() -> None:
    """(Re)register the Step-4b acceptance-gate claims (idempotent, reset-safe).

    MUST stay wired into ``enforcement._ensure_production_claims_registered``: a
    registration authored but un-wired there is an ORPHAN whose floor membership is a
    facade.
    """
    from gzkit.enforcement import (  # noqa: PLC0415
        EXEMPTS_NONE,
        POPULATION_NONE,
        enforces,
        extend_known_claims,
        get_enforcement_registry,
    )

    extend_known_claims(ACCEPTANCE_GATE_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            _build_kind,
            _ep_refutation_loops,
            expect=_OPEN,
            exempts=ADMIT_CLAIM_ID,
            population=refutation_population,
        )(_AcceptanceGateMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            _build_kind,
            _ep_clean_verdict_admitted,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_AcceptanceGateMarker)
