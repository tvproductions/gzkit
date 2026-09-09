"""Durable acceptance records and receipt-bound review ingestion (GHI #985).

The ledger owns history. Readiness is rebuilt against current canon and bytes;
neither a Markdown standing verdict nor a disposable pipeline marker owns it.
Review meaning remains a reviewer judgment. Receipt binding records its actual
producer/output; it is not a claim of cryptographic reviewer authentication.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.acceptance import (
    Obligation,
    Proof,
    Readiness,
    Review,
    assess_readiness,
    validate_review_record,
)
from gzkit.acceptance_execution import canonical_obligations, digest_components, input_digest
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger
from gzkit.ledger_events import acceptance_recorded_event
from gzkit.req_kind_fence import resolve_fence_proof
from gzkit.req_kind_support import resolve_support_proof

REVIEW_SCHEMA = "gzkit.acceptance.review.v1"


class Contract(BaseModel):
    """The canonical acceptance population captured before verification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    author_id: str = Field(..., min_length=1, description="Implementing session identity")
    obligations: tuple[Obligation, ...] = Field(..., description="Canonical obligations")


class AcceptanceHistory(BaseModel):
    """Rebuildable view of immutable ledger records for one OBPI."""

    model_config = ConfigDict(extra="forbid")

    contract: Contract | None = Field(None, description="Initial obligation population")
    proofs: list[Proof] = Field(default_factory=list, description="Execution history")
    reviews: list[Review] = Field(default_factory=list, description="Independent review history")


def acceptance_ledger(root: Path) -> Ledger:
    """Resolve the configured ledger without consulting a pipeline marker."""
    config_file = root / ".gzkit.json"
    relative = (
        GzkitConfig.load(config_file).paths.ledger
        if config_file.exists()
        else ".gzkit/ledger.jsonl"
    )
    return Ledger(root / relative)


def resolve_brief(root: Path, obpi_id: str) -> Path:
    """Resolve a real canonical brief; an evidence filename is not an OBPI."""
    from gzkit.commands.obpi_precomplete import resolve_brief_path  # noqa: PLC0415

    brief = resolve_brief_path(root, obpi_id)
    if brief is None:
        raise ValueError(f"No canonical brief for {obpi_id}")
    return brief


def _append(
    root: Path,
    obpi_id: str,
    record_type: Literal["contract", "proof", "review", "human-review"],
    payload: dict[str, Any],
) -> None:
    """Append through the ledger's durable writer, never edit its JSONL."""
    acceptance_ledger(root).append(acceptance_recorded_event(obpi_id, record_type, payload))


def load_history(root: Path, obpi_id: str) -> AcceptanceHistory:
    """Replay this OBPI's netted ledger history, refusing malformed records."""
    history = AcceptanceHistory()
    for event in acceptance_ledger(root).read_all():
        if event.event != "acceptance_recorded" or event.id != obpi_id:
            continue
        kind, payload = event.extra["record_type"], event.extra["payload"]
        if kind == "contract":
            contract = Contract.model_validate(payload)
            if history.contract is not None and history.contract != contract:
                raise ValueError("Acceptance contract cannot be silently replaced")
            history.contract = contract
        elif kind == "proof":
            history.proofs.append(Proof.model_validate(payload))
        elif kind == "review":
            # Re-derive the same judgment from the captured executed output. A
            # second agent-authored interpretation cannot replace the receipt.
            history.reviews.append(review_from_receipt(payload))
        elif kind == "human-review":
            history.reviews.append(_human_review(payload))
        else:
            raise ValueError(f"Unknown acceptance record type: {kind}")
    return history


def initialize(root: Path, obpi_id: str, author_id: str) -> Contract:
    """Capture canon once; repeated calls cannot erase findings or change authors."""
    contract = Contract(
        author_id=author_id,
        obligations=tuple(canonical_obligations(root, resolve_brief(root, obpi_id))),
    )
    previous = load_history(root, obpi_id).contract
    if previous is not None:
        if previous != contract:
            raise ValueError(
                "Acceptance already initialized; preserve its author and obligation identities"
            )
        return previous
    _append(root, obpi_id, "contract", contract.model_dump(mode="json"))
    return contract


def record_proof(root: Path, obpi_id: str, proof: Proof) -> None:
    """Persist a proof produced by the execution path, including failed controls."""
    history = load_history(root, obpi_id)
    if history.contract is None:
        raise ValueError("Initialize acceptance before recording proof")
    current = canonical_obligations(root, resolve_brief(root, obpi_id))
    obligation = next((item for item in current if item.id == proof.obligation_id), None)
    if obligation is None or obligation.contract_digest != proof.contract_digest:
        raise ValueError("Proof does not describe a current canonical obligation")
    if any(item.id == proof.id for item in history.proofs):
        raise ValueError("A proof ID cannot replace an earlier execution")
    _append(root, obpi_id, "proof", proof.model_dump(mode="json"))


