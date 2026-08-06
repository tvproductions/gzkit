"""Exchange records — the OBPI token block's register entries (ADR-0.0.41).

An **exchange record** notes one block's vacation: the token holder surrendering
its claim, plus an observation report of what happened during the traversal. It
is NOT a session handoff. Operator canon, ruled 2026-08-06 and seated at
``invariant`` tier in ``.gzkit/corpus/AGENTS.md.jsonl`` (spelling preserved):

    transit (how we enter and leave the designed ecosysten); exchange (noting
    block vacation and an observation report of what happened); handoff
    (sythetic memory refresh, from agent session to agent session, for context
    management). Three vital features, that, as it turns out, are vital for
    campaign success.

Each term owns a different SUBJECT: transit is the ECOSYSTEM (airlock,
ADR-0.33.0), exchange is ONE BLOCK's occupancy (this module, ADR-0.0.41),
handoff is ONE SESSION (``gzkit.handoff_api``, ADR-0.0.65). ``handoff`` is
critical only to the session system; on the token side ``exchange`` substitutes.

Why this module exists (GHI #763). These functions previously lived in
``gzkit.handoff_validation`` and wrote into ``.gzkit/handoffs/``, so the token
system named, stored, and discovered its artifacts as session handoffs. System
membership then had to be *inferred* from a shared field name, path, or
directory — and it was inferred wrongly twice in one session, once by the GHI
that preceded this one and once by a sweep that grouped four unrelated ledger
event types on the shared ``handoff_path`` key. Location now types membership:
this directory holds exchange records and nothing else.

What is deliberately still shared with the session system: the *document
format*. Both systems write Markdown with YAML frontmatter, so
:func:`gzkit.handoff_validation.parse_frontmatter` is imported rather than
duplicated. That is a shared FORMAT, not a shared system — and it is precisely
why no property of the artifact can discriminate the two. Properties of the ACT
(the citing ledger event type) and now of the LOCATION are what discriminate.

Frozen out of scope: the ledger payload key ``handoff_path``. 204 historical
events carry it and the ledger is append-only, so the field name is part of the
record (GHI #763 § Prescribed scope).
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from gzkit.handoff_validation import HandoffValidationError, parse_frontmatter

__all__ = [
    "ABANDON_CATEGORIES",
    "AbandonSpec",
    "InvalidAbandonSpec",
    "exchange_dir",
    "find_exchange_for_release",
    "is_exchange_register_entry",
    "parse_abandon_spec",
    "write_completion_exchange",
    "write_degenerate_exchange",
]


#: Canonical on-disk home for exchange records, relative to the project root.
#:
#: Under ``.gzkit/locks/`` because an exchange record is the audit pairing for a
#: lock surrender, and named ``exchange`` because that is what the record is.
#: ``.gitignore`` re-includes this one subtree: locks themselves are ephemeral
#: runtime state and stay ignored, while exchange records must reach git's index
#: or ``validate_lock_exchange_coupling`` fails them closed (GHI #759).
EXCHANGE_DIR_PARTS = (".gzkit", "locks", "exchange")

#: The only frontmatter ``mode`` an exchange writer emits.
#:
#: Read by :func:`is_exchange_register_entry` as an ALLOW-list. The predicate is
#: default-DENY by construction: a document shape nobody has explicitly admitted
#: is refused. The previous predicate was default-admit with a blocklist
#: (``not abandoned``, ``not CHECKPOINT``), both entries learned reactively after
#: a session-system document kind had already been accepted as token-surrender
#: evidence. GHI #756 states that cost in its own rule text — *"a token
#: surrendered on the evidence of a session that never departed."*
EXCHANGE_MODE = "CREATE"


def exchange_dir(project_root: Path) -> Path:
    """Return the exchange-record directory for ``project_root``."""
    return project_root.joinpath(*EXCHANGE_DIR_PARTS)


# ---------------------------------------------------------------------------
# Abandon-category enum
# ---------------------------------------------------------------------------
#
# Source of truth: ``.gzkit/rules/token-block-discipline.md`` § Sub-Invariant 1.
# The base category enum is CLOSED here in code; extending it requires an ADR
# per the rule's extension protocol. Mirror — not re-author — the enum.

ABANDON_CATEGORIES: tuple[str, ...] = (
    "network_loss",
    "external_blocker",
    "wrong_obpi_claimed",
    "tool_failure",
    # reaping is the OBPI-03 surface; OBPI-02 ships base + reaping placeholder
    # so reap-driven release in OBPI-03 lands cleanly.
    "reaping",
)


class InvalidAbandonSpec(ValueError):
    """Raised when --abandon argument cannot be parsed or category is unknown."""


class AbandonSpec(BaseModel):
    """Parsed `--abandon <category>:<reason>` specification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: str
    reason: str

    @field_validator("category")
    @classmethod
    def _validate_category(cls, v: str) -> str:
        if v not in ABANDON_CATEGORIES:
            allowed = " | ".join(ABANDON_CATEGORIES)
            raise ValueError(
                f"Unknown abandon category {v!r}; closed enum (see "
                f".gzkit/rules/token-block-discipline.md § Sub-Invariant 1): {allowed}"
            )
        return v


