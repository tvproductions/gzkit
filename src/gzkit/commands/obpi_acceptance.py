"""Execute and record requirement proof and independent acceptance reviews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.acceptance_context import build_review_context
from gzkit.acceptance_execution import prove
from gzkit.acceptance_store import (
    initialize,
    load_history,
    record_human_review,
    record_proof,
    record_review,
    resolve_brief,
)
from gzkit.arb.paths import receipts_root
from gzkit.cli.helpers.exit_codes import EXIT_USER_ERROR
from gzkit.commands.common import get_project_root
from gzkit.commands.obpi_precomplete import ObpiEntryError, resolve_obpi_at_entry
from gzkit.config import GzkitConfig
from gzkit.mutation_witness import Mutation
from gzkit.pipeline_runtime import RunCrossing, record_run_position


class ProofRequest(BaseModel):
    """Instructions to execute a control; contains no caller-supplied results."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_id: str = Field(..., min_length=1, description="Canonical acceptance requirement")
    source: str | None = Field(None, description="Production source to mutate")
    selectors: list[str] = Field(default_factory=list, description="Full covering unittest IDs")
    mutations: list[Mutation] = Field(default_factory=list, description="Exact behavioral controls")
    environment_keys: list[str] = Field(
        default_factory=list, description="Environment dependencies necessary to this proof claim"
    )


def obpi_acceptance_cmd(
    *,
    obpi_id: str,
    action: str,
    author: str | None = None,
    specification: str | None = None,
    receipt: str | None = None,
    stage: str = "stage4",
    as_json: bool = False,
    req_ids: list[str] | None = None,
    attestor: str | None = None,
    ruling: str | None = None,
) -> int:
    """Use the same durable records for Stage 2, 4a, 4b and completion.

    Exit codes: ``0`` when the action succeeded, ``3`` when acceptance is
    blocked, and ``1`` when ``review`` or ``human-review`` is given an id the
    launcher's resolver cannot give to exactly one OBPI with a brief on disk
    (OBPI-0.35.0-15, operator ruling 2026-10-12 on Open Design Question 20).
    That refusal is a user error and prints the resolver's own message:
    nothing is read, imported or recorded.
    """
    root = get_project_root()
    try:
        result, successful = _execute(
            root,
            obpi_id,
            action,
            author=author,
            specification=specification,
            receipt=receipt,
            stage=stage,
            req_ids=req_ids,
            attestor=attestor,
            ruling=ruling,
        )
    except ObpiEntryError as exc:
        print(json.dumps({"error": str(exc)}) if as_json else str(exc))  # noqa: T201
        return EXIT_USER_ERROR
    except (ValueError, OSError, KeyError) as exc:
        message = (
            f"Acceptance blocked: {exc}. GHI #985 and T1/T2/T3 require current, "
            "executed proof and receipt-bound independent closure. Use "
            f"`gz obpi acceptance {obpi_id} status` to inspect the retained obligations; "
            "repair or record the named evidence through the existing pipeline."
        )
        print(json.dumps({"error": message}) if as_json else message)  # noqa: T201
        return 3
    print(json.dumps(result, indent=2))  # noqa: T201 — JSON is the handoff contract
    return 0 if successful else 3


def _execute(
    root: Path,
    obpi_id: str,
    action: str,
    *,
    author: str | None,
    specification: str | None,
    receipt: str | None,
    stage: str,
    req_ids: list[str] | None = None,
    attestor: str | None = None,
    ruling: str | None = None,
) -> tuple[dict, bool]:
    """Keep executable producers separate from status presentation.

    A review import marks a boundary of the run, so ``review`` and
    ``human-review`` name the OBPI once, here, by the launcher's resolver
    before anything is read or imported (:func:`resolve_obpi_at_entry`). The
    boundary is recorded under the id it returns. The acceptance records stay
    keyed by ``obpi_id`` as typed, and ``init``, ``prove`` and ``status``
    resolve nothing.

    Raises:
        ObpiEntryError: when ``review`` or ``human-review`` is given an id that
            names no single OBPI with a brief on disk.

    """
    if action in ("review", "human-review"):
        launch_id = resolve_obpi_at_entry(root, obpi_id)[0]
        if action == "review":
            return _execute_review(root, obpi_id, receipt, launch_id)
        return _execute_human_review(root, obpi_id, attestor, ruling, launch_id)
    if action == "init":
        if not author:
            raise ValueError("init requires --author naming the implementing session")
        contract = initialize(root, obpi_id, author)
        return contract.model_dump(mode="json"), True
    if action == "prove":
        return _execute_proof(root, obpi_id, specification)
    if action != "status" or stage not in ("stage2", "stage4"):
        raise ValueError("Use init, prove, review or status with stage2/stage4")
    return _status_report(root, obpi_id, stage, req_ids)


