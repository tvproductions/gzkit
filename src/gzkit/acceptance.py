"""Preserve acceptance obligations and independently reviewed closure.

This reducer consumes execution and receipt-bound review records supplied by
the acceptance store. It validates their identities and relationships; it does
not infer semantic test adequacy from metadata or authenticate raw receipts.
Historical reviews and findings remain inputs even after replacement proofs.
"""

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AcceptanceModel(BaseModel):
    """Immutable records, with tuples to prevent nested collection mutation."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Obligation(AcceptanceModel):
    """One approved requirement or canonical invariant and its proof channel."""

    id: str = Field(min_length=1, description="Stable canonical acceptance obligation identity")
    kind: Literal["BEHAVIOR", "SUPPORT", "STRUCTURAL-FENCE"] = Field(
        description="Canonical requirement proof channel"
    )
    statement: str = Field(min_length=1, description="Approved behavior or invariant")
    authority: str = Field(min_length=1, description="Canonical requirement or invariant reference")
    contract_digest: str = Field(min_length=1, description="Digest of the approved contract")


class Proof(AcceptanceModel):
    """Executed proof; the producer derives validity from the recorded runs."""

    id: str = Field(min_length=1, description="Unique immutable proof identity")
    obligation_id: str = Field(min_length=1, description="Obligation this proof addresses")
    contract_digest: str = Field(min_length=1, description="Contract used to execute the proof")
    input_digest: str = Field(min_length=1, description="Digest of actual execution inputs")
    selectors: tuple[str, ...] = Field(default=(), description="Fully qualified executed test IDs")
    evidence: str = Field(description="Exact serialized execution evidence payload")
    valid: bool = Field(description="Validity derived by the producer from observed execution")


class Finding(AcceptanceModel):
    """A mapped acceptance defect or a retained auxiliary observation."""

    id: str = Field(min_length=1, description="Stable finding identity retained across rounds")
    obligation_id: str | None = Field(
        default=None, description="Canonical obligation; absent for auxiliary observations"
    )
    kind: Literal["counterexample", "missing-proof"] = Field(description="Reason for the finding")
    description: str = Field(min_length=1, description="Concrete violation or missing evidence")


class Closure(AcceptanceModel):
    """An enclosing independent review verifies this original finding's repair."""

    finding_id: str = Field(min_length=1, description="Original finding independently verified")
    obligation_id: str = Field(min_length=1, description="Original acceptance obligation retained")
    proof_id: str = Field(min_length=1, description="Exact proof independently judged to close it")


class Review(AcceptanceModel):
    """A receipt-bound judgment of explicitly named obligations and proofs."""

    id: str = Field(min_length=1, description="Unique immutable review identity")
    stage: Literal["spec", "quality", "adversarial"] = Field(description="Review responsibility")
    input_digest: str = Field(min_length=1, description="Actual input snapshot reviewed")
    obligation_ids: tuple[str, ...] = Field(description="Explicit acceptance subject of the review")
    proof_ids: tuple[str, ...] = Field(description="Exact proof records examined")
    accepted_proof_ids: tuple[str, ...] = Field(
        default=(), description="Examined proofs explicitly approved independently of raw verdict"
    )
    findings: tuple[Finding, ...] = Field(default=(), description="New or reaffirmed findings")
    closures: tuple[Closure, ...] = Field(default=(), description="Independently verified repairs")
    receipt_id: str = Field(min_length=1, description="Execution receipt containing this review")
    reviewer_id: str = Field(min_length=1, description="Named reviewer bound to receipt provenance")
    verdict: Literal["accepted", "refuted"] = Field(
        default="accepted",
        description="Preserved overall review token; never grants proof approval",
    )
    tier: Literal[1, 2, 3] = Field(default=1, description="Recorded review transport tier")
    fallback_reason: str = Field(
        default="", description="Recorded reason for a degraded review tier"
    )


