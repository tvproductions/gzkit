#!/usr/bin/env python
"""Measure declared-but-never-fired ledger vocabulary, and report paired-event ratios.

The sibling chore `control-surface-validator-reachability` asks whether a
*validator* runs. This one asks the same question of the *ledger*: an event type
declared in ``src/gzkit/schemas/ledger.json`` that nothing ever emits is
vocabulary without a producer — it reads as a modelled fact and records nothing.

Two dimensions, deliberately unequal in force:

**Never-fired (enforced).** A declared type that has never appeared in
``.gzkit/ledger.jsonl`` is held to a shrink-only baseline. Growth is not
forbidden outright — declaring a type before wiring its producer is legitimate —
but it must be DISCLOSED by an explicit baseline entry, never absorbed silently.
Same posture as ``data/uncalled_gate_grandfather.json``: an entry records an
absence, it does not justify one.

**Paired-event ratios (reported, never judged).** For event types that come in
enter/exit pairs, the ratio of one to the other is reported and nothing else.
This chore does not decide what a lopsided ratio means, and that restraint is
load-bearing: the 2026-08-15 audit read ``obpi_parked``/``obpi_unparked`` as an
operator "abandonment channel" and named a ``gz obpi park`` verb that does not
exist. The counts were right; the story was invented. Parking is in fact emitted
by ``foundation/sunset_migrate.py`` when an ADR is demoted to pool, and that
module says in its own words that parking "is reversible on re-promotion and is
not a negation of completed work." A ratio is evidence for an operator ruling,
not a verdict this chore is entitled to reach.

Exit codes: 0 clean, 1 user/config error, 2 system/IO error, 3 policy breach
(an undisclosed never-fired type appeared).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

#: Enter/exit event pairs. Membership is a claim about SEMANTICS — that the
#: first event opens a state the second closes — so a pair is added only when
#: both halves name the same subject. Ratios are reported for these and for
#: nothing else; an unpaired event has no counterpart to be missing.
_PAIRS: tuple[tuple[str, str], ...] = (
    ("obpi_lock_claimed", "obpi_lock_released"),
    ("obpi_parked", "obpi_unparked"),
    ("airlock_in", "airlock_out"),
    ("mx_session_opened", "mx_session_closed"),
)

_SCHEMA_REL = Path("src") / "gzkit" / "schemas" / "ledger.json"
_LEDGER_REL = Path(".gzkit") / "ledger.jsonl"
_BASELINE_REL = Path("data") / "ledger_vocabulary_grandfather.json"


def declared_events(root: Path) -> set[str]:
    """Event types the ledger schema declares."""
    payload = json.loads((root / _SCHEMA_REL).read_text(encoding="utf-8"))
    events = payload.get("events")
    return set(events) if isinstance(events, dict) else set()


def fired_events(root: Path) -> Counter[str]:
    """Event types the ledger actually contains, with counts.

    A malformed line is skipped rather than fatal: the ledger is append-only and
    a partial final write must not make the whole audit unrunnable.
    """
    counts: Counter[str] = Counter()
    with (root / _LEDGER_REL).open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            event = record.get("event")
            if isinstance(event, str):
                counts[event] += 1
    return counts


def never_fired(root: Path) -> list[str]:
    """Return declared event types with zero occurrences in the ledger."""
    return sorted(declared_events(root) - set(fired_events(root)))


def _baseline_types(payload: dict[str, object]) -> set[str]:
    raw = payload.get("never_fired")
    return {str(x) for x in raw} if isinstance(raw, list) else set()


def _load_baseline(root: Path) -> dict[str, object]:
    path = root / _BASELINE_REL
    if not path.is_file():
        msg = (
            f"Baseline missing at {_BASELINE_REL.as_posix()}.\n"
            "  Why: never-fired vocabulary is shrink-only; with no baseline on "
            "disk a newly declared type that nothing emits is absorbed silently.\n"
            "  Next step: run this script with --report --write, then commit the baseline."
        )
        raise SystemExit(msg)
    return json.loads(path.read_text(encoding="utf-8"))


def enforce(root: Path) -> int:
    """Fail closed when an undisclosed never-fired type appears."""
    current = set(never_fired(root))
    baseline = _baseline_types(_load_baseline(root))

    drained = sorted(baseline - current)
    added = sorted(current - baseline)

    if drained:
        print(f"drained {len(drained)} type(s) — a producer now emits: {', '.join(drained)}")
    if not added:
        print(f"never-fired: {len(current)} (baseline {len(baseline)}) — disclosure holds")
        return 0

    print(
        f"POLICY BREACH: {len(added)} declared event type(s) fire nowhere and are "
        f"not disclosed: {', '.join(added)}\n"
        "  Why: a declared type with no producer is vocabulary that records "
        "nothing while reading as a modelled fact. Growth is allowed but must be "
        "visible — an undisclosed one is indistinguishable from a wired producer.\n"
        "  Next step: wire the producer, or disclose it by adding the type to "
        f"{_BASELINE_REL.as_posix()} with a reason. Set 'never_fired' to the CURRENT "
        "set and 'baseline_count' in data/waiver_ratchet_registry.json to its length "
        "-- run this script with --report --write to compute both. Drained types come "
        "OUT in the same edit, which is usually why the count still falls. RAISE the "
        "baseline only when the honest current set is genuinely larger, and say so in "
        "the commit: ADR-0.0.73 BI #8 makes this a shrink-ratchet, 'a committed "
        "baseline the list can only decrease against', and a raise to clear this gate "
        "is the laundering it exists to refuse (GHI #611 review, 2026-09-06).",
        file=sys.stderr,
    )
    return 3


def report(root: Path, *, write: bool) -> int:
    """Print both dimensions; optionally re-baseline (shrink only)."""
    counts = fired_events(root)
    declared = declared_events(root)
    missing = never_fired(root)

    print(f"declared event types: {len(declared)}")
    print(f"fired at least once:  {len(declared) - len(missing)}")
    print(f"never fired:          {len(missing)}")
    for event in missing:
        print(f"    {event}")

    print("\npaired-event ratios (reported, not judged):")
    for opener, closer in _PAIRS:
        left, right = counts[opener], counts[closer]
        if not left and not right:
            print(f"    {opener} / {closer}: neither has ever fired")
            continue
        pct = f"{100 * right / left:.1f}%" if left else "n/a"
        print(f"    {opener} {left} / {closer} {right}  ({pct})")
    print(
        "\n  A ratio is evidence for an operator ruling, never a verdict. What a\n"
        "  lopsided pair MEANS depends on which surface emits it — read the\n"
        "  producer before drawing a conclusion."
    )

    if not write:
        return 0

    path = root / _BASELINE_REL
    prior = _baseline_types(_load_baseline(root)) if path.is_file() else set(missing)
    if set(missing) - prior:
        print(
            "Refusing to re-baseline: the never-fired set grew. Disclose the new "
            "type deliberately rather than letting a re-run absorb it.",
            file=sys.stderr,
        )
        return 3
    payload = {
        "schema_version": 1,
        "rationale": (
            "Shrink-only disclosure of ledger event types declared in "
            "src/gzkit/schemas/ledger.json that have never appeared in .gzkit/ledger.jsonl. "
            "An entry records a DISCLOSED absence, never a justified one: the type still "
            "owes either a producer or a retirement. Drain by wiring the producer or "
            "removing the declaration; this list may only decrease."
        ),
        "never_fired": missing,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nre-baselined: {len(missing)} never-fired type(s)")
    return 0


def self_test() -> int:
    """Deterministic checks over the pure helpers — no repo state, no network."""
    failures: list[str] = []

    # Baseline narrowing: a malformed payload reads as empty, which fails the
    # gate closed rather than passing it vacuously.
    if _baseline_types({"never_fired": ["a", "b"]}) != {"a", "b"}:
        failures.append("baseline list must narrow to a str set")
    if _baseline_types({"never_fired": "not-a-list"}) != set():
        failures.append("malformed baseline must read as empty, not raise")
    if _baseline_types({}) != set():
        failures.append("absent key must read as empty")

    # Every pair names two DISTINCT events; a pair of one event with itself
    # would report a meaningless 100% and hide a missing counterpart.
    for opener, closer in _PAIRS:
        if opener == closer:
            failures.append(f"pair {opener} names itself")

    if failures:
        for line in failures:
            print(f"FAIL {line}", file=sys.stderr)
        return 1
    print(f"self-test: {3 + len(_PAIRS)} assertions passed")
    return 0


def _project_root() -> Path | None:
    """Return the project root, or None when cwd is not one.

    ``Path.cwd()`` rather than a positional walk from ``__file__``: the walk is
    the ``Path(__file__).parents`` pattern `gz check`'s parents-lint forbids, and
    cwd is the chore-script precedent (``module-sloc-cap-radon``). It also makes
    the script aimable — a negative control points cwd at a fixture and the real
    code under test runs against it.
    """
    root = Path.cwd()
    return root if (root / "pyproject.toml").is_file() else None


def _mx_demoted(guard_name: str, root: Path) -> bool:
    """Return True when an open MX hangar demotes this guard to advisory.

    ADR-0.0.74 Boundary Invariant #2 -- every fail-closed funnel resolves its
    severity through the shared checkpoint. This chore runs as its own
    pre-commit entrypoint, so it consults the checkpoint itself rather than
    inheriting the seam in ``gzkit.hooks.guards`` (GHI #843).

    The guard name is deliberately ``ledger-vocabulary-inertness`` and NOT
    ``ledger``: ``ledger`` is a ``GATE5_INVARIANTS`` member meaning ledger
    INTEGRITY, which never demotes. This chore audits schema-vocabulary
    disclosure, a different subject that shares a word.

    Fails CLOSED: a broken or half-repaired ``gzkit.mx`` is precisely the state
    MX mode exists to survive, so anything unresolvable blocks rather than
    demotes.
    """
    try:
        from gzkit.mx import checkpoint, levels

        return not checkpoint.blocks(guard_name, levels.ERROR, root)
    except Exception:  # noqa: BLE001 - an unreadable checkpoint must never demote a guard
        return False


def _mx_notice(guard_name: str) -> str:
    """Return the shared operator-facing demotion line, or a local fallback."""
    try:
        from gzkit.mx import checkpoint

        return checkpoint.demote_notice(guard_name)
    except Exception:  # noqa: BLE001 - never crash a hook over its own advisory text
        return f"[MX advisory] guard '{guard_name}' demoted by the open MX hangar marker."


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Ledger vocabulary inertness audit")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--self-test", action="store_true", help="Run helper assertions and exit")
    mode.add_argument("--report", action="store_true", help="Print both dimensions")
    parser.add_argument(
        "--write", action="store_true", help="With --report: re-baseline (shrink only)"
    )
    args = parser.parse_args(argv)

    root = _project_root()
    if root is None:  # pragma: no cover - defensive
        print("project root not found", file=sys.stderr)
        return 2

    if args.self_test:
        return self_test()
    if args.report:
        return report(root, write=args.write)
    rc = enforce(root)
    if rc and _mx_demoted("ledger-vocabulary-inertness", root):
        print(_mx_notice("ledger-vocabulary-inertness"), file=sys.stderr)
        return 0
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
