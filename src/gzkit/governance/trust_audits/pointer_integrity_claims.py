"""Enforcement claims for the pointer-integrity validator (GHI #1155, gate GHI #932).

``pointer_integrity.validate_pointer_integrity`` once discharged a pointer's back-pointer
obligation with a bare substring test: one ``<!-- lifted-from: -->`` comment anywhere in a
destination satisfied every pointer from every source into that file, forever. It was
repaired to require a comment naming ``<source-path>#<anchor>`` for the pointer under
validation, but no registered claim named the validator, so the repair's green was
unfalsified.

Two claims, on the exemption-half precedent (GHI #797).

* ``pointer-back-pointer-matched`` plants, for each shape of destination that carries a
  ``lifted-from`` comment which does not name the pointer under validation (another source,
  another anchor, a file-level comment with no anchor, one comment standing in for two
  pointers) or carries none, a tree whose pointer must be refused, naming the source it
  refused.
* ``pointer-back-pointer-matched-admitted`` is the admit control: a destination carrying a
  matching comment for each of its pointers is not refused, so an always-refuse validator
  cannot discharge the first claim alone.

The destination sits outside ``docs/governance`` so the reverse arm (GHI #933) has no
declaration to read and every finding comes from the forward arm.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

REFUSE_CLAIM_ID = "pointer-back-pointer-matched"
ADMIT_CLAIM_ID = "pointer-back-pointer-matched-admitted"
BACK_POINTER_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

_REFUSED = "back-pointer refused"
_DEST = "notes/dest.md"
_FIRST = "section-one"
_SECOND = "section-two"
_DEST_BODY = "# Dest\n\n## Section one\n\ntext\n\n## Section two\n\ntext\n"


def _comment(source: str, anchor: str | None = _FIRST) -> str:
    return f"<!-- lifted-from: {source}{'#' + anchor if anchor else ''} -->"


#: shape -> (the destination's comments, whether CLAUDE.md also points at the second
#: section, the source whose pointer must be refused). The destination carries a comment
#: in every shape but ``absent``: the old test accepted any one of them.
_SHAPES: dict[str, tuple[tuple[str, ...], bool, str]] = {
    "absent": ((), False, "AGENTS.md"),
    "other-source": ((_comment("CLAUDE.md"),), False, "AGENTS.md"),
    "other-anchor": ((_comment("AGENTS.md", _SECOND),), False, "AGENTS.md"),
    "file-level": ((_comment("AGENTS.md", None),), False, "AGENTS.md"),
    "one-comment-for-two-pointers": ((_comment("AGENTS.md"),), True, "CLAUDE.md"),
}


def unmatched_shape_population() -> list[str]:
    """Return every shape of destination whose pointer must be refused."""
    return list(_SHAPES)


def _plant(root: Path, comments: tuple[str, ...], claude_points: bool) -> None:
    """Write AGENTS.md (and optionally CLAUDE.md) pointing at a destination with *comments*."""
    (root / "notes").mkdir()
    (root / _DEST).write_text(_DEST_BODY + "\n".join(comments) + "\n", encoding="utf-8")
    (root / "AGENTS.md").write_text(f"> See [one]({_DEST}#{_FIRST})\n", encoding="utf-8")
    if claude_points:
        (root / "CLAUDE.md").write_text(f"> See [two]({_DEST}#{_SECOND})\n", encoding="utf-8")


def _build_shape(member: str | None = None) -> str | None:
    """Name the destination shape to plant; ``None`` plants every pointer matched."""
    return member


# Each entrypoint imports the validator itself: the registry derives a claim's
# `gate_targets` from the entrypoint's own imports (GHI #798), so a helper doing the import
# would leave the claim naming no gate at all.


def _ep_unmatched_refused(shape: str) -> list[str]:
    """Return a finding naming *shape* when its pointer is refused for its back-pointer."""
    from gzkit.governance.trust_audits.pointer_integrity import (  # noqa: PLC0415
        validate_pointer_integrity,
    )

    comments, claude_points, failing_source = _SHAPES[shape]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _plant(root, comments, claude_points)
        errors = validate_pointer_integrity(root)
    refused = [
        e.message
        for e in errors
        if "back-pointer" in e.message and f"referenced by {failing_source}:" in e.message
    ]
    return [f"{shape}: {_REFUSED}: {refused[0]}"] if refused else []


def _ep_matched_admitted(_shape: str | None) -> int:
    """Truthy only when every pointer carries its own matching back-pointer and none is refused."""
    from gzkit.governance.trust_audits.pointer_integrity import (  # noqa: PLC0415
        validate_pointer_integrity,
    )

    comments = (_comment("AGENTS.md"), _comment("CLAUDE.md", _SECOND))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _plant(root, comments, claude_points=True)
        return 0 if validate_pointer_integrity(root) else 1


class _BackPointerMarker:
    """Inert carrier for the back-pointer ``@enforces`` registrations."""


def ensure_back_pointer_claims_registered() -> None:
    """(Re)register the back-pointer claims (idempotent, reset-safe).

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

    extend_known_claims(BACK_POINTER_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            _build_shape,
            _ep_unmatched_refused,
            expect=_REFUSED,
            exempts=ADMIT_CLAIM_ID,
            population=unmatched_shape_population,
        )(_BackPointerMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            _build_shape,
            _ep_matched_admitted,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_BackPointerMarker)
