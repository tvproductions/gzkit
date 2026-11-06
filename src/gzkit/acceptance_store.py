"""Durable acceptance records and receipt-bound review ingestion (GHI #985).

The ledger owns history. Readiness is rebuilt against current canon and bytes;
neither a Markdown standing verdict nor a disposable pipeline marker owns it.
Review meaning remains a reviewer judgment. Receipt binding records its actual
producer/output; it is not a claim of cryptographic reviewer authentication.
"""

import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.acceptance import (
    REVIEW_SCHEMA,
    Obligation,
    Proof,
    Readiness,
    Review,
    ReviewResponse,
    assess_readiness,
    proof_aliases,
    review_objects,
    validate_review_record,
)
from gzkit.acceptance_execution import (
    AcceptanceSource,
    canonical_obligations,
    digest_components,
    execution_conditions_digest,
    input_digest,
)
from gzkit.acceptance_grounds import refuse_uncited_approval
from gzkit.acceptance_package import departed_reqs, is_work_package_id, package_contract
from gzkit.adversary_workspace import validate_replay_records
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.ledger_events import acceptance_recorded_event
from gzkit.models.catalog import load_catalog
from gzkit.pipeline_dispatch import MAX_REVIEW_FIX_CYCLES
from gzkit.registries import RegistryError
from gzkit.req_kind_fence import resolve_fence_proof
from gzkit.req_kind_support import resolve_support_proof
from gzkit.work_package_ledger import package_rows

if TYPE_CHECKING:
    from collections.abc import Iterator


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


class CompletionReview(Review):
    """Derived primary judgment plus its supporting set; never a new reviewer record."""

    supporting_reviews: tuple[Review, ...] = Field(description="Required approvals and closures")


def acceptance_ledger(root: Path) -> Ledger:
    """Resolve the configured ledger without consulting a pipeline marker."""
    config_file = root / ".gzkit.json"
    relative = (
        GzkitConfig.load(config_file).paths.ledger
        if config_file.exists()
        else ".gzkit/ledger.jsonl"
    )
    return Ledger(root / relative)


def resolve_brief(root: Path, obpi_id: str) -> AcceptanceSource:
    """Resolve a real canonical brief; an evidence filename is not an OBPI.

    A work package supplies its contract in place of a brief (RO-14 act 5).

    Returns:
        The work package's contract for a work-package ID, otherwise the path of the OBPI's
        canonical brief.

    """
    from gzkit.commands.obpi_precomplete import resolve_brief_path  # noqa: PLC0415

    if is_work_package_id(obpi_id):
        try:
            return package_contract(load_catalog(root), acceptance_ledger(root), obpi_id)
        except RegistryError as exc:
            raise ValueError(str(exc)) from exc

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
    """Replay this OBPI's history as acceptance reads it, a departed REQ moved out.

    Returns:
        The history of what is still owed.

    """
    return _without_departed(root, obpi_id, _replay_history(root, obpi_id))


def _replay_history(root: Path, obpi_id: str) -> AcceptanceHistory:
    """Replay this OBPI's netted ledger history, refusing malformed records.

    Returns:
        Every recorded proof and review.

    """
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
            history.reviews.append(
                _at_ledger_position(review_from_receipt(payload), history.proofs)
            )
        elif kind == "human-review":
            history.reviews.append(_at_ledger_position(_human_review(payload), history.proofs))
        else:
            raise ValueError(f"Unknown acceptance record type: {kind}")
    return history


def _without_departed(root: Path, obpi_id: str, history: AcceptanceHistory) -> AcceptanceHistory:
    """Take the REQs a departure moved out of a package's history (ruling 12).

    The one place this is done, so the reducer, the store and the review context
    agree: a departed REQ's proofs and findings stay on the ledger and leave the
    acceptance of what the package still owes.

    Returns:
        The history of what the package still owes.

    """
    if not is_work_package_id(obpi_id):
        return history
    departed = departed_reqs(acceptance_ledger(root), obpi_id)
    if not departed:
        return history
    kept = [proof for proof in history.proofs if proof.obligation_id not in departed]
    gone = {proof.id for proof in history.proofs} - {proof.id for proof in kept}
    reviews = [_scoped(review, departed, gone) for review in history.reviews]
    history.proofs = kept
    history.reviews = [review for review in reviews if review.obligation_ids]
    return history


