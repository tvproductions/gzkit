"""gz content retire command handler — append-only corpus retirement (GHI #635).

The corpus store has exactly one mutation, append, and no delete. That made a
superseded operator directive permanent: two invariant-tier entries carrying the
same doctrine in different wording both bound the floor forever, and any
rendition that deduplicated them was rejected. The only escape was hand-deleting
a line from the append-only store, which is not a governed operation.

``gz content retire <surface> --entry <id> [--reason <text>]`` is the governed
exit. It appends a *retraction row* whose ``retires`` field names the superseded
id. Nothing is deleted — the retired row stays on disk with its provenance — but
``tier_policy.invariant_entries`` skips it, so the invariant floor shrinks.

Retirement therefore never invalidates a committed rendition: the floor only
loses requirements, never gains them. No recomposition is implied, and this
command never touches a rendered surface.

Retirement is corpus attestation (OBPI-0.35.0-02, GHI #635): a tier=invariant
entry is the 0-Kelvin floor every rendition must carry verbatim, so retiring
one requires a named ``--attestor``. Routine compressible-tier retirement
stays frictionless — no ``--attestor`` is required there. ``--reason`` is
required on EVERY tier: it becomes the retraction row's text and the
``corpus_entry_retired`` event's reason, and both surfaces reject an empty one
(operator ruling 2026-08-25). Whitespace-only values for either flag are
refused as not-attestation.
"""

from __future__ import annotations

import sys
import unicodedata
from datetime import UTC, datetime

from gzkit.commands.common import get_project_root
from gzkit.commands.content._drift import warn_on_rendition_drift
from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models import CorpusEntry
from gzkit.content.models.corpus import effective_corpus
from gzkit.ledger import Ledger
from gzkit.ledger_events import corpus_entry_appended_event, corpus_entry_retired_event

_ID_SAMPLE = 3


def _is_named(value: str) -> bool:
    """Return True when *value* is plausibly a human name.

    "At least one visible character" was the first fix here and it was too weak:
    an independent review retired invariant-tier canon with an attestor of ``.``,
    ``7``, a lone combining mark, and a lone surrogate, each recorded as the human
    who authorized the change (2026-08-25). The audit record this gate protects
    asks WHO, so punctuation and digits do not answer it.

    The bar is at least one Unicode LETTER after NFKC normalization, with
    surrogates, unassigned code points, controls and formats excluded. This is a
    plausibility floor, not identity verification -- ``gz`` has no operator
    registry to check a name against. It rejects the values that are certainly not
    names; it cannot confirm that a name is the person's.
    """
    try:
        normalized = unicodedata.normalize("NFKC", value)
    except (TypeError, ValueError):
        return False
    for ch in normalized:
        category = unicodedata.category(ch)
        if category in {"Cs", "Cn", "Cc", "Cf"}:
            # Surrogate, unassigned, control, format -- never name content, and a
            # lone surrogate cannot even round-trip through the ledger's UTF-8.
            continue
        if category.startswith("L"):
            return True
    return False


def _floor_direction_prose(added: set[str], removed: set[str]) -> str:
    """Describe which way the invariant floor moved, for the success message."""
    if added and removed:
        return (
            f"The invariant floor CHANGED: {len(added)} entr"
            f"{'y' if len(added) == 1 else 'ies'} revived "
            f"({', '.join(sorted(added))}) and {len(removed)} retired. A committed "
            "rendition may no longer SATISFY it — recompose and re-attest."
        )
    if added:
        return (
            f"The invariant floor GREW — retiring this row revived "
            f"{', '.join(sorted(added))}. A committed rendition that satisfied the "
            "old floor may FAIL the new one; recompose and re-attest."
        )
    if removed:
        return "The invariant floor shrank, so every committed rendition still SATISFIES it."
    return "The invariant floor is unchanged."


def _floor_liveness_delta(corpus, retraction: CorpusEntry) -> tuple[set[str], set[str]]:
    """Return ``(added, removed)`` invariant ids this retirement would move.

    Computed as a before/after delta over the fold, never by walking tombstone
    edges. An edge-walk has to pick a hop count and every finite choice is wrong:
    a one-hop lookup was the first fix here and an independent review found the
    two-hop chain it misses — ``invariant -> tombstone -> tombstone``, where
    retiring the SECOND tombstone drops the invariant out of the effective corpus
    with no attestor required. Two hops would then miss three.

    The two directions are kept SEPARATE rather than symmetric-differenced,
    because they mean opposite things to a consumer and the command was reporting
    one while doing the other: retiring a tombstone REVIVES its target, so the
    floor GROWS, while the success message claimed it shrank and suppressed the
    floor-coherence warning. A rendition that satisfied the old floor may fail the
    new one — the operator has to be told which way it went (2026-08-25).
    """

    def _invariant_ids(c) -> set[str]:
        return {e.id for e in effective_corpus(c).entries if e.tier == "invariant"}

    try:
        before = _invariant_ids(corpus)
        after = _invariant_ids(corpus.append(retraction))
    except ValueError:
        # `effective_corpus` raises on a corpus whose tombstones do not resolve.
        # An unreadable fold is not evidence that the floor is unaffected, so fail
        # toward requiring attestation rather than waving the write through.
        return ({"<unresolvable-fold>"}, set())
    return (after - before, before - after)


