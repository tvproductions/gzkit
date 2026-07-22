"""Rendition floor-coherence gate (GHI #623 — corrective to ADR-0.0.37).

Every ``tier: invariant`` corpus entry MUST appear verbatim in the committed
rendition for its surface. A rendition that drops an invariant entry is
fail-closed outside the MX hangar. Authored because ``--invariant-coherence``
diffs a rendition against its own committed twin, which never asserts that the
rendition reflects canon at all.

SIBLING GATE — read both before changing the corpus or its model (GHI #635).
``--rendition-freshness`` guards the same seam and asks a DIFFERENT question,
so a change can satisfy one and trip the other:

    this gate   SEMANTIC  — "is every invariant text present in the rendition?"
    freshness   IDENTITY  — "does this rendition provably derive from THIS corpus?"
                            (SHA-256 over ``Corpus.dumps()``, the model
                            serialization — so the corpus FIELD SET is part of
                            the answer, not just the values)

Consequence: relaxing the floor (retiring an entry) leaves this gate green
while freshness fires, because canon changed. Adding an optional model field
leaves this gate green while freshness fires for every surface, even with the
.jsonl byte-identical on disk — the trap ``BASELINE_IDENTITY_FIELDS`` /
``POST_BASELINE_IDENTITY_FIELDS`` in ``gzkit.content.models.corpus`` now close.

(Prior text here described freshness as comparing ``corpus.st_mtime <=
rendition.st_mtime``. That mtime tautology was repudiated 2026-06-16 and
replaced by the content-fingerprint comparison above; the description outlived
the behavior it described and read as "the sibling is inert.")

Severity resolved through the shared MX checkpoint (OBPI-0.0.74-09): advisory
inside the hangar (marker present), fail-closed at full strength outside.

Registered as ``gz validate --rendition-floor-coherence``; also runs in
``gz check``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.tier_policy import invariant_entries
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.events import emit_composition_drift_detected
from gzkit.mx import checkpoint as _checkpoint
from gzkit.mx import disposition as _disposition
from gzkit.mx import levels as _levels


def validate_rendition_floor_coherence(
    root: Path, *, fail_closed: bool | None = None
) -> list[ValidationError]:
    """Assert every committed rendition carries its surface's invariant floor verbatim.

    Scans ``<root>/.gzkit/renditions/<surface>/`` for committed renditions and,
    for each, checks that every ``tier: invariant`` entry of the surface's corpus
    (``<root>/.gzkit/corpus/<surface>.jsonl``) appears verbatim in the rendition
    text. In fail-closed mode each rendition that omits any invariant entry yields
    one ``ValidationError`` (exit 3) and emits a ``composition_drift_detected``
    event; in warn mode (the staged default) each yields a stderr WARNING and is
    omitted from the returned list (no ledger mutation). Empty list when the floor
    holds, the corpus is absent, or no invariant entries are declared
    (bootstrap-safe).
    """
    closed = (
        _disposition.grounds(_checkpoint.resolve("rendition-floor-coherence", _levels.ERROR, root))
        if fail_closed is None
        else fail_closed
    )

    renditions_dir = root / ".gzkit" / "renditions"
    if not renditions_dir.exists():
        return []

    errors: list[ValidationError] = []

    for surface_dir in sorted(renditions_dir.iterdir()):
        if not surface_dir.is_dir():
            continue
        surface = surface_dir.name
        if not corpus_path(root, surface).exists():
            continue

        invariants = invariant_entries(load_corpus(root, surface))
        if not invariants:
            continue

        for rendition_file in sorted(surface_dir.glob("*.md")):
            rendered_text = rendition_file.read_text(encoding="utf-8")
            missing = [entry for entry in invariants if entry.text not in rendered_text]
            if not missing:
                continue

            consumer = rendition_file.stem
            target = f"{surface}/{consumer}"
            missing_ids = ", ".join(entry.id for entry in missing)
            message = (
                f"Committed rendition {target!r} omits {len(missing)} invariant-tier "
                f"corpus entr{'y' if len(missing) == 1 else 'ies'} ({missing_ids}); the "
                "rendition does not satisfy canon's invariant floor (the canon->rendition "
                "seam ADR-0.0.37 requires). Recompose with a candidate that includes "
                f"every invariant-tier entry verbatim: `gz content compose {surface}`, "
                "attest the candidate, then recommit the rendition."
            )
            if not closed:
                print(
                    f"WARNING [rendition-floor-coherence, staged warn]: {message}", file=sys.stderr
                )
                continue
            emit_composition_drift_detected(
                root=root,
                target=target,
                diff_first_50_lines=f"missing invariant-tier entries: {missing_ids}",
            )
            errors.append(
                ValidationError(
                    type="rendition_floor_coherence",
                    artifact=target,
                    message=message,
                )
            )

    return errors
