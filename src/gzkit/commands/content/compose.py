"""gz content compose command handler — OBPI-0.0.37-21, OBPI-0.35.0-05.

Compress stage of the CMS pipeline. Two modes:

- **Explicit** (unchanged, OBPI-0.0.37-21): the agent supplies
  ``candidate_text`` via ``--candidate <file>`` or piped/redirected stdin;
  this command validates invariant-floor compliance, writes the candidate
  artifact, and emits a ``composition_candidate_emitted`` ledger event.
- **Generated** (OBPI-0.35.0-05): when ``--candidate`` is absent and no
  caller-supplied text is available -- stdin is a tty (never read, so the
  command can never block on an interactive terminal), OR stdin is
  redirected/piped but carries only empty/whitespace-only content -- the
  candidate and its section lineage are DERIVED from the corpus via
  ``generate_candidate()``.

NEVER edits a rendered surface (AGENTS.md, CLAUDE.md, mirrors). Only the
candidate artifact and its staged lineage under ``.gzkit/renditions/``, plus
the ledger, change.

Exit 0: candidate written + ledger event emitted.
Exit 1: user/config error (missing corpus, undeclared setpoint, invariant
    violation, off-route consumer, duplicate live invariant, missing prior
    rendition, preamble refusal).
Exit 2: system/IO error.
"""

from __future__ import annotations

import sys
from pathlib import Path

from gzkit.commands.common import get_project_root
from gzkit.content.composer import CandidateRendition, compose, generate_candidate
from gzkit.content.lineage import ConsumerLineage, candidate_lineage_path, save_candidate_lineage
from gzkit.content.rendition import candidate_path
from gzkit.ledger import Ledger
from gzkit.ledger_events import composition_candidate_emitted_event


def _stdin_is_tty() -> bool:
    """Return True when stdin is an interactive terminal.

    ``isatty()`` can raise on an unusual stdin object; any exception is
    treated as "not a tty" so this guard can never break a currently-working
    piped/redirected invocation.
    """
    try:
        return sys.stdin.isatty()
    except Exception:  # noqa: BLE001 -- unusual stdin can raise any exception type
        # (io.UnsupportedOperation, OSError, ValueError); all mean "not a tty".
        return False


def _generate(
    root: Path, surface: str, consumer: str
) -> tuple[CandidateRendition, ConsumerLineage]:
    """Run the generated path; exits (code 1) on a config/validation error."""
    try:
        result = generate_candidate(root, surface, consumer)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    return result.rendition, result.lineage


def _read_candidate_file(root: Path, candidate: str) -> str:
    """Read *candidate*'s file contents relative to *root*; exits (2) on IO error."""
    try:
        return (root / candidate).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error reading candidate file {candidate!r}: {exc}", file=sys.stderr)
        sys.exit(2)


def _compose_explicit(
    root: Path, surface: str, consumer: str, candidate_text: str
) -> tuple[CandidateRendition, None]:
    """Validate and account *candidate_text* via ``compose()``; exits (1) on failure."""
    try:
        rendition = compose(root, surface, consumer, candidate_text)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    return rendition, None


def content_compose_cmd(*, surface: str, consumer: str, candidate: str | None) -> None:
    """Handle ``gz content compose <surface> --consumer <vendor> [--candidate <file>]``.

    Mode selection (ADR-0.35.0 Task 4 contract):

    * ``--candidate <file>`` given -> EXPLICIT, read the file.
    * no ``--candidate``, stdin IS a tty -> GENERATED, stdin never read.
    * no ``--candidate``, stdin not a tty, content empty/whitespace-only ->
      GENERATED -- empty stdin IS "no caller-supplied text".
    * no ``--candidate``, stdin not a tty, stdin has real content -> EXPLICIT,
      use it.

    Exit 0 on success; 1 on config/validation error; 2 on IO error.
    """
    root = get_project_root()

    if candidate is not None:
        candidate_text = _read_candidate_file(root, candidate)
        rendition, lineage = _compose_explicit(root, surface, consumer, candidate_text)
    elif _stdin_is_tty():
        rendition, lineage = _generate(root, surface, consumer)
    else:
        stdin_text = sys.stdin.read()
        if stdin_text.strip():
            rendition, lineage = _compose_explicit(root, surface, consumer, stdin_text)
        else:
            rendition, lineage = _generate(root, surface, consumer)

    out_path = candidate_path(root, surface, consumer)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # write_bytes, never write_text (Fix 3, cross-vendor adversarial
        # review): write_text opens with newline=None and performs
        # platform-dependent line-ending translation (LF -> CRLF on
        # Windows), which would change the persisted byte length away from
        # the length the generated lineage's byte spans were computed over.
        out_path.write_bytes(rendition.candidate_text.encode("utf-8"))
    except OSError as exc:
        print(f"Error writing candidate to {out_path.as_posix()!r}: {exc}", file=sys.stderr)
        sys.exit(2)

    lineage_out_path = None
    if lineage is not None:
        try:
            lineage_out_path = save_candidate_lineage(root, lineage)
        except OSError as exc:
            print(f"Error writing lineage: {exc}", file=sys.stderr)
            sys.exit(2)
    else:
        # Fix 4 (cross-vendor adversarial review): the explicit path
        # overwrites <consumer>.candidate.md but, without this, leaves a
        # PRIOR generated run's <consumer>.candidate.lineage.json untouched --
        # a supported generated -> explicit workflow left a provenance map
        # describing DIFFERENT bytes than the new candidate. Never stage a
        # lineage the explicit path did not itself produce.
        stale_lineage_path = candidate_lineage_path(root, surface, consumer)
        if stale_lineage_path.exists():
            try:
                stale_lineage_path.unlink()
            except OSError as exc:
                print(
                    f"Error removing stale lineage {stale_lineage_path.as_posix()!r}: {exc}",
                    file=sys.stderr,
                )
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
    lines = [f"Candidate: {out_path.as_posix()}"]
    if lineage_out_path is not None:
        lines.append(f"Lineage: {lineage_out_path.as_posix()}")
    lines.append(
        f"Byte evidence: invariant={ev.invariant_bytes}B "
        f"compressible={ev.compressible_bytes_before}B→{ev.compressible_bytes_after}B "
        f"total={ev.total_bytes}B setpoint={ev.setpoint}"
    )
    print("\n".join(lines))