def parse_abandon_spec(raw: str) -> AbandonSpec:
    """Parse ``<category>:<reason>``; reject whitespace around category.

    Whitespace around the category is rejected so the audit surface stays
    canonical — ``" network_loss:reason"`` is the same operator typo class as
    misspelling the category itself.
    """
    if ":" not in raw:
        raise InvalidAbandonSpec("abandon spec must be '<category>:<reason>' (missing colon)")
    category, _, reason = raw.partition(":")
    if category != category.strip():
        raise InvalidAbandonSpec(
            f"abandon category must not have leading/trailing whitespace: {category!r}"
        )
    if not category:
        raise InvalidAbandonSpec("abandon category is empty")
    if not reason:
        raise InvalidAbandonSpec("abandon reason is empty")
    try:
        return AbandonSpec(category=category, reason=reason)
    except ValidationError as e:  # surface as InvalidAbandonSpec for the CLI
        raise InvalidAbandonSpec(str(e)) from e


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------


def _filesystem_safe_timestamp(iso_ts: str) -> str:
    """Render an ISO timestamp into a filesystem-safe filename token."""
    return iso_ts.replace(":", "").replace("-", "").replace(".", "")[:15] + "Z"


_PLACEHOLDER_WORD_RE = re.compile(r"\b(?:TBD|TODO|FIXME|PLACEHOLDER|XXX|CHANGEME)\b", re.IGNORECASE)


def _sanitize_exchange_text(text: str | None, *, limit: int = 600) -> str:
    """Collapse whitespace and neutralize placeholder/ellipsis tokens in embedded text.

    Auto-drafted completion exchange records embed operator-authored evidence
    (attestation text, implementation summary, key proof). An elision (``...``) or a
    placeholder word would otherwise trip ``validate_no_placeholders`` at ``gz check``
    time, so a mechanically-written record would fail its own validator. Newlines are
    collapsed so embedded text can never introduce a spurious ``## section`` or ``---``
    line into the rendered document.

    HTML comments are dropped, not carried. A brief that kept its scaffold prompt
    above the authored content (``<!-- One concrete usage example… -->``) would
    otherwise embed that prompt in a required section of the register entry, and
    nothing downstream would flag it: ``validate_no_placeholders`` and
    ``validate_sections_populated`` both *strip* comments before scanning, so the
    gate is blind to their presence by construction. Refusing to carry one inward
    fixes the class; editing the one brief would not.

    Truncation is marked and lands on a word boundary. A bare ``[:limit]`` cut
    severed tokens mid-word (``AGENTS.md`` → ``AGE``), which a reader cannot
    distinguish from prose that simply trails off — and on the attestation field it
    silently dropped operator verbatim words (``AGENTS.md`` § Attestation). The
    marker is ``…``, the same glyph elisions already fold to, so it cannot trip
    the placeholder scan. The returned text never exceeds ``limit``.
    """
    if not text:
        return ""
    collapsed = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    collapsed = " ".join(collapsed.split())
    collapsed = re.sub(r"\.{3,}", "…", collapsed)
    collapsed = _PLACEHOLDER_WORD_RE.sub("(noted)", collapsed)
    if len(collapsed) <= limit:
        return collapsed
    head = collapsed[: limit - 1]
    truncated = head.rsplit(" ", 1)[0] if " " in head else head
    return f"{truncated.rstrip()}…"


