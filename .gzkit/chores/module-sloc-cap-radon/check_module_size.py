#!/usr/bin/env python3
"""Module-size gate for the ``module-sloc-cap-radon`` chore.

Reads the ``radon_raw_nloc`` ``block`` band from the ONE canonical threshold
table (``.gzkit/rules/complexity-thresholds.json``) and enforces it over
``src/``. The chore previously declared its own ``<=1000 SLOC`` hard cap and
``<=600`` soft cap, which is the drift ``.gzkit/rules/complexity-thresholds.md``
§ Invariant names outright:

    Downstream surfaces ... consume the table; none of them owns its own
    thresholds. A new threshold authority appearing anywhere else is doctrine
    drift by another name.

Neither invented number matched the corpus: the p95 ``block`` band is 1031.9 and
the p90 ``warn`` band is 733.2. The chore's 1000 sat between them, so it failed
one module the corpus does not block (``cli/parser_governance.py`` at 1010) while
presenting itself as the authority.

``radon_raw_nloc`` is radon's ``sloc`` field — see
``gzkit.complexity.measurement._run_radon_raw``, which records
``entry.get("sloc")`` under that metric key. This gate measures the same field
the corpus was measured with, or it would be comparing different quantities.

Shrink-only ratchet
-------------------
Modules already over the band at cutover are listed in
``data/module_size_grandfather.json``. Each entry carries a ``ceiling`` (the
value this gate enforces) alongside ``sloc_at_cutover`` (the dated 2026-08-01
measurement, preserved as a historical record and never read by the gate). The
list is shrink-only, in all five directions:

* a module over the band and NOT listed  -> fail (no new over-band modules)
* a listed module that GREW              -> fail (the ratchet only turns one way)
* a listed module now UNDER the band     -> fail, asking for the entry's removal
* a listed module no longer measured     -> fail, asking for the entry's removal
* an entry LOOSER than its module        -> fail, asking for the entry's tightening

The last two are what make it a ratchet rather than a permanent exemption: a
module that improves must surrender headroom it no longer uses, so the list can
only shrink. Without the fifth, improvement is silently re-consumable — measured
2026-08-22, 928 SLOC across four entries with the gate at exit 0 (GHI #853).
``ADR-0.0.73`` Boundary Invariant #8 requires "a committed baseline the list can
only decrease against", and a baseline nothing reports as un-advanced decreases
only when someone remembers.

The resting state is therefore zero headroom: every entry equals its module's
current SLOC, so a line added to a grandfathered module needs a compensating
extraction in the same commit. That is the ratchet's intended pressure, ruled
explicitly by the operator on 2026-08-22 rather than arriving as a side effect.
An operator may still RAISE an entry (as ``fc3f0956`` did, with the Boundary
Invariant #8 contradiction surfaced first); the raise then shows up as slack the
next time this arm runs, which is what keeps it recorded-and-visible rather than
blocked.

Exit codes: 0 clean, 1 usage/IO error, 3 policy breach.
"""

from __future__ import annotations

import contextlib
import json
import subprocess
import sys
from pathlib import Path

from gzkit.commands.common import get_project_root

_METRIC = "radon_raw_nloc"
# Manifest-based resolution, never `Path(__file__).parents[N]`: this file is
# mirrored to `src/gzkit/chores/` by `gz agent sync control-surfaces`, so its
# depth below the project root differs between the two copies and a positional
# walk is wrong in one of them. `gz lint` fails closed on the positional form
# (hardcoded-root-eradication). Chores execute from the project root.
_PROJECT_ROOT = get_project_root()
_THRESHOLDS = _PROJECT_ROOT / ".gzkit" / "rules" / "complexity-thresholds.json"
_GRANDFATHER = _PROJECT_ROOT / "data" / "module_size_grandfather.json"
_MEASURE_ROOT = _PROJECT_ROOT / "src"

# `.gzkit/rules/cross-platform.md` § Console requires the explicit UTF-8
# reconfigure in a helper script, but `sys.stdout` is not always a real stream:
# `unittest-parallel` swaps in a `StringIO`, which has no `reconfigure`, so an
# unguarded call raises at IMPORT time for anything loading this module under a
# capturing harness. EAFP rather than `hasattr` — the guard form narrows the
# attribute to `object` and breaks ty's own suppression code.
with contextlib.suppress(AttributeError):
    sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[unresolved-attribute]


def _block_band() -> float:
    """Return the canonical ``radon_raw_nloc`` block threshold."""
    table = json.loads(_THRESHOLDS.read_text(encoding="utf-8"))
    for band in table["bands"]:
        if band["metric"] == _METRIC and band["trigger_semantic"] == "block":
            return float(band["absolute_number"])
    raise SystemExit(f"no block band for {_METRIC} in {_THRESHOLDS}")


