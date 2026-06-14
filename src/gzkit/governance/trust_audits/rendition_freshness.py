"""Corpus↔rendition freshness gate (ADR-0.0.37 § Re-Alignment, OBPI-0.0.37-22).

Fail-closed when the corpus for a surface has mutated after its committed
rendition — exit 3 with a recompose recovery hint. Exit 0 when corpus and
rendition timestamps agree, or when either is absent.

Registered as ``gz validate --rendition-freshness``; also runs in ``gz check``.
"""

from __future__ import annotations

from pathlib import Path

from gzkit.content.corpus_store import corpus_path as _corpus_path
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.events import emit_composition_drift_detected


def validate_rendition_freshness(root: Path) -> list[ValidationError]:
    """Check corpus↔rendition timestamps for every committed rendition.

    Scans ``<root>/.gzkit/renditions/<surface>/`` for committed rendition
    artifacts and compares each against the corresponding corpus at
    ``<root>/.gzkit/corpus/<surface>.jsonl``.

    Returns empty list when corpus is absent, rendition is absent, or rendition
    is at least as recent as the corpus (exit 0). Returns one
    ``ValidationError`` per stale rendition when the corpus is newer (exit 3).
    """
    renditions_dir = root / ".gzkit" / "renditions"
    if not renditions_dir.exists():
        return []

    errors: list[ValidationError] = []

    for surface_dir in renditions_dir.iterdir():
        if not surface_dir.is_dir():
            continue
        surface = surface_dir.name
        corpus = _corpus_path(root, surface)
        if not corpus.exists():
            continue

        corpus_mtime = corpus.stat().st_mtime

        for rendition_file in surface_dir.glob("*.md"):
            rendition_mtime = rendition_file.stat().st_mtime
            if corpus_mtime <= rendition_mtime:
                continue

            consumer = rendition_file.stem
            target = f"{surface}/{consumer}"
            emit_composition_drift_detected(
                root=root,
                target=target,
                diff_first_50_lines=(
                    f"corpus={corpus.as_posix()} "
                    f"mtime={corpus_mtime:.3f} > "
                    f"rendition={rendition_file.as_posix()} "
                    f"mtime={rendition_mtime:.3f}"
                ),
            )
            errors.append(
                ValidationError(
                    type="rendition_freshness",
                    artifact=target,
                    message=(
                        f"Corpus for {surface!r} has mutated after its committed rendition"
                        f" ({consumer!r}). "
                        f"Run `gz content compose {surface}` and attest to recompose."
                    ),
                )
            )

    return errors
