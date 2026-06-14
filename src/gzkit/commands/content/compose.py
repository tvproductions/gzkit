"""gz content compose command handler — OBPI-0.0.37-21.

Compress stage of the CMS pipeline. The agent (skill wielder) supplies a
``candidate_text`` via ``--candidate <file>`` or stdin; this command
validates invariant-floor compliance, writes the candidate artifact, and
emits a ``composition_candidate_emitted`` ledger event.

NEVER edits a rendered surface (AGENTS.md, CLAUDE.md, mirrors). Only the
candidate artifact under ``.gzkit/renditions/`` and the ledger change.

Exit 0: candidate written + ledger event emitted.
Exit 1: user/config error (missing corpus, undeclared setpoint, invariant violation).
Exit 2: system/IO error.
"""

from __future__ import annotations

import sys

from gzkit.commands.common import get_project_root
from gzkit.content.composer import compose
from gzkit.content.rendition import candidate_path
from gzkit.ledger import Ledger
from gzkit.ledger_events import composition_candidate_emitted_event


def content_compose_cmd(*, surface: str, consumer: str, candidate: str | None) -> None:
    """Handle ``gz content compose <surface> --consumer <vendor> [--candidate <file>]``.

    Exit 0 on success; 1 on config/validation error; 2 on IO error.
    """
    root = get_project_root()

    if candidate is not None:
        try:
            candidate_text = (root / candidate).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Error reading candidate file {candidate!r}: {exc}", file=sys.stderr)
            sys.exit(2)
    else:
        candidate_text = sys.stdin.read()

    try:
        rendition = compose(root, surface, consumer, candidate_text)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    out_path = candidate_path(root, surface, consumer)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        out_path.write_text(rendition.candidate_text, encoding="utf-8")
    except OSError as exc:
        print(f"Error writing candidate to {out_path.as_posix()!r}: {exc}", file=sys.stderr)
        sys.exit(2)

    Ledger(root / ".gzkit" / "ledger.jsonl").append(
        composition_candidate_emitted_event(
            surface=surface,
            consumer=consumer,
            setpoint=rendition.setpoint,
            invariant_bytes=rendition.byte_evidence.invariant_bytes,
            compressible_bytes_before=rendition.byte_evidence.compressible_bytes_before,
            compressible_bytes_after=rendition.byte_evidence.compressible_bytes_after,
            total_bytes=rendition.byte_evidence.total_bytes,
        )
    )

    ev = rendition.byte_evidence
    print(
        f"Candidate: {out_path.as_posix()}\n"
        f"Byte evidence: invariant={ev.invariant_bytes}B "
        f"compressible={ev.compressible_bytes_before}B→{ev.compressible_bytes_after}B "
        f"total={ev.total_bytes}B setpoint={ev.setpoint}"
    )
