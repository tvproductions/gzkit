"""Build and validate reviewer handoff from current canon, evidence, and response models."""

import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from gzkit.acceptance import (
    AcceptanceModel,
    Closure,
    Finding,
    Ground,
    Obligation,
    Proof,
    Review,
    ReviewResponse,
    validate_review_record,
)
from gzkit.acceptance_execution import canonical_obligations, digest_components, input_digest
from gzkit.acceptance_grounds import MIN_EXCERPT_CHARS
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


class ReviewSubject(AcceptanceModel):
    """The working set a reviewer is handed; the proof history stays in the ledger.

    The frame validates the whole ``ReviewContext`` locally, then embeds only this
    projection, so a prompt scales with the current obligations and their open
    findings rather than with every repair round the OBPI has run (GHI #1096).
    """

    input_digest: str = Field(min_length=1, description="Single supplied review subject")
    input_components: dict[str, str] = Field(description="Audited artifact and contract identities")
    implementer_id: str = Field(
        min_length=1, description="Implementing identity; never a valid reviewer_id"
    )
    obligations: tuple[Obligation, ...] = Field(description="Canonical obligations under review")
    proofs: tuple[Proof, ...] = Field(description="Current executed proof for each obligation")
    open_findings: tuple[Finding, ...] = Field(
        description="Mapped findings in scope that still need independent closure"
    )
    ready: bool = Field(description="Readiness at capture")
    blockers: tuple[str, ...] = Field(description="Required evidence still missing at capture")


def _open_finding_records(context: ReviewContext) -> tuple[Finding, ...]:
    """Return the full record of each open mapped finding in the review scope."""
    mapped = {item.id: item for review in context.reviews for item in review.findings}
    return tuple(
        mapped[key]
        for key in context.open_findings
        if key in mapped and mapped[key].obligation_id in context.obligation_ids
    )


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
    open_mapped = _open_finding_records(context)
    subject = ReviewSubject(
        input_digest=context.input_digest,
        input_components=context.input_components,
        implementer_id=context.contract.author_id,
        obligations=obligations,
        proofs=proofs,
        open_findings=open_mapped,
        ready=context.ready,
        blockers=context.blockers,
    )
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
    ground = Ground(proof_id=proof.id, path=None, excerpt="replace with the exact text you read")
    return [
        "### Durable Acceptance Result",
        "",
        "Captured current subject (the working set; the full history was validated",
        "locally and stays in the ledger):",
        "```json",
        subject.model_dump_json(indent=2),
        "```",
        "Your whole reply is exactly one acceptance envelope; emit no other JSON object.",
        "The response schema below comes from the same model used by the importer.",
        "Do not recompute the supplied input identity in a different process environment.",
        "Independently judge proof adequacy, approvals, mapped findings, and repair closure.",
        "The example grants no approval. Populate accepted_proof_ids only after your review.",
        "Verdicts retain history; explicit approvals and mapped closures govern readiness.",
        "Auxiliary observations are non-blocking; required defects they expose stay mapped.",
        "Obligation mapping, not wording, determines acceptance blocking.",
        "Put checks you could not perform in verification_gaps; they never approve or block.",
        "Never discard a mapped finding when withdrawing an auxiliary diagnostic.",
        "Import rules (the importer refuses a reply that breaks any of them):",
        '- "schema" is exactly "gzkit.acceptance.review.v1"; "verdict" is exactly',
        '  "accepted" or "refuted".',
        '- "reviewer_id" is a non-empty name of your own, never the implementer\'s.',
        '- "obligation_ids" and "proof_ids" name the supplied scope; every id in',
        '  "accepted_proof_ids" also appears in "proof_ids".',
        "- A finding is {id, obligation_id, kind, description}; kind is counterexample",
        "  or missing-proof; obligation_id null marks a non-blocking auxiliary observation.",
        "- An obligation with no current proof gets a missing-proof finding, never an",
        "  invented proof id.",
        "- A closure's proof_id must also appear in accepted_proof_ids, and a finding",
        "  you report in this reply cannot also be closed in it.",
        "- Omit id, receipt_id, tier, and every field the schema does not list.",
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
        "Ground shape: name an examined proof, the repository-relative path you read (null",
        "for that proof's recorded evidence), and an excerpt copied verbatim from that source,",
        f"at least {MIN_EXCERPT_CHARS} characters. The importer refuses an excerpt that does not",
        "occur where it says. A reviewer whose tool grant has no shell grounds every approved",
        "proof; a check you did not perform is a verification gap, never a basis for approval.",
        "```json",
        ground.model_dump_json(indent=2),
        "```",
        "Import actual executed reviewer output; never edit its receipt.",
        "For formatting repair, use a fresh invocation retaining the original receipt reference,",
        "subject, findings and approval. Relevant subject changes need fresh context.",
    ]
