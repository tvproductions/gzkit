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
from gzkit.content.vendors import temperature_for


def compose(
    root: Path,
    surface: str,
    consumer: str,
    candidate_text: str,
    *,
    content_type: str = "AgentContract",
) -> CandidateRendition:
    """Validate and account a candidate rendition for *surface* toward *consumer*.

    Steps:
    1. Fail closed when no corpus store exists for *surface*.
    2. Resolve the compression setpoint via ``temperature_for``
       (raises ``ValueError`` when undeclared).
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

    setpoint = temperature_for(content_type, consumer, project_root=root)

    invariant_entries = [e for e in corpus.entries if e.tier == "invariant"]
    compressible_entries = [e for e in corpus.entries if e.tier == "compressible"]

    for entry in invariant_entries:
        if entry.text not in candidate_text:
            raise ValueError(
                f"Invariant-floor violation: entry {entry.id!r} text not found verbatim "
                "in candidate. Invariant-tier entries MUST appear unchanged at every "
                "setpoint (0-Kelvin floor)."
            )

    invariant_bytes = sum(len(e.text.encode("utf-8")) for e in invariant_entries)
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