def write_degenerate_exchange(
    project_root: Path,
    *,
    obpi_id: str,
    adr_id: str | None = None,
    agent: str,
    spec: AbandonSpec,
    last_claim_timestamp: str | None,
    commit_sha: str,
    branch: str,
    decision_context: str | None = None,
) -> Path:
    """Write an abandoned-state exchange record under ``.gzkit/locks/exchange/``.

    Returns the on-disk path written. The record carries the four
    minimum-information fields per Sub-Invariant 2 (last lock-event timestamp,
    last commit SHA, decision context, branch state) plus abandon-specific
    frontmatter (``abandoned: true``, ``category``, ``reason``).
    """
    target_dir = exchange_dir(project_root)
    target_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    timestamp_token = _filesystem_safe_timestamp(now)
    filename = f"{timestamp_token}-{obpi_id}-abandoned.md"
    path = target_dir / filename

    frontmatter = {
        "mode": EXCHANGE_MODE,
        "adr_id": adr_id,
        "obpi_id": obpi_id,
        "branch": branch,
        "timestamp": now,
        "agent": agent,
        "abandoned": True,
        "category": spec.category,
        "reason": spec.reason,
        "last_lock_event_timestamp": last_claim_timestamp,
        "last_commit_sha": commit_sha,
    }

    decision = decision_context or (
        f"Lock for {obpi_id} abandoned by {agent} (category={spec.category}, reason={spec.reason})."
    )

    body = (
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False)
        + "---\n\n"
        + f"<!-- Degenerate exchange record for {obpi_id} — abandon path -->\n\n"
        + "## Current State Summary\n\n"
        + f"Lock surrender via `--abandon {spec.category}:{spec.reason}` "
        + f"by agent `{agent}`.\n\n"
        + "## Important Context\n\n"
        + "Degenerate exchange record written as the register-entry pairing for an "
        + "abandoned lock release (token-block discipline; see "
        + "`.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1).\n\n"
        + "## Decisions Made\n\n"
        + f"- {decision}\n\n"
        + "## Immediate Next Steps\n\n"
        + "1. Operator review of the abandonment reason.\n"
        + "2. If recovery is intended, re-claim the lock via `gz obpi lock claim`.\n\n"
        + "## Pending Work / Open Loops\n\n"
        + f"- OBPI {obpi_id} was abandoned mid-traversal; resume work requires "
        + "re-claim plus a fresh exchange record at completion.\n\n"
        + "## Verification Checklist\n\n"
        + f"- [ ] `git rev-parse HEAD` returns `{commit_sha}` (or operator "
        + "explains drift).\n"
        + f"- [ ] Branch matches `{branch}`.\n\n"
        + "## Evidence / Artifacts\n\n"
        + f"- `.gzkit/locks/obpi/{obpi_id}.lock.json` — lock file at abandon "
        + "(deleted on release).\n"
    )

    path.write_text(body, encoding="utf-8", newline="\n")
    return path