def _measure() -> dict[str, int]:
    """Return {project-relative posix path: sloc} for every module under src/."""
    completed = subprocess.run(
        ["uvx", "radon", "raw", "--json", str(_MEASURE_ROOT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(f"radon failed (exit {completed.returncode}): {completed.stderr[:400]}")
    payload = json.loads(completed.stdout)
    sizes: dict[str, int] = {}
    for raw_path, entry in payload.items():
        if not isinstance(entry, dict) or "sloc" not in entry:
            continue
        path = Path(raw_path)
        rel = path.relative_to(_PROJECT_ROOT) if path.is_absolute() else path
        sizes[rel.as_posix()] = int(entry["sloc"])
    return sizes


def _grandfathered() -> dict[str, int]:
    """Return {path: ceiling} from the shrink-only ratchet file.

    Reads ``ceiling``, never ``sloc_at_cutover``. The two were one field until
    GHI #853 and they mean different things: the cutover SLOC is a dated
    measurement that must stay true, while the ceiling moves down as the ratchet
    turns. Conflating them made a tightened entry falsify its own field name.
    """
    if not _GRANDFATHER.is_file():
        return {}
    data = json.loads(_GRANDFATHER.read_text(encoding="utf-8"))
    return {e["path"]: int(e["ceiling"]) for e in data.get("grandfathered_modules", [])}


def compute_breaches(block: float, sizes: dict[str, int], listed: dict[str, int]) -> list[str]:
    """Return one prose breach per ratchet violation; empty when clean.

    Pure over its three inputs — no radon, no filesystem — so ``--self-test`` can
    drive every failure direction with synthetic data. A gate whose teeth are only
    ever verified by hand is the shape this whole chore repair exists to remove.

    ``listed`` maps a path to its enforced ``ceiling``, which the ratchet drives
    down toward current SLOC; it is not the dated cutover measurement (GHI #853).
    """
    breaches: list[str] = []
    for path, sloc in sorted(sizes.items(), key=lambda kv: -kv[1]):
        if sloc <= block:
            continue
        if path not in listed:
            breaches.append(
                f"  {path} is {sloc} SLOC, over the {block} block band, and is not "
                f"grandfathered.\n"
                f"    Why: {_METRIC} blocks at {block} (p95, corpus revision 1) per "
                f".gzkit/rules/complexity-thresholds.json — the one canonical table.\n"
                f"    Fix: split it by cohesion. Adding it to "
                f"data/module_size_grandfather.json to go green is the laundering "
                f"ADR-0.0.73 Boundary Invariant #8 forbids."
            )
        elif sloc > listed[path]:
            breaches.append(
                f"  {path} GREW from {listed[path]} to {sloc} SLOC.\n"
                f"    Why: the grandfather list is shrink-only; an entry records the "
                f"ceiling a module may never exceed again.\n"
                f"    Fix: bring it back to <= {listed[path]} SLOC."
            )

    for path, recorded in sorted(listed.items()):
        current = sizes.get(path)
        if current is None:
            breaches.append(
                f"  {path} is grandfathered but no longer measured.\n"
                f"    Fix: drop its entry from data/module_size_grandfather.json."
            )
        elif current <= block:
            breaches.append(
                f"  {path} is now {current} SLOC, under the {block} band "
                f"(entry records {recorded}).\n"
                f"    Why: a module that improved must surrender its grandfather "
                f"entry, or the list stops being a ratchet.\n"
                f"    Fix: drop its entry from data/module_size_grandfather.json."
            )
        elif current < recorded:
            breaches.append(
                f"  {path} has {recorded - current} SLOC of unrecorded slack: the "
                f"entry records {recorded}, the module is {current}.\n"
                f"    Why: an entry records the ceiling a module may never exceed "
                f"again. One above current SLOC licenses that much silent re-growth, "
                f"so the baseline is not one the list can only decrease against "
                f"(ADR-0.0.73 Boundary Invariant #8).\n"
                f'    Fix: tighten its "ceiling" to {current} in '
                f"data/module_size_grandfather.json."
            )

    return breaches


def _self_test() -> int:
    """Drive every ratchet direction with synthetic data; 0 when all have teeth."""
    block = 1000.0
    cases: list[tuple[str, dict[str, int], dict[str, int], bool]] = [
        ("clean: under the band, nothing listed", {"a.py": 900}, {}, False),
        ("clean: over the band and listed at its ceiling", {"a.py": 1500}, {"a.py": 1500}, False),
        ("TEETH: over the band, not listed", {"a.py": 1500}, {}, True),
        ("TEETH: listed module grew past its ceiling", {"a.py": 1600}, {"a.py": 1500}, True),
        ("TEETH: listed module dropped under the band", {"a.py": 900}, {"a.py": 1500}, True),
        ("TEETH: listed module no longer measured", {}, {"a.py": 1500}, True),
        ("TEETH: entry looser than its module", {"a.py": 1200}, {"a.py": 1500}, True),
    ]
    failures = 0
    for label, sizes, listed, expect_breach in cases:
        got = bool(compute_breaches(block, sizes, listed))
        ok = got == expect_breach
        failures += not ok
        print(f"  [{'ok' if ok else 'FAIL'}] {label}")
    if failures:
        print(f"\nself-test FAILED: {failures} case(s)", file=sys.stderr)
        return 3
    print(f"\nself-test PASSED: {len(cases)} cases, all five breach directions fire.")
    return 0


def main(argv: list[str]) -> int:
    """Enforce the canonical module-size block band with a shrink-only ratchet."""
    if argv and argv[0] == "--self-test":
        return _self_test()
    block = _block_band()
    sizes = _measure()
    listed = _grandfathered()
    breaches = compute_breaches(block, sizes, listed)

    over = [p for p, s in sizes.items() if s > block]
    slack = sum(max(0, recorded - sizes[p]) for p, recorded in listed.items() if p in sizes)
    print(f"module-size gate — {_METRIC} block band {block} (p95, corpus revision 1)")
    print(f"  modules measured:  {len(sizes)}")
    print(f"  over the band:     {len(over)}")
    print(f"  grandfathered:     {len(listed)} (shrink-only)")
    print(f"  unrecorded slack:  {slack} SLOC")

    if breaches:
        print("\nPOLICY BREACH:", file=sys.stderr)
        for line in breaches:
            print(line, file=sys.stderr)
        return 3
    print(
        "\nPASS: no un-grandfathered module over the band; no grandfathered module "
        "grew, dropped under the band, went unmeasured, or holds unrecorded slack."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
