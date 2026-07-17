"""gz content commit command handler — OBPI-0.0.37-22 (REQ-0.0.37-22-07).

The governed candidate→committed promotion seam. ``gz content compose`` stages a
candidate; this command promotes it to the durable committed rendition AND freezes
the corpus content-fingerprint in a provenance sidecar, under operator attestation
(Gate 5). It is the missing REQ-22-01 substance — before this, ``save_rendition``
had no governed caller and renditions were hand-placed.

Gate 5 is fail-closed: empty ``--attestor`` or ``--attestation-text`` writes nothing.
Promotion is explicit and operator-attested, never automatic — the operator's
verbatim ``--attestation-text`` IS Gate 5 (mirrors ``gz obpi repudiate``).

Exit 0: rendition + sidecar committed + ledger event emitted.
Exit 1: user/config error (empty attestation, absent candidate, absent corpus).
Exit 2: system/IO error.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime

from gzkit.commands.common import get_project_root
from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.rendition import candidate_path
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    fingerprint_path,
    rendition_fingerprint,
    rendition_path,
    save_fingerprint,
    save_rendition,
)
from gzkit.governance.events import emit_rendition_committed


def content_commit_cmd(
    *, surface: str, consumer: str, attestor: str, attestation_text: str
) -> None:
    """Handle ``gz content commit <surface> --consumer <c> --attestor <n> --attestation-text <t>``.

    Exit 0 on success; 1 on config/validation error; 2 on IO error.
    """
    root = get_project_root()

    # Gate 5 fail-closed: attestation is required and may not be empty.
    if not attestor.strip() or not attestation_text.strip():
        print(
            "Error: --attestor and --attestation-text are required and may not be empty "
            "(Gate 5 fail-closed). Nothing committed.",
            file=sys.stderr,
        )
        sys.exit(1)

    candidate = candidate_path(root, surface, consumer)
    if not candidate.exists():
        print(
            f"Error: no staged candidate at {candidate.as_posix()!r}. "
            f"Run `gz content compose {surface} --consumer {consumer}` first.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not corpus_path(root, surface).exists():
        print(
            f"Error: no corpus for {surface!r} at {corpus_path(root, surface).as_posix()!r}; "
            "cannot freeze a corpus fingerprint. Capture content with `gz content remember` first.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        # read_text normalizes CRLF→LF (universal newlines); re-encode to LF bytes so
        # playback stays line-ending clean across platforms.
        candidate_text = candidate.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error reading candidate {candidate.as_posix()!r}: {exc}", file=sys.stderr)
        sys.exit(2)

    if not candidate_text.strip():
        print(
            f"Error: candidate {candidate.as_posix()!r} is empty. Nothing committed.",
            file=sys.stderr,
        )
        sys.exit(1)

    corpus = load_corpus(root, surface)
    fingerprint = corpus_fingerprint(corpus)
    rendition_bytes = candidate_text.encode("utf-8")

    try:
        save_rendition(root, surface, consumer, rendition_bytes)
        save_fingerprint(
            root,
            surface,
            consumer,
            RenditionProvenance(
                corpus_fingerprint=fingerprint,
                corpus_entry_count=len(corpus.entries),
                rendition_fingerprint=rendition_fingerprint(rendition_bytes),
                committed_ts=datetime.now(UTC).isoformat(),
                attestor=attestor,
                attestation_text=attestation_text,
            ),
        )
    except OSError as exc:
        print(f"Error committing rendition for {surface!r}/{consumer!r}: {exc}", file=sys.stderr)
        sys.exit(2)

    emit_rendition_committed(
        root=root,
        surface=surface,
        consumer=consumer,
        corpus_fingerprint=fingerprint,
        attestor=attestor,
    )

    print(
        f"Committed: {rendition_path(root, surface, consumer).as_posix()}\n"
        f"Provenance: {fingerprint_path(root, surface, consumer).as_posix()} "
        f"(corpus_fingerprint={fingerprint[:12]}…, entries={len(corpus.entries)})\n"
        f"Attested by: {attestor}"
    )
