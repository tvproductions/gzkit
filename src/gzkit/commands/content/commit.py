"""gz content commit command handler — OBPI-0.0.37-22 (REQ-0.0.37-22-07).

The governed candidate→committed promotion seam. ``gz content compose`` stages a
candidate; this command promotes it to the durable committed rendition AND freezes
the corpus content-fingerprint in a provenance sidecar, under operator attestation
(the corpus attestation). It is the missing REQ-22-01 substance — before this, ``save_rendition``
had no governed caller and renditions were hand-placed.

The corpus attestation is fail-closed: empty ``--attestor`` or ``--attestation-text``
writes nothing.
Promotion is explicit and operator-attested, never automatic — the operator's
verbatim ``--attestation-text`` IS the corpus attestation (mirrors ``gz obpi repudiate``).

This attestation is NOT Gate 5. Gate 5 names OBPI/ADR completion attestation
(``ADR-0.0.36``) and nothing else; a build step wearing that name is the collision
the transit/exchange/handoff fence forbids (operator ruling 2026-08-17, GHI #822).

OBPI-0.35.0-14 (ADR-0.35.0 § Decision item 10) adds the RETENTION GATE: when the
candidate drops a block the prior committed rendition carried, promotion requires a
``--retention-map`` accounting for every condition of every removed block, so a
compression can never silently lose a binding condition again (GHI #1090, #1091).
``enforce_retention`` is the one callable that runs this check, so a future
``content land`` seam can call it without going through the CLI (ADR-0.35.0 BI-10).

Exit 0: rendition + sidecar (+ retention sidecar, when blocks were removed) committed
    and ledger event emitted.
Exit 1: user/config error (empty attestation, absent candidate, absent corpus,
    malformed --retention-map).
Exit 2: system/IO error (including an unreadable prior committed rendition).
Exit 3: retention gate refusal — a removed block is unaccounted for. Writes NOTHING.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import get_project_root
from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.rendition import candidate_path
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    fingerprint_path,
    load_fingerprint,
    rendition_fingerprint,
    rendition_path,
    save_fingerprint,
    save_rendition,
)
from gzkit.content.retention import (
    RetentionMap,
    RetentionViolation,
    first_line,
    removed_blocks,
    retention_path,
    validate_retention,
)
from gzkit.governance.events import emit_rendition_committed


class RetentionOutcome(BaseModel):
    """Result of running the retention gate: whether to proceed, and what to write.

    Pure with respect to the filesystem beyond reads — ``enforce_retention`` never
    writes a rendition, sidecar, or ledger event; the caller writes only when
    ``ok`` is True (Requirement 4).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ok: bool = Field(..., description="True when the gate passed; caller may write")
    exit_code: int | None = Field(None, description="sys.exit code on failure (1, 2, or 3)")
    message: str | None = Field(None, description="stderr recovery prose on failure")
    removed: list[str] = Field(
        default_factory=list, description="Prior blocks removed by this promotion"
    )
    retention_map: RetentionMap | None = Field(
        None,
        description="Validated map to persist, or None when no block was removed",
    )


def _render_violation_report(violations: list[RetentionViolation]) -> str:
    """Render every violation plus three-part recovery prose (guardrail-feedback-prose.md)."""
    findings = "\n".join(f"- [{v.kind}] {v.message}" for v in violations)
    return (
        "Error: the retention gate refused this commit. Nothing was written.\n"
        f"{findings}\n"
        "Why forbidden: a removed block with an unaccounted condition is an "
        "unreviewed meaning loss (ADR-0.35.0 § Decision item 10) — the "
        "2026-09-17 compression dropped 23 binding conditions this way and every "
        "check passed (GHI #1090, #1091).\n"
        "Next: account for every condition of each removed block in a "
        "--retention-map (`gz content commit --help`; manpage `content` § commit) — mark "
        "each KEPT with its verbatim candidate span or DROPPED with a reason, name "
        "every DROPPED condition's id in --attestation-text, then re-run "
        "`gz content commit`."
    )


