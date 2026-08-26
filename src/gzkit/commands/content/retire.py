"""gz content retire command handler — append-only corpus retirement (GHI #635).

The corpus store has exactly one mutation, append, and no delete. That made a
superseded operator directive permanent: two invariant-tier entries carrying the
same doctrine in different wording both bound the floor forever, and any
rendition that deduplicated them was rejected. The only escape was hand-deleting
a line from the append-only store, which is not a governed operation.

``gz content retire <surface> --entry <id> [--reason <text>]`` is the governed
exit. It appends a *retraction row* whose ``retires`` field names the superseded
id, and emits BOTH a ``corpus_entry_appended`` event for that tombstone row and
a ``corpus_entry_retired`` event carrying the retired entry's tier and
attestor. Nothing is deleted — the retired row stays on disk with its
provenance — but ``tier_policy.invariant_entries`` skips it, so that row stops
binding the invariant floor.

Which way the floor moves is a before/after DELTA over invariant-tier liveness,
never a property of what kind of row was named. Four outcomes: unchanged (no
invariant entry's liveness moved — the usual case for a routine compressible
retirement), shrank (an invariant entry stopped binding), GREW (retiring a
tombstone revived the entry it superseded, AND that revived entry is
invariant-tier — Algebra 6; reviving a compressible entry moves the floor not
at all), or CHANGED (both at once). A rendition that satisfied the old floor
still SATISFIES a shrunk one but may FAIL a GREW or CHANGED one. Either way the
retraction row moves the
corpus fingerprint, so a committed rendition's derivation proof no longer
holds and ``gz validate --rendition-freshness`` requires a recompose and
re-attest before the next push (GHI #863). This command never touches a
rendered surface itself, and it fails closed — nothing written — on an
unknown or already-retired id.

Retirement is corpus attestation (OBPI-0.35.0-02, GHI #635): a retirement that
MOVES invariant-tier liveness — including retiring a *compressible* tombstone
whose target is invariant — requires a named ``--attestor``, because the
0-Kelvin floor every rendition must carry verbatim is what moved. Routine
retirement that leaves invariant-tier liveness untouched stays frictionless —
no ``--attestor`` is required there. ``--reason`` is required on EVERY tier:
it becomes the retraction row's text and the ``corpus_entry_retired`` event's
reason, and both surfaces reject an empty one (operator ruling 2026-08-25).
Whitespace-only values for either flag are refused as not-attestation.
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

# Unicode's Default_Ignorable_Code_Point property (DerivedCoreProperties.txt) names
# code points a conformant renderer draws at ZERO advance width regardless of
# General_Category. Almost every one is already Cs/Cn/Cc/Cf and excluded below; these
# four are the entire exception -- Unicode classifies them General_Category=Lo
# (letter) even though they are placeholders for an EMPTY Hangul syllable-composition
# slot, never a script character a human is named with. A tier-1 cross-vendor
# adversary found the letter-category bar admitted them, one of which (U+3164) still
# NFKC-normalizes to another member of this same set (U+1160).
#
# Only two of the four are ever tested at the `_is_named` call site below: NFKC
# normalization runs BEFORE the membership check, and U+3164 -> U+1160 and
# U+FFA0 -> U+1160 under NFKC (measured against UCD 15.1.0), so `ch` is never
# U+3164 or U+FFA0 by the time this set is consulted there. All four stay --
# as a complete, readable statement of the class, and as defense-in-depth for a
# future caller that tests a pre-normalization string.
#
# This is the complete Lo-category subset of Default_Ignorable_Code_Point for UCD
# 15.1.0 -- the Unicode version bundled with CPython's `unicodedata` at the time
# this set was derived -- not the three code points the adversary happened to
# probe. stdlib `unicodedata` has no accessor for Default_Ignorable_Code_Point
# (the `regex` module's `\p{Default_Ignorable_Code_Point}` would need an
# ADR-level STDLIB-FIRST departure), so this literal set IS the compliant shape;
# `ucd_currency_warning` below is the drift witness for the one thing a literal
# set cannot self-check -- that the UCD it was derived against is still the UCD
# in use. It WARNS on the retire path and asserts hard only in the test suite
# (operator ruling 2026-08-25): a maintainer in CI can re-derive the set, an
# operator mid-retirement cannot.
_DEFAULT_IGNORABLE_LETTERS_UCD_VERSION = "15.1.0"

_DEFAULT_IGNORABLE_LETTERS = frozenset(
    {
        "ᅟ",  # HANGUL CHOSEONG FILLER
        "ᅠ",  # HANGUL JUNGSEONG FILLER
        "ㅤ",  # HANGUL FILLER
        "ﾠ",  # HALFWIDTH HANGUL FILLER
    }
)


def ucd_currency_warning(version: str | None = None) -> str:
    """Return the UCD-drift warning text, or ``""`` when the bundled UCD is current.

    ``_DEFAULT_IGNORABLE_LETTERS`` is a hand-transcribed subset of
    DerivedCoreProperties.txt: stdlib exposes no accessor for
    ``Default_Ignorable_Code_Point``, so a literal set is the compliant shape
    under STDLIB-FIRST, but a literal set cannot self-check its own currency.
    A future CPython bundling a newer UCD would silently change which code
    points this set excludes, and ``_is_named`` would resume accepting an
    invisible glyph as a named attestor with nothing to signal it.

    This WARNS; it does not raise. An earlier revision asserted here and the
    module-level call site therefore aborted ``gz content retire`` at import on
    any runtime whose UCD differed -- and ``pyproject.toml`` declares
    ``requires-python >=3.13`` with NO upper bound, so a declared-SUPPORTED
    CPython (3.14 bundles UCD 16.0.0) crashed the command outright. A tier-1
    cross-vendor adversary found it 2026-08-25; the operator ruled warn-not-raise
    the same day. The reasoning is where the witness has to land: a maintainer in
    CI can re-derive the set, while an operator mid-retirement cannot, so the
    HARD failure belongs in the test suite (``unidata_version`` is asserted there)
    and the runtime gets a line on stderr it can act on or ignore.
    """
    actual = unicodedata.unidata_version if version is None else version
    if actual == _DEFAULT_IGNORABLE_LETTERS_UCD_VERSION:
        return ""
    return (
        f"warning: unicodedata.unidata_version is {actual!r}, but "
        "_DEFAULT_IGNORABLE_LETTERS was derived against UCD "
        f"{_DEFAULT_IGNORABLE_LETTERS_UCD_VERSION!r}. An invisible attestor "
        "admitted by the newer UCD would not be refused. Re-derive "
        "_DEFAULT_IGNORABLE_LETTERS from DerivedCoreProperties.txt for the new "
        "UCD (the full General_Category=Lo subset of "
        "Default_Ignorable_Code_Point), then update "
        "_DEFAULT_IGNORABLE_LETTERS_UCD_VERSION to match."
    )


def _is_named(value: str) -> bool:
    """Return True when *value* is plausibly a human name.

    "At least one visible character" was the first fix here and it was too weak:
    an independent review retired invariant-tier canon with an attestor of ``.``,
    ``7``, a lone combining mark, and a lone surrogate, each recorded as the human
    who authorized the change (2026-08-25). The audit record this gate protects
    asks WHO, so punctuation and digits do not answer it.

    The bar is at least one Unicode LETTER after NFKC normalization, with
    surrogates, unassigned code points, controls and formats excluded. That bar was
    still too weak: General_Category alone cannot tell letter from glyph -- a code
    point can be category Lo and STILL be `Default_Ignorable_Code_Point`, meaning a
    renderer draws it with no visible mark at all (`_DEFAULT_IGNORABLE_LETTERS`).
    This is a plausibility floor, not identity verification -- ``gz`` has no
    operator registry to check a name against. It rejects the values that are
    certainly not names; it cannot confirm that a name is the person's.
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
        if category.startswith("L") and ch not in _DEFAULT_IGNORABLE_LETTERS:
            return True
    return False


