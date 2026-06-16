"""Rendition floor-coherence gate (GHI #623 — corrective to ADR-0.0.37).

The REAL content witness that repudiated OBPI-0.0.37-22 only simulated. The
"freshness" gate it shipped compares ``corpus.st_mtime <= rendition.st_mtime``
(timestamps), and ``--invariant-coherence`` diffs the rendition against its own
committed twin — neither asserts that the committed rendition actually reflects
canon. This gate closes that seam: every ``tier: invariant`` corpus entry MUST
appear verbatim in the committed rendition for its surface. A rendition that
drops an invariant entry fails closed (exit 3).

Registered as ``gz validate --rendition-floor-coherence``; also runs in
``gz check``.
"""

from __future__ import annotations

from pathlib import Path

from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.tier_policy import invariant_entries
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.events import emit_composition_drift_detected


def validate_rendition_floor_coherence(root: Path) -> list[ValidationError]:
    """Assert every committed rendition carries its surface's invariant floor verbatim.

    Scans ``<root>/.gzkit/renditions/<surface>/`` for committed renditions and,
    for each, checks that every ``tier: invariant`` entry of the surface's corpus
    (``<root>/.gzkit/corpus/<surface>.jsonl``) appears verbatim in the rendition
    text. Returns one ``ValidationError`` per rendition that omits any invariant
    entry (exit 3); empty list when the floor holds, the corpus is absent, or no
    invariant entries are declared (bootstrap-safe).
    """
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
            emit_composition_drift_detected(
                root=root,
                target=target,
                diff_first_50_lines=f"missing invariant-tier entries: {missing_ids}",
            )
            errors.append(
                ValidationError(
                    type="rendition_floor_coherence",
                    artifact=target,
                    message=(
                        f"Committed rendition {target!r} omits {len(missing)} invariant-tier "
                        f"corpus entr{'y' if len(missing) == 1 else 'ies'} ({missing_ids}); the "
                        "rendition does not satisfy canon's invariant floor (the canon->rendition "
                        "seam ADR-0.0.37 requires). Recompose with a candidate that includes "
                        f"every invariant-tier entry verbatim: `gz content compose {surface}`, "
                        "attest the candidate, then recommit the rendition."
                    ),
                )
            )

    return errors