def _scoped(review: Review, departed: set[str], gone: set[str]) -> Review:
    return review.model_copy(
        update={
            "obligation_ids": tuple(i for i in review.obligation_ids if i not in departed),
            "proof_ids": tuple(i for i in review.proof_ids if i not in gone),
            "accepted_proof_ids": tuple(i for i in review.accepted_proof_ids if i not in gone),
            "recorded_current_ids": tuple(
                i for i in review.recorded_current_ids or () if i not in gone
            ),
            "findings": tuple(f for f in review.findings if f.obligation_id not in departed),
            "closures": tuple(c for c in review.closures if c.obligation_id not in departed),
        }
    )


def _at_ledger_position(review: Review, proofs: list[Proof]) -> Review:
    """Bind observation chronology without modifying a captured reviewer receipt."""
    current = {proof.obligation_id: proof.id for proof in proofs}
    return review.model_copy(update={"recorded_current_ids": tuple(current.values())})


def initialize(root: Path, obpi_id: str, author_id: str) -> Contract:
    """Capture canon once; repeated calls cannot erase findings or change authors."""
    contract = Contract(
        author_id=author_id,
        obligations=tuple(canonical_obligations(root, resolve_brief(root, obpi_id))),
    )
    previous = load_history(root, obpi_id).contract
    if previous is not None:
        # A departure narrows a package's obligations; its author stays the identity.
        same = previous == contract or (
            is_work_package_id(obpi_id) and previous.author_id == contract.author_id
        )
        if not same:
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


def _refuse_inadequate_replay(judgment: ReviewResponse) -> None:
    """Refuse a replay claim the reviewer's own record does not support (GHI #961).

    A ``replay`` block is a claim that the reviewer REPRODUCED the proof inside
    its disposable checkout. Absence claims nothing and is left alone; presence
    is checked, because an execution error, a skipped selector, or an inspected
    record must never be counted as independent replay. Every record is judged
    against the workspace it names, so this refuses the internally-inconsistent
    claim without asserting which checkout the importer "should" have seen.
    """
    if not judgment.replay:
        return
    reasons: list[str] = []
    for digest in {record.workspace_digest for record in judgment.replay}:
        reasons.extend(
            validate_replay_records(
                [r for r in judgment.replay if r.workspace_digest == digest],
                workspace_digest=digest,
            )
        )
    if reasons:
        raise ValueError(
            "Review claims independent replay its own record does not establish: "
            + "; ".join(reasons)
        )