class Readiness(AcceptanceModel):
    """Derived status; no authored standing-verdict line controls this result."""

    ready: bool = Field(
        description="Whether current proof and independent closure satisfy the stage"
    )
    blockers: tuple[str, ...] = Field(description="Concrete unsatisfied acceptance conditions")
    open_findings: tuple[str, ...] = Field(description="Mapped findings lacking current closure")


class _ReviewState(BaseModel):
    """Private working state rebuilt from the complete append-only history."""

    model_config = ConfigDict(extra="forbid")

    findings: dict[str, Finding] = Field(default_factory=dict, description="All recorded findings")
    closures: dict[str, str] = Field(
        default_factory=dict, description="Last closure proof per finding"
    )
    judgments: dict[tuple[str, str], str] = Field(
        default_factory=dict, description="Explicit proof approvals by stage; raw verdicts excluded"
    )
    errors: list[str] = Field(default_factory=list, description="Malformed record relationships")


def _index_records(records: Sequence, subject: str, errors: list[str]) -> dict:
    indexed = {}
    for record in records:
        if record.id in indexed:
            errors.append(f"Duplicate {subject} identity: {record.id}")
        else:
            indexed[record.id] = record
    return indexed


def _current_proofs(
    obligations: dict[str, Obligation], proofs: Sequence[Proof], errors: list[str]
) -> dict[str, Proof]:
    current = {}
    for proof in proofs:
        if proof.obligation_id not in obligations:
            errors.append(f"Proof {proof.id} names unknown obligation {proof.obligation_id}")
        else:
            current[proof.obligation_id] = proof
    return current


def _proof_blockers(obligation: Obligation, proof: Proof | None, input_digest: str) -> list[str]:
    if proof is None:
        return [f"{obligation.id}: missing proof"]
    errors = []
    if proof.contract_digest != obligation.contract_digest:
        errors.append(f"{obligation.id}: proof {proof.id} has stale contract")
    if proof.input_digest != input_digest:
        errors.append(f"{obligation.id}: proof {proof.id} has stale inputs")
    if not proof.valid or not proof.evidence.strip():
        errors.append(f"{obligation.id}: proof {proof.id} lacks valid executed evidence")
    if obligation.kind == "BEHAVIOR" and (
        not proof.selectors or any(not selector.strip() for selector in proof.selectors)
    ):
        errors.append(f"{obligation.id}: behavior proof {proof.id} has no executed selector")
    return errors


def _review_scope_errors(
    review: Review,
    obligations: dict[str, Obligation],
    proofs: dict[str, Proof],
    author_id: str,
) -> list[str]:
    errors = []
    prefix = f"Review {review.id}: "
    if review.reviewer_id == author_id:
        errors.append(prefix + "implementer cannot supply independent review")
    if not review.obligation_ids:
        errors.append(prefix + "empty acceptance scope")
    if len(set(review.obligation_ids)) != len(review.obligation_ids):
        errors.append(prefix + "duplicate obligation scope")
    if len(set(review.proof_ids)) != len(review.proof_ids):
        errors.append(prefix + "duplicate proof scope")
    if len(set(review.accepted_proof_ids)) != len(review.accepted_proof_ids):
        errors.append(prefix + "duplicate accepted proof scope")
    if not set(review.accepted_proof_ids).issubset(review.proof_ids):
        errors.append(prefix + "accepted proof outside examined scope")
    for obligation_id in review.obligation_ids:
        if obligation_id not in obligations:
            errors.append(prefix + f"unknown obligation {obligation_id}")
    errors.extend(_review_proof_scope_errors(review, proofs))
    return errors