def enforce_retention(
    root: Path,
    surface: str,
    consumer: str,
    candidate_text: str,
    retention_map_path: str | None,
    attestation_text: str,
) -> RetentionOutcome:
    """Run the retention gate for one candidate→committed promotion.

    The prior rendition is the consumer's COMMITTED rendition
    (``rendition_path(root, surface, consumer)``). The vacuous branch tests that
    path's EXISTENCE, never an empty delta after a failed read — an absent prior
    is never evidence that nothing was lost; it means there is no prior delta to
    lose (Requirement 1). An existing-but-unreadable prior is a system error
    (exit 2), never silently treated as vacuous.

    Args:
        root: Project root.
        surface: Control surface name (e.g. 'AGENTS.md').
        consumer: Target vendor consumer.
        candidate_text: The candidate rendition text about to be promoted.
        retention_map_path: Path to a ``--retention-map`` JSON file, or None.
        attestation_text: The attestation text supplied on THIS invocation --
            never a carried-forward standing attestation. ADR-0.35.0 Decision 10:
            the operator rules on every drop in the words supplied WITH THIS
            COMMIT, so a DROPPED condition's id must appear here, not in an
            earlier, unrelated commit's text that happens to be exempt because
            the CORPUS (not the candidate) is unchanged (GHI #821).

    Returns:
        A ``RetentionOutcome``. ``ok=False`` never has a side effect; the caller
        writes the rendition, provenance sidecar, retention sidecar, and ledger
        event only when ``ok`` is True.

    """
    prior_path = rendition_path(root, surface, consumer)
    if not prior_path.exists():
        removed: list[str] = []
    else:
        try:
            prior_text = prior_path.read_text(encoding="utf-8")
        except OSError as exc:
            return RetentionOutcome(
                ok=False,
                exit_code=2,
                message=f"Error reading prior rendition {prior_path.as_posix()!r}: {exc}",
            )
        removed = removed_blocks(prior_text, candidate_text)

    retention_map: RetentionMap | None = None
    if retention_map_path is not None:
        try:
            raw = Path(retention_map_path).read_text(encoding="utf-8")
            retention_map = RetentionMap.model_validate_json(raw)
        except (OSError, ValueError) as exc:
            # ValueError catches both UnicodeDecodeError (read_text's base for
            # invalid UTF-8 bytes) and ValidationError (pydantic-core's own base
            # for a JSON/schema error) -- a malformed map file is a user/config
            # error (exit 1) either way, never an uncaught traceback.
            return RetentionOutcome(
                ok=False,
                exit_code=1,
                message=(
                    f"Error: --retention-map {retention_map_path!r} is malformed: "
                    f"{exc}. Nothing committed."
                ),
            )

    if not removed:
        # No block was removed this promotion — no sidecar governs a delta that
        # does not exist (Requirement 5), whether or not a map was supplied.
        return RetentionOutcome(ok=True, removed=[], retention_map=None)

    if retention_map is None:
        violations = [
            RetentionViolation(
                kind="missing-retention-map",
                message=(
                    f"Removed block '{first_line(block)}' has no --retention-map accounting for it"
                ),
            )
            for block in removed
        ]
        return RetentionOutcome(ok=False, exit_code=3, message=_render_violation_report(violations))

    violations = validate_retention(removed, candidate_text, retention_map, attestation_text)
    if violations:
        return RetentionOutcome(ok=False, exit_code=3, message=_render_violation_report(violations))

    return RetentionOutcome(ok=True, removed=removed, retention_map=retention_map)


def _retention_correspondence_lines(retention_map: RetentionMap) -> list[str]:
    """Render the KEPT/DROPPED correspondence the tool cannot judge (Requirement 9)."""
    lines: list[str] = []
    for block in retention_map.blocks:
        for condition in block.conditions:
            if condition.disposition == "kept":
                lines.append(f'{condition.id}: "{condition.quote}" -> "{condition.span}"')
            else:
                lines.append(f"{condition.id}: DROPPED -- {condition.reason}")
    return lines