def write_completion_exchange(
    project_root: Path,
    *,
    obpi_id: str,
    agent: str,
    attestor: str,
    attestation_text: str,
    implementation_summary: str,
    key_proof: str,
    last_lock_event_timestamp: str | None,
    commit_sha: str,
    branch: str,
    brief_rel_path: str,
    observation: str | None = None,
    residual: str | None = None,
    open_loops: str | None = None,
    artifacts: str | None = None,
) -> Path:
    r"""Write a full exchange record as the register entry for OBPI completion.

    Unlike :func:`write_degenerate_exchange` (the abandon path), this is a
    non-abandoned record carrying all seven required sections, so
    :func:`find_exchange_for_release` accepts it as the completion-surrender register
    entry and ``gz validate --lock-exchange-coupling`` passes. The parent ADR id is
    derived from the OBPI semver (bare ``ADR-X.Y.Z``) when the id is semver-shaped,
    and recorded as absent otherwise — ``adr_id`` is optional (GHI #709).
    Auto-drafted from completion evidence and written mechanically at every
    ``gz obpi complete`` (token-block exit edge, GHI #619); it may be terse. Written
    with explicit ``\n`` newlines so the committed artifact is LF on every platform.

    **The observation report (GHI #764).** An exchange record is two things —
    the fact of block vacation *and* an observation report of what happened during
    possession (operator canon, 2026-08-06). Only the second half needed wiring:
    the writer had three content inlets for seven sections, so four sections emitted
    boilerplate that was byte-identical across all 33 records on disk. Those four
    were not low-value sections; they are the observation report's own subject
    matter, with no channel to reach the document.

    ``observation``, ``residual``, ``open_loops``, and ``artifacts`` are those
    channels. **All four are optional by design.** GHI #619 made surrender mechanical
    because locks were being stranded whenever nobody authored a record, so requiring
    them would re-create exactly that friction. Absent, each falls back to the prior
    boilerplate: the fallback stops being the normal path without ceasing to be a
    valid floor. ``gz obpi complete`` fills them from the brief's own
    ``### Value Narrative`` and ``## Tracked Defects``, which is where the completing
    agent already wrote the observation report — so the usual path needs no new
    operator input at all.
    """
    target_dir = exchange_dir(project_root)
    target_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    path = target_dir / f"{_filesystem_safe_timestamp(now)}-{obpi_id}-complete.md"

    # An OBPI always has a parent ADR, so derivation normally succeeds. When the
    # id is not semver-shaped the parent is genuinely unknown — record that as
    # absent rather than synthesizing `ADR-0.0.0`, an id naming no real artifact
    # (GHI #709).
    semver_match = re.match(r"OBPI-(\d+\.\d+\.\d+)", obpi_id)
    adr_id = f"ADR-{semver_match.group(1)}" if semver_match else None
    parent_phrase = f" under {adr_id}" if adr_id else ""
    next_step = (
        f"1. Continue the parent {adr_id} checklist, or open the next OBPI.\n\n"
        if adr_id
        else "1. Open the next OBPI, or continue the parent ADR checklist.\n\n"
    )

    frontmatter = {
        "mode": EXCHANGE_MODE,
        "adr_id": adr_id,
        "obpi_id": obpi_id,
        "branch": branch,
        "timestamp": now,
        "agent": agent,
        "last_lock_event_timestamp": last_lock_event_timestamp,
        "last_commit_sha": commit_sha,
    }

    decision = _sanitize_exchange_text(attestation_text) or "Attested complete."
    summary = _sanitize_exchange_text(implementation_summary) or "See brief Implementation Summary."
    proof = _sanitize_exchange_text(key_proof) or "See brief Key Proof and the ledger receipt."

    # The mechanical provenance note is a CODA, not the section. It was the whole of
    # `## Important Context` in all 33 prior records — byte-identical, and displacing
    # the observation report that section exists to carry.
    provenance = (
        "Written mechanically at `gz obpi complete` as the token-block exit-edge register "
        "entry (token surrender at the section's end; see "
        "`.gzkit/rules/token-block-discipline.md`)."
    )
    observed = _sanitize_exchange_text(observation)
    context_block = f"{observed}\n\n{provenance}\n\n" if observed else f"{provenance}\n\n"

    residual_text = _sanitize_exchange_text(residual)
    next_block = f"1. {residual_text}\n\n" if residual_text else next_step

    loops = _sanitize_exchange_text(open_loops)
    loops_block = f"- {loops}\n\n" if loops else "- None recorded at surrender; see the brief.\n\n"

    extra_artifacts = _sanitize_exchange_text(artifacts)
    artifacts_block = f"- {extra_artifacts}\n" if extra_artifacts else ""

    body = (
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False)
        + "---\n\n"
        + f"<!-- Completion exchange record for {obpi_id} — mechanical register entry "
        + "(GHI #619) -->\n\n"
        + "## Current State Summary\n\n"
        + f"OBPI {obpi_id} completed and attested by `{attestor}`{parent_phrase}. The work "
        + "lock (if held) was surrendered mechanically at completion; the "
        + "`obpi_lock_released` ledger event is the surrender audit.\n\n"
        # The implementation summary is RETROSPECTIVE and belongs here. It was filed
        # under `## Pending Work / Open Loops` — a prospective section — because the
        # writer had retrospective content and a prospective schema, so it placed the
        # content where it fit rather than where it belonged (GHI #764).
        + f"Work performed: {summary}\n\n"
        + "## Important Context\n\n"
        + context_block
        + "## Decisions Made\n\n"
        # `[operator-ruled]` is unconditional here: Gate 5 is universal (ADR-0.0.36), so
        # a COMPLETION record's decision is always a human attestation. Written bare it
        # parsed UNATTRIBUTED, and an unattributed entry does not carry forward — the
        # successor's Settled Rulings promoted zero of them. `validate_decision_markers`
        # cannot catch this shape: it is asymmetric by design, firing only on a line that
        # CLAIMS attribution and lacks a list marker. This is the mirror (marker present,
        # attribution absent), so it passed clean — GHI #696 defect 4 reappearing through
        # the mechanical producer. The abandon-path writer above stays deliberately
        # unattributed: its entry is a mechanical lock-surrender record, not a ruling.
        + f"- [operator-ruled] {decision}\n\n"
        + "## Immediate Next Steps\n\n"
        + next_block
        + "## Pending Work / Open Loops\n\n"
        + loops_block
        + "## Verification Checklist\n\n"
        + f"- [ ] `git rev-parse HEAD` resolves to `{commit_sha}` (or operator explains drift).\n"
        + f"- [ ] Branch matches `{branch}`.\n"
        + f"- [ ] Key proof: {proof}\n\n"
        + "## Evidence / Artifacts\n\n"
        + f"- `{brief_rel_path}` — the completed OBPI brief.\n"
        + "- `.gzkit/ledger.jsonl` — completion receipt and lock-release event.\n"
        + artifacts_block
    )

    path.write_text(body, encoding="utf-8", newline="\n")
    return path