def _review_objects(text: str) -> list[dict[str, Any]]:
    """Read schema-tagged JSON objects from executed output, including code fences."""
    decoder = json.JSONDecoder()
    objects: list[dict[str, Any]] = []
    index = 0
    while index < len(text):
        start = text.find("{", index)
        if start < 0:
            break
        try:
            value, length = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        if isinstance(value, dict) and value.get("schema") == REVIEW_SCHEMA:
            objects.append(value)
        index = start + length
    return objects


def review_from_receipt(receipt: dict[str, Any]) -> Review:
    """Extract exactly one review from a successful ARB execution's output.

    The producer must be an actual agent invocation, not an echo/cat/JSON copier.
    This uses the existing vendor/wrapper vocabulary at its execution boundary.
    The CLI accepts no separately authored review file or verdict override.
    """
    from gzkit.commands.obpi_complete_adversarial import (  # noqa: PLC0415
        receipt_binary_name,
        receipt_proves_cross_vendor,
    )

    if receipt.get("schema") != "gzkit.arb.step_receipt.v1" or receipt.get("exit_status") != 0:
        raise ValueError("Review requires a successful ARB step receipt")
    run_id = receipt.get("run_id")
    if not isinstance(run_id, str) or not run_id.startswith("arb-step-"):
        raise ValueError("Review receipt has no execution identity")
    candidates = _review_objects(str(receipt.get("stdout_tail", "")))
    candidates.extend(_review_objects(str(receipt.get("stderr_tail", ""))))
    if len(candidates) != 1:
        raise ValueError(
            "Receipt output must contain exactly one gzkit.acceptance.review.v1 object"
        )
    payload = dict(candidates[0])
    payload.pop("schema")
    step = receipt.get("step")
    if not isinstance(step, dict) or not isinstance(step.get("command"), list):
        raise ValueError("Review receipt has no executable command")
    command = step["command"]
    # Stage-2 reviewers may share the implementation vendor; Step 4b keeps
    # the existing cross-vendor execution requirement.
    native_claude = (
        bool(command) and receipt_binary_name(str(command[0])).removesuffix(".exe") == "claude"
    )
    cross_vendor = receipt_proves_cross_vendor(receipt)
    if not cross_vendor and not native_claude:
        raise ValueError("Acceptance review receipt must record the independent agent invocation")
    if (
        not cross_vendor
        and payload.get("stage") == "adversarial"
        and not str(payload.get("fallback_reason", "")).strip()
    ):
        raise ValueError(
            "Tier-2 adversarial review requires the observed cross-vendor unavailability"
        )
    if "tier" in payload:
        raise ValueError("Review tier is derived from the execution transport")
    payload["tier"] = 1 if cross_vendor else 2
    if "id" in payload or "receipt_id" in payload:
        raise ValueError("Review IDs are assigned from the executed receipt, never caller supplied")
    digest = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    return Review(id=digest, receipt_id=run_id, **payload)


def _stale_review_message(root: Path, brief: Path, reviewed: str) -> str:
    """Refuse without claiming a cause this function cannot establish (GHI #989).

    The digest composes two terms -- the audited file roster and the contract --
    and a review record carries only their composite. Which term moved is
    therefore NOT derivable here, so the message does not guess: it says the
    inputs are superseded, names the two terms that compose them, and prints
    both digests so the reader can compare. The prior wording asserted "stale
    file contents" whichever term differed, sending readers hunting for a file
    change that need not exist -- twice in one session, against a tree that
    `git status` reported clean.
    """
    components = digest_components(root, brief)
    return (
        "Review describes superseded acceptance inputs; re-review the current proof. "
        f"Reviewed digest {reviewed[:12]}..., current {input_digest(root, brief)[:12]}.... "
        f"The digest composes the audited files roster ({components['files'][:12]}...) "
        f"and the contract ({components['contract'][:12]}...); compare both to see "
        "which moved."
    )


def _validate_new_review(root: Path, obpi_id: str, review: Review) -> bool:
    """Validate a forward judgment; return false for an identical already-recorded run."""
    history = load_history(root, obpi_id)
    if history.contract is None:
        raise ValueError("Initialize acceptance before recording reviews")
    if any(item.id == review.id for item in history.reviews):
        return False
    brief = resolve_brief(root, obpi_id)
    if review.input_digest != input_digest(root, brief):
        raise ValueError(_stale_review_message(root, brief, review.input_digest))
    # Reduction validates finding/closure referential integrity. Open findings
    # are legitimate outcomes and must be recorded, including a refuted round.
    errors = validate_review_record(
        canonical_obligations(root, brief),
        history.proofs,
        history.reviews,
        review,
        author_id=history.contract.author_id,
    )
    if errors:
        raise ValueError("; ".join(errors))
    return True


def record_review(root: Path, obpi_id: str, receipt: dict[str, Any]) -> Review:
    """Bind executed judgment to current proof and preserve its complete findings."""
    review = review_from_receipt(receipt)
    if not _validate_new_review(root, obpi_id, review):
        return review
    _append(root, obpi_id, "review", receipt)
    return review