def content_commit_cmd(
    *,
    surface: str,
    consumer: str,
    attestor: str = "",
    attestation_text: str = "",
    retention_map: str | None = None,
) -> None:
    """Handle ``gz content commit <surface> --consumer <c> --attestor <n> --attestation-text <t>``.

    Exit 0 on success; 1 on config/validation error; 2 on IO error; 3 on a
    retention-gate refusal (a removed block is unaccounted for).
    """
    root = get_project_root()

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

    # The corpus attestation attaches to the CANON change, never to this Layer-3
    # re-render (operator ruling 2026-08-17, GHI #821: "a rerender of unhanged canon
    # doesn't require my attestation"). `fingerprint` is the discriminator and was
    # already computed here — read for freshness since OBPI-0.0.37-22, never for this.
    #
    # An ABSENT sidecar is not evidence that canon is unchanged; it is absence of
    # evidence either way. Treating it as an exemption would make the first commit of
    # every consumer the one that escapes the gate, which is the inversion in a new
    # costume. So `standing` requires a sidecar AND a matching digest.
    prior = load_fingerprint(root, surface, consumer)
    standing = prior if prior is not None and prior.corpus_fingerprint == fingerprint else None

    if attestor.strip() and attestation_text.strip():
        # Exempt means "not required", never "not accepted".
        effective_attestor, effective_text = attestor, attestation_text
    elif standing is not None:
        # Canon has not moved, so the operator's standing attestation still describes
        # this corpus. Carrying it forward keeps the sidecar's provenance true; writing
        # an empty attestor would record that nobody attested a corpus somebody did.
        effective_attestor, effective_text = standing.attestor, standing.attestation_text
    else:
        print(
            "Error: --attestor and --attestation-text are required and may not be empty "
            "when the corpus has changed since this consumer's last committed rendition "
            "(corpus attestation fail-closed). Nothing committed.\n"
            "  A re-render of UNCHANGED canon needs no attestation; this corpus moved.",
            file=sys.stderr,
        )
        sys.exit(1)

    # The retention gate runs after the checks above and before any write
    # (Requirement 8) — it never weakens an existing `commit` refusal, only
    # adds its own. It checks a DROPPED id against `attestation_text`, the RAW
    # text supplied on THIS invocation — never `effective_text`, which may be
    # a standing attestation carried forward from an earlier, unrelated commit
    # (exempt only because the CORPUS is unchanged, GHI #821). ADR-0.35.0
    # Decision 10 requires the operator to rule on every drop in the words
    # supplied WITH THIS COMMIT, so an old attestation that happens to contain
    # a condition id must never satisfy this check.
    outcome = enforce_retention(
        root, surface, consumer, candidate_text, retention_map, attestation_text
    )
    if not outcome.ok:
        print(outcome.message, file=sys.stderr)
        sys.exit(outcome.exit_code)

    retention_sidecar = retention_path(root, surface, consumer)
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
                attestor=effective_attestor,
                attestation_text=effective_text,
            ),
        )
        if outcome.retention_map is not None:
            retention_sidecar.parent.mkdir(parents=True, exist_ok=True)
            retention_sidecar.write_text(outcome.retention_map.model_dump_json(), encoding="utf-8")
        elif retention_sidecar.exists():
            # No block was removed this promotion — a stale sidecar from an
            # earlier one must never describe a delta it did not govern
            # (Requirement 5).
            retention_sidecar.unlink()
    except OSError as exc:
        print(f"Error committing rendition for {surface!r}/{consumer!r}: {exc}", file=sys.stderr)
        sys.exit(2)

    emit_rendition_committed(
        root=root,
        surface=surface,
        consumer=consumer,
        corpus_fingerprint=fingerprint,
        attestor=effective_attestor,
    )

    retention_report = ""
    if outcome.retention_map is not None:
        lines = _retention_correspondence_lines(outcome.retention_map)
        if lines:
            retention_report = "\nRetention:\n" + "\n".join(lines)

    print(
        f"Committed: {rendition_path(root, surface, consumer).as_posix()}\n"
        f"Provenance: {fingerprint_path(root, surface, consumer).as_posix()} "
        f"(corpus_fingerprint={fingerprint[:12]}…, entries={len(corpus.entries)})\n"
        f"Attested by: {effective_attestor}"
        + (
            "  (standing attestation carried forward — corpus unchanged since "
            f"{standing.committed_ts})"
            if standing is not None and not attestor.strip()
            else ""
        )
        + retention_report
        # Three-part next step (`.claude/rules/guardrail-feedback-prose.md`): this seam
        # writes the RENDITION only, and a session that stops here has a played-back
        # surface still showing the prior canon. Naming the playback writer here is the
        # difference between a half-applied canon change and a finished one.
        + f"\nNext: `uv run gz agent sync control-surfaces` — this wrote the rendition "
        f"only; playback is the sole writer of {surface} and its mirrors, so "
        "`uv run gz validate --invariant-coherence` stays red until it runs."
    )