def review_from_receipt(receipt: dict[str, Any]) -> Review:
    """Extract exactly one review from a successful ARB execution's output.

    The producer must be an actual agent invocation, not an echo/cat/JSON copier.
    This uses the existing vendor/wrapper vocabulary at its execution boundary.
    The CLI accepts no separately authored review file or verdict override.

    Returns:
        The review, identified by the receipt's SHA-256 digest and run ID, with tier 1 when the
        receipt proves a cross-vendor invocation and tier 2 otherwise.

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
    candidates = review_objects(str(receipt.get("stdout_tail", "")))
    candidates.extend(review_objects(str(receipt.get("stderr_tail", ""))))
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
    if "id" in payload or "receipt_id" in payload:
        raise ValueError("Review IDs are assigned from the executed receipt, never caller supplied")
    judgment = ReviewResponse.model_validate({"schema": REVIEW_SCHEMA, **payload})
    _refuse_inadequate_replay(judgment)
    digest = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    return Review(
        id=digest,
        receipt_id=run_id,
        tier=1 if cross_vendor else 2,
        **judgment.model_dump(exclude={"schema_name"}),
    )


def _stale_review_message(root: Path, brief: AcceptanceSource, reviewed: str) -> str:
    """Refuse without claiming a cause this function cannot establish (GHI #989).

    The digest composes two terms -- the audited file roster and the contract --
    and a review record carries only their composite. Which term moved is
    therefore NOT derivable here, so the message does not guess: it says the
    inputs are superseded, names the two terms that compose them, and prints
    both digests so the reader can compare. The prior wording asserted "stale
    file contents" whichever term differed, sending readers hunting for a file
    change that need not exist -- twice in one session, against a tree that
    `git status` reported clean.

    Returns:
        The refusal message, naming both composing terms and printing the reviewed, current, files
        and contract digest prefixes.

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
    known_subjects = {proof.input_digest for proof in history.proofs}
    known_subjects.update(item.input_digest for item in history.reviews)
    if (
        review.input_digest != input_digest(root, brief)
        and review.input_digest not in known_subjects
    ):
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


def review_round_limit() -> int:
    """Give the adversarial rounds a package may run (GHI #1028, the ruled N=2).

    Each follow-up round reviews one fix cycle, so the limit is the first round
    plus the fix-cycle bound, and the number lives in one place.

    Returns:
        The first round and its follow-ups.

    """
    return 1 + MAX_REVIEW_FIX_CYCLES


def _review_rows(root: Path, work_package: str) -> Iterator[LedgerEvent]:
    for event in acceptance_ledger(root).read_all():
        if event.id == work_package and event.event in {
            "acceptance_recorded",
            "work_package_unblocked",
        }:
            yield event


def _has_mapped_finding(review: Review) -> bool:
    return any(finding.obligation_id for finding in review.findings)


def refuted_rounds(root: Path, work_package: str) -> int:
    """Count adversarial rounds with a mapped finding since the operator last ruled.

    A mapped finding is what blocks readiness, so it counts and the verdict token
    does not. An unblock is the operator's ruling and restarts the count, once the
    block has shown the facts; a repair still needs a dispatch, which the fix-cycle
    bound holds.

    Returns:
        The rounds that count against :func:`review_round_limit`.

    """
    rounds = 0
    for event in _review_rows(root, work_package):
        if event.event == "work_package_unblocked":
            rounds = 0
        elif event.extra.get("record_type") == "review" and _is_round(event):
            rounds += 1
    return rounds


def _is_round(event: LedgerEvent) -> bool:
    """Say whether a review row counts; a malformed one cannot, and never stops a dispatch.

    `gz wp accept` still refuses such a history, through :func:`load_history`.

    Returns:
        True for a readable adversarial review with a mapped finding.

    """
    try:
        review = review_from_receipt(event.extra["payload"])
    except ValueError, KeyError, TypeError, AttributeError:
        return False
    return review.stage == "adversarial" and _has_mapped_finding(review)


def round_bound_refusal(root: Path, work_package: str) -> str | None:
    """Say why the package stops for the operator, once its rounds are used (GHI #1028).

    An import is never refused here: a truthful finding must be recorded, so the
    bound stands where the work would restart.

    Returns:
        The refusal for `gz wp dispatch`, `gz wp accept` and `human-review`, or None
        under the limit.

    """
    if refuted_rounds(root, work_package) < review_round_limit():
        return None
    return (
        f"{work_package} has used its {review_round_limit()} adversarial rounds (GHI #1028). "
        f"Record the block with `uv run gz wp block {work_package} --reason <text> "
        "--next-action <text>`, so the operator can rule"
    )


def refutation_counts(root: Path, work_package: str) -> dict[str, int]:
    """Count the reviews carrying a mapped finding on each obligation.

    Read from the whole replay, never a receipt's truncated tail: a departed REQ's
    refutations left acceptance and stay facts, so a later block counts them (ruling
    8). A review counts once per obligation it maps a finding to, whatever its
    verdict token says, since a mapped finding is what blocks readiness. A package
    with no acceptance history has refuted nothing.

    Returns:
        Reviews per obligation id.

    """
    counts: dict[str, int] = {}
    for review in _replay_history(root, work_package).reviews:
        for obligation_id in {item.obligation_id for item in review.findings}:
            if obligation_id:
                counts[obligation_id] = counts.get(obligation_id, 0) + 1
    return counts


def record_review(root: Path, obpi_id: str, receipt: dict[str, Any]) -> Review:
    """Retain authenticated observations; readiness separately checks applicability."""
    history = load_history(root, obpi_id)
    review = _at_ledger_position(review_from_receipt(receipt), history.proofs)
    if not _validate_new_review(root, obpi_id, review):
        return next(item for item in history.reviews if item.id == review.id)
    # New imports only: replaying history must never reinterpret a recorded review.
    refuse_uncited_approval(root, review, history.proofs, receipt)
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

    Returns:
        The human adversarial review, accepting every current proof and closing each open finding
        whose obligation has a current proof. It is appended to the ledger only when no identical
        review is already recorded; a review that fails validation raises instead.

    Raises:
        ValueError: A package is past its round limit, so the block comes first (ruling
            20), or the ruling has no current proof to judge.

    """
    if is_work_package_id(obpi_id):
        refusal = round_bound_refusal(root, obpi_id)
        if refusal:
            raise ValueError(refusal)
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
    review = _at_ledger_position(_human_review(payload), history.proofs)
    if _validate_new_review(root, obpi_id, review):
        _append(root, obpi_id, "human-review", payload)
    return review


def owed_ids(root: Path, obpi_id: str, contract: Contract) -> set[str]:
    """Read the roster a contract still owes: a departure moves a REQ out (ruling 12).

    Returns:
        The obligation ids.

    """
    owed = {item.id for item in contract.obligations}
    if is_work_package_id(obpi_id):
        owed -= departed_reqs(acceptance_ledger(root), obpi_id)
    return owed


def _declared_single_driver(root: Path, obpi_id: str) -> bool:
    from gzkit.obpi_dispatch_channel import single_driver_declaration  # noqa: PLC0415

    if is_work_package_id(obpi_id):
        rows = package_rows(acceptance_ledger(root), "work_package_dispatched", obpi_id)
        return any(row.extra.get("role") == "SingleDriver" for row in rows)
    return single_driver_declaration(root, obpi_id) is not None


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
        if {item.id for item in current} != owed_ids(root, obpi_id, history.contract):
            raise ValueError(
                "Canonical obligation roster changed; it cannot silently replace acceptance scope"
            )
        declared_single_driver = _declared_single_driver(root, obpi_id)
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
        live_blockers = _live_proof_blockers(root, current, history.proofs, obligation_ids)
        return Readiness(
            ready=status.ready and not live_blockers,
            blockers=(*status.blockers, *live_blockers),
            open_findings=status.open_findings,
        )
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return Readiness(ready=False, blockers=(str(exc),), open_findings=())


def _live_proof_blockers(
    root: Path,
    current: list[Obligation],
    proofs: list[Proof],
    obligation_ids: tuple[str, ...] | None,
) -> list[str]:
    """Recheck explicitly declared conditions and the two live canonical resolvers."""
    live_blockers = []
    for proof in {item.obligation_id: item for item in proofs}.values():
        if obligation_ids is not None and proof.obligation_id not in obligation_ids:
            continue
        if proof.environment_keys and proof.conditions_digest != execution_conditions_digest(
            proof.environment_keys
        ):
            live_blockers.append(f"{proof.obligation_id}: declared execution conditions changed")
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
    return live_blockers


def acceptance_verb(obpi_id: str) -> str:
    """Name the verb that reads this id's acceptance.

    Returns:
        `gz wp acceptance` for a work package, else `gz obpi acceptance`.

    """
    return "gz wp acceptance" if is_work_package_id(obpi_id) else "gz obpi acceptance"


def acceptance_blockers(
    root: Path, obpi_id: str, *, stage: Literal["stage2", "stage4"] = "stage4"
) -> list[str]:
    """Shared refusal prose for actual stage and completion consumers."""
    status = acceptance_status(root, obpi_id, stage=stage)
    if status.ready:
        return []
    return [
        f"Acceptance blocked: {message}. Required proof and independent closure must remain "
        f"bound to canon (GHI #985; T1/T2/T3). Run `{acceptance_verb(obpi_id)} {obpi_id} status "
        f"--stage {stage}` and repair the named obligation through the existing pipeline."
        for message in status.blockers
    ]


def completion_review(root: Path, obpi_id: str) -> CompletionReview:
    """Retain all required approval/closure provenance and the actual degraded floor."""
    blockers = acceptance_blockers(root, obpi_id)
    if blockers:
        raise ValueError("; ".join(blockers))
    history = load_history(root, obpi_id)
    current = {proof.obligation_id: proof for proof in history.proofs}
    aliases = proof_aliases(history.proofs)
    channels = (
        ("adversarial",)
        if _declared_single_driver(root, obpi_id)
        else (
            "spec",
            "quality",
            "adversarial",
        )
    )
    needed = {(stage, aliases[proof.id]) for stage in channels for proof in current.values()}
    selected: dict[str, Review] = {}
    for review in history.reviews:
        covered = {(review.stage, aliases[key]) for key in review.accepted_proof_ids}
        if needed.intersection(covered):
            selected[review.id] = review
            needed.difference_update(covered)
    # Explicit closures are evidence independently of the approval set.
    closed: set[str] = set()
    for review in reversed(history.reviews):
        for closure in review.closures:
            proof = current.get(closure.obligation_id)
            if (
                proof is not None
                and closure.finding_id not in closed
                and aliases[closure.proof_id] == aliases[proof.id]
            ):
                selected[review.id] = review
                closed.add(closure.finding_id)
    primary = max(
        (review for review in selected.values() if review.stage == "adversarial"),
        key=lambda review: review.tier,
    )
    return CompletionReview(**primary.model_dump(), supporting_reviews=tuple(selected.values()))
