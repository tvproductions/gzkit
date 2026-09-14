"""An approval must cite what its reviewer could read, and the citation must hold (GHI #994).

A Stage-2 reviewer granted only reading recorded an "independently located"
ledger observation that did not exist, and approved a proof on it. The claim sat
in narrative prose the importer never reads, so nothing challenged it -- and the
failure runs OPEN, because a fabricated confirmation only makes a requirement
look more proven than it is.

Prose is never parsed for claims; that is the substring-guessing failure GHI
#888 closed. The structured channel is ``grounds``: an excerpt copied from a
repository file the reviewer read, or from a proof's recorded evidence. Presence
is checked the way a replay claim is (GHI #961): every citation supplied must
occur where it says. A reviewer whose transport cannot execute must additionally
cite each proof it approves, because reading is the only observation it has.
Whether an excerpt SUPPORTS the approval stays the reviewer's judgment; this
establishes only that the reviewer can point at bytes that exist.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from gzkit.acceptance import Ground, Proof, Review
from gzkit.pipeline_dispatch import reviewer_capability

MIN_EXCERPT_CHARS = 20
"""Shorter text cannot identify what was read -- ``value`` occurs in most source files."""


_PERSONA_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
# Flags that replace or narrow the tool set at invocation, so the persona file no
# longer states what ran; their presence makes the grant unresolvable.
_TOOL_OVERRIDES = frozenset(
    {
        "--agents",
        "--tools",
        "--allowedTools",
        "--allowed-tools",
        "--disallowedTools",
        "--disallowed-tools",
    }
)


def _invoked_agent(command: Sequence[Any]) -> str | None:
    """Return the one persona whose file decides the grant, or None when argv leaves it open.

    None -- and therefore "cannot execute" -- when no persona is named, when two
    are, when the name is not a plain persona name (``../escape`` would read a
    file outside the agent directory), or when a flag overrides the tool set.
    """
    names: list[str] = []
    for index, token in enumerate(command):
        flag, separator, inline = str(token).partition("=")
        if flag in _TOOL_OVERRIDES:
            return None
        if flag == "--agent":
            if separator:
                names.append(inline)
            elif index + 1 < len(command):
                names.append(str(command[index + 1]))
    if len(names) != 1 or not _PERSONA_NAME.fullmatch(names[0]):
        return None
    return names[0]


def reviewer_executes(root: Path, review: Review, receipt: dict[str, Any]) -> bool:
    """Whether the review's transport could execute; an unresolvable grant cannot.

    Tier 1 is the cross-vendor transport, whose execution claims travel as replay
    records (GHI #961). A native invocation executes only when the persona it
    names declares a shell -- read from the agent definition by the same reader
    that discloses the grant to the reviewer (GHI #941), never assumed.
    """
    if review.tier == 1:
        return True
    agent = _invoked_agent(receipt["step"]["command"])
    return agent is not None and reviewer_capability(root, agent).can_execute


def _normalized(text: str) -> str:
    """Whitespace-insensitive: a reviewer quoting two lines reflows them."""
    return " ".join(text.split())


def _source_text(root: Path, ground: Ground, proofs: dict[str, Proof]) -> str | None:
    """Return the text a citation names, or None when it names nothing in the repository."""
    if ground.path is None:
        proof = proofs.get(ground.proof_id)
        return None if proof is None else proof.evidence
    base = root.resolve()
    target = (base / ground.path).resolve()
    if not target.is_relative_to(base) or not target.is_file():
        return None
    try:
        return target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _citation_error(root: Path, ground: Ground, review: Review, proofs: dict[str, Proof]) -> str:
    """Why one citation fails, or an empty string when its excerpt occurs where it says."""
    where = ground.path or f"proof {ground.proof_id} evidence"
    excerpt = _normalized(ground.excerpt)
    if ground.proof_id not in review.proof_ids:
        return f"a citation names proof {ground.proof_id}, which the review did not examine"
    if len(excerpt) < MIN_EXCERPT_CHARS:
        return f"the excerpt cited from {where} is under {MIN_EXCERPT_CHARS} characters"
    source = _source_text(root, ground, proofs)
    if source is None:
        return f"{where} is not a readable file inside the repository"
    if excerpt not in _normalized(source):
        return f"the excerpt cited from {where} does not occur there"
    return ""


def refuse_uncited_approval(
    root: Path, review: Review, proofs: Sequence[Proof], receipt: dict[str, Any]
) -> None:
    """Refuse a false citation, and an uncited approval from a reviewer that cannot execute."""
    by_id = {proof.id: proof for proof in proofs}
    reasons: list[str] = []
    cited: set[str] = set()
    for ground in review.grounds:
        error = _citation_error(root, ground, review, by_id)
        if error:
            reasons.append(error)
        else:
            cited.add(ground.proof_id)
    executes = reviewer_executes(root, review, receipt)
    if not executes:
        reasons.extend(
            f"the approval of proof {proof_id} cites nothing the reviewer read"
            for proof_id in review.accepted_proof_ids
            if proof_id not in cited
        )
    if not reasons:
        return
    who = "a reviewer that can execute" if executes else "a reviewer that cannot execute"
    raise ValueError(
        f"Review from {who} approves on evidence it does not ground: "
        + "; ".join(reasons)
        + ". Cite in `grounds` an excerpt copied from a repository file you read or from "
        "the proof's recorded evidence, or leave a check you could not perform in "
        "`verification_gaps` and do not approve on it (GHI #994)."
    )
