"""Corpus↔rendition freshness gate (ADR-0.0.37 § Re-Alignment, OBPI-0.0.37-22).

Fail-closed when the corpus for a surface no longer matches the committed
rendition it was attested against — i.e. when the rendition can no longer be
proven to derive from the current corpus. The proof is a CONTENT comparison:
a corpus fingerprint frozen in the provenance sidecar at commit time
(``<consumer>.corpus.json``) vs. the corpus's current fingerprint. This
replaces the prior mtime tautology (repudiated 2026-06-16: "compares st_mtime
not content (a zero-byte content-restore flips it red)").

Staging (OBPI-0.0.41 warn→fail precedent): ``_FRESHNESS_FAIL_CLOSED`` is
``False`` in Increment 1 — drift is reported as a stderr WARNING and the gate
returns no errors, so ``gz check`` stays green while the corpus is enriched and
the real renditions are re-seeded under operator attestation. Increment 2 flips
the flag to ``True``: drift becomes a fail-closed ``ValidationError`` (exit 3)
that also emits a ``composition_drift_detected`` ledger event.

Registered as ``gz validate --rendition-freshness``; also runs in ``gz check``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from gzkit.content.corpus_store import corpus_path as _corpus_path
from gzkit.content.corpus_store import load_corpus
from gzkit.content.rendition_store import (
    corpus_fingerprint,
    fingerprint_path,
    load_fingerprint,
)
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.events import emit_composition_drift_detected

# Staging flag (OBPI-0.0.41 warn→fail precedent). Increment 2 flips this to True.
_FRESHNESS_FAIL_CLOSED = False


def _recovery_prose(surface: str, consumer: str, what: str) -> str:
    """Three-part recovery message (.claude/rules/guardrail-feedback-prose.md)."""
    return (
        f"{what} for {surface!r}/{consumer!r}: the committed rendition can no longer be "
        f"proven to derive from the current corpus (ADR-0.0.37 § Re-Alignment; "
        f"rendition-freshness gate, OBPI-0.0.37-22 REQ-03). Recompose and re-attest: "
        f"`gz content compose {surface} --consumer {consumer}` then "
        f"`gz content commit {surface} --consumer {consumer} "
        f"--attestor <you> --attestation-text <verbatim>`."
    )


def validate_rendition_freshness(
    root: Path, *, fail_closed: bool | None = None
) -> list[ValidationError]:
    """Check every committed rendition against the current corpus content-fingerprint.

    For each ``<surface>/<consumer>.md`` whose surface has a corpus, drift is one of:
    a missing provenance sidecar, or a frozen fingerprint that no longer matches the
    corpus. In fail-closed mode each drift yields one ``ValidationError`` and emits a
    ``composition_drift_detected`` event; in warn mode each drift prints a stderr
    WARNING and is omitted from the returned list (no ledger mutation).

    Returns no errors when the corpus is absent (bootstrap), the rendition is absent,
    or every committed rendition agrees with its corpus.
    """
    closed = _FRESHNESS_FAIL_CLOSED if fail_closed is None else fail_closed

    renditions_dir = root / ".gzkit" / "renditions"
    if not renditions_dir.exists():
        return []

    errors: list[ValidationError] = []

    for surface_dir in renditions_dir.iterdir():
        if not surface_dir.is_dir():
            continue
        surface = surface_dir.name
        corpus_file = _corpus_path(root, surface)
        if not corpus_file.exists():
            continue
        current = corpus_fingerprint(load_corpus(root, surface))

        for rendition_file in surface_dir.glob("*.md"):
            # Skip staged candidates (`<consumer>.candidate.md`) — only committed
            # renditions carry a provenance sidecar and are subject to this gate.
            if rendition_file.name.endswith(".candidate.md"):
                continue
            consumer = rendition_file.stem
            provenance = load_fingerprint(root, surface, consumer)
            if provenance is None:
                what = f"No provenance sidecar ({fingerprint_path(root, surface, consumer).name})"
            elif provenance.corpus_fingerprint != current:
                what = (
                    f"Corpus drift (committed {provenance.corpus_fingerprint[:12]} "
                    f"!= current {current[:12]})"
                )
            else:
                continue

            target = f"{surface}/{consumer}"
            message = _recovery_prose(surface, consumer, what)
            if closed:
                emit_composition_drift_detected(root=root, target=target, diff_first_50_lines=what)
                errors.append(
                    ValidationError(type="rendition_freshness", artifact=target, message=message)
                )
            else:
                print(f"WARNING [rendition-freshness, staged warn]: {message}", file=sys.stderr)

    return errors
