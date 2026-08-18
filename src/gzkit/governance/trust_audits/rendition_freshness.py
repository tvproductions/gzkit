"""Corpus↔rendition freshness gate (ADR-0.0.37 § Re-Alignment, OBPI-0.0.37-22).

Fail-closed when the corpus for a surface no longer matches the committed
rendition it was attested against — i.e. when the rendition can no longer be
proven to derive from the current corpus. The proof is a CONTENT comparison:
a corpus fingerprint frozen in the provenance sidecar at commit time
(``<consumer>.corpus.json``) vs. the corpus's current fingerprint. This
replaces the prior mtime tautology (repudiated 2026-06-16: "compares st_mtime
not content (a zero-byte content-restore flips it red)").

Because the fingerprint is taken over ``Corpus.dumps()`` — the canonical model
serialization, not the file bytes, for cross-platform CRLF/LF stability — the
corpus FIELD SET is part of the identity, not merely the values. Adding an
optional field to ``CorpusEntry`` therefore re-fingerprints every surface even
when the .jsonl is byte-identical on disk. ``BASELINE_IDENTITY_FIELDS`` /
``POST_BASELINE_IDENTITY_FIELDS`` in ``gzkit.content.models.corpus`` classify
each field so additive evolution stays inert here; a field left unclassified
fails closed in that module's fence rather than silently demanding a corpus-attested
recompose (GHI #635).

SIBLING GATE — read both before changing the corpus or its model.
``--rendition-floor-coherence`` guards the same seam and asks a DIFFERENT
question: it is SEMANTIC ("is every invariant text present in the rendition?")
where this gate is IDENTITY ("does this rendition provably derive from THIS
corpus?"). A change can satisfy one and trip the other — retiring a corpus
entry relaxes the floor (that gate stays green) while changing what canon
requires (this gate fires, correctly).

Severity resolved through the shared MX checkpoint (OBPI-0.0.74-09): advisory
inside the hangar (marker present), fail-closed at full strength outside.

Registered as ``gz validate --rendition-freshness``; also runs in ``gz check``.
"""

from __future__ import annotations

from pathlib import Path

from gzkit.advisory import emit_advisory
from gzkit.content.corpus_store import corpus_path as _corpus_path
from gzkit.content.corpus_store import load_corpus
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    fingerprint_path,
    is_graded_rendition,
    load_fingerprint,
    rendition_fingerprint,
)
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.events import emit_composition_drift_detected
from gzkit.mx import checkpoint as _checkpoint
from gzkit.mx import disposition as _disposition
from gzkit.mx import levels as _levels


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


def _integrity_prose(surface: str, consumer: str, what: str) -> str:
    """Three-part recovery message for a rendition that is not the bytes attested."""
    return (
        f"{what} for {surface!r}/{consumer!r}: the committed rendition's bytes are not the "
        f"bytes an operator attested. `gz content commit` is a byte copy, so this artifact was "
        f"written outside the promotion seam — the deterministic-playback seam ADR-0.0.37 "
        f"§ Re-Alignment part 4 names load-bearing, and editing a derived artifact in place is "
        f"forbidden by docs/governance/agent-control-surface-rendering-substrate.md "
        f"§ Anti-patterns (GHI #694). Recompose the intended content and re-attest: "
        f"`gz content compose {surface} --consumer {consumer} --candidate <file>` then "
        f"`gz content commit {surface} --consumer {consumer} "
        f"--attestor <you> --attestation-text <verbatim>`."
    )


def _integrity_findings(
    provenance: RenditionProvenance, rendition_file: Path
) -> list[tuple[str, str]]:
    """Return ``(kind, what)`` findings for the committed bytes vs their frozen digest.

    An absent ``rendition_fingerprint`` is drift, never a skip: treating it as
    "nothing to check" would make the gate bypassable by deleting one JSON field.
    """
    if provenance.rendition_fingerprint is None:
        return [
            (
                "rendition_integrity",
                "No rendition fingerprint in the provenance sidecar (integrity unprovable)",
            )
        ]
    current = rendition_fingerprint(rendition_file.read_bytes())
    if provenance.rendition_fingerprint != current:
        return [
            (
                "rendition_integrity",
                (
                    f"Rendition byte drift (attested {provenance.rendition_fingerprint[:12]} "
                    f"!= on-disk {current[:12]})"
                ),
            )
        ]
    return []


def validate_rendition_freshness(
    root: Path, *, fail_closed: bool | None = None
) -> list[ValidationError]:
    """Check every committed rendition against its corpus AND against its own frozen digest.

    For each ``<surface>/<consumer>.md`` whose surface has a corpus, drift is one of:
    a missing provenance sidecar; a frozen corpus fingerprint that no longer matches the
    corpus (``rendition_freshness`` — the rendition cannot be proven to derive from canon);
    or committed bytes that no longer match their frozen ``rendition_fingerprint``
    (``rendition_integrity`` — the rendition is not what was attested; GHI #694).

    The two arms are independent and can both fire for one rendition: a stale corpus and
    a tampered artifact are different failures with different recoveries. In fail-closed
    mode each drift yields one ``ValidationError`` and emits a ``composition_drift_detected``
    event; in warn mode each prints a stderr WARNING and is omitted (no ledger mutation).

    Returns no errors when the corpus is absent (bootstrap), the rendition is absent,
    or every committed rendition agrees with both its corpus and its attestation.
    """
    closed = (
        _disposition.grounds(_checkpoint.resolve("rendition-freshness", _levels.ERROR, root))
        if fail_closed is None
        else fail_closed
    )

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
            # Grade committed, still-routed renditions only. Staged candidates carry
            # no sidecar, and a superseded record retained per OBPI-0.35.0-09
            # Requirement 4a would otherwise be measured forever against a corpus it
            # was never committed against. Shared with the floor gate so the two
            # cannot disagree about what exists (REQ-0.35.0-09-11).
            if not is_graded_rendition(rendition_file, root):
                continue
            consumer = rendition_file.stem
            target = f"{surface}/{consumer}"
            provenance = load_fingerprint(root, surface, consumer)

            # A missing sidecar defeats both proofs at once — report it once, as freshness.
            if provenance is None:
                findings = [
                    (
                        "rendition_freshness",
                        f"No provenance sidecar ({fingerprint_path(root, surface, consumer).name})",
                    )
                ]
            else:
                findings = []
                if provenance.corpus_fingerprint != current:
                    findings.append(
                        (
                            "rendition_freshness",
                            (
                                f"Corpus drift (committed {provenance.corpus_fingerprint[:12]} "
                                f"!= current {current[:12]})"
                            ),
                        )
                    )
                findings.extend(_integrity_findings(provenance, rendition_file))

            for kind, what in findings:
                prose = (
                    _integrity_prose(surface, consumer, what)
                    if kind == "rendition_integrity"
                    else _recovery_prose(surface, consumer, what)
                )
                if closed:
                    emit_composition_drift_detected(
                        root=root, target=target, diff_first_50_lines=what
                    )
                    errors.append(ValidationError(type=kind, artifact=target, message=prose))
                else:
                    emit_advisory(f"WARNING [rendition-freshness, staged warn]: {prose}")

    return errors
