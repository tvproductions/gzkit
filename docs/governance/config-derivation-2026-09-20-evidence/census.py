"""Census gzkit's policy/threshold config surface for recorded derivation.

Read-only. Reads the working tree and writes nothing. Unlike the f1 family-share
measurement, this census carries NO hand-classified literals: every figure is
derived from the tree at run time, so re-running it on a later tree reports that
tree rather than replaying this one.

The question is not "who reads this value" -- `data/config_registry.json` already
answers that and fail-closes on an undeclared registry. The question is "where did
this value come from", which no gate asks.

Three fail-closed asserts guard the census against reporting a number it did not
actually derive.
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path

#: Keys a registry may use to carry provenance. `$schema` is excluded: it declares
#: shape, never where a value came from.
PROVENANCE_KEYS = ("$comment", "_comment", "_doc", "doc", "citation", "note", "_note", "rationale")

#: A provenance string counts as CITING AN AUTHORITY only when it points somewhere
#: a reader can go. Prose that explains what a field means is documentation, not
#: derivation -- the distinction this census exists to draw.
AUTHORITY_RE = re.compile(r"(docs/[\w/.-]+\.md|ADR-[\w.]+|GHI #\d+|operator ruling)", re.I)

#: Names that mark a module-level constant as a policy threshold rather than an
#: implementation detail. Deliberately broad; the census reports the population,
#: and a reader judges individual rows.
THRESHOLD_NAME_RE = re.compile(
    r"(MAX|MIN|THRESHOLD|LIMIT|CEILING|FLOOR|BUDGET|CAP|DAYS|COUNT|SIZE|LEN|PCT"
    r"|PERCENT|RATIO|TIMEOUT|DEPTH)",
    re.I,
)

REPO = Path(__file__).resolve().parents[3]


def registry_rows():
    """Classify every top-level data registry by the provenance it records."""
    rows = []
    for path in sorted((REPO / "data").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            rows.append((path.name, "structural", ""))
            continue
        fields = [k for k in payload if k in PROVENANCE_KEYS]
        blob = " ".join(str(payload[k]) for k in fields)
        if not fields:
            state = "absent"
        elif AUTHORITY_RE.search(blob):
            state = "cites-authority"
        else:
            state = "prose-only"
        rows.append((path.name, state, ",".join(fields)))
    return rows


def threshold_constants():
    """Return module-level numeric policy constants defined in `src/gzkit`."""
    found = []
    for path in sorted((REPO / "src" / "gzkit").rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names, value = [node.target.id], node.value
            else:
                continue
            if not isinstance(value, ast.Constant):
                continue
            if isinstance(value.value, bool) or not isinstance(value.value, (int, float)):
                continue
            for name in names:
                if name.isupper() and THRESHOLD_NAME_RE.search(name):
                    found.append((path.relative_to(REPO).as_posix(), name, value.value))
    return found


def duplicate_constants(constants):
    """Group policy constants that share a name across two or more modules."""
    by_name = defaultdict(list)
    for module, name, value in constants:
        by_name[name.lstrip("_")].append((module, value))
    return {n: hits for n, hits in sorted(by_name.items()) if len(hits) > 1}


def main():
    """Print the census, its derivation gap and the duplications it found."""
    rows = registry_rows()
    constants = threshold_constants()
    duplicates = duplicate_constants(constants)

    counts = defaultdict(int)
    for _, state, _ in rows:
        counts[state] += 1
    assert sum(counts.values()) == len(rows), "registry states do not reconcile"
    assert rows, "no registries found -- run this from a gzkit checkout"
    assert constants, "no threshold constants found -- the AST walk is broken"

    untraceable = counts["absent"] + counts["prose-only"] + counts["structural"]

    print("=== data/*.json: does the registry record where its values came from? ===")
    print(f" registries:                  {len(rows)}")
    print(f"   cites an authority:        {counts['cites-authority']}")
    print(f"   no provenance field:       {counts['absent']}")
    print(f"   prose only, no authority:  {counts['prose-only']}")
    print(f"   bare array (cannot carry): {counts['structural']}")
    print(
        f" NO TRACEABLE DERIVATION:     {untraceable}/{len(rows)}"
        f" ({100 * untraceable / len(rows):.0f}%)"
    )

    for label, state in (
        ("NO PROVENANCE FIELD", "absent"),
        ("PROSE ONLY", "prose-only"),
        ("BARE ARRAY", "structural"),
    ):
        named = [r[0] for r in rows if r[1] == state]
        if named:
            print(f"\n  {label} ({len(named)}):")
            for name in named:
                print(f"    {name}")

    print("\n=== src/gzkit: policy thresholds hardcoded in module bodies ===")
    print(f" constants: {len(constants)}")
    print(" `data/config_registry.json` declares itself exhaustive over data/*.json,")
    print(" so none of these are reachable by the gate built to catch unowned config.")

    print(f"\n=== same policy name, two or more homes: {len(duplicates)} ===")
    for name, hits in duplicates.items():
        values = {v for _, v in hits}
        flag = "  <-- VALUES DISAGREE" if len(values) > 1 else ""
        print(f"  {name}{flag}")
        for module, value in hits:
            print(f"    {value!s:>10}  {module}")


if __name__ == "__main__":
    main()
