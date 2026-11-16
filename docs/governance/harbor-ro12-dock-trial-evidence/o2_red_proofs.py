# noqa: INP001 — a dated evidence script run by path, never imported as a package
"""RP-12 O2's dock trial: each test the trial added or changed, shown red against its mutant.

A dated evidence script (`docs/governance/harbor-ro12-contractor-kit.md`, rulings 27 and
90 to 102), the companion of ``o2_mutation_sweep.py`` beside it. The sweep shows which
mutants the test modules kill; this script shows that each test the trial wrote or
changed is red against the mutant it was written for, and green without it. Under
ruling 102 the fifth sweep is O2's last, so a test written after it is witnessed by
its case here alone.

Each case in the record ``o2-red-proofs-2026-11-15.json`` names a swept file, a mutant by
the sweep's own label (built by the sweep's own rule, so a label that no longer names a
mutant of the tree fails the run before anything is graded) and one test by its dotted
name. Each runs through :func:`gzkit.mutation_witness.run_mutation_sweep` in an isolated
copy of the tree, nominating that test alone, so a kill is that test failing on an
assertion with the mutant in place, and its baseline is that test passing without it.
The run writes each case's outcome back into the record.

Usage:

    uv run python docs/governance/harbor-ro12-dock-trial-evidence/o2_red_proofs.py --check
    uv run python docs/governance/harbor-ro12-dock-trial-evidence/o2_red_proofs.py --run
"""

import json
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(REPO / "src"), str(HERE)]

import o2_mutation_sweep as sweep  # noqa: E402

from gzkit.mutation_witness import Mutation, run_mutation_sweep  # noqa: E402

RECORD = HERE / "o2-red-proofs-2026-11-15.json"
WORKERS = 4


def _mutants(cases: list[dict[str, str]]) -> dict[tuple[str, str], Mutation]:
    """Return each case's mutant, built by the sweep's rule.

    Raises:
        SystemExit: a case names a mutant the sweep's rule no longer builds.

    """
    built: dict[tuple[str, str], Mutation] = {}
    for relative in sorted({case["file"] for case in cases}):
        _, planned = sweep._planned(relative)  # noqa: SLF001
        for mutation in planned:
            built[relative, mutation.label.split(":", 1)[1]] = mutation
    missing = [case for case in cases if (case["file"], case["mutant"]) not in built]
    if missing:
        msg = f"cases naming no mutant of the tree: {missing}"
        raise SystemExit(msg)
    return built


def _run(group: list[dict[str, str]], built: dict[tuple[str, str], Mutation]) -> list[dict]:
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sweep._copy(root)  # noqa: SLF001
        for case in group:
            mutation = built[case["file"], case["mutant"]]
            test = case["test"]
            result = run_mutation_sweep(
                root,
                root / case["file"],
                [mutation.model_copy(update={"expected_tests": [test]})],
                sweep._command([test]),  # noqa: SLF001
            )
            witness = result.witnesses[0]
            results.append({
                **case,
                "baseline_green": result.baseline_green,
                "outcome": witness.outcome,
                "failure_class": witness.failure_class,
            })
    return results


def main(argv: list[str]) -> int:
    """Check every case names a mutant of the tree; with ``--run``, run and record each."""
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    cases: list[dict[str, str]] = [
        {key: case[key] for key in ("file", "mutant", "test")} for case in record["cases"]
    ]
    built = _mutants(cases)
    if "--run" not in argv:
        sys.stdout.write(f"{len(cases)} cases, each naming a mutant the sweep's rule builds\n")
        return 0
    groups = [cases[i::WORKERS] for i in range(WORKERS)]
    with ThreadPoolExecutor(WORKERS) as pool:
        ran = [row for rows in pool.map(lambda g: _run(g, built), groups) for row in rows]
    order = {(c["file"], c["mutant"], c["test"]): i for i, c in enumerate(cases)}
    ran.sort(key=lambda row: order[row["file"], row["mutant"], row["test"]])
    record["cases"] = ran
    record["counts"] = dict(
        Counter(f"{row['outcome']}/{row['failure_class'] or '-'}" for row in ran)
    )
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for row in ran:
        if not (row["baseline_green"] and row["outcome"] == "killed"):
            sys.stdout.write(f"NOT A RED PROOF: {row}\n")
    sys.stdout.write(f"{record['counts']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
