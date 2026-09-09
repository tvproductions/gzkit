"""Build and validate reviewer handoff from current canon, evidence, and response models."""

import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from gzkit.acceptance import (
    AcceptanceModel,
    Closure,
    Obligation,
    Proof,
    Review,
    ReviewResponse,
    validate_review_record,
)
from gzkit.acceptance_execution import canonical_obligations, digest_components, input_digest
from gzkit.acceptance_store import Contract, acceptance_status, load_history, resolve_brief


class ReviewContext(AcceptanceModel):
    """A captured read model, not a new source of acceptance requirements."""

    input_digest: str = Field(min_length=1, description="Single supplied review subject")
    input_components: dict[str, str] = Field(description="Audited artifact and contract identities")
    contract: Contract = Field(
        description="Current canonical requirements and implementing identity"
    )
    proofs: tuple[Proof, ...] = Field(description="Retained executed proof observations")
    reviews: tuple[Review, ...] = Field(
        description="Retained independent observations and closures"
    )
    ready: bool = Field(description="Readiness at capture")
    blockers: tuple[str, ...] = Field(description="Required evidence still missing at capture")
    open_findings: tuple[str, ...] = Field(description="Mapped finding IDs requiring closure")
    obligation_ids: tuple[str, ...] = Field(description="Requested canonical review scope")


def build_review_context(
    root: Path,
    obpi_id: str,
    *,
    stage: Literal["stage2", "stage4"],
    obligation_ids: tuple[str, ...] | None = None,
) -> ReviewContext:
    """Capture a stable subject once; refuse concurrent change during assembly."""
    brief = resolve_brief(root, obpi_id)
    before = input_digest(root, brief)
    history = load_history(root, obpi_id)
    if history.contract is None:
        raise ValueError("Review context requires initialized canonical acceptance records")
    obligations = tuple(canonical_obligations(root, brief))
    if {item.id for item in obligations} != {item.id for item in history.contract.obligations}:
        raise ValueError("Canonical obligation roster changed; cannot dispatch a narrowed context")
    status = acceptance_status(root, obpi_id, stage=stage, obligation_ids=obligation_ids)
    context = ReviewContext(
        input_digest=before,
        input_components=digest_components(root, brief),
        contract=Contract(author_id=history.contract.author_id, obligations=obligations),
        proofs=tuple(history.proofs),
        reviews=tuple(history.reviews),
        obligation_ids=obligation_ids
        if obligation_ids is not None
        else tuple(item.id for item in obligations),
        **status.model_dump(),
    )
    if input_digest(root, brief) != before:
        raise ValueError("Acceptance subject changed while building review context")
    return context


def _review_subject(context: ReviewContext) -> tuple[tuple[Obligation, ...], tuple[Proof, ...]]:
    obligations = {item.id: item for item in context.contract.obligations}
    if not context.obligation_ids or len(set(context.obligation_ids)) != len(
        context.obligation_ids
    ):
        raise ValueError("Review context needs a nonempty unique obligation scope")
    if not set(context.obligation_ids).issubset(obligations):
        raise ValueError("Review context names an unknown obligation")
    proofs = {item.obligation_id: item for item in context.proofs}
    selected = tuple(obligations[key] for key in context.obligation_ids)
    current = []
    for obligation in selected:
        proof = proofs.get(obligation.id)
        if proof is None:
            raise ValueError(f"Review context lacks executed proof for {obligation.id}")
        if (
            proof.input_digest != context.input_digest
            or proof.contract_digest != obligation.contract_digest
        ):
            raise ValueError(f"Review context contains superseded proof for {obligation.id}")
        current.append(proof)
    return selected, tuple(current)


def acceptance_review_frame(stage: str, serialized: str) -> list[str]:
    """Validate local context and examples before an expensive reviewer dispatch."""
    if not serialized.strip():
        raise ValueError("Supply current acceptance context before composing a review")
    context = ReviewContext.model_validate_json(serialized)
    obligations, proofs = _review_subject(context)
    example = ReviewResponse.model_validate(
        {
            "schema": "gzkit.acceptance.review.v1",
            "stage": stage,
            "input_digest": context.input_digest,
            "obligation_ids": [item.id for item in obligations],
            "proof_ids": [item.id for item in proofs],
            "accepted_proof_ids": [],
            "findings": [],
            "closures": [],
            "reviewer_id": "independent-reviewer-example",
            "verdict": "refuted",
        }
    )
    trial = Review(
        id="local-example",
        receipt_id="local-example",
        **example.model_dump(exclude={"schema_name"}),
    )
    errors = validate_review_record(
        context.contract.obligations,
        context.proofs,
        context.reviews,
        trial,
        author_id=context.contract.author_id,
    )
    if errors:
        raise ValueError("Invalid review context: " + "; ".join(errors))
    mapped = {item.id: item for review in context.reviews for item in review.findings}
    open_mapped = [
        mapped[key]
        for key in context.open_findings
        if key in mapped and mapped[key].obligation_id in context.obligation_ids
    ]
    finding = open_mapped[0] if open_mapped else None
    proof = next(
        (item for item in proofs if finding and item.obligation_id == finding.obligation_id),
        proofs[0],
    )
    closure = Closure(
        finding_id=finding.id if finding else "illustrative-finding-not-an-obligation",
        obligation_id=proof.obligation_id,
        proof_id=proof.id,
    )
    return [
        "### Durable Acceptance Result",
        "",
        "Captured current context (single supplied subject):",
        "```json",
        context.model_dump_json(indent=2),
        "```",
        "Return the legacy ReviewResult separately, followed by exactly one acceptance envelope.",
        "The response schema below comes from the same model used by the importer.",
        "Do not recompute the supplied input identity in a different process environment.",
        "Independently judge proof adequacy, approvals, mapped findings, and repair closure.",
        "The example grants no approval. Populate accepted_proof_ids only after your review.",
        "Verdicts retain history; explicit approvals and mapped closures govern readiness.",
        "Auxiliary observations are non-blocking; required defects they expose stay mapped.",
        "Severity describes importance; obligation mapping determines acceptance blocking.",
        "Omit id, receipt_id, tier, verification_gaps, and all unlisted fields.",
        "verification_gaps belongs only to the separate legacy ReviewResult.",
        "Never discard a mapped finding when withdrawing an auxiliary diagnostic.",
        "Response schema:",
        "```json",
        json.dumps(ReviewResponse.model_json_schema(), indent=2),
        "```",
        "Response shape (replace judgments with your independently established result):",
        "```json",
        example.model_dump_json(by_alias=True, indent=2),
        "```",
        "Closure shape: use only for an existing finding whose repair you verified.",
        "description is a finding field, never a closure field.",
        "```json",
        closure.model_dump_json(indent=2),
        "```",
        "Import actual executed reviewer output; never edit its receipt.",
        "For formatting repair, use a fresh invocation retaining the original receipt reference,",
        "subject, findings and approval. Relevant subject changes need fresh context.",
    ]
