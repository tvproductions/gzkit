"""Deterministic authoring-time compression composer (OBPI-0.0.37-21).

The composer is the **compress** stage of the CMS pipeline
(``corpus → compress → rendition → playback``). It is deterministic:
NO LLM call, NO network I/O. The drop/combine/rewrite judgment is the
agent's (supplied via ``candidate_text``); the tool validates, accounts
bytes, and returns a ``CandidateRendition``.

Raises ``FileNotFoundError`` when no corpus store exists for the surface.
Raises ``ValueError`` when the (content_type, consumer) setpoint is
undeclared or when the candidate violates the invariant-floor constraint.
"""

from __future__ import annotations

from pathlib import Path

from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.rendition import ByteEvidence, CandidateRendition
from gzkit.content.tier_policy import assert_invariant_verbatim, invariant_entries
from gzkit.content.vendors import content_type_for_surface, temperature_for


def compose(
    root: Path,
    surface: str,
    consumer: str,
    candidate_text: str,
    *,
    content_type: str | None = None,
) -> CandidateRendition:
    """Validate and account a candidate rendition for *surface* toward *consumer*.

    Steps:
    1. Fail closed when no corpus store exists for *surface*.
    2. Resolve the owning content type from *surface* via
       ``content_type_for_surface`` (an explicit *content_type* overrides), then
       the compression setpoint via ``temperature_for``. Both raise ``ValueError``
       when undeclared -- an unmapped surface is never composed under a guess.
    3. Validate invariant-tier verbatim presence in *candidate_text*
       (raises ``ValueError`` on violation — the 0-Kelvin floor).
    4. Compute per-tier byte evidence.
    5. Return a ``CandidateRendition`` (caller writes to disk and ledger).
    """
    store_path = corpus_path(root, surface)
    if not store_path.exists():
        raise FileNotFoundError(
            f"No corpus store for {surface!r} at {store_path.as_posix()}. "
            "Run 'gz content remember' to seed the corpus first."
        )

    corpus = load_corpus(root, surface)

    owner = content_type or content_type_for_surface(surface, project_root=root)
    if owner is None:
        raise ValueError(
            f"No content type declared for surface {surface!r}; declare it in "
            "surface_content_types in data/vendor-manifest.json. Composing under a "
            "guessed owner would grade the candidate against another type's setpoint "
            "and invariant floor (GHI #921)."
        )

    setpoint = temperature_for(owner, consumer, project_root=root)

    # Centralized invariant-tier enforcement (OBPI-0.0.37-23): the 0-Kelvin
    # floor is owned by tier_policy — the single composer-consumable surface.
    # No duplicated inline check here.
    assert_invariant_verbatim(corpus, candidate_text)

    inv_entries = invariant_entries(corpus)
    compressible_entries = [e for e in corpus.entries if e.tier == "compressible"]

    invariant_bytes = sum(len(e.text.encode("utf-8")) for e in inv_entries)
    compressible_bytes_before = sum(len(e.text.encode("utf-8")) for e in compressible_entries)
    total_bytes = len(candidate_text.encode("utf-8"))
    compressible_bytes_after = max(0, total_bytes - invariant_bytes)

    evidence = ByteEvidence(
        invariant_bytes=invariant_bytes,
        compressible_bytes_before=compressible_bytes_before,
        compressible_bytes_after=compressible_bytes_after,
        total_bytes=total_bytes,
        setpoint=setpoint,
    )
    return CandidateRendition(
        surface=surface,
        consumer=consumer,
        setpoint=setpoint,
        candidate_text=candidate_text,
        byte_evidence=evidence,
    )