# ---------------------------------------------------------------------------
# Reader
# ---------------------------------------------------------------------------


def is_exchange_register_entry(frontmatter: dict) -> bool:
    """Return True when ``frontmatter`` is a completion-pairing exchange record.

    **Default-deny.** A document is admitted only when it carries a shape an
    exchange writer actually emits; everything else is refused without needing to
    be enumerated. That inverts the predicate this replaces, which admitted by
    default and subtracted known-bad shapes one reactive commit at a time —
    ``abandoned`` first, then ``CHECKPOINT`` under GHI #756. Each new session-system
    document kind was accepted as token-surrender evidence until somebody
    remembered to exclude it, and the exclusions could only ever be written after
    the harm. Location now keeps session documents out of the directory entirely
    (GHI #763); this predicate is the second, independent fence.

    Two conditions, both from the writers above:

    - ``mode`` is :data:`EXCHANGE_MODE`. Refuses ``CHECKPOINT`` (a mid-flight
      bookmark records a pause, never a surrender — token-block discipline
      § Sub-Invariant 5), ``RESUME``, and any mode invented later.
    - ``abandoned`` is not true. An abandoned record satisfies the pairing only
      when release is invoked through the ``--abandon`` code path, which cites the
      record it just wrote rather than searching for one.
    """
    if str(frontmatter.get("mode", "")).upper() != EXCHANGE_MODE:
        return False
    return frontmatter.get("abandoned") is not True


def find_exchange_for_release(
    project_root: Path,
    *,
    obpi_id: str,
    after_timestamp: str | None = None,
) -> Path | None:
    """Search `.gzkit/locks/exchange/` for a matching exchange record.

    Matches when the record's frontmatter declares the given `obpi_id`, its
    timestamp is later than ``after_timestamp`` (the matching
    ``obpi_lock_claimed`` event time), and :func:`is_exchange_register_entry`
    admits its shape. Returns the newest match, or ``None``.

    Deliberately NOT a caller of ``gzkit.handoff_selection.selection_rank``. That
    rule answers *"which document describes the current state?"* and ranks an
    authored handoff above a mechanical bookmark; this answers *"may this document
    discharge a surrender?"*, which is a different question over a different
    corpus. Sharing a rule across two questions that merely look alike is how the
    wrong filter gets applied to the wrong arm.
    """
    search_dir = exchange_dir(project_root)
    if not search_dir.is_dir():
        return None

    candidates: list[tuple[str, Path]] = []
    for path in search_dir.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
        except (OSError, yaml.YAMLError, HandoffValidationError):
            continue
        if not isinstance(fm, dict):
            continue
        if fm.get("obpi_id") != obpi_id:
            continue
        ts = str(fm.get("timestamp", ""))
        if after_timestamp and ts <= after_timestamp:
            continue
        if not is_exchange_register_entry(fm):
            continue
        candidates.append((ts, path))

    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][1]