def _human_review(payload: dict[str, Any]) -> Review:
    """Preserve the existing explicitly recorded human degraded floor."""
    attestor, ruling = payload.get("attestor"), payload.get("ruling")
    if not isinstance(attestor, str) or not attestor.strip():
        raise ValueError("Human review requires an identified attestor")
    if not isinstance(ruling, str) or not ruling.strip():
        raise ValueError("Human review requires the operator's verbatim ruling")
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return Review(
        id=digest,
        receipt_id=f"human-{digest}",
        reviewer_id=f"human:{attestor}",
        tier=3,
        fallback_reason=ruling,
        **payload["review"],
    )


def record_human_review(root: Path, obpi_id: str, *, attestor: str, ruling: str) -> Review:
    """Record explicit human judgment of the displayed current proof and findings.

    Caller authorization is the same operator-verbatim boundary as attestation;
    never infer this action from permission to implement or repair an OBPI.
    """
    history = load_history(root, obpi_id)
    current = {proof.obligation_id: proof for proof in history.proofs}
    status = acceptance_status(root, obpi_id)
    known_findings = {
        finding.id: finding for review in history.reviews for finding in review.findings
    }
    closures = []
    for finding_id in status.open_findings:
        obligation_id = known_findings[finding_id].obligation_id
        if obligation_id is not None and obligation_id in current:
            closures.append(
                {
                    "finding_id": finding_id,
                    "obligation_id": obligation_id,
                    "proof_id": current[obligation_id].id,
                }
            )
    payload = {
        "attestor": attestor,
        "ruling": ruling,
        "review": {
            "stage": "adversarial",
            "verdict": "accepted",
            "input_digest": input_digest(root, resolve_brief(root, obpi_id)),
            "obligation_ids": list(current),
            "proof_ids": [p.id for p in current.values()],
            "accepted_proof_ids": [p.id for p in current.values()],
            "closures": closures,
        },
    }
    review = _human_review(payload)
    if _validate_new_review(root, obpi_id, review):
        _append(root, obpi_id, "human-review", payload)
    return review


def acceptance_status(
    root: Path,
    obpi_id: str,
    *,
    stage: Literal["stage2", "stage4"] = "stage4",
    obligation_ids: tuple[str, ...] | None = None,
) -> Readiness:
    """Derive readiness from current obligations, bytes and durable closure history."""
    try:
        brief = resolve_brief(root, obpi_id)
        history = load_history(root, obpi_id)
        if history.contract is None:
            raise ValueError("No durable acceptance contract/proof history")
        current = canonical_obligations(root, brief)
        if {item.id for item in current} != {item.id for item in history.contract.obligations}:
            raise ValueError(
                "Canonical obligation roster changed; it cannot silently replace acceptance scope"
            )
        from gzkit.obpi_dispatch_channel import single_driver_declaration  # noqa: PLC0415

        declared_single_driver = single_driver_declaration(root, obpi_id) is not None
        required_stages = None
        if declared_single_driver:
            required_stages = () if stage == "stage2" else ("adversarial",)
        status = assess_readiness(
            current,
            history.proofs,
            history.reviews,
            input_digest=input_digest(root, brief),
            stage=stage,
            author_id=history.contract.author_id,
            obligation_ids=obligation_ids,
            required_review_stages=required_stages,
        )
        live_blockers = []
        for obligation in current:
            if obligation_ids is not None and obligation.id not in obligation_ids:
                continue
            if obligation.kind == "SUPPORT":
                result = resolve_support_proof(obligation.statement, root, req_id=obligation.id)
            elif obligation.kind == "STRUCTURAL-FENCE":
                result = resolve_fence_proof(obligation.id, root, obligation.statement)
            else:
                continue
            if result != "pass":
                live_blockers.append(
                    f"{obligation.id}: current canonical proof resolver returned {result}"
                )
        return Readiness(
            ready=status.ready and not live_blockers,
            blockers=(*status.blockers, *live_blockers),
            open_findings=status.open_findings,
        )
    except (OSError, ValueError, KeyError) as exc:
        return Readiness(ready=False, blockers=(str(exc),), open_findings=())


def acceptance_blockers(
    root: Path, obpi_id: str, *, stage: Literal["stage2", "stage4"] = "stage4"
) -> list[str]:
    """Shared refusal prose for actual stage and completion consumers."""
    status = acceptance_status(root, obpi_id, stage=stage)
    if status.ready:
        return []
    return [
        f"Acceptance blocked: {message}. Required proof and independent closure must remain "
        f"bound to canon (GHI #985; T1/T2/T3). Run `gz obpi acceptance {obpi_id} status "
        f"--stage {stage}` and repair the named obligation through the existing pipeline."
        for message in status.blockers
    ]


def completion_review(root: Path, obpi_id: str) -> Review:
    """Return current receipted judgment only after the entire obligation set clears."""
    blockers = acceptance_blockers(root, obpi_id)
    if blockers:
        raise ValueError("; ".join(blockers))
    history = load_history(root, obpi_id)
    current = {proof.obligation_id: proof for proof in history.proofs}
    current_ids = {proof.id for proof in current.values()}
    return next(
        review
        for review in reversed(history.reviews)
        if review.stage == "adversarial" and current_ids.intersection(review.accepted_proof_ids)
    )
