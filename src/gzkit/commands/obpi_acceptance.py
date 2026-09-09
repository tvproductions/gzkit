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
from gzkit.commands.common import get_project_root
from gzkit.config import GzkitConfig
from gzkit.mutation_witness import Mutation


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
    """Use the same durable records for Stage 2, 4a, 4b and completion."""
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
    """Keep executable producers separate from status presentation."""
    if action == "init":
        if not author:
            raise ValueError("init requires --author naming the implementing session")
        contract = initialize(root, obpi_id, author)
        return contract.model_dump(mode="json"), True
    if action == "prove":
        return _execute_proof(root, obpi_id, specification)
    if action == "review":
        return _execute_review(root, obpi_id, receipt)
    if action == "human-review":
        return _execute_human_review(root, obpi_id, attestor, ruling)
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


def _execute_review(root: Path, obpi_id: str, receipt: str | None) -> tuple[dict, bool]:
    """Resolve the named transport receipt and retain its independent judgment."""
    if not receipt or Path(receipt).name != receipt:
        raise ValueError("review requires --receipt with an ARB run ID")
    config = GzkitConfig.load(root / ".gzkit.json")
    path = receipts_root(config=config, project_root=root) / f"{receipt}.json"
    captured = json.loads(path.read_text(encoding="utf-8"))
    if captured.get("run_id") != receipt:
        raise ValueError("Receipt filename and execution identity disagree")
    review = record_review(root, obpi_id, captured)
    return review.model_dump(mode="json"), True


def _execute_human_review(
    root: Path, obpi_id: str, attestor: str | None, ruling: str | None
) -> tuple[dict, bool]:
    """Record an explicitly supplied operator ruling against current proof."""
    if not attestor or not ruling:
        raise ValueError("human-review requires --attestor and the operator's verbatim --ruling")
    review = record_human_review(root, obpi_id, attestor=attestor, ruling=ruling)
    return review.model_dump(mode="json"), True


def _status_report(
    root: Path, obpi_id: str, stage: Literal["stage2", "stage4"], req_ids: list[str] | None
) -> tuple[dict, bool]:
    """Assemble the current contract and retained evidence alongside readiness."""
    context = build_review_context(
        root, obpi_id, stage=stage, obligation_ids=tuple(req_ids) if req_ids else None
    )
    return context.model_dump(mode="json"), context.ready
