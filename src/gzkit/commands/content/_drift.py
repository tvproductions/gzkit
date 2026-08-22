"""Rendition-drift announcement shared by every corpus-mutating content verb.

GHI #654 established that appending to the corpus must announce the drift it
causes, and gave ``gz content remember`` a warning. ``gz content retire`` never
got one, and its help asserted the opposite — *"no recomposition is implied"*
(GHI #863). Both verbs append a row, both move the corpus fingerprint, and both
therefore break every committed rendition's derivation proof.

The announcement is a property of **appending to the store**, not of the
particular verb, so it lives here rather than in either command. A future
corpus-mutating verb inherits it by calling :func:`warn_on_rendition_drift`
instead of re-deriving the reporting logic.
"""

from __future__ import annotations

import sys
from pathlib import Path

from gzkit.content.corpus_store import load_corpus
from gzkit.content.rendition_store import corpus_fingerprint, load_fingerprint


def drifted_consumers(root: Path, surface: str) -> list[str]:
    """Return the committed consumers of *surface* whose provenance no longer matches.

    Reads the same two facts the freshness gate compares — the sidecar's
    ``corpus_fingerprint`` and the current corpus digest — but deliberately does NOT
    call ``validate_rendition_freshness``: that validator emits ``composition_drift_
    detected`` ledger events on its fail-closed path, and a mutating command must not
    write drift events for a condition it is merely reporting.

    A consumer with no sidecar is skipped. Its rendition was already unprovable before
    this mutation, so naming it here would misattribute pre-existing drift.
    """
    rendition_dir = root / ".gzkit" / "renditions" / surface
    if not rendition_dir.is_dir():
        return []
    current = corpus_fingerprint(load_corpus(root, surface))
    drifted = []
    for path in sorted(rendition_dir.glob("*.md")):
        if path.name.endswith(".candidate.md"):
            continue
        provenance = load_fingerprint(root, surface, path.stem)
        if provenance is not None and provenance.corpus_fingerprint != current:
            drifted.append(path.stem)
    return drifted


def warn_on_rendition_drift(
    root: Path,
    surface: str,
    *,
    mutation: str,
    floor_risk: bool,
) -> None:
    """Announce, on stderr, the rendition drift this mutation just caused.

    *mutation* is the noun used in the warning ("append", "retirement"), and
    *floor_risk* says whether the floor gate is also at stake.

    The floor distinction is the substantive difference between the verbs and is
    why this is not a single boolean tier check: an invariant-tier APPEND adds an
    entry every rendition must now carry verbatim, so floor coherence can fail. A
    RETIREMENT only ever removes entries from that set, so a rendition satisfying
    the floor before still satisfies it after — naming the floor gate there would
    send the operator to recompose for a reason that cannot occur.

    Advisory only — never changes the exit code. The mutation succeeded and IS the
    intended effect; what the operator lacked was any signal that ``gz check`` would
    now fail on gates the command never mentioned.
    """
    # The row is already durable. Drift detection is best-effort reporting ON TOP of
    # it, so no fault here may cost the operator their words or their exit code: a
    # malformed sidecar makes `RenditionProvenance.model_validate_json` raise, and an
    # unreadable corpus makes `load_corpus` raise. Capture must stay unblockable.
    try:
        drifted = drifted_consumers(root, surface)
    except (OSError, ValueError):
        return
    if not drifted:
        return

    # Flush first: stdout is buffered and stderr is not, so without this the warning
    # lands ABOVE the success line it is annotating (observed 2026-07-22).
    sys.stdout.flush()

    lines = [
        "",
        f"Warning: this {mutation} drifted {len(drifted)} committed rendition(s) of {surface!r}",
        f"  ({', '.join(drifted)}). They no longer derive from the current corpus,",
        "  so `gz check` will now fail on:",
        "    - Rendition freshness",
    ]
    if floor_risk:
        lines.append("    - Rendition floor coherence (invariant-tier entry)")
    lines.append("")
    lines.append("  Recover by recomposing and re-attesting each consumer:")
    for consumer in drifted:
        lines.append(f"    uv run gz content compose {surface} --consumer {consumer} \\")
        lines.append("        --candidate <file>")
        lines.append(f"    uv run gz content commit {surface} --consumer {consumer} \\")
        lines.append("        --attestor <you> --attestation-text <words>")
    if floor_risk:
        lines.append("")
        lines.append("  The invariant-tier text must appear VERBATIM in every rendition;")
        lines.append("  omitting it fails the floor gate even after a recompose.")

    print("\n".join(lines), file=sys.stderr)
