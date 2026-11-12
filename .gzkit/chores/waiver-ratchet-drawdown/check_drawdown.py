#!/usr/bin/env python
"""Measure how far each shrink-ratchet surface has been drawn down.

Reads ``data/waiver_ratchet_registry.json`` and, for every surface declaring the
``shrink-ratchet`` mechanism, counts its live entries the way
``gz validate --waiver-ratchet`` does (the length of the collection at
``entries_path``) and compares the count with the committed ``baseline_count``.
The gate refuses growth; this chore reports what the gate cannot see: a
surface that never shrinks.

Read-only. It never edits a baseline, a waiver file or the registry.

Usage:
    uv run python .gzkit/chores/waiver-ratchet-drawdown/check_drawdown.py --report
    uv run python .gzkit/chores/waiver-ratchet-drawdown/check_drawdown.py --self-test
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

REGISTRY_REL = Path("data") / "waiver_ratchet_registry.json"


def _out(text: str) -> None:
    sys.stdout.write(text + "\n")


def _err(text: str) -> None:
    sys.stderr.write(text + "\n")


AT_ZERO = "at zero"
OVER = "over baseline"
TIGHTEN = "drawn down; baseline can tighten"
STALLED = "not drawn down"


def classify(live: int, baseline: int) -> str:
    """Name a surface's drawdown state from its live and baseline counts."""
    if live > baseline:
        return OVER
    if live == 0:
        return AT_ZERO
    if live < baseline:
        return TIGHTEN
    return STALLED


def count_live(project_root: Path, surface: dict) -> int | None:
    """Count a surface's entries, as the gate does; None when unreadable."""
    path = project_root / str(surface.get("data_file", ""))
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError, json.JSONDecodeError:
        return None
    entries_path = str(surface.get("entries_path", ""))
    collection = (
        payload
        if not entries_path
        else (payload.get(entries_path) if isinstance(payload, dict) else None)
    )
    if isinstance(collection, (list, dict)):
        return len(collection)
    return None


def measure(project_root: Path) -> list[dict]:
    """One row per shrink-ratchet surface: file, live, baseline, state."""
    registry = json.loads((project_root / REGISTRY_REL).read_text(encoding="utf-8"))
    rows = []
    for surface in registry.get("surfaces", []):
        if surface.get("mechanism") != "shrink-ratchet":
            continue
        baseline = surface.get("baseline_count")
        live = count_live(project_root, surface)
        state = (
            "unreadable"
            if live is None or not isinstance(baseline, int)
            else classify(live, baseline)
        )
        rows.append(
            {
                "data_file": surface.get("data_file"),
                "live": live,
                "baseline": baseline,
                "state": state,
            }
        )
    return rows


def report(rows: list[dict]) -> str:
    """Render the rows and a summary as plain text."""
    lines = ["| Surface | Live | Baseline | State |", "|---|---|---|---|"]
    lines += [
        f"| `{r['data_file']}` | {r['live']} | {r['baseline']} | {r['state']} |" for r in rows
    ]
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    live_total = sum(r["live"] or 0 for r in rows)
    base_total = sum(r["baseline"] if isinstance(r["baseline"], int) else 0 for r in rows)
    lines.append("")
    lines.append(
        f"{len(rows)} shrink-ratchet surfaces; {live_total} live entries "
        f"against {base_total} baselined."
    )
    lines.append("; ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    return "\n".join(lines)


def self_test() -> int:
    """Check classification and counting on a synthetic registry; no repo state."""
    cases = [
        ((0, 0), AT_ZERO),
        ((0, 5), AT_ZERO),
        ((3, 5), TIGHTEN),
        ((5, 5), STALLED),
        ((6, 5), OVER),
    ]
    for (live, base), want in cases:
        got = classify(live, base)
        if got != want:
            _err(f"self-test FAILED: classify({live}, {base}) = {got!r}, expected {want!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "data").mkdir()
        (root / "data" / "a.json").write_text(json.dumps({"waivers": ["x", "y"]}), encoding="utf-8")
        (root / "data" / "b.json").write_text(json.dumps(["x"]), encoding="utf-8")
        registry = {
            "surfaces": [
                {
                    "data_file": "data/a.json",
                    "mechanism": "shrink-ratchet",
                    "entries_path": "waivers",
                    "baseline_count": 2,
                },
                {
                    "data_file": "data/b.json",
                    "mechanism": "shrink-ratchet",
                    "entries_path": "",
                    "baseline_count": 4,
                },
                {"data_file": "data/c.json", "mechanism": "closed-set-lock"},
            ]
        }
        (root / REGISTRY_REL).write_text(json.dumps(registry), encoding="utf-8")
        rows = measure(root)
        states = [(r["data_file"], r["state"]) for r in rows]
        want_states = [("data/a.json", STALLED), ("data/b.json", TIGHTEN)]
        if states != want_states:
            _err(f"self-test FAILED: measure gave {states}, expected {want_states}")
            return 1
    _out("self-test passed: 5 classifications, 2 surfaces measured, closed-set lock skipped")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--self-test", action="store_true", help="run the detector semantics on synthetic input"
    )
    parser.add_argument(
        "--report", action="store_true", help="print the drawdown table (the default)"
    )
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    rows = measure(Path.cwd())
    _out(report(rows))
    unreadable = [r["data_file"] for r in rows if r["state"] == "unreadable"]
    if unreadable:
        _err(
            f"Unreadable surfaces: {', '.join(map(str, unreadable))}. The registry names a "
            "file or entries_path the chore cannot count (ADR-0.0.73 Boundary Invariant #8 "
            "needs a countable list). Run `uv run gz validate --waiver-ratchet` for the "
            "gate's diagnosis."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