def _review_proof_scope_errors(review: Review, proofs: dict[str, Proof]) -> list[str]:
    errors = []
    prefix = f"Review {review.id}: "
    reviewed_obligations = []
    for proof_id in review.proof_ids:
        if proof_id not in proofs:
            errors.append(prefix + f"unknown proof {proof_id}")
            continue
        proof = proofs[proof_id]
        reviewed_obligations.append(proof.obligation_id)
        if proof.input_digest != review.input_digest:
            errors.append(prefix + f"proof {proof_id} input mismatch")
    missing_findings = {
        finding.obligation_id for finding in review.findings if finding.kind == "missing-proof"
    }
    missing = set(review.obligation_ids) - set(reviewed_obligations)
    if (
        not missing.issubset(missing_findings)
        or not set(reviewed_obligations).issubset(review.obligation_ids)
        or len(set(reviewed_obligations)) != len(reviewed_obligations)
    ):
        errors.append(prefix + "proof scope does not match obligation scope")
    return errors


def _record_findings(review: Review, state: _ReviewState) -> None:
    for finding in review.findings:
        previous = state.findings.get(finding.id)
        if previous is not None and previous != finding:
            state.errors.append(f"Finding {finding.id}: identity was rewritten")
            continue
        state.findings[finding.id] = finding
        state.closures.pop(finding.id, None)
        if finding.obligation_id is not None and finding.obligation_id not in review.obligation_ids:
            state.errors.append(f"Finding {finding.id}: obligation outside review scope")


def _record_closures(review: Review, proofs: dict[str, Proof], state: _ReviewState) -> None:
    for closure in review.closures:
        finding = state.findings.get(closure.finding_id)
        proof = proofs.get(closure.proof_id)
        if (
            not _closure_retains_subject(closure, finding, review)
            or proof is None
            or proof.obligation_id != closure.obligation_id
            or not proof.valid
            or not proof.evidence.strip()
        ):
            state.errors.append(
                f"Closure {closure.finding_id}: original finding/proof scope mismatch"
            )
            continue
        state.closures[closure.finding_id] = closure.proof_id


def _closure_retains_subject(closure: Closure, finding: Finding | None, review: Review) -> bool:
    return (
        finding is not None
        and finding.id not in {item.id for item in review.findings}
        and finding.obligation_id == closure.obligation_id
        and closure.obligation_id in review.obligation_ids
        and closure.proof_id in review.proof_ids
        and closure.proof_id in review.accepted_proof_ids
    )


def _reduce_reviews(
    reviews: Sequence[Review],
    obligations: dict[str, Obligation],
    proofs: dict[str, Proof],
    author_id: str,
) -> _ReviewState:
    state = _ReviewState()
    indexed = _index_records(reviews, "review", state.errors)
    receipts: set[str] = set()
    for review in indexed.values():
        scope_errors = _review_scope_errors(review, obligations, proofs, author_id)
        if review.receipt_id in receipts:
            scope_errors.append(f"Review {review.id}: receipt identity was reused")
        receipts.add(review.receipt_id)
        _record_findings(review, state)
        state.errors.extend(scope_errors)
        if scope_errors:
            continue
        _record_closures(review, proofs, state)
        for proof_id in review.accepted_proof_ids:
            state.judgments[(review.stage, proof_id)] = "accepted"
    return state


def _open_findings(
    state: _ReviewState, current: dict[str, Proof], errors: list[str], selected: set[str] | None
) -> tuple[str, ...]:
    outstanding = []
    for finding in state.findings.values():
        if finding.obligation_id is None or (
            selected is not None and finding.obligation_id not in selected
        ):
            continue
        proof = current.get(finding.obligation_id)
        if proof is None or state.closures.get(finding.id) != proof.id:
            outstanding.append(finding.id)
            errors.append(
                f"Finding {finding.id}: {finding.obligation_id} requires verified closure"
            )
    return tuple(outstanding)