def _live_id_hint(corpus, surface: str) -> str:
    """Name a few live entry ids the caller could have meant.

    No `gz` verb lists corpus entries for a surface -- `gz content list` enumerates
    registered content MODEL TYPES and takes no positional argument. The prose used to
    send the operator to `gz content list <surface>`, which argparse rejects outright.
    The command already holds the loaded corpus, so it answers the question itself
    rather than delegating it to a verb that does not exist (AGENTS.md Invariant 6g).
    """
    retired = corpus.retired_ids()
    live = [e.id for e in corpus.entries if e.id not in retired and e.retires is None]
    if not live:
        return f"  The corpus for {surface!r} holds no live entries."
    shown = ", ".join(repr(i) for i in live[:_ID_SAMPLE])
    more = f" (+{len(live) - _ID_SAMPLE} more)" if len(live) > _ID_SAMPLE else ""
    return f"  Live entry ids include: {shown}{more}."


def content_retire_cmd(
    *, surface: str, entry_id: str, reason: str, origin: str, attestor: str = ""
) -> None:
    """Handle ``gz content retire <surface> --entry <id> [--reason <text>] [--attestor <name>]``.

    Exit 0 on a successful retirement; 1 on unknown entry, an entry already
    retired, a whitespace-only ``--attestor``/``--reason``, or an invariant-tier
    entry retired without BOTH a named ``--attestor`` and a ``--reason``; 2 on
    IO error writing the
    corpus store.
    """
    root = get_project_root()
    corpus = load_corpus(root, surface)

    target = corpus.entry(entry_id)
    if target is None:
        print(
            f"Error: no corpus entry {entry_id!r} in surface {surface!r}. "
            "Retirement targets an existing entry (append-only corpus store, "
            "GHI #635); nothing written.\n"
            f"{_live_id_hint(corpus, surface)}\n"
            f"  Retry with `gz content retire {surface} --entry <id> "
            '--reason "<why>" --attestor "<your name>"`.',
            file=sys.stderr,
        )
        sys.exit(1)

    if entry_id in corpus.retired_ids():
        print(
            f"Error: corpus entry {entry_id!r} is already retired. "
            "Retirement is idempotent by refusal, not by silent re-append "
            "(GHI #635); nothing written.\n"
            f"{_live_id_hint(corpus, surface)}\n"
            f"  Retry with `gz content retire {surface} --entry <id> "
            '--reason "<why>" --attestor "<your name>"`.',
            file=sys.stderr,
        )
        sys.exit(1)

    # Whitespace is not attestation: a caller who passes "   " has supplied
    # something that LOOKS like a value but carries no content. `--reason` is
    # argparse-required, so an omitted one never reaches here; `--attestor` is
    # optional and arrives as "" when omitted, which the tier gate below handles.
    if attestor and not _is_named(attestor):
        print(
            "Error: --attestor is whitespace-only. Whitespace is not "
            "attestation (AGENTS.md § Operator Doctrine; the ATTESTATION "
            "GRANULARITY FOR THE CONTENT SURFACE ruling); nothing written.\n"
            f"  Retry with `gz content retire {surface} --entry {entry_id} "
            '--reason "<why>" --attestor "<your name>"`.',
            file=sys.stderr,
        )
        sys.exit(1)

    if reason and not _is_named(reason):
        print(
            "Error: --reason is whitespace-only. Whitespace is not "
            "attestation (AGENTS.md § Operator Doctrine; the ATTESTATION "
            "GRANULARITY FOR THE CONTENT SURFACE ruling); nothing written.\n"
            f"  Retry with `gz content retire {surface} --entry {entry_id} "
            '--reason "<why>" --attestor "<your name>"`.',
            file=sys.stderr,
        )
        sys.exit(1)

    # Requirement 2 gates on BOTH: "an empty or whitespace-only --attestor OR
    # --reason MUST exit non-zero". --reason defaults to "" at the parser, so the
    # whitespace guard above never sees an omitted one -- gating on the attestor half
    # alone lets a 0-Kelvin-floor entry be un-bound with no reason recorded.
    # `--reason` is argparse-required, but this handler is importable and IS called
    # directly (the adversary retired a row through it with reason="" and wrote an
    # event `gz validate --ledger` then rejected). Enforce the contract HERE, where
    # the invariant actually lives, not only at the parser that usually fronts it.
    if not _is_named(reason):
        print(
            "Error: --reason is empty or carries no visible character. It becomes the "
            "retraction row's text and the corpus_entry_retired event's reason, and "
            "both reject an empty one (.claude/rules/guardrail-feedback-prose.md); "
            "nothing written.\n"
            f"  Retry with `gz content retire {surface} --entry {entry_id} "
            '--reason "<why>" --attestor "<your name>"`.',
            file=sys.stderr,
        )
        sys.exit(1)

    timestamp = datetime.now(UTC).isoformat()
    retraction = CorpusEntry(
        id=f"corpus-retraction-{entry_id}-{timestamp}",
        surface=surface,
        # Inherit the retired row's section so the retraction stays addressable
        # against the same Pillar its target was validated against.
        section=target.section,
        # Compressible: the retraction is bookkeeping, never new canon to render.
        tier="compressible",
        classification="Mechanical",
        text=reason,
        origin=origin,
        ts=timestamp,
        retires=entry_id,
    )

    floor_added, floor_removed = _floor_liveness_delta(corpus, retraction)
    at_risk = floor_added | floor_removed
    if at_risk and not _is_named(attestor):
        print(
            f"Error: retiring {entry_id!r} moves the liveness of invariant-tier "
            f"{'entries' if len(at_risk) > 1 else 'entry'} "
            f"{', '.join(sorted(at_risk))} — the 0-Kelvin floor every rendition must carry "
            "verbatim — so it requires a named --attestor (AGENTS.md § Operator "
            "Doctrine; the ATTESTATION GRANULARITY FOR THE CONTENT SURFACE "
            "ruling, which makes removing an entry attested; operator ruling "
            "2026-08-25 scopes the blocking arm to floor-tier removal); "
            "nothing written.\n"
            f"  Retry with `gz content retire {surface} --entry {entry_id} "
            '--reason "<why>" --attestor "<your name>"`.',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        append_entry(root, surface, retraction)
    except OSError as exc:
        print(
            f"Error writing corpus store for {surface!r}: {exc}. "
            "The corpus store must be writable for an append-only mutation "
            "(GHI #635); nothing written.\n"
            "  Check the file/directory permissions and disk space for "
            f"`.gzkit/corpus/{surface}.jsonl`, then retry.",
            file=sys.stderr,
        )
        sys.exit(2)

    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    # The tombstone row is itself an append (Algebra 4) -- witness its own birth
    # BEFORE the retirement that depends on it, so a ledger replay never sees a
    # retirement of a row it has not yet observed (OBPI-0.35.0-02).
    #
    # The corpus row is ALREADY on disk by this point and both stores are
    # append-only, so a failure here cannot be rolled back -- the retirement has
    # taken effect with an incomplete Layer-2 witness. That state is not
    # preventable without a transaction the stores do not offer, but it MUST NOT
    # be silent: an operator who is told only "OSError" cannot know that canon
    # moved. Report exactly which witnesses landed and name the recovery.
    for label, event in (
        (
            "corpus_entry_appended",
            corpus_entry_appended_event(
                surface=surface,
                section=retraction.section,
                entry_id=retraction.id,
                tier=retraction.tier,
            ),
        ),
        (
            "corpus_entry_retired",
            corpus_entry_retired_event(
                surface=surface,
                retired_entry_id=entry_id,
                retraction_entry_id=retraction.id,
                reason=reason,
                tier=target.tier,
                attestor=attestor,
            ),
        ),
    ):
        try:
            ledger.append(event)
        except OSError as exc:
            print(
                f"Error writing ledger event {label!r} for {surface!r}: {exc}. "
                f"THE RETIREMENT ALREADY HAPPENED — the tombstone row "
                f"{retraction.id!r} is on disk and {entry_id!r} is retired, but "
                "the ledger witness is incomplete (append-only stores cannot roll "
                "back, GHI #635).\n"
                "  Fix the ledger write, then verify with "
                "`gz validate --ledger`.",
                file=sys.stderr,
            )
            sys.exit(2)

    print(
        f"Retired corpus entry {entry_id} in {surface} "
        f"(retraction {retraction.id}). {_floor_direction_prose(floor_added, floor_removed)} "
        "This row moved the corpus fingerprint, so every committed rendition's "
        "derivation proof no longer holds."
    )
    # `floor_risk` is TRUE when the floor GREW. "Retirement only ever shrinks the
    # floor" was the standing assumption and it is false: retiring a tombstone
    # REVIVES its target, adding a requirement back. A revived invariant is exactly
    # the case a committed rendition can now fail, which is what GHI #863's warning
    # exists to raise (2026-08-25).
    warn_on_rendition_drift(root, surface, mutation="retirement", floor_risk=bool(floor_added))