def _at_risk_rationale(added: set[str], removed: set[str]) -> str:
    """Say which WAY the refused retirement would have moved the floor.

    The refusal used to cite the 2026-08-25 ruling as scoping the blocking arm to
    floor-tier REMOVAL, on every path — including the tombstone-revival path, where
    the entry is revived and the floor GROWS. A round-8 adversary caught the
    diagnostic mischaracterizing the exact class the delta gate was added to catch.
    """
    if added and removed:
        return "this retirement would both revive and un-bind floor canon"
    if added:
        return "this retirement would REVIVE floor canon and GROW the floor"
    return "un-binding floor canon is a canon change"


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
    """Handle ``gz content retire <surface> --entry <id> --reason <text> [--attestor <name>]``.

    ``--reason`` is required on EVERY tier, not optional: it becomes the
    retraction row's text and the ``corpus_entry_retired`` event's reason, and
    both surfaces reject an empty one.

    Exit 0 on a successful retirement; 1 on an unknown entry, an entry already
    retired, a whitespace-only or not-a-name ``--attestor``/``--reason``, or a
    retirement that MOVES invariant-tier liveness without a named ``--attestor``
    — the gate reads the before/after liveness delta, never the tier of the row
    named; 2 on IO error writing the corpus store.
    """
    drift = ucd_currency_warning()
    if drift:
        print(drift, file=sys.stderr)

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
        # Two distinct causes, two distinct diagnoses. Reporting every rejected value
        # as "whitespace-only" told an operator who typed `--attestor 7` the wrong
        # cause AND the wrong recovery (a tier-1 adversary observed exactly that,
        # 2026-08-25). The amended REQ-01 names digits, punctuation, combining marks
        # and invisible letters as no-WHO classes distinct from whitespace.
        cause = (
            "is whitespace-only"
            if not attestor.strip()
            else "names no human — it carries no visible letter"
        )
        print(
            f"Error: --attestor {cause}. The audit record asks WHO authorized this "
            "retirement (AGENTS.md § Operator Doctrine; the ATTESTATION GRANULARITY "
            "FOR THE CONTENT SURFACE ruling); nothing written.\n"
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
    if not reason.strip():
        print(
            "Error: --reason is empty or whitespace-only. It becomes the "
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
            f"verbatim — {_at_risk_rationale(floor_added, floor_removed)}, so it requires a "
            "named --attestor (AGENTS.md § Operator Doctrine; the ATTESTATION "
            "GRANULARITY FOR THE CONTENT SURFACE ruling); nothing written.\n"
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
                floor_added=floor_added,
                floor_removed=floor_removed,
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