def assess_readiness(
    obligations: Sequence[Obligation],
    proofs: Sequence[Proof],
    reviews: Sequence[Review],
    *,
    input_digest: str,
    author_id: str,
    stage: Literal["stage2", "stage4"] = "stage4",
    obligation_ids: tuple[str, ...] | None = None,
    required_review_stages: tuple[Literal["spec", "quality", "adversarial"], ...] | None = None,
) -> Readiness:
    """Derive readiness from current proof and every historical finding.

    The last appended proof per obligation is current. A new proof therefore
    invalidates prior judgments and closures even when its input digest is the
    same. Historical artifact changes outside the digested acceptance subject
    have no effect. Receipt authentication and execution validity belong to the
    producer; semantic adequacy belongs to the named independent reviews.
    An explicit Stage 2 obligation subset supports one task's review; canonical
    identity and historical record validation still covers the entire population.
    Stage 4 always requires every obligation.
    """
    errors: list[str] = []
    if not obligations:
        errors.append("Acceptance has no canonical obligations")
    if not input_digest.strip() or not author_id.strip():
        errors.append("Acceptance requires current input and implementer identities")
    if stage not in ("stage2", "stage4"):
        errors.append(f"Unknown acceptance stage: {stage}")
    obligation_index = _index_records(obligations, "obligation", errors)
    selected = _selected_obligations(obligation_index, obligation_ids, stage, errors)
    proof_index = _index_records(proofs, "proof", errors)
    current = _current_proofs(obligation_index, proofs, errors)
    state = _reduce_reviews(reviews, obligation_index, proof_index, author_id)
    errors.extend(state.errors)
    required_stages = _required_review_channels(stage, required_review_stages, errors)
    for obligation in obligations:
        if obligation.id not in selected:
            continue
        proof = current.get(obligation.id)
        errors.extend(
            _reviewed_proof_blockers(obligation, proof, input_digest, required_stages, state)
        )
    outstanding = _open_findings(
        state, current, errors, selected if obligation_ids is not None else None
    )
    return Readiness(ready=not errors, blockers=tuple(errors), open_findings=outstanding)


def _required_review_channels(
    stage: str, required: tuple[str, ...] | None, errors: list[str]
) -> tuple[str, ...]:
    if required is None:
        return ("spec", "quality") if stage == "stage2" else ("spec", "quality", "adversarial")
    if len(set(required)) != len(required) or not set(required).issubset(
        {"spec", "quality", "adversarial"}
    ):
        errors.append("Required review stages must be unique canonical review channels")
    return required


def _reviewed_proof_blockers(
    obligation: Obligation,
    proof: Proof | None,
    input_digest: str,
    stages: tuple[str, ...],
    state: _ReviewState,
) -> list[str]:
    errors = _proof_blockers(obligation, proof, input_digest)
    if proof is not None:
        for stage in stages:
            if state.judgments.get((stage, proof.id)) != "accepted":
                errors.append(f"{obligation.id}: proof {proof.id} lacks accepted {stage} review")
    return errors


def _selected_obligations(
    obligations: dict[str, Obligation],
    requested: tuple[str, ...] | None,
    stage: str,
    errors: list[str],
) -> set[str]:
    if requested is None:
        return set(obligations)
    if stage != "stage2":
        errors.append("Only intermediate Stage 2 review may select an obligation subset")
    if not requested or len(set(requested)) != len(requested):
        errors.append("Explicit acceptance scope must be nonempty and contain unique obligations")
    if not set(requested).issubset(obligations):
        errors.append("Explicit acceptance scope contains an unknown canonical obligation")
    return set(requested)


def validate_review_record(
    obligations: Sequence[Obligation],
    proofs: Sequence[Proof],
    previous_reviews: Sequence[Review],
    review: Review,
    *,
    author_id: str,
) -> tuple[str, ...]:
    """Reject malformed appends without rejecting legitimate refutations.

    Receipt authentication belongs to the caller. This validates structural
    identity, scope, and closure relationships with the same reducer used for
    readiness. Missing stage approvals and open findings are ordinary state,
    never reasons to reject a truthful review record.
    """
    errors: list[str] = []
    obligation_index = _index_records(obligations, "obligation", errors)
    proof_index = _index_records(proofs, "proof", errors)
    state = _reduce_reviews((*previous_reviews, review), obligation_index, proof_index, author_id)
    return (*errors, *state.errors)