def _execute_proof(root: Path, obpi_id: str, specification: str | None) -> tuple[dict, bool]:
    """Execute a proof request and persist its observed result."""
    if not specification:
        raise ValueError("prove requires --spec with the requirement and controls")
    request = ProofRequest.model_validate_json(Path(specification).read_text(encoding="utf-8"))
    if load_history(root, obpi_id).contract is None:
        raise ValueError("Run acceptance init before executing proof controls")
    proof = prove(
        root,
        resolve_brief(root, obpi_id),
        request.req_id,
        source=Path(request.source) if request.source else None,
        mutations=request.mutations,
        selectors=request.selectors,
        environment_keys=tuple(request.environment_keys),
    )
    record_proof(root, obpi_id, proof)
    return proof.model_dump(mode="json"), proof.valid


def _record_review_round(root: Path, launch_id: str) -> None:
    """Record the boundary a successful review import marks (OBPI-0.35.0-15).

    Called for an adversarial review and for a human review only (operator
    ruling 2026-10-11, Open Design Question 7): a spec or quality review is
    imported during Stage 2 and marks no boundary. An import is a check, so it
    is recorded inside the stage the run has reached and never moves it
    (Question 9). Nothing is recorded unless a pipeline run is in flight for
    ``launch_id``, and a refused import never reaches this call.

    ``launch_id`` is the id the launcher's resolver gave the id as typed, at
    the command's entry (operator rulings 2026-10-12, Open Design Questions 19
    and 20), so a review imported under any spelling the launcher accepts
    lands on the launch's id. There is no fallback to the id as typed: an id
    the resolver cannot name is refused before the import.
    """
    record_run_position(root, launch_id, RunCrossing(boundary="acceptance-review"))


def _execute_review(
    root: Path, obpi_id: str, receipt: str | None, launch_id: str
) -> tuple[dict, bool]:
    """Resolve the named transport receipt and retain its independent judgment.

    The review is stored under ``obpi_id`` as typed; an adversarial review's
    boundary is recorded under ``launch_id``, the resolver's id for it.
    """
    if not receipt or Path(receipt).name != receipt:
        raise ValueError("review requires --receipt with an ARB run ID")
    config = GzkitConfig.load(root / ".gzkit.json")
    path = receipts_root(config=config, project_root=root) / f"{receipt}.json"
    captured = json.loads(path.read_text(encoding="utf-8"))
    if captured.get("run_id") != receipt:
        raise ValueError("Receipt filename and execution identity disagree")
    review = record_review(root, obpi_id, captured)
    if review.stage == "adversarial":
        _record_review_round(root, launch_id)
    return review.model_dump(mode="json"), True


def _execute_human_review(
    root: Path, obpi_id: str, attestor: str | None, ruling: str | None, launch_id: str
) -> tuple[dict, bool]:
    """Record an explicitly supplied operator ruling against current proof.

    The ruling is stored under ``obpi_id`` as typed; its boundary is recorded
    under ``launch_id``, the resolver's id for it.
    """
    if not attestor or not ruling:
        raise ValueError("human-review requires --attestor and the operator's verbatim --ruling")
    review = record_human_review(root, obpi_id, attestor=attestor, ruling=ruling)
    _record_review_round(root, launch_id)
    return review.model_dump(mode="json"), True


def _status_report(
    root: Path, obpi_id: str, stage: Literal["stage2", "stage4"], req_ids: list[str] | None
) -> tuple[dict, bool]:
    """Assemble the current contract and retained evidence alongside readiness."""
    context = build_review_context(
        root, obpi_id, stage=stage, obligation_ids=tuple(req_ids) if req_ids else None
    )
    return context.model_dump(mode="json"), context.ready
